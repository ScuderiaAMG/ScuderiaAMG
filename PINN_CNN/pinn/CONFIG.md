# PINN 电池SOH快速筛查模型 — 配置手册

## 硬件配置

| 组件 | 型号 |
|------|------|
| GPU | NVIDIA RTX 4060 Laptop 8GB GDDR6 |
| CPU | Intel Core i7-14700HX (20核28线程) |
| RAM | 64GB DDR5 |
| 环境 | Anaconda |
| 部署目标 | 瑞萨 RZ/G2L (Cortex-A55 ×2, ARM NEON) |

---

## 零、数据集获取

### 数据源优先级 (自动降级)

```
NASA PCoE (.mat)  >  CALCE (.xlsx)  >  Synthetic (自动生成)
```

训练启动时自动检测 `D:/ScuderiaAMG/PINN_CNN/data/` 下的文件，按优先级加载并合并。
三种数据源都没有时，自动降级为合成数据。每个真实数据源首次加载后自动缓存为 `.npz` 文件，后续秒级加载。

### 0.1 NASA PCoE 电池老化数据集 (推荐)

**来源**: NASA Prognostics Center of Excellence
**电池型号**: 18650 NCA 锂离子电池 (额定 2Ah)
**电池编号**: B0005, B0006, B0007, B0018
**工况**: 室温, 1.5A CC 放电, 循环至容量衰减至 ~70% (EOL)
**每个 .mat 文件包含**: 充放电循环的电压、电流、温度时间序列 + 容量数据
**总循环数**: ~168 次/电芯 × 4 电芯 ≈ 670 次充放电循环
**IC特征电压范围**: 3.2–4.2V (NCA化学体系)
**缓存文件**: `data/nasa_pcoe/nasa_cache.npz` (首次加载后自动生成)

**下载步骤** (NASA 官网已下线，以下为有效替代):

**方式一 — GitHub (推荐, 最简)**:
```bash
mkdir -p D:\ScuderiaAMG\PINN_CNN\data\nasa_pcoe
cd D:\ScuderiaAMG\PINN_CNN\data\nasa_pcoe
git clone --depth 1 https://github.com/changyeon99/Battery-Data-Set.git .
```

**方式二 — Kaggle (更全, 34 电芯)**:
```bash
pip install kaggle
kaggle datasets download ckskaggle/li-ion-battery-dataset-from-nasa-pcoe -p D:\ScuderiaAMG\PINN_CNN\data\nasa_pcoe --unzip
```

**方式三 — Kaggle CSV (已预处理)**:
```bash
kaggle datasets download yashxss/nasa-battery-cycle-level-dataset -p D:\ScuderiaAMG\PINN_CNN\data\nasa_pcoe --unzip
```

**预期提取**: ~500–600 个带标签充电循环样本
**已验证**: B0005.mat (16MB), B0006.mat (16MB), B0007.mat (16MB), B0018.mat (8.2MB)

### 0.2 CALCE 电池数据集

**来源**: University of Maryland CALCE Battery Research Group
**电池型号**: 18650 LiCoO₂ (CS2 系列, 额定 ~1.0Ah)
**电池编号**: CS2_35, CS2_36, CS2_37, CS2_38
**申请网址**: `https://calce.umd.edu/battery-data`
**说明**: 需填写申请表，通常 1–2 个工作日审批通过
**IC特征电压范围**: 3.0–4.2V (LiCoO₂ 化学体系)

**文件格式**: Arbin 电池测试仪导出的 `.xlsx` 文件，每个文件为一次测试会话

**每个 .xlsx 包含 3 个 Sheet**:

| Sheet | 内容 | 关键列 |
|-------|------|--------|
| `Info` | 测试元信息 | (跳过) |
| `Channel_1-008` | 逐采样点时间序列 | `Voltage(V)`, `Current(A)`, `Test_Time(s)`, `Cycle_Index`, `Charge_Capacity(Ah)` |
| `Statistics_1-008` | 逐循环汇总 | `Cycle_Index`, `Discharge_Capacity(Ah)`, `Internal_Resistance(Ohm)` |

> **注意**: CALCE 的 `Discharge_Capacity(Ah)` 列是**跨循环累计值** (如 0.88→1.75→2.60 Ah)。
> 加载器使用 `np.diff()` 计算单次循环放电容量。SOH = 单次放电容量 / 额定容量。

