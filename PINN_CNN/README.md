# 基于 PINN+CNN 双 AI 模型的锂电池老化测试与数据黑匣子系统

## 项目概述

本项目围绕瑞萨 RA8 (Cortex-M85) + RZ/G2L (Cortex-A55) 双芯架构，构建双 AI 模型电池 SOH 评估系统：

| 模型 | 部署芯片 | 任务 | 输入 | 输出 | 性能 |
|---|---|---|---|---|---|
| **PINN** | RZ/G2L | SOH 回归 | 132-d 特征向量 | SOH ∈ [0, 1] | MAE < 1%, R² > 0.99 |
| **CNN** | RZ/G2L | 3 阶段分类 + RUL | (2, 128) IC 双通道 | healthy/degrading/EOL + RUL | 准确率 70% |

```
产线快速筛查 (8 分钟数据) → PINN → SOH 值
梯次利用分选 (完整充电)   → CNN  → 健康等级 + 剩余寿命
```

---

## 目录结构

```
PINN_CNN/
├── pinn/                       PINN 物理信息神经网络 (快速筛查)
│   ├── config.py               训练/模型/物理约束超参数
│   ├── model.py                MLP + 残差块 (~53K 参数)
│   ├── dataset.py              数据管线 + 多源合并 + 特征构建
│   ├── physics.py              物理损失: ECM一致性/退化平滑性/单调性
│   ├── train.py                训练入口 + TensorBoard 日志
│   ├── export.py               ONNX FP32 → INT8 量化导出
│   ├── battery_sim.py          LFP 18650 2-RC ECM 合成数据生成器
│   ├── real_data.py            NASA PCoE (.mat) + CALCE (.xlsx) 数据加载器
│   ├── demo.py                 NASA .mat 结构诊断工具
│   └── env.txt                 Conda 环境 (batpinn)

├── cnn/                        CNN 残差卷积网络 (精准评估)
│   ├── config.py               模型/3阶段阈值/数据增强超参数
│   ├── model.py                残差1D-CNN: Stem + 3×ResBlock + GAP (~44K 参数)
│   ├── dataset.py              双通道构建 + 质量过滤 + 增强 + cell-based split
│   ├── train.py                多任务训练 + 类别加权 + 早停
│   ├── export.py               ONNX FP32 → INT8 量化导出
│   ├── env.txt                 Conda 环境 (batcnn)
│   └── CONFIG.md               CNN 详细配置与架构文档

├── deploy/                     部署产物与推理脚本
│   ├── inference.py            RZ/G2L 双模型推理入口
│   └── requirements.txt        ARM aarch64 端依赖

├── data/                       共享数据集
│   ├── nasa_pcoe/              NASA PCoE .mat 文件 (B0005/6/7/18)
│   └── calce/                  CALCE Arbin .xlsx 文件 (CS2_35/36/37/38)

└── README.md                   本文件
```

---

# 第一部分：Windows 11 训练服务器部署

## 1.1 硬件要求

| 组件 | 配置 |
|---|---|
| GPU | NVIDIA RTX 4060 Laptop (8 GB VRAM, CUDA 12.4) |
| CPU | Intel Core i7-14700HX |
| RAM | 64 GB DDR5 |
| 系统 | Windows 11 |
| Python | Anaconda 3, Python 3.11 |

## 1.2 环境安装

```bash
# PINN 环境
conda create -n batpinn python=3.11 -y
conda activate batpinn
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu124
pip install -r pinn/env.txt

# CNN 环境
conda create -n batcnn python=3.11 -y
conda activate batcnn
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu124
pip install -r cnn/env.txt
```

> `batpinn` 与 `batcnn` 依赖完全一致，分两个环境仅为隔离。也可只用一个。

## 1.3 验证 CUDA

```bash
python -c "import torch; print(f'CUDA: {torch.cuda.is_available()}'); print(f'GPU: {torch.cuda.get_device_name(0)}')"
# 期望: CUDA: True  |  GPU: NVIDIA GeForce RTX 4060 Laptop GPU
```

若输出 `CUDA: False`，说明装的是 CPU 版 PyTorch。重新执行：

```bash
pip uninstall torch torchvision torchaudio -y
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu124
```

## 1.4 数据集

NASA PCoE 和 CALCE 数据集已部署在 `data/` 下：

```
data/nasa_pcoe/B0005.mat, B0006.mat, B0007.mat, B0018.mat
data/calce/CS2_35/, CS2_36/, CS2_37/, CS2_38/
```

程序自动检测并合并数据源。若真实数据缺失，自动降级为 `pinn/battery_sim.py` 生成的 LFP 合成数据。

