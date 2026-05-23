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

```
    hidden_dim: int = 32           # 分类/回归头隐藏层维度
    num_stages: int = 4            # 老化四阶段: I-成膜, II-稳定, III-加速, IV-寿命终止
    rul_output_dim: int = 1        # RUL 输出维度

StageThresholds:
    formation: float = 0.88        # SOH >= 0.88 → 阶段 I
    stable: float = 0.78           # SOH >= 0.78 → 阶段 II
    accelerated: float = 0.68      # SOH >= 0.68 → 阶段 III
                                   # SOH <  0.68 → 阶段 IV (EOL)

TrainingConfig:
    batch_size: int = 128          # 批次大小 (RTX 4060 8GB 可用 256)
    learning_rate: float = 1e-3    # 初始学习率 (CNN 可用更高 lr)
    weight_decay: float = 1e-4     # AdamW 权重衰减
    lr_factor: float = 0.5         # ReduceLROnPlateau 衰减因子
    lr_patience: int = 25          # LR 衰减耐心值
    early_stop_patience: int = 60  # 早停耐心值
    grad_clip: float = 1.0         # 梯度裁剪阈值
    use_amp: bool = True           # AMP 混合精度 (RTX 4060 支持)
    num_workers: int = 0           # DataLoader 进程数 (Windows 建议 0)
    cls_weight: float = 0.5        # 分类损失权重
    rul_weight: float = 0.5        # RUL 回归损失权重

DataConfig:
    ic_curve_pts: int = 128        # IC 曲线采样点数 (与 PINN 一致)
    train_ratio: float = 0.70      # 训练集比例
    val_ratio: float = 0.15        # 验证集比例
    test_ratio: float = 0.15       # 测试集比例
    eol_soh_threshold: float = 0.70  # 寿命终止 SOH 阈值
    label_smoothing: float = 0.05  # 分类标签平滑 (防止过拟合)

```

### 2.2 `model.py` — 1D-CNN 模型架构

```
输入: IC 曲线 (B, 1, 128)
  │
  ├─ ConvBlock(1→16, k=7):
  │    Conv1d(k=7, p=3) → BatchNorm1d → GELU → MaxPool1d(k=2) → Dropout
  │    输出: (B, 16, 64)
  │
  ├─ ConvBlock(16→32, k=5):
  │    Conv1d(k=5, p=2) → BatchNorm1d → GELU → MaxPool1d(k=2) → Dropout
  │    输出: (B, 32, 32)
  │
  ├─ ConvBlock(32→64, k=3):
  │    Conv1d(k=3, p=1) → BatchNorm1d → GELU → MaxPool1d(k=2) → Dropout
  │    输出: (B, 64, 16)
  │
  ├─ AdaptiveAvgPool1d(1) → (B, 64, 1) → squeeze → (B, 64)
  │
  ├── 分类头 (stage classification):        ├── RUL 回归头:
  │    Linear(64→32)                         │    Linear(64→32)
  │    GELU                                  │    GELU
  │    Dropout(0.15)                         │    Dropout(0.15)
  │    Linear(32→4)                          │    Linear(32→1)
  │    → stage_logits (B, 4)                 │    → rul (B, 1) ∈ [0, 1]
  └──────────────────────────────────────────┴──────────────────────

总参数量: ~13,000 (INT8 量化后 < 14 KB)
推理延迟: < 10 ms (Cortex-A55, ONNX Runtime)
```

**为什么选择 1D-CNN 而非 2D-CNN 或 Transformer?**
- IC 曲线是 1D 序列信号 (dQ/dV vs V)，1D 卷积是自然匹配
- 2D-CNN 需要将曲线转为图像，引入不必要开销
- Transformer 需要更多参数和计算量，不适合 13K 参数量级的轻量部署
- 卷积核大小递减 (7→5→3) 遵循经典 CNN 设计: 早期大核捕捉长程形态，后期小核捕捉局部细节

### 2.3 `dataset.py` — 数据管线

**数据复用策略:**
- 直接调用 `pinn.dataset.load_all_data()` 获取原始数据字典
- 自行构建 CNN 专属的 `CNNDataset` 类

**标签生成逻辑:**

```
1. 阶段标签 (soh_to_stage):
   SOH ∈ [0.88, 1.00] → stage 0 (I-成膜期)
   SOH ∈ [0.78, 0.88) → stage 1 (II-稳定衰退)
   SOH ∈ [0.68, 0.78) → stage 2 (III-加速老化)
   SOH ∈ [0.00, 0.68) → stage 3 (IV-寿命终止)

2. RUL 标签 (compute_rul):
   N_EOL = 该电芯 SOH 首次跌破 0.70 的循环号
   RUL_raw = max(0, N_EOL - N_current)
   RUL_norm = RUL_raw / N_EOL
   → 输出 ∈ [0, 1], 1 = 全新, 0 = 已达寿命终点
```