**下载后放入**:

```
PINN_CNN/data/calce/
├── CS2_35/
│   ├── CS2_35_1_10_11.xlsx
│   ├── CS2_35_10_15_10.xlsx
│   └── ... (25 sessions)
├── CS2_36/   (26 sessions)
├── CS2_37/   (27 sessions)
├── CS2_38/   (28 sessions)
└── calce_cache.npz  ← 首次加载后自动生成
```

**已验证 (CS2_35)**:
- c_nominal = 0.988 Ah
- 618 charge cycles extracted
- SOH range: [0.30, 1.01]
- Capacity range: [0.25, 1.00] Ah

**预期总样本**: ~2,400 (4 cells × ~600 cycles each)
**首次加载耗时**: ~3–4 分钟 (解析 100+ 个 .xlsx 文件)
**缓存加载耗时**: ~2 秒 (从 calce_cache.npz)

### 0.3 合成数据 (自动兜底)

当以上两个数据源都不存在时，训练脚本自动调用 `battery_sim.py` 生成 50 个虚拟 LFP 电芯 × ~800 循环 = ~24,000 样本的合成数据集。生成约需 2–3 分钟，结果缓存至 `pinn/cache/lfp_synthetic.npz`。

**合成数据局限性**: 虽然基于 2-RC ECM 物理模型生成，但无法完全替代真实电芯的不一致性。建议至少获取 NASA PCoE 数据集进行实际训练。

### 0.4 数据集比较

| 特性 | NASA PCoE | CALCE | Synthetic |
|------|-----------|-------|-----------|
| 电芯数量 | 4 | 4 | 50 (虚拟) |
| 实际样本数 (验证) | ~600 | ~2,400 | ~24,000 |
| 化学体系 | NCA | LiCoO₂ | LFP (模拟) |
| 与目标(LFP)差异 | 中等 | 较大 | 无(但为模拟) |
| 额定容量 | 2.0 Ah | 1.0 Ah | 1.1 Ah |
| 文件格式 | .mat (MATLAB) | .xlsx (Arbin) | .npz |
| 获取难度 | GitHub/Kaggle 镜像 | 需申请 | 自动 |
| IC电压范围 | 3.2–4.2V | 3.0–4.2V | 2.8–3.6V |
| 推荐用途 | **主力训练** | 补充/迁移学习 | 代码调试/原型 |

### 0.5 IC 曲线电压范围 (按化学体系)

| 化学体系 | 电压范围 | 对应数据集 | IC特征峰位置 |
|----------|---------|-----------|-------------|
| NCA (LiNiCoAlO₂) | 3.2–4.2V | NASA PCoE | 3.5–3.8V (多个尖峰) |
| LiCoO₂ | 3.0–4.2V | CALCE CS2 | 3.6–3.9V (单峰+肩峰) |
| LFP (LiFePO₄) | 2.8–3.6V | Synthetic / 项目目标 | 3.3–3.4V (极窄尖峰) |

> **重要**: `DataConfig.voltage_span` 默认值为 `(2.8, 3.6)` (针对 LFP)。加载 NASA/CALCE 数据时，`real_data.py` 的加载器使用各自化学体系对应的电压范围提取 IC 曲线。这意味着不同来源的 IC 曲线特征峰在固定电压网格上的位置不同——模型需要学习跨化学体系的泛化能力，或通过迁移学习适配 LFP。

> **强烈建议**在获取真实 LFP 实测数据后，采用**迁移学习**策略: 用 NASA+CALCE 预训练全部层 → 冻结 encoder 和 residual block → 仅微调 head 层 (最后 2 层 FC) → 用少量 LFP 实测数据适配。

---

## 一、模型配置 `ModelConfig`

| 参数 | 值 | 说明 |
|------|-----|------|
| `input_dim` | 132 | IC曲线128点 + 温度 + log(cycle) + dV代理电阻 + 实测容量 |
| `hidden_dims` | (128, 128, 64) | 三层隐藏层，逐层压缩 |
| `dropout` | 0.1 | 仅训练时生效，防止过拟合 |
| `output_dim` | 1 | SOH标量 ∈ [0, 1] |
| `activation` | gelu | GELU梯度光滑，比ReLU更适合物理约束训练 |

**输入特征向量结构** (索引 0-131):

