# CNN 残差1D-CNN 电池老化三阶段分类与 RUL 预测 — 配置与运行指南

## 目录结构

```
PINN_CNN/
├── pinn/                       ← PINN 快速 SOH 筛查 (已有)
├── cnn/                        ← **CNN 精准评估**
│   ├── __init__.py
│   ├── config.py               Slim模型 + 3阶段阈值 + 数据增强
│   ├── model.py                残差1D-CNN: Stem + 3×ResBlock + GAP (~40K参数)
│   ├── dataset.py              双通道构建 + 质量过滤 + 增强 + cell-based split
│   ├── train.py                多任务训练 + 类别加权 + 评估
│   ├── export.py               ONNX FP32 → INT8 (目标 Cortex-A55)
│   ├── env.txt                 Conda 环境 (batcnn)
│   └── CONFIG.md               本文件
└── data/                       共享数据集 (NASA PCoE + CALCE)
```

---

## 一、三阶段分类定义

```
阶段 0 — healthy   (健康):    SOH ≥ 0.82
阶段 1 — degrading (衰退):    0.82 > SOH ≥ 0.70
阶段 2 — EOL       (寿命终止): SOH < 0.70
```

**为什么三阶段优于四阶段：**
- 原阶段 I+II 的 IC 曲线形态高度相似 (仅峰值高度微弱下降)，CNN 无论多深都无法可靠区分
- 合并后三个阶段的 IC 形态差异明显：健康(清晰峰)→衰退(峰降+偏移)→报废(峰消失)
- 对工业场景足够：产线分选正品/次品，回收分选可梯次利用/报废

---

## 二、文件详解

### 2.1 `config.py` — 配置中心

```python
ModelConfig:                          # Slim残差1D-CNN (~40K params)
    in_channels: int = 2              # ch1: IC曲线, ch2: IC梯度
    conv_filters: tuple = (16, 32, 48)      # 3层残差块通道数
    conv_kernels: tuple = (7, 7, 5)         # 大核起步
    dropout: float = 0.2
    head_hidden: int = 24
    num_stages: int = 3               # healthy / degrading / EOL

StageThresholds:
    healthy: float = 0.82             # SOH >= 0.82 → healthy
    degrading: float = 0.70           # SOH >= 0.70 → degrading
                                      # SOH <  0.70 → EOL

TrainingConfig:
    batch_size: int = 128
    epochs: int = 600
    learning_rate: float = 8e-4
    early_stop_patience: int = 100
    cls_weight: float = 0.55
    rul_weight: float = 0.45

AugConfig:                            # 仅训练集增强
    gaussian_noise_std: float = 0.03
    scale_range: tuple = (0.85, 1.15)
    shift_max: int = 6

DataConfig:
    ic_curve_pts: int = 128
    train_ratio: float = 0.70
    eol_soh_threshold: float = 0.70
    label_smoothing: float = 0.08
```

### 2.2 `model.py` — 残差 1D-CNN (~40K 参数)

```
输入: (B, 2, 128) — IC曲线 + IC梯度 双通道

Stem:
  Conv1d(2→16, k=7, s=2) → BN → GELU
  输出: (B, 16, 64)                            ← stride=2 快速降采样

ResidualBlock(16→32, k=7):                     ← 通道扩展, 1×1Conv shortcut
  ┌─ Conv1d(16→32, k=7)→BN→GELU→Drop(0.2) ─┐
  │  Conv1d(32→32, k=7)→BN                   │
  └── 1×1Conv shortcut (16→32) ──────────────┘ → + → GELU → Drop(0.1) → MaxPool
  输出: (B, 32, 32)

ResidualBlock(32→48, k=5):                     ← 通道扩展, 1×1Conv shortcut
  输出: (B, 48, 16)

ResidualBlock(48→48, k=5):                     ← 同通道, identity shortcut
  输出: (B, 48, 8)

AdaptiveAvgPool1d(1) → (B, 48)

├── 分类头:                    ├── RUL回归头:
│    Linear(48→48)              │    Linear(48→48)
│    GELU + Dropout(0.2)        │    GELU + Dropout(0.2)
│    Linear(48→24)              │    Linear(48→24)
│    GELU + Dropout(0.1)        │    GELU + Dropout(0.1)
│    Linear(24→3)               │    Linear(24→1)
│    → logits (B, 3)            │    → RUL (B, 1) ∈ [0,1]
└───────────────────────────────┴───────────────────

总参数量: ~40,000  |  INT8量化: < 40 KB  |  推理: < 15 ms (Cortex-A55)
```

