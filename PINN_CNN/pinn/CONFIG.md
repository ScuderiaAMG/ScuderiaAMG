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
NASA PCoE (.mat)  >  CALCE (.csv)  >  Synthetic (自动生成)
```

训练启动时自动检测 `D:/ScuderiaAMG/PINN_CNN/data/` 下的文件，按优先级加载并合并。
三种数据源都没有时，自动降级为合成数据。

### 0.1 NASA PCoE 电池老化数据集 (推荐)

**来源**: NASA Prognostics Center of Excellence  
**电池型号**: 18650 锂离子电池 (额定 2Ah)  
**电池编号**: B0005, B0006, B0007, B0018  
**工况**: 室温, 1.5A CC 放电, 循环至容量衰减至 ~70% (EOL)  
**每个 .mat 文件包含**: 充放电循环的电压、电流、温度时间序列 + 容量数据  
**总循环数**: ~168 次/电芯 × 4 电芯 ≈ 670 次充放电循环  

**下载步骤** (NASA官网已下线, 以下为有效替代):

**方式一 — GitHub (推荐, 最简)**:
```bash
mkdir -p D:\ScuderiaAMG\PINN_CNN\data\nasa_pcoe
cd D:\ScuderiaAMG\PINN_CNN\data\nasa_pcoe
git clone --depth 1 https://github.com/changyeon99/Battery-Data-Set.git .
```

**方式二 — Kaggle (更全, 34电芯)**:
```bash
pip install kaggle
kaggle datasets download ckskaggle/li-ion-battery-dataset-from-nasa-pcoe -p D:\ScuderiaAMG\PINN_CNN\data\nasa_pcoe --unzip
```

**方式三 — Kaggle CSV (已预处理)**:
```bash
kaggle datasets download yashxss/nasa-battery-cycle-level-dataset -p D:\ScuderiaAMG\PINN_CNN\data\nasa_pcoe --unzip
```

下载后放入: `D:\ScuderiaAMG\PINN_CNN\data\nasa_pcoe\`

```
PINN_CNN/data/nasa_pcoe/
├── B0005.mat
├── B0006.mat
├── B0007.mat
└── B0018.mat
```

**预期提取**: ~500–600 个带标签充电循环样本

### 0.2 CALCE 电池数据集

**来源**: University of Maryland CALCE Battery Research Group  
**电池型号**: 18650 LiCoO₂ (CS2 系列)  
**申请网址**: `https://calce.umd.edu/battery-data`  
**说明**: 需填写申请表 (姓名、机构、研究用途)，通常 1–2 个工作日审批通过  
**数据格式**: CSV (循环汇总 + 逐循环详细时间序列)  

**下载后放入**:

```
PINN_CNN/data/calce/
├── CS2_35/
│   ├── CS2_35_cycle_data.csv
│   └── ...
├── CS2_36/
├── CS2_37/
└── CS2_38/
```

### 0.3 合成数据 (自动兜底)

当以上两个数据源都不存在时，训练脚本自动调用 `battery_sim.py` 生成 50 个虚拟 LFP 电芯 × ~800 循环 = ~24,000 样本的合成数据集。生成约需 2–3 分钟，结果缓存至 `pinn/cache/lfp_synthetic.npz`。

**合成数据局限性**: 虽然基于 2-RC ECM 物理模型生成，但无法完全替代真实电芯的不一致性。建议至少获取 NASA PCoE 数据集进行实际训练。

### 0.4 数据集比较

| 特性 | NASA PCoE | CALCE | Synthetic |
|------|-----------|-------|-----------|
| 电芯数量 | 4 | 4+ | 50 (虚拟) |
| 样本数 | ~600 | ~400 | ~24,000 |
| 化学体系 | NCA | LiCoO₂ | LFP (模拟) |
| 与目标(LFP)差异 | 中等 | 较大 | 无(但为模拟) |
| 获取难度 | GitHub/Kaggle 镜像 | 需申请 | 自动 |
| 推荐用途 | **主力训练** | 补充/迁移学习 | 代码调试/原型 |