| 索引范围 | 特征 | 来源 |
|----------|------|------|
| 0–127 | IC曲线 (dQ/dV, 归一化) | 电压-容量数值微分 + Savitzky-Golay 滤波 |
| 128 | 温度 (°C) | AHT10 传感器 / 数据集标注 |
| 129 | log₁₀(循环数 + 1) | 系统计数器 |
| 130 | dV_start / I (ohm代理) | 充电起始电压阶跃 ÷ 电流 |
| 131 | 实测容量 (Ah) | 库仑计数 / 数据集放电容量 |

**参数量**: ~52,320 (FP32: ~209KB, INT8: ~52KB)

---

## 二、物理约束配置 `PhysicsConfig`

| 参数 | 值 | 公式 | 说明 |
|------|-----|------|------|
| `ecm_weight` | 0.15 | λ₁·MSE(R_pred, R_meas) | ECM内阻一致性权重 |
| `smoothness_weight` | 0.05 | λ₂·mean((Δ²SOH)²) | 退化轨迹平滑性权重 |
| `monotonic_weight` | 0.02 | λ₃·mean(ReLU(ΔSOH)) | SOH单调递减软约束 |
| `r0_initial_ohm` | 0.045 | R₀ | 全新 LFP 电芯欧姆内阻 |
| `r0_aging_coeff` | 0.12 | β | 内阻增长系数: R = R₀·(1+β·(1-SOH)) |
| `degradation_alpha` | 0.78 | α | 容量衰减幂律指数: C(N) = C₀·(1-k·N^α) |

**物理约束详解**:

1. **ECM一致性**: 测量的起始电压阶跃(dV/I)应等于老化模型预测的内阻
2. **退化平滑性**: 同一电芯相邻三个周期的SOH二阶差分越小越好
3. **单调性**: 正常老化过程中SOH只降不升，违反时施加惩罚

**调参建议**:
- 训练初期(前100 epoch)物理权重保持默认
- 若验证集MAE不下降，降低 `ecm_weight` 至 0.05
- 若SOH曲线出现锯齿，提升 `smoothness_weight` 至 0.10
- 若模型过于保守(SOH总是偏低), 降低 `monotonic_weight` 至 0.005
- 使用 NASA/CALCE 多化学体系数据训练时，`ecm_weight` 建议降至 0.05–0.08 (ECM 参数基于 LFP 标定，NCA/LiCoO₂ 的 R₀/β 不同)

---

## 三、训练配置 `TrainingConfig`

| 参数 | 值 | 说明 |
|------|-----|------|
| `batch_size` | 256 | 52K参数模型, 8GB VRAM绰绰有余 |
| `epochs` | 600 | 最大训练轮数 |
| `learning_rate` | 5e-4 | AdamW初始学习率 |
| `weight_decay` | 1e-5 | 轻微L2正则化 |
| `lr_factor` | 0.5 | ReduceLROnPlateau衰减系数 |
| `lr_patience` | 30 | 学习率衰减的等待轮数 |
| `early_stop_patience` | 80 | 早停等待轮数 |
| `grad_clip` | 1.0 | 梯度裁剪阈值 |
| `use_amp` | True | RTX 4060自动混合精度 (CUDA Tensor Core) |
| `num_workers` | 4 | DataLoader子进程数 |

**训练耗时预估** (RTX 4060 Laptop):

| 数据源 | 首次加载 | 训练耗时 | 总耗时 |
|--------|---------|---------|--------|
| 仅合成数据 | 2–3 min (生成) | 5–8 min | **< 15 min** |
| 仅 NASA | < 5 sec (.mat) | 5–8 min | **< 10 min** |
| 仅 CALCE | 3–4 min (xlsx→缓存) | 8–12 min | **< 16 min** |
| NASA + CALCE | 3–4 min (CALCE 首次) | 10–15 min | **< 20 min** |

---

## 四、数据配置 `DataConfig`

| 参数 | 值 | 说明 |
|------|-----|------|
| `ic_curve_pts` | 128 | IC曲线重采样点数 |
| `voltage_span` | (2.8, 3.6) | 默认 LFP 电压范围 (V)；真实数据加载器按化学体系自动覆盖 |
| `train_ratio` | 0.70 | 训练集比例 |
| `val_ratio` | 0.15 | 验证集比例 |
| `test_ratio` | 0.15 | 测试集比例 |

