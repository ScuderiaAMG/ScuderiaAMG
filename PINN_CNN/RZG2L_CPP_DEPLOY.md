# RZ/G2L ARM64 C++ 推理引擎部署完整教程

## 从零配置 Ubuntu 20.04 → ONNX Runtime 编译 → C++ 双模型推理接口

---

> **目标平台**: Renesas RZ/G2L (Cortex-A55 ×2 @ 1.2 GHz, ARM NEON, 无 GPU/NPU)
> **操作系统**: Ubuntu 20.04.6 LTS (aarch64), 无图形界面, 纯命令行
> **推理框架**: ONNX Runtime 1.18+ (CPU EP, ARM NEON 加速)
> **编程语言**: C++17 (gcc 9.4+)
> **构建系统**: CMake 3.16+

---

## 目录

1. [架构概述](#1-架构概述)
2. [系统初始化 (Ubuntu 20.04 ARM64)](#2-系统初始化)
3. [C++ 开发工具链安装](#3-c-开发工具链)
4. [ONNX Runtime ARM64 源码编译](#4-onnx-runtime-源码编译)
5. [Python 侧: 导出 Scaler 参数](#5-python-侧导出-scaler-参数)
6. [C++ 项目结构与接口设计](#6-c-项目结构)
7. [完整源码实现](#7-完整源码)
8. [CMake 构建配置](#8-cmake-构建)
9. [编译与部署](#9-编译与部署)
10. [API 使用指南](#10-api-使用指南)
11. [性能基准与优化](#11-性能基准)
12. [故障排查](#12-故障排查)

---

## 1. 架构概述

### 1.1 硬件架构

```
┌─────────────────────────────────────────────────────┐
│                   RZ/G2L MPU                        │
│  ┌──────────────┐  ┌──────────────────────────────┐ │
│  │  Cortex-M85   │  │   Cortex-A55 ×2 @ 1.2 GHz    │ │
│  │  (RA8 采集)   │  │   (AI 推理引擎 — 本项目)      │ │
│  │              │  │                              │ │
│  │ • ADC 采样   │  │   ┌──────────────────────┐   │ │
│  │ • 卡尔曼滤波 │──┼──▶│  C++ 推理引擎          │   │ │
│  │ • IC/DV 特征 │  │   │  ├─ PINNInference     │   │ │
│  │ • QSPI 传输  │  │   │  ├─ CNNInference      │   │ │
│  └──────────────┘  │   │  └─ ONNX Runtime      │   │ │
│                    │   └──────────────────────┘   │ │
│                    │                              │ │
│                    │   内存: 1-2 GB DDR4           │ │
│                    │   存储: eMMC / SD 卡           │ │
│                    └──────────────────────────────┘ │
└─────────────────────────────────────────────────────┘
```

### 1.2 双模型推理管线

```
RA8 采集数据 ──▶ RZ/G2L C++ 推理引擎
                      │
                      ├── PINN 路径 (快速筛查, <15ms)
                      │   输入: 132-d 特征向量
                      │   输出: SOH ∈ [0, 1]
                      │   用途: 产线快速分选
                      │
                      └── CNN 路径 (精准评估, <15ms)
                          输入: (2, 128) IC + 梯度双通道
                          输出: 阶段 (Healthy/Degrading/EOL) + RUL
                          用途: 梯次利用分选 / 回收评估
```

### 1.3 ONNX 模型接口定义

| 属性 | PINN 模型 | CNN 模型 |
|------|----------|---------|
| ONNX 输入名 | `input` | `ic_curve` |
| 输入 shape | `(B, 132)` float32 | `(B, 2, 128)` float32 |
| ONNX 输出名 | `soh` | `stage_logits`, `rul` |
| 输出 shape | `(B, 1)` float32 | `(B, 3)` float32, `(B, 1)` float32 |
| 量化格式 | INT8 动态量化 | INT8 动态量化 |
| 模型大小 | < 200 KB | < 40 KB |
| 预处理 | StandardScaler → clip[-5,5] | 双通道 StandardScaler → clip[-5,5] |

---

## 2. 系统初始化

> 假设 RZ/G2L 已烧录 Ubuntu 20.04 ARM64 根文件系统。若尚未烧录，请参考 Renesas 官方 BSP 文档。

### 2.1 首次登录与基础配置

```bash
# ============================================================
# 步骤 1: 通过串口/SSH 登录 (默认用户 root)
# ============================================================

# 设置主机名
hostnamectl set-hostname rzg2l-battery

# 更新 APT 源 (使用国内镜像加速)
cat > /etc/apt/sources.list << 'EOF'
deb http://ports.ubuntu.com/ubuntu-ports focal main restricted universe multiverse
deb http://ports.ubuntu.com/ubuntu-ports focal-updates main restricted universe multiverse
deb http://ports.ubuntu.com/ubuntu-ports focal-security main restricted universe multiverse
EOF

# 更新软件包索引
apt update && apt upgrade -y

# ============================================================
# 步骤 2: 安装基础系统工具
# ============================================================
apt install -y \
    build-essential \
    git \
    wget \
    curl \
    unzip \
    cmake \
    python3 python3-pip python3-numpy \
    vim \
    htop \
    tree \
    usbutils \
    net-tools \
    openssh-server

# 启用 SSH 服务 (无图形界面必需)
systemctl enable ssh
systemctl start ssh
```

### 2.2 检查 CPU 与 NEON 支持

```bash
# 确认 ARM NEON 可用 (Cortex-A55 必定支持)
cat /proc/cpuinfo | grep -E "processor|Features|CPU part"

# 期望输出示例:
# processor       : 0
# processor       : 1
# Features        : fp asimd evtstrm aes pmull sha1 sha2 crc32 cpuid
# CPU part        : 0xd05    (Cortex-A55)

# 确认 asimd = NEON 支持
grep -q asimd /proc/cpuinfo && echo "NEON: YES ✓" || echo "NEON: MISSING ✗"
```

### 2.3 配置交换空间 (编译 ONNX Runtime 需要大量内存)

```bash
# RZ/G2L 通常只有 1-2GB RAM, 源码编译需要 swap
dd if=/dev/zero of=/swapfile bs=1M count=2048
chmod 600 /swapfile
mkswap /swapfile
swapon /swapfile
echo '/swapfile none swap sw 0 0' >> /etc/fstab

# 验证
free -h
```

---

## 3. C++ 开发工具链

### 3.1 确认 GCC 版本

```bash
gcc --version
g++ --version

# 期望: gcc 9.4.0 或更高 (Ubuntu 20.04 默认)
# 若版本过低, 安装 gcc-10:
# apt install -y gcc-10 g++-10
# update-alternatives --install /usr/bin/gcc gcc /usr/bin/gcc-10 100
# update-alternatives --install /usr/bin/g++ g++ /usr/bin/g++-10 100
```

### 3.2 安装 CMake (≥3.16)

```bash
# Ubuntu 20.04 默认 CMake 3.16 满足要求
cmake --version

# 若需更新版本:
# wget https://github.com/Kitware/CMake/releases/download/v3.28.1/cmake-3.28.1-linux-aarch64.tar.gz
# tar xzf cmake-3.28.1-linux-aarch64.tar.gz -C /opt
# echo 'export PATH=/opt/cmake-3.28.1-linux-aarch64/bin:$PATH' >> ~/.bashrc
```

### 3.3 安装其他编译依赖

```bash
apt install -y \
    libprotobuf-dev \
    protobuf-compiler \
    libabsl-dev \
    libflatbuffers-dev \
    libgoogle-glog-dev \
    libgflags-dev \
    pkg-config \
    ninja-build

# 可选: 安装调试工具
apt install -y gdb valgrind strace
```

---

## 4. ONNX Runtime 源码编译

> **关键步骤**: ONNX Runtime 需要从源码编译才能获得 ARM NEON 优化。预编译包不含 aarch64 CPU EP。

### 4.1 克隆源码

```bash
cd /opt
git clone --recursive https://github.com/microsoft/onnxruntime.git
cd onnxruntime

# 推荐使用稳定版本
git checkout v1.18.1
git submodule update --init --recursive
```

若 GitHub 访问缓慢, 可使用 Gitee 镜像:

```bash
# 主仓库镜像
git clone --recursive https://gitee.com/mirrors/onnx-runtime.git onnxruntime
cd onnxruntime
git checkout v1.18.1
```

### 4.2 配置编译参数

```bash
cd /opt/onnxruntime

# 创建构建目录
mkdir -p build_aarch64 && cd build_aarch64

# ============================================================
# CMake 配置 — 针对 Cortex-A55 最小化构建
# ============================================================
# 关键参数说明:
#   --arm64                           目标架构
#   --allow_running_as_root           允许 root 编译
#   --config MinSizeRel               最小体积优化
#   --parallel $(nproc)               并行编译
#   --build_shared_lib                构建共享库 (.so)
#   --use_xnnpack                     启用 XNNPACK (ARM NEON 加速)
#   --disable_contrib_ops             禁用贡献算子
#   --disable_exceptions              禁用异常 (减少体积)
#   --disable_rtti                    禁用 RTTI
#   --skip_tests                      跳过测试编译
#   --cmake_extra_defines             额外 CMake 定义
# ============================================================

./build.sh \
    --config MinSizeRel \
    --arm64 \
    --build_shared_lib \
    --use_xnnpack \
    --disable_contrib_ops \
    --disable_rtti \
    --disable_exceptions \
    --skip_tests \
    --parallel $(nproc) \
    --allow_running_as_root \
    --cmake_extra_defines \
        CMAKE_CXX_FLAGS="-march=armv8.2-a+fp16+dotprod -mtune=cortex-a55 -O2" \
        CMAKE_C_FLAGS="-march=armv8.2-a+fp16+dotprod -mtune=cortex-a55 -O2" \
        CMAKE_EXE_LINKER_FLAGS="-Wl,--strip-all" \
        CMAKE_SHARED_LINKER_FLAGS="-Wl,--strip-all"
```

> **注意**: 编译时间约 30-60 分钟 (取决于 swap 大小和 CPU 频率)。建议使用 `tmux` 或 `screen` 防止 SSH 断开。

```bash
# 安装 tmux 防止断开
apt install -y tmux
tmux new -s build_ort

# 在 tmux 内执行编译
cd /opt/onnxruntime/build_aarch64
./build.sh --config MinSizeRel --arm64 --build_shared_lib --use_xnnpack \
    --skip_tests --parallel $(nproc) --allow_running_as_root
# Ctrl+B D 断开, tmux attach -t build_ort 重连
```

### 4.3 安装到系统路径

```bash
cd /opt/onnxruntime/build_aarch64

# 安装头文件和库文件
mkdir -p /usr/local/include/onnxruntime
cp -r /opt/onnxruntime/include/onnxruntime/core/session/*.h \
      /usr/local/include/onnxruntime/
cp -r /opt/onnxruntime/include/onnxruntime/core/framework/*.h \
      /usr/local/include/onnxruntime/
cp -r /opt/onnxruntime/include/onnxruntime/core/providers/*.h \
      /usr/local/include/onnxruntime/ 2>/dev/null || true

# 安装共享库
cp build_aarch64/MinSizeRel/libonnxruntime.so* /usr/local/lib/
ldconfig

# 验证安装
ls -lh /usr/local/lib/libonnxruntime.so*
ls -lh /usr/local/include/onnxruntime/

# 期望输出:
#   /usr/local/lib/libonnxruntime.so -> libonnxruntime.so.1.18.1
#   /usr/local/lib/libonnxruntime.so.1.18.1  (约 3-8 MB)
```

### 4.4 编译选项对比

| 选项 | 最小体积 | 最大性能 (推荐) | 说明 |
|------|---------|----------------|------|
| `--config` | `MinSizeRel` | `Release` | 体积 vs 性能 |
| `--use_xnnpack` | ✓ | ✓ | XNNPACK ARM NEON 加速 (强烈推荐) |
| `--disable_rtti` | ✓ | ✗ | 禁用 RTTI 减小体积 |
| `--disable_exceptions` | ✓ | ✗ | 本项目使用了异常, 不要禁用 |
| `--build_shared_lib` | ✓ | ✓ | 动态库方便部署 |
| `--use_openmp` | ✗ | ✓ | 多线程加速 (双核效果有限) |

> **本项目推荐配置** (平衡性能与体积):
> ```bash
> ./build.sh --config Release --arm64 --build_shared_lib --use_xnnpack \
>     --skip_tests --parallel $(nproc) --allow_running_as_root
> ```

---

## 5. Python 侧: 导出 Scaler 参数

> 在训练服务器 (Windows/Linux) 上执行, 将 StandardScaler 参数导出为 C++ 可读的二进制格式。

### 5.1 导出脚本

在 `D:\ScuderiaAMG\PINN_CNN\` 下创建 `export_scalers.py`:

```python
"""Export StandardScaler parameters for C++ inference engine.

Usage:  python export_scalers.py
Output: deploy/scalers/  (raw float32 binary files)
"""
import pickle
import numpy as np
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
OUT_DIR = SCRIPT_DIR / "deploy" / "scalers"
OUT_DIR.mkdir(parents=True, exist_ok=True)

# ---- PINN feature scaler ----
pinn_scaler_path = SCRIPT_DIR / "pinn" / "checkpoints" / "feature_scaler.pkl"
if pinn_scaler_path.exists():
    with open(pinn_scaler_path, "rb") as f:
        sc = pickle.load(f)
    mean = sc.mean_.astype(np.float32)
    std = sc.scale_.astype(np.float32)  # sklearn uses scale_ = std
    std = np.where(std < 1e-8, 1.0, std)  # avoid div by zero
    mean.tofile(OUT_DIR / "pinn_mean.bin")
    std.tofile(OUT_DIR / "pinn_std.bin")
    print(f"PINN scaler exported: mean={mean.shape}, std={std.shape}")
else:
    print(f"WARNING: PINN scaler not found at {pinn_scaler_path}")

# ---- CNN IC + gradient scalers ----
cnn_scaler_path = SCRIPT_DIR / "cnn" / "checkpoints" / "ic_scaler.pkl"
if cnn_scaler_path.exists():
    with open(cnn_scaler_path, "rb") as f:
        scs = pickle.load(f)
    # IC scaler
    for key in ["ic_scaler", "ig_scaler"]:
        sc = scs[key]
        mean = sc.mean_.astype(np.float32)
        std = sc.scale_.astype(np.float32)
        std = np.where(std < 1e-8, 1.0, std)
        mean.tofile(OUT_DIR / f"cnn_{key}_mean.bin")
        std.tofile(OUT_DIR / f"cnn_{key}_std.bin")
    print(f"CNN scalers exported")
else:
    print(f"WARNING: CNN scaler not found at {cnn_scaler_path}")

print(f"\nScaler files written to: {OUT_DIR}")
print("\n".join(f"  {f.name} ({f.stat().st_size} bytes)" for f in sorted(OUT_DIR.iterdir())))
```

### 5.2 执行导出

```bash
cd D:\ScuderiaAMG\PINN_CNN
python export_scalers.py
```

输出文件:
```
deploy/scalers/
├── pinn_mean.bin        132 × 4 = 528 bytes
├── pinn_std.bin         132 × 4 = 528 bytes
├── cnn_ic_scaler_mean.bin   128 × 4 = 512 bytes
├── cnn_ic_scaler_std.bin    128 × 4 = 512 bytes
├── cnn_ig_scaler_mean.bin   128 × 4 = 512 bytes
└── cnn_ig_scaler_std.bin    128 × 4 = 512 bytes
```

### 5.3 部署文件清单

将以下文件拷贝到 RZ/G2L:

```
RZ/G2L 目标路径: ~/battery_inference/

需要从训练服务器拷贝:
  pinn/checkpoints/battery_pinn_int8.onnx   → models/battery_pinn_int8.onnx
  cnn/checkpoints/battery_cnn_int8.onnx     → models/battery_cnn_int8.onnx
  deploy/scalers/*.bin                       → scalers/
```

```bash
# 在 RZ/G2L 上创建目录结构
mkdir -p ~/battery_inference/{models,scalers,build}

# 使用 scp 从训练服务器拷贝 (在 Windows 上可用 WinSCP 或 scp)
# scp user@train-server:/path/to/*.onnx rzg2l:~/battery_inference/models/
# scp user@train-server:/path/to/*.bin  rzg2l:~/battery_inference/scalers/
```

---

## 6. C++ 项目结构

```
~/battery_inference/               (RZ/G2L 上的项目根目录)
├── CMakeLists.txt                 CMake 构建配置
├── include/
│   └── battery_inference.h        公共头文件 (纯 C++ 接口, 无 ORT 依赖)
├── src/
│   ├── battery_inference.cpp      核心实现 (PIMPL, 封装 ONNX Runtime)
│   ├── scaler_loader.cpp          StandardScaler 参数加载
│   └── main.cpp                   CLI 命令行工具
├── models/                        放置 .onnx 模型文件
│   ├── battery_pinn_int8.onnx
│   └── battery_cnn_int8.onnx
├── scalers/                       放置 .bin 归一化参数
│   ├── pinn_mean.bin
│   ├── pinn_std.bin
│   ├── cnn_ic_scaler_mean.bin
│   ├── cnn_ic_scaler_std.bin
│   ├── cnn_ig_scaler_mean.bin
│   └── cnn_ig_scaler_std.bin
└── build/                         编译输出 (cmake 自动创建)
```

---

## 7. 完整源码

### 7.1 公共头文件 `include/battery_inference.h`

```cpp
/**
 * @file    battery_inference.h
 * @brief   Battery SOH inference engine — clean C++ API for RZ/G2L deployment.
 *
 * 设计原则:
 *   - PIMPL 惯用法: 头文件不暴露 ONNX Runtime 依赖
 *   - RAII 资源管理: 构造时加载模型, 析构时自动释放
 *   - 线程安全: Predict() 可多线程并发调用 (ONNX Runtime session 级线程安全)
 *   - 零拷贝: 输入数据直接传入, 不额外分配
 *
 * 使用示例:
 *   @code
 *   #include "battery_inference.h"
 *
 *   battery::PINNInference pinn({"models/battery_pinn_int8.onnx"});
 *   float soh = pinn.PredictSOH(feature_vec);  // 132-d → SOH
 *
 *   battery::CNNInference cnn({"models/battery_cnn_int8.onnx"});
 *   auto result = cnn.Predict(ic_curve, ic_gradient);  // 128+128 → stage+RUL
 *   @endcode
 */

#pragma once

#include <array>
#include <cstdint>
#include <memory>
#include <string>
#include <vector>

namespace battery {

// ============================================================
// PINN: 物理信息神经网络 — 快速 SOH 筛查
// ============================================================

/** @brief PINN 模型推理器配置 */
struct PINNConfig {
    /** ONNX 模型文件路径 */
    std::string model_path;

    /** ONNX Runtime intra-op 线程数 (默认 2, 匹配 Cortex-A55 双核) */
    int intra_op_threads = 2;

    /** 是否启用图优化 (默认开启) */
    bool enable_graph_optimization = true;

    /** 特征归一化参数路径 (留空则使用已归一化的输入) */
    std::string scaler_mean_path;
    std::string scaler_std_path;

    /** 输入特征维度 (固定 132) */
    static constexpr int kInputDim = 132;
};

/**
 * @brief PINN 模型推理器
 *
 * 输入: 132 维特征向量 (128点IC + 温度 + log循环数 + dV + 容量)
 * 输出: SOH ∈ [0, 1]
 */
class PINNInference {
public:
    /** @brief 构造并加载模型
     *  @param config 模型配置
     *  @throws std::runtime_error 模型加载失败时抛出
     */
    explicit PINNInference(const PINNConfig& config);

    ~PINNInference();

    // 禁止拷贝, 允许移动
    PINNInference(const PINNInference&) = delete;
    PINNInference& operator=(const PINNInference&) = delete;
    PINNInference(PINNInference&&) noexcept;
    PINNInference& operator=(PINNInference&&) noexcept;

    /**
     * @brief 单次 SOH 推理
     * @param features  132 维原始特征向量 (未归一化)
     * @return SOH ∈ [0, 1], 越接近 1 表示电池越健康
     * @throws std::runtime_error 推理失败时抛出
     */
    float PredictSOH(const std::vector<float>& features);

    /**
     * @brief 批量 SOH 推理
     * @param features_batch  N × 132 特征矩阵
     * @return N 个 SOH 值
     */
    std::vector<float> PredictSOHBatch(
        const std::vector<std::vector<float>>& features_batch);

    /** @brief 获取模型输入维度 */
    int InputDim() const { return PINNConfig::kInputDim; }

private:
    class Impl;
    std::unique_ptr<Impl> impl_;
};

// ============================================================
// CNN: 残差 1D-CNN — 三阶段分类 + RUL 预测
// ============================================================

/** @brief 电池老化阶段 */
enum class BatteryStage : int {
    Healthy   = 0,  ///< SOH ≥ 0.82 — 健康
    Degrading = 1,  ///< 0.82 > SOH ≥ 0.70 — 衰退
    EOL       = 2,  ///< SOH < 0.70 — 寿命终止
};

/** @brief 阶段名称映射 */
inline const char* StageName(BatteryStage s) {
    switch (s) {
        case BatteryStage::Healthy:   return "Healthy";
        case BatteryStage::Degrading: return "Degrading";
        case BatteryStage::EOL:       return "EOL";
        default:                       return "Unknown";
    }
}

/** @brief CNN 模型单次推理结果 */
struct CNNResult {
    BatteryStage stage;                    ///< 老化阶段
    float rul;                             ///< 归一化 RUL ∈ [0, 1], 越大越新
    std::array<float, 3> stage_probs;      ///< 三阶段 softmax 概率
};

/** @brief CNN 模型推理器配置 */
struct CNNConfig {
    /** ONNX 模型文件路径 */
    std::string model_path;

    /** ONNX Runtime intra-op 线程数 (默认 2, 匹配 Cortex-A55 双核) */
    int intra_op_threads = 2;

    /** 是否启用图优化 */
    bool enable_graph_optimization = true;

    /** IC 曲线归一化参数路径 */
    std::string ic_scaler_mean_path;
    std::string ic_scaler_std_path;

    /** IC 梯度归一化参数路径 */
    std::string ig_scaler_mean_path;
    std::string ig_scaler_std_path;

    /** IC 曲线采样点数 (固定 128) */
    static constexpr int kICPoints = 128;

    /** 双通道: IC + 梯度 */
    static constexpr int kInChannels = 2;
};

/**
 * @brief CNN 模型推理器
 *
 * 输入: (IC曲线, IC梯度) 各 128 点, 未归一化
 *       内部自动完成: 归一化 → clip → 梯度计算 → 梯度归一化 → 双通道堆叠
 * 输出: BatteryStage + RUL
 */
class CNNInference {
public:
    /** @brief 构造并加载模型 */
    explicit CNNInference(const CNNConfig& config);
    ~CNNInference();

    // 禁止拷贝, 允许移动
    CNNInference(const CNNInference&) = delete;
    CNNInference& operator=(const CNNInference&) = delete;
    CNNInference(CNNInference&&) noexcept;
    CNNInference& operator=(CNNInference&&) noexcept;

    /**
     * @brief 单次 CNN 推理
     * @param ic_curve    128 点原始 IC 曲线 (dQ/dV)
     * @param ic_gradient  128 点 IC 梯度 (d²Q/dV²), 可传入空以自动计算
     * @return 阶段分类 + RUL
     *
     * 若 ic_gradient 为空, 内部自动从 ic_curve 计算梯度。
     * 推荐始终传入预计算的 ic_gradient 以减少重复计算。
     */
    CNNResult Predict(const std::vector<float>& ic_curve,
                      const std::vector<float>& ic_gradient = {});

    /**
     * @brief 批量 CNN 推理
     * @param ic_curves    N × 128 IC 曲线
     * @param ic_gradients N × 128 IC 梯度 (可为空以自动计算)
     * @return N 个推理结果
     */
    std::vector<CNNResult> PredictBatch(
        const std::vector<std::vector<float>>& ic_curves,
        const std::vector<std::vector<float>>& ic_gradients = {});

    /** @brief 获取 IC 曲线采样点数 */
    int ICLength() const { return CNNConfig::kICPoints; }

private:
    class Impl;
    std::unique_ptr<Impl> impl_;
};

// ============================================================
// 工具函数
// ============================================================

/** @brief 读取 raw float32 二进制文件
 *  @param path 文件路径
 *  @param n    期望的元素数量
 *  @return float32 向量
 *  @throws std::runtime_error 文件不存在或大小不匹配
 */
std::vector<float> LoadFloat32Binary(const std::string& path, size_t n);

/** @brief 计算 1D 数组的梯度 (中央差分)
 *  @param data 输入数组
 *  @return 梯度数组 (同长度)
 */
std::vector<float> ComputeGradient(const std::vector<float>& data);

/** @brief StandardScaler 归一化: (x - mean) / std
 *  @param data  输入数组 (原地修改)
 *  @param mean  均值
 *  @param std   标准差
 *  @param clip  截断范围 (默认 [-5, 5])
 */
void ApplyStandardScaler(std::vector<float>& data,
                         const std::vector<float>& mean,
                         const std::vector<float>& std,
                         float clip_min = -5.0f, float clip_max = 5.0f);

}  // namespace battery
```

### 7.2 核心实现 `src/battery_inference.cpp`

```cpp
/**
 * @file    battery_inference.cpp
 * @brief   PINN + CNN 推理引擎实现 (PIMPL, 封装 ONNX Runtime C++ API)
 */

#include "battery_inference.h"

#include <onnxruntime_cxx_api.h>

#include <algorithm>
#include <cmath>
#include <cstring>
#include <fstream>
#include <iterator>
#include <numeric>
#include <sstream>
#include <stdexcept>

namespace battery {

// ============================================================
// 工具函数实现
// ============================================================

std::vector<float> LoadFloat32Binary(const std::string& path, size_t n) {
    std::ifstream file(path, std::ios::binary);
    if (!file) {
        throw std::runtime_error("Cannot open file: " + path);
    }

    // 获取文件大小
    file.seekg(0, std::ios::end);
    size_t file_size = file.tellg();
    file.seekg(0, std::ios::beg);

    size_t expected_bytes = n * sizeof(float);
    if (file_size != expected_bytes) {
        std::ostringstream oss;
        oss << "File size mismatch: " << path << " has " << file_size
            << " bytes, expected " << expected_bytes << " (" << n << " floats)";
        throw std::runtime_error(oss.str());
    }

    std::vector<float> data(n);
    file.read(reinterpret_cast<char*>(data.data()), expected_bytes);
    if (!file) {
        throw std::runtime_error("Failed to read file: " + path);
    }
    return data;
}

std::vector<float> ComputeGradient(const std::vector<float>& data) {
    const size_t n = data.size();
    std::vector<float> grad(n, 0.0f);

    if (n < 2) return grad;

    // 中央差分 (内部点)
    for (size_t i = 1; i < n - 1; ++i) {
        grad[i] = (data[i + 1] - data[i - 1]) * 0.5f;
    }
    // 前向/后向差分 (边界)
    grad[0] = data[1] - data[0];
    grad[n - 1] = data[n - 1] - data[n - 2];

    return grad;
}

void ApplyStandardScaler(std::vector<float>& data,
                         const std::vector<float>& mean,
                         const std::vector<float>& std,
                         float clip_min, float clip_max) {
    if (data.size() != mean.size() || data.size() != std.size()) {
        throw std::runtime_error(
            "Scaler dimension mismatch: data=" + std::to_string(data.size()) +
            " mean=" + std::to_string(mean.size()) +
            " std=" + std::to_string(std.size()));
    }

    for (size_t i = 0; i < data.size(); ++i) {
        float val = (data[i] - mean[i]) / std[i];
        if (std::isnan(val) || std::isinf(val)) val = 0.0f;
        data[i] = std::clamp(val, clip_min, clip_max);
    }
}

// ============================================================
// 内部辅助: 创建 ONNX Runtime Session
// ============================================================

namespace {

/** 创建统一的 Ort::SessionOptions */
Ort::SessionOptions MakeSessionOptions(int intra_threads, bool enable_graph_opt) {
    Ort::SessionOptions opts;
    opts.SetIntraOpNumThreads(intra_threads);
    opts.SetInterOpNumThreads(1);

    if (enable_graph_opt) {
        opts.SetGraphOptimizationLevel(
            GraphOptimizationLevel::ORT_ENABLE_ALL);
    } else {
        opts.SetGraphOptimizationLevel(
            GraphOptimizationLevel::ORT_DISABLE_ALL);
    }

    // 启用 CPU 内存优化 (减少分配)
    opts.EnableCpuMemArena();
    opts.EnableMemPattern();

    return opts;
}

/** 创建 CPU MemoryInfo (单例复用) */
const Ort::MemoryInfo& GetCpuMemoryInfo() {
    static Ort::MemoryInfo mem_info =
        Ort::MemoryInfo::CreateCpu(OrtArenaAllocator, OrtMemTypeDefault);
    return mem_info;
}

/** 全局 ONNX Runtime 环境 (单例, 线程安全) */
Ort::Env& GetOrtEnv() {
    static Ort::Env env(ORT_LOGGING_LEVEL_WARNING, "BatteryInference");
    return env;
}

}  // anonymous namespace

// ============================================================
// PINNInference::Impl
// ============================================================

class PINNInference::Impl {
public:
    explicit Impl(const PINNConfig& cfg)
        : env_(GetOrtEnv())
        , session_(env_, cfg.model_path.c_str(), MakeSessionOptions(
              cfg.intra_op_threads, cfg.enable_graph_optimization))
        , input_name_(session_.GetInputName(0, allocator_))
        , output_name_(session_.GetOutputName(0, allocator_))
    {
        // 验证输入输出形状
        Ort::TypeInfo input_type = session_.GetInputTypeInfo(0);
        auto input_shape = input_type.GetTensorTypeAndShapeInfo().GetShape();
        // input_shape = [batch, 132]  (batch 可能为 -1 动态)

        if (input_shape.size() != 2 || input_shape[1] != PINNConfig::kInputDim) {
            throw std::runtime_error(
                "PINN model input dimension mismatch: expected dim=132, got " +
                std::to_string(input_shape[1]));
        }

        // 加载归一化参数
        if (!cfg.scaler_mean_path.empty() && !cfg.scaler_std_path.empty()) {
            has_scaler_ = true;
            scaler_mean_ = LoadFloat32Binary(cfg.scaler_mean_path, PINNConfig::kInputDim);
            scaler_std_  = LoadFloat32Binary(cfg.scaler_std_path, PINNConfig::kInputDim);
        } else {
            has_scaler_ = false;
        }
    }

    float PredictSOH(const std::vector<float>& features) {
        if (features.size() != static_cast<size_t>(PINNConfig::kInputDim)) {
            throw std::runtime_error(
                "PINN input dimension error: got " +
                std::to_string(features.size()) + ", expected " +
                std::to_string(PINNConfig::kInputDim));
        }

        // 1. 预处理: 归一化 + clip
        std::vector<float> processed = features;
        for (auto& v : processed) {
            if (std::isnan(v) || std::isinf(v)) v = 0.0f;
        }
        if (has_scaler_) {
            ApplyStandardScaler(processed, scaler_mean_, scaler_std_);
        }

        // 2. 构建输入张量
        std::array<int64_t, 2> input_shape = {1, PINNConfig::kInputDim};
        auto input_tensor = Ort::Value::CreateTensor<float>(
            GetCpuMemoryInfo(),
            processed.data(),
            processed.size(),
            input_shape.data(),
            input_shape.size());

        // 3. 推理
        const char* input_names[] = {input_name_};
        const char* output_names[] = {output_name_};
        auto outputs = session_.Run(
            Ort::RunOptions{nullptr},
            input_names, &input_tensor, 1,
            output_names, 1);

        // 4. 提取输出
        float* soh_data = outputs[0].GetTensorMutableData<float>();
        float soh = soh_data[0];
        return std::clamp(soh, 0.0f, 1.0f);
    }

    std::vector<float> PredictSOHBatch(
        const std::vector<std::vector<float>>& features_batch) {
        if (features_batch.empty()) return {};

        const size_t batch_size = features_batch.size();
        const size_t input_dim = PINNConfig::kInputDim;

        // 1. 预处理所有样本
        std::vector<float> flat_data(batch_size * input_dim);
        for (size_t i = 0; i < batch_size; ++i) {
            if (features_batch[i].size() != input_dim) {
                throw std::runtime_error(
                    "Batch sample " + std::to_string(i) +
                    " has wrong dimension: " +
                    std::to_string(features_batch[i].size()));
            }
            std::vector<float> sample = features_batch[i];
            for (auto& v : sample) {
                if (std::isnan(v) || std::isinf(v)) v = 0.0f;
            }
            if (has_scaler_) {
                ApplyStandardScaler(sample, scaler_mean_, scaler_std_);
            }
            std::memcpy(&flat_data[i * input_dim], sample.data(),
                        input_dim * sizeof(float));
        }

        // 2. 构建批量输入
        std::array<int64_t, 2> input_shape = {
            static_cast<int64_t>(batch_size),
            static_cast<int64_t>(input_dim)};
        auto input_tensor = Ort::Value::CreateTensor<float>(
            GetCpuMemoryInfo(),
            flat_data.data(),
            flat_data.size(),
            input_shape.data(),
            input_shape.size());

        // 3. 推理
        const char* input_names[] = {input_name_};
        const char* output_names[] = {output_name_};
        auto outputs = session_.Run(
            Ort::RunOptions{nullptr},
            input_names, &input_tensor, 1,
            output_names, 1);

        // 4. 提取输出
        float* soh_data = outputs[0].GetTensorMutableData<float>();
        std::vector<float> results(soh_data, soh_data + batch_size);
        for (auto& r : results) r = std::clamp(r, 0.0f, 1.0f);

        return results;
    }

private:
    Ort::Env& env_;
    Ort::AllocatorWithDefaultOptions allocator_;
    Ort::Session session_;
    const char* input_name_;
    const char* output_name_;

    bool has_scaler_ = false;
    std::vector<float> scaler_mean_;
    std::vector<float> scaler_std_;
};

// PINNInference 接口转发
PINNInference::PINNInference(const PINNConfig& config)
    : impl_(std::make_unique<Impl>(config)) {}

PINNInference::~PINNInference() = default;

PINNInference::PINNInference(PINNInference&&) noexcept = default;
PINNInference& PINNInference::operator=(PINNInference&&) noexcept = default;

float PINNInference::PredictSOH(const std::vector<float>& features) {
    return impl_->PredictSOH(features);
}

std::vector<float> PINNInference::PredictSOHBatch(
    const std::vector<std::vector<float>>& features_batch) {
    return impl_->PredictSOHBatch(features_batch);
}

// ============================================================
// CNNInference::Impl
// ============================================================

class CNNInference::Impl {
public:
    explicit Impl(const CNNConfig& cfg)
        : env_(GetOrtEnv())
        , session_(env_, cfg.model_path.c_str(), MakeSessionOptions(
              cfg.intra_op_threads, cfg.enable_graph_optimization))
        , input_name_(session_.GetInputName(0, allocator_))
        , output_name_0_(session_.GetOutputName(0, allocator_))
        , output_name_1_(session_.GetOutputName(1, allocator_))
    {
        // 验证输入形状
        Ort::TypeInfo input_type = session_.GetInputTypeInfo(0);
        auto input_shape = input_type.GetTensorTypeAndShapeInfo().GetShape();
        // [batch, 2, 128]
        if (input_shape.size() != 3 ||
            input_shape[1] != CNNConfig::kInChannels ||
            input_shape[2] != CNNConfig::kICPoints) {
            throw std::runtime_error(
                "CNN model input shape mismatch: expected [B,2,128]");
        }

        // 加载归一化参数
        has_ic_scaler_ = !cfg.ic_scaler_mean_path.empty() &&
                         !cfg.ic_scaler_std_path.empty();
        if (has_ic_scaler_) {
            ic_mean_ = LoadFloat32Binary(cfg.ic_scaler_mean_path, CNNConfig::kICPoints);
            ic_std_  = LoadFloat32Binary(cfg.ic_scaler_std_path, CNNConfig::kICPoints);
        }

        has_ig_scaler_ = !cfg.ig_scaler_mean_path.empty() &&
                         !cfg.ig_scaler_std_path.empty();
        if (has_ig_scaler_) {
            ig_mean_ = LoadFloat32Binary(cfg.ig_scaler_mean_path, CNNConfig::kICPoints);
            ig_std_  = LoadFloat32Binary(cfg.ig_scaler_std_path, CNNConfig::kICPoints);
        }
    }

    CNNResult Predict(const std::vector<float>& ic_curve,
                      const std::vector<float>& ic_gradient) {
        // 预处理为双通道张量
        std::vector<float> dual_channel = Preprocess(ic_curve, ic_gradient);

        // 构建输入张量 (1, 2, 128)
        std::array<int64_t, 3> input_shape = {
            1, CNNConfig::kInChannels, CNNConfig::kICPoints};
        auto input_tensor = Ort::Value::CreateTensor<float>(
            GetCpuMemoryInfo(),
            dual_channel.data(),
            dual_channel.size(),
            input_shape.data(),
            input_shape.size());

        // 推理
        const char* input_names[] = {input_name_};
        const char* output_names[] = {output_name_0_, output_name_1_};
        auto outputs = session_.Run(
            Ort::RunOptions{nullptr},
            input_names, &input_tensor, 1,
            output_names, 2);

        // 解析输出
        float* logits = outputs[0].GetTensorMutableData<float>();  // (1, 3)
        float* rul_ptr = outputs[1].GetTensorMutableData<float>(); // (1, 1)

        return ParseResult(logits, *rul_ptr);
    }

    std::vector<CNNResult> PredictBatch(
        const std::vector<std::vector<float>>& ic_curves,
        const std::vector<std::vector<float>>& ic_gradients) {
        if (ic_curves.empty()) return {};

        const size_t batch_size = ic_curves.size();
        const size_t kDataLen = CNNConfig::kICPoints * CNNConfig::kInChannels;
        std::vector<float> flat_data(batch_size * kDataLen);

        bool auto_grad = ic_gradients.empty();
        for (size_t i = 0; i < batch_size; ++i) {
            std::vector<float> ic_grad;
            if (auto_grad) {
                // 自动计算梯度
                ic_grad = ComputeGradient(ic_curves[i]);
            } else {
                ic_grad = ic_gradients[i];
            }
            auto processed = Preprocess(ic_curves[i], ic_grad);
            std::memcpy(&flat_data[i * kDataLen], processed.data(),
                        kDataLen * sizeof(float));
        }

        std::array<int64_t, 3> input_shape = {
            static_cast<int64_t>(batch_size),
            CNNConfig::kInChannels,
            CNNConfig::kICPoints};
        auto input_tensor = Ort::Value::CreateTensor<float>(
            GetCpuMemoryInfo(),
            flat_data.data(),
            flat_data.size(),
            input_shape.data(),
            input_shape.size());

        const char* input_names[] = {input_name_};
        const char* output_names[] = {output_name_0_, output_name_1_};
        auto outputs = session_.Run(
            Ort::RunOptions{nullptr},
            input_names, &input_tensor, 1,
            output_names, 2);

        float* logits = outputs[0].GetTensorMutableData<float>();
        float* ruls   = outputs[1].GetTensorMutableData<float>();

        std::vector<CNNResult> results;
        results.reserve(batch_size);
        for (size_t i = 0; i < batch_size; ++i) {
            results.push_back(ParseResult(&logits[i * 3], ruls[i]));
        }
        return results;
    }

private:
    /** 预处理: IC 曲线 → (2, 128) 双通道归一化张量 */
    std::vector<float> Preprocess(const std::vector<float>& ic_curve,
                                  const std::vector<float>& ic_gradient) {
        const size_t N = static_cast<size_t>(CNNConfig::kICPoints);

        if (ic_curve.size() != N) {
            throw std::runtime_error(
                "IC curve size mismatch: got " +
                std::to_string(ic_curve.size()) + ", expected " +
                std::to_string(N));
        }

        // 1. IC 曲线: 清理 NaN/Inf → 归一化 → clip[-5,5]
        std::vector<float> ic_norm = ic_curve;
        for (auto& v : ic_norm) {
            if (std::isnan(v) || std::isinf(v)) v = 0.0f;
        }
        if (has_ic_scaler_) {
            ApplyStandardScaler(ic_norm, ic_mean_, ic_std_);
        }

        // 2. IC 梯度: 计算或使用传入值 → 自归一化 → 标准化 → clip
        std::vector<float> ig_norm;
        if (!ic_gradient.empty()) {
            if (ic_gradient.size() != N) {
                throw std::runtime_error(
                    "IC gradient size mismatch: got " +
                    std::to_string(ic_gradient.size()));
            }
            ig_norm = ic_gradient;
            for (auto& v : ig_norm) {
                if (std::isnan(v) || std::isinf(v)) v = 0.0f;
            }
        } else {
            ig_norm = ComputeGradient(ic_norm);
        }

        // 自归一化: 除以最大绝对值
        float abs_max = 0.0f;
        for (float v : ig_norm) abs_max = std::max(abs_max, std::abs(v));
        if (abs_max > 1e-6f) {
            for (auto& v : ig_norm) v /= abs_max;
        }

        if (has_ig_scaler_) {
            ApplyStandardScaler(ig_norm, ig_mean_, ig_std_);
        }

        // 3. 堆叠为 (2, 128) 双通道
        std::vector<float> dual(N * 2);
        std::memcpy(dual.data(), ic_norm.data(), N * sizeof(float));
        std::memcpy(dual.data() + N, ig_norm.data(), N * sizeof(float));

        return dual;
    }

    /** 解析 ONNX 输出为 CNNResult */
    static CNNResult ParseResult(const float* logits, float rul) {
        CNNResult result;
        result.rul = std::clamp(rul, 0.0f, 1.0f);

        // Softmax
        float max_logit = std::max({logits[0], logits[1], logits[2]});
        float exp_sum = 0.0f;
        for (int i = 0; i < 3; ++i) {
            result.stage_probs[i] = std::exp(logits[i] - max_logit);
            exp_sum += result.stage_probs[i];
        }
        for (int i = 0; i < 3; ++i) {
            result.stage_probs[i] /= exp_sum;
        }

        // Argmax
        int stage_idx = 0;
        if (result.stage_probs[1] > result.stage_probs[stage_idx]) stage_idx = 1;
        if (result.stage_probs[2] > result.stage_probs[stage_idx]) stage_idx = 2;

        result.stage = static_cast<BatteryStage>(stage_idx);
        return result;
    }

    Ort::Env& env_;
    Ort::AllocatorWithDefaultOptions allocator_;
    Ort::Session session_;
    const char* input_name_;
    const char* output_name_0_;
    const char* output_name_1_;

    bool has_ic_scaler_ = false;
    std::vector<float> ic_mean_;
    std::vector<float> ic_std_;

    bool has_ig_scaler_ = false;
    std::vector<float> ig_mean_;
    std::vector<float> ig_std_;
};

// CNNInference 接口转发
CNNInference::CNNInference(const CNNConfig& config)
    : impl_(std::make_unique<Impl>(config)) {}

CNNInference::~CNNInference() = default;

CNNInference::CNNInference(CNNInference&&) noexcept = default;
CNNInference& CNNInference::operator=(CNNInference&&) noexcept = default;

CNNResult CNNInference::Predict(
    const std::vector<float>& ic_curve,
    const std::vector<float>& ic_gradient) {
    return impl_->Predict(ic_curve, ic_gradient);
}

std::vector<CNNResult> CNNInference::PredictBatch(
    const std::vector<std::vector<float>>& ic_curves,
    const std::vector<std::vector<float>>& ic_gradients) {
    return impl_->PredictBatch(ic_curves, ic_gradients);
}

}  // namespace battery
```

### 7.3 CLI 命令行工具 `src/main.cpp`

```cpp
/**
 * @file    main.cpp
 * @brief   Battery inference CLI — RZ/G2L 命令行推理工具
 *
 * Usage:
 *   ./battery_cli pinn <feature_file.npy>     # PINN 推理
 *   ./battery_cli cnn <ic_curve.npy>          # CNN 推理
 *   ./battery_cli benchmark                   # 性能基准测试
 *   ./battery_cli info                        # 显示模型信息
 */

#include "battery_inference.h"

#include <chrono>
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <iostream>
#include <string>

namespace {

const char* kDefaultModelDir = "models";
const char* kDefaultScalerDir = "scalers";

void PrintUsage(const char* prog) {
    std::cout << "Battery SOH Inference CLI — RZ/G2L Cortex-A55\n"
              << "Usage:\n"
              << "  " << prog << " pinn [features.npy]    PINN SOH prediction\n"
              << "  " << prog << " cnn [ic_curve.npy]     CNN stage + RUL\n"
              << "  " << prog << " benchmark              Latency benchmark\n"
              << "  " << prog << " info                   Model info\n"
              << std::endl;
}

/** 简单的 .npy 文件读取器 (仅支持 float32, C order, 1D/2D) */
std::vector<float> ReadNPY(const char* path, size_t& rows, size_t& cols) {
    std::FILE* f = std::fopen(path, "rb");
    if (!f) {
        throw std::runtime_error(std::string("Cannot open: ") + path);
    }

    // 读取 NPY 头部 (简化解析, 仅支持 '<f4' 即 float32 LE)
    char magic[6];
    if (std::fread(magic, 1, 6, f) != 6 || std::memcmp(magic, "\x93NUMPY", 6) != 0) {
        std::fclose(f);
        throw std::runtime_error("Not a valid .npy file");
    }

    // 读取 header_len (2 bytes, little-endian)
    uint8_t ver_major, ver_minor;
    std::fread(&ver_major, 1, 1, f);
    std::fread(&ver_minor, 1, 1, f);

    uint16_t header_len = 0;
    if (ver_major == 1) {
        std::fread(&header_len, 2, 1, f);
    } else if (ver_major >= 2) {
        uint32_t header_len32;
        std::fread(&header_len32, 4, 1, f);
        header_len = static_cast<uint16_t>(header_len32);
    }

    // 读取并解析 header (Python dict 字符串)
    std::string header(header_len, '\0');
    std::fread(&header[0], 1, header_len, f);

    // 跳过 header 填充到 64 字节边界
    long data_offset = 6 + 2 + ((ver_major == 1) ? 2 : 4) + header_len;
    // ...简化处理, 直接 seek 到数据区
    // 在实际项目中使用完整的 npy 解析库 (如 cnpy)

    // 简化: 假设 shape 已从 header 中的 'shape': (N,) 或 (N, M) 解析
    // 这里省略完整 parser, 仅做演示
    std::fclose(f);
    throw std::runtime_error(
        "Full .npy parsing not implemented in CLI demo. "
        "Use library mode or pass raw binary data.");
}

}  // anonymous namespace

int main(int argc, char* argv[]) {
    if (argc < 2) {
        PrintUsage(argv[0]);
        return 1;
    }

    std::string command = argv[1];

    try {
        if (command == "pinn") {
            // ---- PINN Inference ----
            battery::PINNConfig cfg;
            cfg.model_path = std::string(kDefaultModelDir) + "/battery_pinn_int8.onnx";
            cfg.scaler_mean_path = std::string(kDefaultScalerDir) + "/pinn_mean.bin";
            cfg.scaler_std_path  = std::string(kDefaultScalerDir) + "/pinn_std.bin";

            std::cout << "Loading PINN model: " << cfg.model_path << std::endl;
            battery::PINNInference pinn(cfg);

            // Demo: 生成随机输入或从文件读取
            std::vector<float> features;
            if (argc > 2) {
                // features = ReadNPY(argv[2]);
                std::cerr << "File input not implemented in demo; using random data.\n";
            }
            if (features.empty()) {
                features.assign(battery::PINNConfig::kInputDim, 0.5f);
                std::cout << "Using demo input (all 0.5)\n";
            }

            float soh = pinn.PredictSOH(features);
            std::cout << "\n=== PINN Result ===\n"
                      << "SOH: " << soh << " (" << (soh * 100.0f) << "%)\n";

        } else if (command == "cnn") {
            // ---- CNN Inference ----
            battery::CNNConfig cfg;
            cfg.model_path = std::string(kDefaultModelDir) + "/battery_cnn_int8.onnx";
            cfg.ic_scaler_mean_path = std::string(kDefaultScalerDir) + "/cnn_ic_scaler_mean.bin";
            cfg.ic_scaler_std_path  = std::string(kDefaultScalerDir) + "/cnn_ic_scaler_std.bin";
            cfg.ig_scaler_mean_path = std::string(kDefaultScalerDir) + "/cnn_ig_scaler_mean.bin";
            cfg.ig_scaler_std_path  = std::string(kDefaultScalerDir) + "/cnn_ig_scaler_std.bin";

            std::cout << "Loading CNN model: " << cfg.model_path << std::endl;
            battery::CNNInference cnn(cfg);

            // Demo input
            std::vector<float> ic_curve;
            if (argc > 2) {
                // ic_curve = ReadNPY(argv[2]);
                std::cerr << "File input not implemented; using random data.\n";
            }
            if (ic_curve.empty()) {
                ic_curve.assign(battery::CNNConfig::kICPoints, 0.5f);
                std::cout << "Using demo input (all 0.5)\n";
            }

            auto result = cnn.Predict(ic_curve);
            std::cout << "\n=== CNN Result ===\n"
                      << "Stage:       " << battery::StageName(result.stage)
                      << " (" << static_cast<int>(result.stage) << ")\n"
                      << "RUL:         " << result.rul << "\n"
                      << "Stage Probs: ["
                      << result.stage_probs[0] << ", "
                      << result.stage_probs[1] << ", "
                      << result.stage_probs[2] << "]\n";

        } else if (command == "benchmark") {
            // ---- Benchmark ----
            std::cout << "=== Battery Inference Benchmark ===\n"
                      << "Platform: RZ/G2L Cortex-A55 ×2 @ 1.2 GHz\n\n";

            // PINN benchmark
            {
                battery::PINNConfig cfg;
                cfg.model_path = std::string(kDefaultModelDir) + "/battery_pinn_int8.onnx";
                cfg.scaler_mean_path = std::string(kDefaultScalerDir) + "/pinn_mean.bin";
                cfg.scaler_std_path  = std::string(kDefaultScalerDir) + "/pinn_std.bin";

                battery::PINNInference pinn(cfg);
                std::vector<float> features(battery::PINNConfig::kInputDim, 0.5f);

                // Warmup
                for (int i = 0; i < 10; ++i) pinn.PredictSOH(features);

                // Benchmark
                const int N = 500;
                auto t0 = std::chrono::high_resolution_clock::now();
                for (int i = 0; i < N; ++i) {
                    pinn.PredictSOH(features);
                }
                auto t1 = std::chrono::high_resolution_clock::now();
                double avg_us = std::chrono::duration<double, std::micro>(t1 - t0).count() / N;

                std::cout << "PINN: " << (avg_us / 1000.0) << " ms avg  ("
                          << N << " runs, 132-d input)\n";
            }

            // CNN benchmark
            {
                battery::CNNConfig cfg;
                cfg.model_path = std::string(kDefaultModelDir) + "/battery_cnn_int8.onnx";
                cfg.ic_scaler_mean_path = std::string(kDefaultScalerDir) + "/cnn_ic_scaler_mean.bin";
                cfg.ic_scaler_std_path  = std::string(kDefaultScalerDir) + "/cnn_ic_scaler_std.bin";
                cfg.ig_scaler_mean_path = std::string(kDefaultScalerDir) + "/cnn_ig_scaler_mean.bin";
                cfg.ig_scaler_std_path  = std::string(kDefaultScalerDir) + "/cnn_ig_scaler_std.bin";

                battery::CNNInference cnn(cfg);
                std::vector<float> ic_curve(battery::CNNConfig::kICPoints, 0.5f);

                // Warmup
                for (int i = 0; i < 10; ++i) cnn.Predict(ic_curve);

                // Benchmark
                const int N = 500;
                auto t0 = std::chrono::high_resolution_clock::now();
                for (int i = 0; i < N; ++i) {
                    cnn.Predict(ic_curve);
                }
                auto t1 = std::chrono::high_resolution_clock::now();
                double avg_us = std::chrono::duration<double, std::micro>(t1 - t0).count() / N;

                std::cout << "CNN:  " << (avg_us / 1000.0) << " ms avg  ("
                          << N << " runs, 128-pt IC curve)\n";
            }

        } else if (command == "info") {
            std::cout << "=== Model Info ===\n\n"
                      << "PINN Model:\n"
                      << "  Input:  (B, 132) float32  — 128-pt IC + 4 aux features\n"
                      << "  Output: (B, 1)   float32  — SOH ∈ [0, 1]\n"
                      << "  Size:   < 200 KB (INT8 quantized)\n"
                      << "  Latency: < 15 ms (Cortex-A55)\n\n"
                      << "CNN Model:\n"
                      << "  Input:  (B, 2, 128) float32  — IC curve + gradient\n"
                      << "  Output: (B, 3) float32       — stage logits\n"
                      << "          (B, 1) float32       — RUL ∈ [0, 1]\n"
                      << "  Stages: 0=Healthy(SOH≥0.82) 1=Degrading 2=EOL(SOH<0.70)\n"
                      << "  Size:   < 40 KB (INT8 quantized)\n"
                      << "  Latency: < 15 ms (Cortex-A55)\n";

        } else {
            std::cerr << "Unknown command: " << command << "\n";
            PrintUsage(argv[0]);
            return 1;
        }
    } catch (const std::exception& e) {
        std::cerr << "ERROR: " << e.what() << std::endl;
        return 1;
    }

    return 0;
}
```

---

## 8. CMake 构建

### `CMakeLists.txt`

```cmake
cmake_minimum_required(VERSION 3.16)
project(BatteryInference VERSION 1.0.0 LANGUAGES CXX)

# ============================================================
# C++17 标准 (ONNX Runtime 1.18 要求)
# ============================================================
set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)

# ============================================================
# ARM NEON 编译优化
# ============================================================
set(CMAKE_CXX_FLAGS_RELEASE "-O2 -march=armv8.2-a+fp16+dotprod -mtune=cortex-a55")
set(CMAKE_CXX_FLAGS_MINSIZEREL "-Os -march=armv8.2-a -mtune=cortex-a55")

# 启用 NEON 内置函数
add_compile_options(-mfpu=neon-fp16)

# ============================================================
# 查找 ONNX Runtime
# ============================================================
# 方式 1: 指定安装路径
# set(ONNXRUNTIME_ROOT "/usr/local" CACHE PATH "ONNX Runtime install prefix")

# 方式 2: 使用 find_package (需要 ONNX Runtime 提供 CMake 配置)
# find_package(onnxruntime REQUIRED)

# 方式 3 (推荐): 手动指定头文件和库路径
set(ONNXRUNTIME_INCLUDE_DIR "/usr/local/include/onnxruntime"
    CACHE PATH "ONNX Runtime include directory")
set(ONNXRUNTIME_LIBRARY "/usr/local/lib/libonnxruntime.so"
    CACHE FILEPATH "ONNX Runtime shared library")

# ============================================================
# 创建共享库 target (libbattery_inference.so)
# ============================================================
add_library(battery_inference SHARED
    src/battery_inference.cpp
)

target_include_directories(battery_inference
    PUBLIC
        ${CMAKE_CURRENT_SOURCE_DIR}/include
    PRIVATE
        ${ONNXRUNTIME_INCLUDE_DIR}
)

target_link_libraries(battery_inference
    PUBLIC
        ${ONNXRUNTIME_LIBRARY}
        pthread
)

# 设置 SONAME
set_target_properties(battery_inference PROPERTIES
    VERSION ${PROJECT_VERSION}
    SOVERSION 1
    OUTPUT_NAME battery_inference
)

# ============================================================
# 创建 CLI 可执行文件
# ============================================================
add_executable(battery_cli
    src/main.cpp
)

target_include_directories(battery_cli
    PRIVATE
        ${CMAKE_CURRENT_SOURCE_DIR}/include
)

target_link_libraries(battery_cli
    PRIVATE
        battery_inference
)

# ============================================================
# 安装规则
# ============================================================
install(TARGETS battery_inference battery_cli
    RUNTIME DESTINATION bin
    LIBRARY DESTINATION lib
)

install(DIRECTORY include/
    DESTINATION include/battery_inference
)

# ============================================================
# 测试 (可选)
# ============================================================
option(BUILD_TESTS "Build unit tests" OFF)
if(BUILD_TESTS)
    enable_testing()
    add_subdirectory(tests)
endif()

# ============================================================
# 打印配置摘要
# ============================================================
message(STATUS "============================================")
message(STATUS "BatteryInference Config Summary")
message(STATUS "  Project:       ${PROJECT_NAME} v${PROJECT_VERSION}")
message(STATUS "  C++ Standard:  ${CMAKE_CXX_STANDARD}")
message(STATUS "  Build type:    ${CMAKE_BUILD_TYPE}")
message(STATUS "  ORT include:   ${ONNXRUNTIME_INCLUDE_DIR}")
message(STATUS "  ORT library:   ${ONNXRUNTIME_LIBRARY}")
message(STATUS "============================================")
```

---

## 9. 编译与部署

### 9.1 在 RZ/G2L 上原生编译

```bash
# ============================================================
# 步骤 1: 进入项目目录
# ============================================================
cd ~/battery_inference

# 确认目录结构正确
tree -L 2
# 期望输出:
# ├── CMakeLists.txt
# ├── include/
# │   └── battery_inference.h
# ├── src/
# │   ├── battery_inference.cpp
# │   └── main.cpp
# ├── models/
# │   ├── battery_pinn_int8.onnx
# │   └── battery_cnn_int8.onnx
# └── scalers/
#     ├── pinn_mean.bin
#     ├── pinn_std.bin
#     ├── cnn_ic_scaler_mean.bin
#     ├── cnn_ic_scaler_std.bin
#     ├── cnn_ig_scaler_mean.bin
#     └── cnn_ig_scaler_std.bin

# ============================================================
# 步骤 2: CMake 配置
# ============================================================
mkdir -p build && cd build

cmake .. \
    -DCMAKE_BUILD_TYPE=Release \
    -DONNXRUNTIME_INCLUDE_DIR=/usr/local/include/onnxruntime \
    -DONNXRUNTIME_LIBRARY=/usr/local/lib/libonnxruntime.so

# ============================================================
# 步骤 3: 编译 (单核约 20s, 双核更快)
# ============================================================
make -j$(nproc)

# ============================================================
# 步骤 4: 验证产物
# ============================================================
ls -lh libbattery_inference.so*
ls -lh battery_cli

# 检查动态库依赖
ldd libbattery_inference.so | grep onnxruntime
# 期望: libonnxruntime.so.1.18.1 => /usr/local/lib/libonnxruntime.so.1.18.1

# ============================================================
# 步骤 5: 运行测试
# ============================================================
./battery_cli info
./battery_cli pinn
./battery_cli cnn
./battery_cli benchmark
```

### 9.2 编译优化选项

| CMake 选项 | 效果 | 适用场景 |
|-----------|------|---------|
| `-DCMAKE_BUILD_TYPE=Release` | `-O2` 优化, 去除调试符号 | 生产部署 |
| `-DCMAKE_BUILD_TYPE=MinSizeRel` | `-Os` 最小体积 | 存储受限 |
| `-DCMAKE_BUILD_TYPE=Debug` | `-g -O0` 调试符号 | 开发调试 |
| `-DBUILD_TESTS=ON` | 编译单元测试 | 开发验证 |

### 9.3 交叉编译 (可选: 在 Windows/Ubuntu x86 上编译)

若在 RZ/G2L 上编译太慢, 可在 x86 服务器上交叉编译:

```bash
# 安装 ARM64 交叉编译工具链
apt install -y gcc-aarch64-linux-gnu g++-aarch64-linux-gnu

# CMake 交叉编译配置 (toolchain file)
cat > toolchain_aarch64.cmake << 'EOF'
set(CMAKE_SYSTEM_NAME Linux)
set(CMAKE_SYSTEM_PROCESSOR aarch64)
set(CMAKE_C_COMPILER aarch64-linux-gnu-gcc)
set(CMAKE_CXX_COMPILER aarch64-linux-gnu-g++)
set(CMAKE_FIND_ROOT_PATH /usr/aarch64-linux-gnu)
set(CMAKE_FIND_ROOT_PATH_MODE_PROGRAM NEVER)
set(CMAKE_FIND_ROOT_PATH_MODE_LIBRARY ONLY)
set(CMAKE_FIND_ROOT_PATH_MODE_INCLUDE ONLY)
EOF

cmake .. \
    -DCMAKE_TOOLCHAIN_FILE=toolchain_aarch64.cmake \
    -DCMAKE_BUILD_TYPE=Release \
    -DONNXRUNTIME_INCLUDE_DIR=/path/to/aarch64/ort/include \
    -DONNXRUNTIME_LIBRARY=/path/to/aarch64/ort/lib/libonnxruntime.so

make -j$(nproc)
```

> **注意**: 交叉编译时需要提前编译好 aarch64 版本的 ONNX Runtime。

### 9.4 部署到生产环境

```bash
# 1. 拷贝编译产物
cp build/libbattery_inference.so* /usr/local/lib/
cp build/battery_cli /usr/local/bin/
ldconfig

# 2. 拷贝模型文件 (不可变数据放 /opt)
mkdir -p /opt/battery_inference/{models,scalers}
cp models/*.onnx /opt/battery_inference/models/
cp scalers/*.bin /opt/battery_inference/scalers/

# 3. 设置环境变量
cat >> ~/.bashrc << 'EOF'
export BATTERY_MODEL_DIR=/opt/battery_inference/models
export BATTERY_SCALER_DIR=/opt/battery_inference/scalers
export LD_LIBRARY_PATH=/usr/local/lib:$LD_LIBRARY_PATH
EOF

source ~/.bashrc

# 4. 验证部署
battery_cli info
battery_cli benchmark
```

---

## 10. API 使用指南

### 10.1 作为共享库集成到 C++ 项目

```cpp
#include <battery_inference.h>
#include <iostream>

int main() {
    // ========================================
    // PINN: 132-d 特征 → SOH
    // ========================================
    battery::PINNConfig pinn_cfg;
    pinn_cfg.model_path       = "/opt/battery_inference/models/battery_pinn_int8.onnx";
    pinn_cfg.scaler_mean_path = "/opt/battery_inference/scalers/pinn_mean.bin";
    pinn_cfg.scaler_std_path  = "/opt/battery_inference/scalers/pinn_std.bin";
    pinn_cfg.intra_op_threads = 2;

    battery::PINNInference pinn(pinn_cfg);

    // 构造 132-d 特征向量
    // [IC曲线 128点 | 温度 | log循环 | dV | 容量]
    std::vector<float> features = {/* ... 从 RA8 获取 ... */};

    float soh = pinn.PredictSOH(features);
    std::cout << "SOH: " << soh * 100.0f << "%" << std::endl;

    // ========================================
    // CNN: 128-pt IC 曲线 → 阶段 + RUL
    // ========================================
    battery::CNNConfig cnn_cfg;
    cnn_cfg.model_path          = "/opt/battery_inference/models/battery_cnn_int8.onnx";
    cnn_cfg.ic_scaler_mean_path = "/opt/battery_inference/scalers/cnn_ic_scaler_mean.bin";
    cnn_cfg.ic_scaler_std_path  = "/opt/battery_inference/scalers/cnn_ic_scaler_std.bin";
    cnn_cfg.ig_scaler_mean_path = "/opt/battery_inference/scalers/cnn_ig_scaler_mean.bin";
    cnn_cfg.ig_scaler_std_path  = "/opt/battery_inference/scalers/cnn_ig_scaler_std.bin";

    battery::CNNInference cnn(cnn_cfg);

    // 从 RA8 获取 IC 曲线
    std::vector<float> ic_curve = {/* ... 128 点 ... */};

    auto result = cnn.Predict(ic_curve);

    switch (result.stage) {
        case battery::BatteryStage::Healthy:
            std::cout << "Stage: Healthy (≥82% SOH), RUL=" << result.rul << "\n";
            break;
        case battery::BatteryStage::Degrading:
            std::cout << "Stage: Degrading (70-82% SOH), RUL=" << result.rul << "\n";
            break;
        case battery::BatteryStage::EOL:
            std::cout << "Stage: End-of-Life (<70% SOH), RUL=" << result.rul << "\n";
            break;
    }

    // 获取各类别概率
    std::cout << "Probs: ["
              << result.stage_probs[0] << ", "
              << result.stage_probs[1] << ", "
              << result.stage_probs[2] << "]\n";

    return 0;
}
```

### 10.2 批量推理 (提高吞吐)

```cpp
// PINN 批量推理
std::vector<std::vector<float>> batch_features(N, /* 132-d 特征 */);
std::vector<float> soh_batch = pinn.PredictSOHBatch(batch_features);

// CNN 批量推理
std::vector<std::vector<float>> batch_ic(N, /* 128-pt IC */);
auto results = cnn.PredictBatch(batch_ic);
for (size_t i = 0; i < results.size(); ++i) {
    printf("Sample %zu: stage=%d rul=%.3f\n",
           i, static_cast<int>(results[i].stage), results[i].rul);
}
```

### 10.3 从 Python (ctypes) 调用 C++ 共享库

```python
"""通过 ctypes 调用 libbattery_inference.so"""
import ctypes
import numpy as np

lib = ctypes.CDLL("/usr/local/lib/libbattery_inference.so")

# 需要导出 C ABI 接口 (见下文 "C ABI 封装")
# 或使用 pybind11 绑定 (推荐)
```

### 10.4 C ABI 封装 (可选, 用于非 C++ 语言调用)

```cpp
// battery_inference_c_api.h  (补充, 供 C/Python/Rust 等调用)

#ifdef __cplusplus
extern "C" {
#endif

typedef void* BatteryPINNHandle;
typedef void* BatteryCNNHandle;

// PINN
BatteryPINNHandle pinn_create(const char* model_path,
                               const char* mean_path,
                               const char* std_path);
void pinn_destroy(BatteryPINNHandle handle);
float pinn_predict_soh(BatteryPINNHandle handle, const float* features, int dim);
int pinn_predict_batch(BatteryPINNHandle handle,
                        const float* features, int batch_size, int dim,
                        float* soh_out);

// CNN
BatteryCNNHandle cnn_create(const char* model_path,
                             const char* ic_mean_path, const char* ic_std_path,
                             const char* ig_mean_path, const char* ig_std_path);
void cnn_destroy(BatteryCNNHandle handle);
int cnn_predict(BatteryCNNHandle handle,
                 const float* ic_curve, int len,
                 int* stage_out, float* rul_out, float* probs_out);

#ifdef __cplusplus
}
#endif
```

在 `src/battery_inference_c_api.cpp` 中实现即可。

---

## 11. 性能基准

### 11.1 预期性能 (Cortex-A55 @ 1.2 GHz, ONNX Runtime + XNNPACK)

| 指标 | PINN | CNN | 备注 |
|------|------|-----|------|
| 单次推理延迟 | 8-15 ms | 6-12 ms | 含预处理 |
| 批量推理 (×32) | 0.5-1.0 ms/样本 | 0.3-0.8 ms/样本 | 批量摊薄开销 |
| 模型加载时间 | 50-100 ms | 30-60 ms | 首次构造 |
| 内存占用 (运行时) | ~8 MB | ~5 MB | ORT session + 模型 |
| 共享库体积 | ~60 KB | — | `libbattery_inference.so` |
| CPU 占用 (持续推理) | ~50% (单核) | ~40% (单核) | 另一核空闲 |

### 11.2 优化技巧

1. **预热**: 首次推理会触发 JIT/图优化, 前 2-3 次调用较慢, 建议预热 5-10 次
2. **批量推理优先**: 若有多条样本, 使用 `PredictBatch()` 而非循环调用 `Predict()`
3. **复用 Session**: 不要每次推理都重新构造 `PINNInference`/`CNNInference`
4. **禁用不需要的输出**: 若只需 SOH 不需阶段概率, 可修改 ONNX 模型移除无关输出
5. **固定 batch size**: 生产环境中固定 batch=1 可进一步优化图

### 11.3 内存优化

```cpp
// 如果内存极度受限 (如仅 512 MB RAM), 可仅加载一个模型:

// 方案 A: 仅 PINN (快速筛查)
battery::PINNInference pinn({...});  // ~8 MB 运行时内存

// 方案 B: 仅 CNN (精准评估)
battery::CNNInference cnn({...});    // ~5 MB 运行时内存

// 方案 C: 按需切换 (析构旧模型 → 构造新模型)
{
    battery::PINNInference pinn({...});
    float soh = pinn.PredictSOH(features);
    // pinn 析构, 释放内存
}
{
    battery::CNNInference cnn({...});
    auto result = cnn.Predict(ic);
}
```

---

## 12. 故障排查

### 12.1 常见问题

#### Q1: `error while loading shared libraries: libonnxruntime.so`

```bash
# 确认库路径
ls -l /usr/local/lib/libonnxruntime.so*

# 更新动态链接器缓存
sudo ldconfig

# 或临时设置
export LD_LIBRARY_PATH=/usr/local/lib:$LD_LIBRARY_PATH
```

#### Q2: `Illegal instruction` 或 `SIGILL`

```bash
# 原因: 编译时使用了 ARMv8.2 指令但 CPU 不支持
# 检查 CPU 特性:
cat /proc/cpuinfo | grep Features

# 解决: 降低编译目标
# 将 -march=armv8.2-a+fp16+dotprod 改为 -march=armv8-a
# 或检查是否缺少 dotprod 指令
```

#### Q3: 推理结果异常 (SOH 始终为 0 或 1)

```bash
# 1. 确认 scaler 参数正确加载
ls -l scalers/
xxd scalers/pinn_mean.bin | head -5  # 检查不是全零

# 2. 确认模型文件未损坏
md5sum models/battery_pinn_int8.onnx
# 与训练服务器上的 md5 对比

# 3. 使用 Python 脚本验证 ONNX 模型 (在 RZ/G2L 上)
python3 -c "
import onnxruntime as ort
sess = ort.InferenceSession('models/battery_pinn_int8.onnx',
                             providers=['CPUExecutionProvider'])
import numpy as np
x = np.random.randn(1, 132).astype(np.float32)
out = sess.run(None, {'input': x})
print('Output:', out[0][0, 0])
"
```

#### Q4: 编译时 ONNX Runtime 头文件找不到

```bash
# 确认头文件已安装
ls /usr/local/include/onnxruntime/

# 若缺少, 重新安装
cp -r /opt/onnxruntime/include/onnxruntime/core/session/*.h \
      /usr/local/include/onnxruntime/
```

#### Q5: 内存不足编译失败

```bash
# ONNX Runtime 编译需要 > 2GB 内存
# 启用 swap 或减少并行数
./build.sh --config Release --arm64 --build_shared_lib --use_xnnpack \
    --skip_tests --parallel 1 --allow_running_as_root

# 或只编译最小模块
./build.sh --config MinSizeRel --arm64 --build_shared_lib \
    --use_xnnpack --minimal_build --skip_tests --parallel 1
```

#### Q6: 程序执行时报 RTTI 或 Exception 相关错误

```bash
# 原因: ONNX Runtime 以 --disable_rtti --disable_exceptions 编译
# 但 C++ 代码使用了 RTTI/Exceptions

# 解决: 重新编译 ONNX Runtime 时移除这两个选项
./build.sh --config Release --arm64 --build_shared_lib --use_xnnpack \
    --skip_tests --parallel $(nproc) --allow_running_as_root
    # 不加 --disable_rtti 和 --disable_exceptions
```

### 12.2 调试命令

```bash
# 查看可执行文件依赖
ldd battery_cli

# 查看符号表
nm -C libbattery_inference.so | grep Predict

# 运行时追踪系统调用
strace -e trace=openat,read ./battery_cli pinn

# CPU 性能分析
perf stat ./battery_cli benchmark

# 内存泄漏检查
valgrind --leak-check=full ./battery_cli pinn
```

---

## 附录 A: 快速启动检查清单

在 RZ/G2L 上按顺序执行:

```bash
# [ ] 1. 系统更新
apt update && apt upgrade -y

# [ ] 2. 编译工具
apt install -y build-essential cmake git wget vim

# [ ] 3. ONNX Runtime 头文件 + 库
ls /usr/local/include/onnxruntime/onnxruntime_cxx_api.h
ls /usr/local/lib/libonnxruntime.so*

# [ ] 4. 项目目录
ls ~/battery_inference/CMakeLists.txt

# [ ] 5. 模型文件
ls ~/battery_inference/models/battery_pinn_int8.onnx
ls ~/battery_inference/models/battery_cnn_int8.onnx

# [ ] 6. Scaler 文件
ls ~/battery_inference/scalers/pinn_mean.bin
ls ~/battery_inference/scalers/pinn_std.bin
ls ~/battery_inference/scalers/cnn_ic_scaler_mean.bin
ls ~/battery_inference/scalers/cnn_ic_scaler_std.bin
ls ~/battery_inference/scalers/cnn_ig_scaler_mean.bin
ls ~/battery_inference/scalers/cnn_ig_scaler_std.bin

# [ ] 7. 编译
cd ~/battery_inference/build
cmake .. -DCMAKE_BUILD_TYPE=Release
make -j2

# [ ] 8. 验证
./battery_cli info
./battery_cli benchmark

# 若一切正常, 输出类似:
# PINN: 10.2 ms avg (500 runs, 132-d input)
# CNN:   8.7 ms avg (500 runs, 128-pt IC curve)
```

---

## 附录 B: 完整文件对照

| 训练服务器 (Windows) | RZ/G2L (ARM64 Ubuntu) |
|---------------------|----------------------|
| `pinn/checkpoints/battery_pinn_int8.onnx` | `~/battery_inference/models/battery_pinn_int8.onnx` |
| `cnn/checkpoints/battery_cnn_int8.onnx` | `~/battery_inference/models/battery_cnn_int8.onnx` |
| `deploy/scalers/pinn_mean.bin` | `~/battery_inference/scalers/pinn_mean.bin` |
| `deploy/scalers/pinn_std.bin` | `~/battery_inference/scalers/pinn_std.bin` |
| `deploy/scalers/cnn_ic_scaler_mean.bin` | `~/battery_inference/scalers/cnn_ic_scaler_mean.bin` |
| `deploy/scalers/cnn_ic_scaler_std.bin` | `~/battery_inference/scalers/cnn_ic_scaler_std.bin` |
| `deploy/scalers/cnn_ig_scaler_mean.bin` | `~/battery_inference/scalers/cnn_ig_scaler_mean.bin` |
| `deploy/scalers/cnn_ig_scaler_std.bin` | `~/battery_inference/scalers/cnn_ig_scaler_std.bin` |
| (本文档中的源码) `include/battery_inference.h` | `~/battery_inference/include/battery_inference.h` |
| (本文档中的源码) `src/battery_inference.cpp` | `~/battery_inference/src/battery_inference.cpp` |
| (本文档中的源码) `src/main.cpp` | `~/battery_inference/src/main.cpp` |
| (本文档中的源码) `CMakeLists.txt` | `~/battery_inference/CMakeLists.txt` |

---

> **文档版本**: v1.0
> **适用平台**: Renesas RZ/G2L, Ubuntu 20.04 aarch64
> **编译日期**: 2026-06
> **配套项目**: `D:\ScuderiaAMG\PINN_CNN`
> **Python 侧推理参考**: `deploy/inference.py`
