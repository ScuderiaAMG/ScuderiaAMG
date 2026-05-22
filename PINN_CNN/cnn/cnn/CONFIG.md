# CNN 1D-CNN 电池老化分类与剩余寿命预测 — 配置与运行指南

## 目录结构

```
PINN_CNN/
├── pinn/                       ← PINN 快速 SOH 筛查 (已有)
│   ├── model.py                BatteryPINN: MLP + 残差块, ~25K 参数
│   ├── train.py                训练: MSE + 物理损失 (ECM/平滑性/单调性)
│   ├── dataset.py              数据管线: NASA PCoE + CALCE + 合成数据
│   ├── physics.py              ECM一致性/退化平滑性/单调性约束
│   ├── export.py               ONNX FP32 → INT8 量化
│   ├── config.py               PINN 专属配置
│   ├── battery_sim.py          LFP 18650 2-RC ECM 模拟器
│   ├── real_data.py            NASA .mat + CALCE .xlsx 加载器
│   └── env.txt                 Conda 环境配置
│
├── cnn/                        ← **CNN 精准评估 (新建)**
│   ├── __init__.py
│   ├── config.py               CNN 专属配置 (模型架构/阶段阈值/训练参数)
│   ├── model.py                1D-CNN: Conv1D 骨干 + 双任务头 (~13K 参数)
│   ├── dataset.py              CNN 数据集: 阶段标签 + RUL 标签生成
│   ├── train.py                多任务训练循环 + 评估
│   ├── export.py               ONNX FP32 → INT8 量化 (目标 Cortex-A55)
│   ├── env.txt                 Conda 环境配置 (batcnn 独立环境)
│   └── CONFIG.md               本文件
│
└── data/                       共享数据集
    ├── nasa_pcoe/              NASA 电池老化 .mat 文件
    ├── calce/                  CALCE 电池老化 .xlsx 文件
    └── README.md
```

---

## 一、CNN 在双 AI 模型中的角色

```
双AI模型 SOH评估
├── PINN (快速筛查)            CNN (精准评估)
│   ├── 8-10 分钟数据          ├── 完整充电周期
│   ├── SOH 回归 [0, 1]        ├── 老化阶段分类 (I-IV)
│   ├── 物理约束引导            ├── RUL 剩余寿命预测
│   ├── 输入: 132-d 特征向量    ├── 输入: IC 曲线 (1, 128) 原始 1D 信号
│   └── 产线快速筛查            └── 实验室验证 / 梯次利用分选
│
└── 部署芯片: RZ/G2L Cortex-A55 (ONNX + INT8 量化)
```

**核心设计逻辑:**
- PINN 将 IC 曲线扁平化为 132-d 向量，丢失了曲线的空间/局部形态信息
- CNN 直接对原始 1D 曲线进行卷积，捕捉 **IC 峰值位移、峰值高度变化、曲线形状畸变** 等与老化机制高度相关的局部形态特征
- 二者互补：PINN 求快 (8 分钟)，CNN 求准 (完整周期)

---

## 二、文件详解

### 2.1 `config.py` — 配置中心

```python
ModelConfig:
    in_channels: int = 1           # IC 曲线单通道输入
    conv_filters: tuple = (16, 32, 64)   # 三层卷积通道数
    conv_kernels: tuple = (7, 5, 3)      # 三层卷积核大小
    dropout: float = 0.15          # Dropout 比率
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
    epochs: int = 500              # 最大训练轮数
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
```

---

## 四、超参数调优指南

| 现象 | 原因 | 调整方向 |
|---|---|---|
| 分类准确率 < 60% | 类别不平衡 或 学习率过高 | 增大 `label_smoothing`, 降低 lr 到 5e-4 |
| RUL MAE > 0.15 | RUL 头收敛困难 | 增大 `rul_weight` 到 0.7, 降低 `cls_weight` 到 0.3 |
| 验证损失震荡 | 批次太小 或 学习率过高 | 增大 `batch_size` 到 256, 降低 lr |
| 早停过早 (< 50 epoch) | `early_stop_patience` 太小 | 增大到 80-100 |
| GPU 显存不足 | 批次过大 | 减小 `batch_size` 到 64 |
| 阶段 I/IV 召回率低 | 类别样本数差异大 | 调整 `StageThresholds` 阈值使分布更均衡 |

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
         PINN 路径                   CNN 路径
    (RZ/G2L Cortex-A55)        (RZ/G2L Cortex-A55)
              │                         │
    输入: 132-d 扁平特征         输入: (1, 128) IC 曲线
    模型: MLP + ResBlock         模型: 1D Conv 骨干
    参数量: ~25K                 参数量: ~13K
    输出: SOH ∈ [0,1]            输出: Stage (0-3) + RUL ∈ [0,1]
    延迟: < 15 ms                延迟: < 10 ms
              │                         │
    适用: 产线快速筛查          适用: 梯次利用分选/实验室验证
```

**两种模型独立运行，针对不同场景分别调用，不构成级联关系。**