**合成数据生成参数**:

| 参数 | 值 | 说明 |
|------|-----|------|
| `n_cells` | 50 | 模拟电芯数量 |
| `max_cycles` | 800 | 每电芯最大循环次数 |
| `temperature_range` | (20.0, 45.0) | 温度范围 (°C) |
| `charge_current_pu` | (0.3, 1.0) | 充电倍率范围 (C-rate) |
| `noise_voltage_mv` | 2.5 | 测量噪声标准差 (mV) |

---

## 五、完整训练流程

### 5.1 环境配置

```bash
conda create -n batpinn python=3.11 -y
conda activate batpinn
pip install -r D:\ScuderiaAMG\PINN_CNN\pinn\env.txt
```

### 5.2 获取数据集

```bash
# NASA (必选)
mkdir -p D:\ScuderiaAMG\PINN_CNN\data\nasa_pcoe
cd D:\ScuderiaAMG\PINN_CNN\data\nasa_pcoe
git clone --depth 1 https://github.com/changyeon99/Battery-Data-Set.git .

# CALCE (可选 — 从 https://calce.umd.edu/battery-data 申请后放入 data/calce/)
```

### 5.3 启动训练

```bash
cd D:\ScuderiaAMG\PINN_CNN
python -m pinn.train
```

首次运行输出示例:

```
[数据] NASA PCoE .mat 文件已检测到
  Loading B0005 ...
    → 168 charge cycles extracted
  ...
  NASA samples: 616

[数据] CALCE 数据目录已检测到
  Loading CS2_35 (25 sessions) ...
    → 618 charge cycles extracted (c_nominal=0.988 Ah)
  ...
  CALCE total: 2412 samples from 4 cells
  合并后总样本: 3028

Train: 2119  Val: 454  Test: 455
Scaler saved → pinn/checkpoints/feature_scaler.pkl
```

### 5.4 导出部署模型

```bash
python -m pinn.export
```

### 5.5 TensorBoard 监控

```bash
tensorboard --logdir pinn/logs --bind_all
# 浏览器打开: http://localhost:6006
```

监控指标:
- `train/data_loss` — 数据MSE损失
- `train/phys_loss` — 总物理损失
- `train/phys_ecm` / `phys_smooth` / `phys_mono` — 各项物理损失
- `val/data_loss` — 验证集MSE
- `val/mae` — 验证集MAE (核心指标)
- `lr` — 学习率变化

### 5.6 预期结果

| 指标 | 目标值 | 判定标准 |
|------|--------|---------|
| 验证MAE | < 0.03 (3% SOH) | 合格 |
| 验证MAE | < 0.015 (1.5% SOH) | 优秀 |
| INT8量化MAE损失 | < 0.01 (1% SOH) | 合格 |
| 单次推理延迟 (A55) | < 20ms | 合格 |
| R² | > 0.95 | 合格 |

---

## 六、RZ/G2L 部署配置

### 6.1 ONNX Runtime 编译参数

```bash
# PC端交叉编译 (Yocto SDK)
./build.sh --config Release \
  --arm64 \
  --minimal_build \
  --disable_ml_ops \
  --disable_exceptions \
  --disable_rtti \
  --build_shared_lib \
  --skip_tests \
  --parallel
```

产物: `libonnxruntime.so` (~2 MB stripped)

### 6.2 RZ/G2L 运行时环境

| 组件 | 版本/说明 |
|------|----------|
| OS | Linux (Yocto BSP) |
| ONNX Runtime | 1.18+ ARM aarch64 |
| 执行后端 | CPU EP (ARM NEON 自动加速) |
| 模型文件 | `battery_pinn_int8.onnx` (~55KB) |
| 归一化参数 | `feature_scaler.pkl` → 转换为C++常量数组 |
| 内存占用 | < 10MB (运行时) |
| 推理延迟 | < 20ms (int8, A55单核) |

### 6.3 Scaler参数传输

训练保存的 `feature_scaler.pkl` 包含归一化参数(4个辅助特征的均值和标准差):

```python
import pickle
with open("pinn/checkpoints/feature_scaler.pkl", "rb") as f:
    scaler = pickle.load(f)
print("mean:", scaler.mean_.tolist())   # [temp, log_cycle, dv, cap]
print("scale:", scaler.scale_.tolist())  # [temp, log_cycle, dv, cap]
```