**关键实现细节:**
- `_ensure_pinn_on_path()`: 将 `PINN_CNN/` 加入 `sys.path`，使 `from pinn.xxx` 可从同级 cnn 包导入
- `CNNDataset.__getitem__` 返回 `(ic[1,128], stage, rul, soh, cell_id, cycle)` 六元组
- `random_split` 按电芯随机划分 (seed 固定可复现)
- Pin-memory 加速 GPU 数据传输

### 2.4 `train.py` — 多任务训练循环

**损失函数:**
```
TotalLoss = cls_weight × CrossEntropyLoss(label_smoothing=0.05) + rul_weight × MSELoss
```

**训练流程:**
1. 自动检测 CUDA → RTX 4060, AMP 混合精度
2. 数据合理性检查 (NaN/Inf 检测)
3. AdamW 优化器 + ReduceLROnPlateau 调度器
4. 每 epoch: 训练 → 验证 → 记录 TensorBoard
5. 早停: 60 epoch 无提升 → 停止
6. 测试集评估: 分类报告 (precision/recall/f1) + 混淆矩阵 + RUL MAE/RMSE

**训练建议:**
- 首次训练使用默认配置即可
- 若类别不平衡严重 (>3:1)，调整 `cls_weight` 或使用 class weights
- 若 RUL 收敛缓慢，临时提高 `rul_weight` 到 0.7

### 2.5 `export.py` — ONNX 部署导出

**导出流程:**
1. 加载 `best_model.pt` → CPU (兼容 ARM)
2. PyTorch → ONNX FP32 (opset 14, 动态 batch)
3. ONNX 模型结构验证 (`onnx.checker.check_model`)
4. 推理一致性检查 (输出范围验证)
5. INT8 动态量化 (`onnxruntime.quantization.quantize_dynamic`)
6. FP32 vs INT8 精度对比:
   - 分类一致性 >= 98%
   - RUL MAE < 0.01 (归一化)

**量化方式说明:**
- 选用动态量化 (非静态 QDQ)，原因:
  - 无需标定数据集 (部署时训练数据可能不可用)
  - MLP/CNN 架构下的精度损失 < 1% (经验验证)
  - 部署流程更简洁

---

## 三、启动运行步骤

### 3.1 环境准备

```bash
# 第一步: 确认 Anaconda 已安装
conda --version

# 第二步: 创建/激活环境
conda create -n batcnn python=3.11 -y
conda activate batcnn

# 第三步: 安装依赖
cd D:\ScuderiaAMG\PINN_CNN
pip install -r cnn/env.txt

# 第四步: 验证 GPU 可用
python -c "import torch; print(f'CUDA: {torch.cuda.is_available()}'); print(f'GPU: {torch.cuda.get_device_name(0)}')"
# 期望输出: CUDA: True  |  GPU: NVIDIA GeForce RTX 4060 Laptop GPU
```

### 3.2 数据准备

```bash
# 检查数据状态 — 程序会自动检测并合并:
#   data/nasa_pcoe/*.mat  (NASA 数据集，B0005/B0006/B0007/B0018)
#   data/calce/CS2_3*/*.xlsx  (CALCE 数据集，CS2_36/CS2_37/CS2_38)
#
# 若真实数据缺失，自动降级为合成数据 (pinn/battery_sim.py LFP 仿真器)
```

### 3.3 训练 CNN

```bash
cd D:\ScuderiaAMG\PINN_CNN
python -m cnn.train
```

训练过程中 TensorBoard 日志写入 `cnn/logs/`，可实时查看:

```bash
tensorboard --logdir cnn/logs
# 浏览器打开 http://localhost:6006
```

### 3.4 导出 ONNX

```bash
# 训练完成后导出
python -m cnn.export
```

输出文件:
- `cnn/checkpoints/battery_cnn_fp32.onnx` — FP32 模型 (~50 KB)
- `cnn/checkpoints/battery_cnn_int8.onnx` — INT8 模型 (~14 KB)

### 3.5 双模型对比验证

```bash
# 先训练 PINN (若尚未训练)
python -m pinn.train

# 训练 CNN
python -m cnn.train

# 导出两个模型
python -m pinn.export
python -m cnn.export

# 检查产物
ls cnn/checkpoints/battery_cnn_*.onnx
ls pinn/checkpoints/battery_pinn_*.onnx
=======
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