## 1.5 训练 PINN (快速筛查模型)

```bash
conda activate batpinn          # 或 batcnn
cd D:\ScuderiaAMG\PINN_CNN
python -m pinn.train
```

训练输出：

```
Device: cuda
  GPU: NVIDIA GeForce RTX 4060 Laptop GPU
  VRAM: 8.0 GB
Training: 600 epochs  |  batch=256
...
Best model: pinn\checkpoints\best_model.pt
  Test MAE:  0.89% SOH
  Test R²:   0.995
```

## 1.6 训练 CNN (精准评估模型)

```bash
conda activate batcnn
cd D:\ScuderiaAMG\PINN_CNN
python -m cnn.train
```

训练输出：

```
Device: cuda
  GPU: NVIDIA GeForce RTX 4060 Laptop GPU
Training: 600 ep  batch=128
3-stage: healthy(SOH≥0.82)  degrading(0.82>SOH≥0.70)  EOL(SOH<0.70)
...
Best model: cnn\checkpoints\best_model.pt
  Test Accuracy: 70.3%
  Test RUL MAE:  0.211
```

## 1.7 导出 ONNX

```bash
python -m pinn.export    # → pinn\checkpoints\battery_pinn_int8.onnx (83 KB)
python -m cnn.export     # → cnn\checkpoints\battery_cnn_int8.onnx  (84 KB)
```

## 1.8 打包部署产物

```bash
mkdir deploy
copy pinn\checkpoints\battery_pinn_int8.onnx deploy\
copy pinn\checkpoints\feature_scaler.pkl     deploy\
copy cnn\checkpoints\battery_cnn_int8.onnx   deploy\
copy cnn\checkpoints\ic_scaler.pkl           deploy\
```

`deploy/` 目录包含 2 个 INT8 ONNX 模型 + 2 个标准化参数文件 + `inference.py` + `requirements.txt`，可直接拷贝到 RZ/G2L。

---

# 第二部分：RZ/G2L 板端部署

## 2.1 目标环境

| 组件 | 规格 |
|---|---|
| 芯片 | RZ/G2L (Cortex-A55 ×2 @ 1.2 GHz) |
| 系统 | Linux (ARM aarch64) |
| 运行时 | ONNX Runtime 1.18+ CPU EP |
| 加速 | ARM NEON SIMD (ONNX Runtime 自动启用) |

## 2.2 文件传输

将 `deploy/` 目录完整拷贝到 RZ/G2L：

```bash
# 方式1: SCP
scp -r deploy/ root@<rzg2l_ip>:/home/root/battery/

# 方式2: U盘
cp -r /mnt/usb/deploy/ /home/root/battery/
```

## 2.3 安装 ONNX Runtime

```bash
# SSH 到 RZ/G2L
cd /home/root/battery
pip3 install -r requirements.txt

# 验证
python3 -c "import onnxruntime; print(onnxruntime.get_available_providers())"
# 期望: ['CPUExecutionProvider']
```

> 若 RZ/G2L 无 pip3，可使用瑞萨 RZ/G2L AI SDK 预置的 onnxruntime，或交叉编译 ONNX Runtime ARM64 版本。

## 2.4 推理接口

### 命令行

```bash
# 基准测试 (测量推理延迟)
python3 inference.py benchmark
# PINN latency: 8.2 ms
# CNN  latency: 7.5 ms

# PINN: 输入 132-d 特征 → SOH
python3 inference.py pinn  /data/sample_132d.npy
# PINN SOH: 0.9234 (92.3%)

# CNN: 输入 IC 曲线 (128,) → 阶段 + RUL
python3 inference.py cnn   /data/ic_curve_128.npy
# CNN Stage: healthy (0)
# CNN RUL:   0.8764
```

### Python API

```python
from inference import PINNInference, CNNInference
import numpy as np

# PINN
pinn = PINNInference()
soh = pinn.predict(features_132d_array)     # → 0.9234

# CNN
cnn = CNNInference()
result = cnn.predict(ic_curve_128_array)     # → {"stage": 0, "stage_name": "healthy", "rul": 0.8764}
```

### 输入数据要求

| 模型 | 输入 | 形状 | 来源 |
|---|---|---|---|
| PINN | 132-d 特征向量 | `(132,)` float32 | RA8 提取: IC[128] + temp + log_cycle + dv_start + capacity |
| CNN | IC 曲线 | `(128,)` float32 | RA8 提取: dQ/dV 在 128 点电压网格上重采样 |

## 2.5 与 RA8 的数据闭环