将这些值写死到RZ/G2L C++代码中:

```cpp
// 4 auxiliary features: temp, log10(cycle+1), dv_start, cap_meas
constexpr float SCALER_MEAN[4]  = {/* from training */};
constexpr float SCALER_SCALE[4] = {/* from training */};
```

---

## 七、完整文件结构

```
PINN_CNN/
├── data/
│   ├── nasa_pcoe/           # NASA PCoE 数据集
│   │   ├── B0005.mat            (16 MB)
│   │   ├── B0006.mat            (16 MB)
│   │   ├── B0007.mat            (16 MB)
│   │   └── B0018.mat            (8.2 MB)
│   └── calce/               # CALCE 数据集
│       ├── CS2_35/              (25 xlsx files)
│       ├── CS2_36/              (26 xlsx files)
│       ├── CS2_37/              (27 xlsx files)
│       ├── CS2_38/              (28 xlsx files)
│       └── calce_cache.npz      (首次加载后自动生成)
│
└── pinn/
    ├── __init__.py
    ├── config.py            # 所有配置的Python定义
    ├── CONFIG.md            # 本文件 — 配置手册
    ├── env.txt              # conda环境配置文件
    ├── battery_sim.py       # LFP电池老化数据模拟器 (合成数据)
    ├── real_data.py         # NASA PCoE + CALCE 真实数据加载器
    ├── model.py             # PINN模型定义 (~52K params)
    ├── physics.py           # 物理信息损失函数 (3项约束)
    ├── dataset.py           # Dataset + DataLoader (多源自动合并)
    ├── train.py             # 训练主入口 (AMP, TensorBoard, 早停)
    ├── export.py            # ONNX导出 + int8量化
    ├── cache/               # 合成数据缓存
    │   └── lfp_synthetic.npz
    ├── checkpoints/         # 模型检查点
    │   ├── best_model.pt
    │   ├── feature_scaler.pkl
    │   ├── battery_pinn_fp32.onnx
    │   └── battery_pinn_int8.onnx
    └── logs/                # TensorBoard日志
```

---

## 八、调参与排错

| 问题 | 可能原因 | 解决方案 |
|------|---------|---------|
| 训练loss不下降 | 学习率过大 | 降低lr至1e-4 |
| 物理loss震荡 | ecm_weight过大 | 降低至0.05 |
| 验证MAE > 10% | 合成数据分布不真实 | 增大n_cells, 添加多工况 |
| CALCE 加载报 "无法读取放电容量" | 累计容量未正确差分 | 检查 `real_data.py` 中 `np.diff(cum_cap, prepend=0)` |
| CALCE c_nominal 异常 (>10Ah) | 未对累计值做差分 | 确认已用 `per_cycle_cap = np.diff(cum_cap_arr)` |
| CALCE 首次加载超时 (>5min) | xlsx 文件过多 (~106 files) | 等待完成; 后续从 `calce_cache.npz` 秒级加载 |
| IC曲线全零 | 电压范围不匹配 | 检查化学体系对应的 voltage_span |
| ONNX导出失败 | opset版本不兼容 | 降opset至11 |
| INT8精度损失 > 2% | 动态量化不适合 | 改用静态量化(需校准集) |
| A55推理 > 50ms | 未启用NEON | 确认ORT ARM64编译选项 |
| 梯度爆炸 | 物理损失无界 | 降低grad_clip至0.5 |

---

## 九、已知限制与后续改进

1. **跨化学体系泛化**: NASA(NCA) + CALCE(LiCoO₂) → 目标 LFP 存在分布偏移。迁移学习是目前最佳缓解策略。理想方案为直接获取 LFP 实测老化数据。

2. **ECM 参数标定**: 物理损失中的 `r0_initial_ohm`(0.045Ω) 和 `r0_aging_coeff`(0.12) 基于 LFP 标定。用于 NCA/LiCoO₂ 训练时物理约束精度降低，建议适当降低 `ecm_weight`。

3. **CALCE 温度缺失**: CALCE CS2 数据未记录每循环的温度，当前默认填 25°C。这对温度敏感模型有影响，但不影响常温工况的 SOH 估算。

4. **IC 曲线电压网格固定**: 固定 128 点重采样在跨化学体系时可能导致特征对齐偏差。后续可考虑动态 voltage_span 或注意力机制。