> **注意**: NASA PCoE 和 CALCE 均为三元锂电池 (NCA/LiCoO₂)，与项目目标 18650 磷酸铁锂 (LFP) 电化学体系不同。LFP 的 OCV 平台电压平坦得多 (3.3V 平台区 10–90% SOC)，IC 曲线特征峰位置不同。**强烈建议**在获取真实 LFP 实测数据后，采用 **迁移学习** 策略: 用 NASA+CALCE 预训练 → 少量 LFP 实测数据微调最后两层。

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
| 0–127 | IC曲线 (dQ/dV, 归一化) | RA8端 Savitzky-Golay 滤波后计算 |
| 128 | 温度 (°C) | AHT10 传感器 |
| 129 | log₁₀(循环数 + 1) | 系统计数器 |
| 130 | dV_start / I (ohm代理) | 充电起始电压阶跃 ÷ 电流 |
| 131 | 实测容量 (Ah) | 库仑计数 |

**参数量**: ~52,320 (FP32: ~209KB, INT8: ~52KB)

---

## 二、物理约束配置 `PhysicsConfig`

| 参数 | 值 | 公式 | 说明 |
|------|-----|------|------|
| `ecm_weight` | 0.15 | λ₁·MSE(R_pred, R_meas) | ECM内阻一致性权重 |
| `smoothness_weight` | 0.05 | λ₂·mean((Δ²SOH)²) | 退化轨迹平滑性权重 |
| `monotonic_weight` | 0.02 | λ₃·mean(ReLU(ΔSOH)) | SOH单调递减软约束 |
| `r0_initial_ohm` | 0.045 | R₀ | 全新LFP电芯欧姆内阻 |
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
- 合成数据生成: ~2–3分钟 (50 virtual cells × ~800 cycles each)
- 训练: ~5–8分钟 (600 epochs, 实际早停在~400 epoch)
- 总耗时: **< 15分钟**

---

## 四、数据配置 `DataConfig`

| 参数 | 值 | 说明 |
|------|-----|------|
| `ic_curve_pts` | 128 | IC曲线重采样点数 |
| `voltage_span` | (2.8, 3.6) | LFP电芯工作电压范围 (V) |
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
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu124
pip install numpy scipy scikit-learn onnx onnxruntime tensorboard
```

### 5.2 启动训练

```bash
cd D:\ScuderiaAMG\PINN_CNN
python -m pinn.train
```

### 5.3 导出部署模型

```bash
python -m pinn.export
```

### 5.4 TensorBoard 监控

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

### 5.5 预期结果

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

## 七、文件结构

```
PINN_CNN/pinn/
├── __init__.py
├── config.py          # 所有配置的Python定义
├── CONFIG.md          # 本文件 — 配置手册
├── env.txt            # conda环境配置文件
├── battery_sim.py     # LFP电池老化数据模拟器
├── model.py           # PINN模型定义
├── physics.py         # 物理信息损失函数
├── dataset.py         # Dataset + DataLoader
├── train.py           # 训练主入口
├── export.py          # ONNX导出 + int8量化
├── cache/             # 合成数据缓存
│   └── lfp_synthetic.npz
├── checkpoints/       # 模型检查点
│   ├── best_model.pt
│   ├── feature_scaler.pkl
│   ├── battery_pinn_fp32.onnx
│   └── battery_pinn_int8.onnx
└── logs/              # TensorBoard日志
```

---

## 八、调参与排错

| 问题 | 可能原因 | 解决方案 |
|------|---------|---------|
| 训练loss不下降 | 学习率过大 | 降低lr至1e-4 |
| 物理loss震荡 | ecm_weight过大 | 降低至0.05 |
| 验证MAE > 10% | 合成数据分布不真实 | 增大n_cells, 添加多工况 |
| ONNX导出失败 | opset版本不兼容 | 降opset至11 |
| INT8精度损失 > 2% | 动态量化不适合 | 改用静态量化(需校准集) |
| A55推理 > 50ms | 未启用NEON | 确认ORT ARM64编译选项 |
| 梯度爆炸 | 物理损失无界 | 降低grad_clip至0.5 |