```
RA8 (Cortex-M85)                        RZ/G2L (Cortex-A55)
──────────────                          ──────────────────
双向 DCDC 充放电控制
电压/电流/温度 实时采集
卡尔曼滤波 + IC/DV 特征提取
    │                                       │
    ├─ 场景1 (产线筛查)                      │
    │   写 132-d 特征到共享内存 ──→           inference.py pinn  → SOH
    │   ←── 读 SOH 结果 ←─────────────────   存入 Octa-NAND
    │                                       │
    ├─ 场景2 (梯次分选)                      │
    │   写 IC 曲线到共享内存 ─────→           inference.py cnn   → Stage + RUL
    │   ←── 读阶段+RUL ←──────────────────   存入 Octa-NAND + UI 显示
    │                                       │
    └─ 通信接口: QSPI / USB HS               │
```

---

# 第三部分：模块详解

## 3.1 `pinn/` — 物理信息神经网络 (快速筛查)

### pinn/config.py
训练/模型/物理约束/数据配置的数据类。关键参数：
- `ModelConfig.input_dim=132`: IC 曲线(128) + 辅助特征(4)
- `ModelConfig.hidden_dims=(128,128,64)`: 3 层 MLP
- `PhysicsConfig`: ECM 电阻一致性/退化平滑性/单调性损失权重
- `TrainingConfig.batch_size=256, epochs=600, lr=5e-4`

### pinn/model.py
`BatteryPINN`: 紧凑型 MLP + 残差瓶颈块。输入经 `encoder` (3×Linear+Norm+GELU) 投影，通过 `ResidualBlock` (FC→Norm→Act→FC→Norm + skip)，经双头输出 SOH(sigmoid) 和辅助电阻代理值。~53K 参数，可 Int8 量化，Cortex-A55 推理 < 15ms。

### pinn/dataset.py
`BatteryDataset` + `create_dataloaders()`:
1. 自动检测数据源优先级: NASA PCoE > CALCE > 合成数据
2. `build_features()` 将原始数据组装为 132-d 向量
3. `StandardScaler` 标准化 + clip[-5,5]
4. `random_split` 划分训练/验证/测试集

### pinn/physics.py
`PhysicsLoss` 三组件:
- **ECM 一致性**: `MSE(R_predicted, dv_measured)`，强制 SOH 与可测量的内阻一致
- **退化平滑性**: 同电芯相邻循环 SOH 二阶差分惩罚
- **单调性**: ReLU(SOH_{n+1} - SOH_n) 惩罚 SOH 非物理上升

### pinn/train.py
训练入口: 自动 CUDA 检测 → 数据加载 → AdamW + ReduceLROnPlateau → AMP 混合精度 → 早停(80 epoch) → TensorBoard 日志 → 测试集评估 (MSE/MAE/R²) → 保存最佳模型。

### pinn/export.py
`export_to_onnx()`: 加载 `best_model.pt` → `torch.onnx.export` (opset 14, 动态 batch) → ONNX 验证 → INT8 动态量化 (`onnxruntime.quantization.quantize_dynamic`) → FP32/INT8 精度对比。

### pinn/battery_sim.py
`LFPBatterySimulator`: 基于 2-RC ECM 的 LFP 18650 电池老化模拟器。生成幂律容量衰减、电阻增长、含噪声的 CC 充电曲线，从中提取 IC 曲线和 SOH 标签。当真实数据缺失时自动兜底。

### pinn/real_data.py
NASA PCoE 和 CALCE 数据加载器:
- `load_nasa_pcoe()`: 解析 .mat 嵌套结构，提取充电曲线 → IC 曲线 → SOH (基于相邻放电容量/额定容量)
- `load_calce()`: 解析 Arbin .xlsx 多 sheet 格式，按循环分组提取充/放电容量 → 计算 SOH → 提取 IC 曲线。首次加载后缓存为 .npz。

### pinn/demo.py
NASA .mat 文件结构诊断工具 — 打印嵌套 cell array 的字段名、形状和数据类型，用于调试新数据集。

---

## 3.2 `cnn/` — 残差卷积网络 (精准评估)

### cnn/config.py
CNN 专属配置:
- `ModelConfig.in_channels=2`: ch1=IC 曲线, ch2=IC 梯度
- `ModelConfig.conv_filters=(16,32,48)`: 3 层残差块通道数
- `StageThresholds.healthy=0.82, degrading=0.70`: 三阶段 SOH 阈值
- `AugConfig`: 高斯噪声(0.03)/随机缩放(0.85-1.15)/电压轴平移(±6)
- `TrainingConfig.label_smoothing=0.08`: 减轻过拟合