**ResidualBlock 设计:**
```
identity shortcut: 当 in_ch == out_ch 时直接加和
1×1 Conv shortcut: 当 in_ch != out_ch 时对齐通道数
每个 block 末尾 MaxPool(k=2) 逐步降采样: 128→64→32→16→8
```

### 2.3 `dataset.py` — 数据管线

**双通道构建:**
```
Channel 1: IC(dQ/dV)       → StandardScaler → clip[-5,5]
Channel 2: d(IC)/dV        → 自归一化 → StandardScaler → clip[-5,5]
           (梯度过零点 = IC峰值位置, 该位置随老化漂移)
```

**质量过滤:** 剔除全零、数值爆炸、完全平坦的 IC 曲线

**数据增强 (仅训练集):**
1. 高斯噪声 N(0, 0.03) — 提高鲁棒性
2. 随机缩放 0.85x~1.15x — 模拟电流波动
3. 电压轴平移 ±6点 — 模拟采样漂移

**划分策略:**
- 按电芯 ID 划分 (cell-based split) — 防止数据泄漏
- 每集合至少 1 个电芯
- 训练集自动计算类别权重 (inverse frequency)

**标签:**
```
阶段: SOH ≥ 0.82 → 0(healthy),  0.82 > SOH ≥ 0.70 → 1(degrading),  SOH < 0.70 → 2(EOL)
RUL:  max(0, N_EOL - N_current) / N_EOL  (每电芯独立, ∈ [0,1])
```

### 2.4 `train.py` — 多任务训练

**损失:**
```
TotalLoss = 0.55 × CrossEntropyLoss(weight=class_weights, label_smoothing=0.08)
          + 0.45 × MSELoss(RUL)
```

**流程:** CUDA检测 → AdamW(8e-4) → AMP混合精度 → ReduceLROnPlateau → 早停(100) → 测试集评估

### 2.5 `export.py` — 部署导出

```
best_model.pt → ONNX FP32 (opset14) → INT8动态量化
  ├─ battery_cnn_fp32.onnx  (~80 KB)
  ├─ battery_cnn_int8.onnx  (~40 KB)
  └─ ic_scaler.pkl          (部署时对 IC/梯度做标准化)
```

---

## 三、启动运行

```bash
conda activate batcnn
cd D:\ScuderiaAMG\PINN_CNN
python -m cnn.train          # 训练
python -m cnn.export         # 导出ONNX
tensorboard --logdir cnn/logs  # 监控
```

---

## 四、超参数调优

| 现象 | 方向 |
|---|---|
| 某阶段召回率低 | 调整 `StageThresholds` 均衡样本分布 |
| 过拟合 (train/val差距>15%) | 增大 dropout 到 0.3, 增大 noise_std |
| RUL 误差大 | 增大 `rul_weight` 到 0.55 |
| 早停过早 | 增大 `early_stop_patience` 到 150 |

---

## 五、与 PINN 模型的关系

```
                    RA8 (Cortex-M85)
                    ├── 电压/电流/温度 原始采集
                    ├── 卡尔曼滤波
                    └── IC/DV 曲线特征提取
                           │
             高速通信 (QSPI/USB HS)
                           │
              ┌────────────┴────────────┐
              ▼                         ▼
         PINN 路径                   CNN 路径 (3-stage)
    (RZ/G2L Cortex-A55)        (RZ/G2L Cortex-A55)
              │                         │
    输入: 132-d 扁平特征         输入: (2,128) IC+梯度双通道
    模型: MLP + ResBlock         模型: Stem + 3×ResBlock + GAP
    参数量: ~25K                 参数量: ~40K
    输出: SOH ∈ [0,1]            输出: Healthy/Degrading/EOL + RUL
    延迟: < 15 ms                延迟: < 15 ms
              │                         │
    适用: 产线快速筛查          适用: 梯次利用分选/回收评估
```

**两种模型独立运行，针对不同场景分别调用，不构成级联关系。**