### cnn/model.py
`BatteryCNN`: 残差 1D-CNN。
- **Stem**: Conv1d(2→16, k=7, s=2) 快速降采样
- **ResidualBlock ×3**: 每个 block 含双 Conv1d+BN+GELU，identity 或 1×1 conv shortcut，末尾 MaxPool 降采样
- **全局池化**: AdaptiveAvgPool1d(1) → 48-d 特征向量
- **双头**: 分类头 48→48→24→3 (healthy/degrading/EOL)，RUL 回归头 48→48→24→1
- ~44K 参数，Int8 < 44 KB，推理 < 15ms

### cnn/dataset.py
CNN 数据管线:
1. 复用 `pinn.dataset.load_all_data()` 获取原始数据
2. `filter_valid_curves()`: 剔除全零/数值爆炸/平坦退化 IC 曲线
3. `compute_ic_gradient()`: 构建 IC 梯度通道 (d(IC)/dV)
4. `StandardScaler` 逐点标准化 (IC + 梯度分别处理)
5. `augment_ic()`: 训练集增强 (噪声+缩放+平移)
6. `soh_to_stage()`: SOH → 3 阶段标签
7. `compute_rul()`: 每电芯独立计算归一化剩余寿命
8. `_cell_split()`: 按电芯 ID 划分 (防止同电芯数据泄漏)
9. 自动计算类别权重 (inverse frequency)

### cnn/train.py
多任务训练: 加权 `CrossEntropyLoss(label_smoothing=0.08)` + `MSELoss(RUL)`，类别权重自动从训练集分布计算，NaN 批次自动跳过，100 epoch 早停。

### cnn/export.py
同 PINN 导出流程: FP32 ONNX → INT8 动态量化，验证 FP32/INT8 分类一致性 (100%) 和 RUL MAE (<0.006)。

---

## 3.3 `deploy/` — RZ/G2L 部署推理

### deploy/inference.py
RZ/G2L 双模型推理脚本。两个类:

`PINNInference`:
- 加载 `battery_pinn_int8.onnx` + `feature_scaler.pkl`
- `predict(features_132d)` → float SOH ∈ [0,1]
- 内部: 标准化输入 → ONNX 推理 → 裁剪输出

`CNNInference`:
- 加载 `battery_cnn_int8.onnx` + `ic_scaler.pkl`
- `predict(ic_curve_128)` → dict {stage, stage_name, rul}
- 内部: IC 标准化 + 梯度通道计算 + 梯度标准化 → 双通道 stack → ONNX 推理

命令行模式:
- `python3 inference.py pinn [input.npy]` — PINN 推理
- `python3 inference.py cnn [input.npy]` — CNN 推理
- `python3 inference.py benchmark` — 延迟基准测试

ONNX Runtime 配置: `ORT_ENABLE_ALL` 图优化 + 2 线程 (Cortex-A55 双核)。

### deploy/requirements.txt
ARM aarch64 端最小依赖: `numpy` + `onnxruntime`。

---

## 训练监控

```bash
tensorboard --logdir pinn/logs    # PINN 训练曲线
tensorboard --logdir cnn/logs     # CNN 训练曲线
```

浏览器打开 `http://localhost:6006`。

---

## 超参数调优

| 现象 | 模型 | 调整方向 |
|---|---|---|
| SOH MAE > 2% | PINN | 增大 `ecm_weight`, 降低 lr |
| 物理损失不下降 | PINN | 检查 `smoothness_weight` 和 `monotonic_weight` |
| CNN 准确率 < 65% | CNN | 调整 `StageThresholds` 均衡分布, 降低 lr |
| RUL MAE > 0.25 | CNN | 增大 `rul_weight` 到 0.55 |
| 验证损失震荡 | 通用 | 降低 lr, 增大 batch_size |
| 早停过早 (< 50 epoch) | 通用 | 增大 `early_stop_patience` |
| GPU OOM | 通用 | 减小 batch_size |

---

## 数据源扩展

向已有数据集添加新电芯:

```bash
# NASA: 下载额外 .mat 文件
cp B0029.mat B0030.mat data/nasa_pcoe/

# CALCE: 下载新 cell 目录
cp -r CS2_39/ data/calce/
```

修改 `pinn/real_data.py` 中 `load_nasa_pcoe(cells=...)` 和 `load_calce(cells=...)` 的默认元组以包含新电芯。

添加 18650 磷酸铁锂实测数据: 将充放电测试数据整理为 `pinn/battery_sim.py` 输出格式 (dict with cell_id/cycle/soh/temp/ic/dv_start/capacity_meas)，保存为 `.npz` 放入 `data/`，在 `pinn/dataset.py` 中新增 loader。
