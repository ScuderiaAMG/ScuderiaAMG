# RZ/G2L Qt 6 图形化交互界面部署教程

## ARM64 嵌入式 Linux → Mali-G31 GPU → Qt eglfs → QML 仪表盘 → 电池推理引擎

---

> **目标平台**: Renesas RZ/G2L (Cortex-A55 ×2 @ 1.2 GHz, Mali-G31 GPU)
> **操作系统**: Ubuntu 20.04.6 LTS (aarch64), 无桌面环境, 纯 DRM/KMS 显示
> **GUI 框架**: Qt 6.5 LTS + eglfs QPA (直接渲染到 DRM, 零 X11/Wayland 依赖)
> **推理后端**: ONNX Runtime 1.18+ (CPU EP, ARM NEON), 复用已有 `libbattery_inference.so`
> **前提条件**: 已完成 [RZG2L_CPP_DEPLOY.md](./RZG2L_CPP_DEPLOY.md) 中的 C++ 推理引擎部署

---

## 目录

1. [架构概述](#1-架构概述)
2. [删除米尔旧应用](#2-删除米尔旧应用)
3. [Mali-G31 GPU 驱动配置](#3-mali-g31-gpu-驱动配置)
4. [Qt 6 ARM64 交叉编译](#4-qt-6-arm64-交叉编译)
5. [GUI 应用完整源码](#5-gui-应用完整源码)
6. [CMake 构建配置](#6-cmake-构建配置)
7. [部署到 RZ/G2L](#7-部署到-rzg2l)
8. [上电自启 (systemd)](#8-上电自启-systemd)
9. [UI 自定义指南](#9-ui-自定义指南)
10. [故障排查](#10-故障排查)

---

## 1. 架构概述

### 1.1 整体架构

```
┌──────────────────────────────────────────────────────────────┐
│                     RZ/G2L Ubuntu 20.04                       │
│                                                               │
│  ┌─────────────────────────────────────────────────────────┐ │
│  │              battery_gui (Qt 6 eglfs 应用)               │ │
│  │                                                          │ │
│  │  ┌─────────────────┐   ┌────────────────────────────┐   │ │
│  │  │   QML UI 层      │   │    C++ 业务逻辑层          │   │ │
│  │  │                  │   │                            │   │ │
│  │  │  SohGauge.qml    │   │  BatteryDashboard (QObject)│   │ │
│  │  │  StageBadge.qml  │◄──│    ├─ PINNInference        │   │ │
│  │  │  IcCurveView.qml │   │    ├─ CNNInference         │   │ │
│  │  │  HistoryTable    │   │    └─ 数据管线 + Demo模式  │   │ │
│  │  │  SettingsPanel   │   │                            │   │ │
│  │  └─────────────────┘   └────────────┬───────────────┘   │ │
│  │                                      │                    │ │
│  │                          libbattery_inference.so         │ │
│  │                          ONNX Runtime (CPU EP, NEON)     │ │
│  └──────────────────────┬──────────────────────────────────┘ │
│                         │                                     │
│  ┌──────────────────────▼──────────────────────────────────┐ │
│  │              Qt eglfs QPA                                │ │
│  │   libQt6EglFsDeviceIntegration → EGL → Mali-G31 GPU     │ │
│  │   libdrm → DRM/KMS → MIPI DSI / LVDS → LCD Panel       │ │
│  └─────────────────────────────────────────────────────────┘ │
└──────────────────────────────────────────────────────────────┘
```

### 1.2 为什么选 Qt 6 + eglfs

| 考量 | 决策 | 理由 |
|------|------|------|
| 显示协议 | eglfs (DRM 直连) | 无 X11/Wayland 开销, 启动快, 内存省 |
| UI 描述 | QML | 声明式, 即时预览, 适合仪表盘 |
| 业务逻辑 | C++ | 与 `libbattery_inference.so` 零 FFI 开销 |
| GPU 后端 | OpenGL ES 2.0 | Mali-G31 原生支持, eglfs 的 `eglfs_mali` 集成 |
| Qt 版本 | 6.5 LTS | ARM Mali 修复最全, 长期支持 |

### 1.3 UI 布局预览

```
┌─────────────────────────────────────────────────────┐
│  🔋  Battery SOH Assessment System     [⚙] [⏻]    │
├────────────┬────────────────────┬───────────────────┤
│            │                    │                   │
│   SOH      │    Current Status  │  History          │
│   Gauge    │    ● Healthy       │  ┌───┬────┬────┐ │
│  (圆环表盘) │    RUL: 0.87      │  │ # │SOH │Stage│ │
│            │    IC Curve        │  │ 1 │.94 │ H   │ │
│   82.4%   │    ▁▃▅▆▇▆▅▃▁      │  │ 2 │.91 │ H   │ │
│            │    ▁▃▅▆▇▆▅▃▁      │  │ 3 │.88 │ D   │ │
│            │                    │  │...│... │ ... │ │
│            │                    │  └───┴────┴────┘ │
├────────────┴────────────────────┴───────────────────┤
│  [Run PINN]  [Run CNN]  [Demo Mode]  [Export CSV]   │
└─────────────────────────────────────────────────────┘
```

---

## 2. 删除米尔旧应用

### 2.1 找到旧应用

```bash
# SSH 登录 RZ/G2L
ssh root@<rzg2l-ip>

# 查找所有自启动服务
systemctl list-units --type=service --state=running | grep -i -E 'myir|qt|gui|display|launcher|lcd|hdmi|weston|wayland'

# 查找旧应用二进制位置
find / -type f -name "*myir*" -o -name "*demo*" -o -name "*launcher*" 2>/dev/null | grep -v proc

# 查看当前占用 DRM 的进程
lsof /dev/dri/card0 2>/dev/null
fuser -v /dev/dri/card0
```

### 2.2 停用并删除

```bash
# 1. 停用所有相关 systemd 服务
# (假设找到的服务名为 myir-demo.service / weston.service 等)
sudo systemctl stop myir-demo.service
sudo systemctl disable myir-demo.service
sudo systemctl mask myir-demo.service    # 防止被其他包重新启用

# 2. 查找并删除自启动脚本
ls -la /etc/init.d/
ls -la /etc/profile.d/
ls -la /opt/
ls -la /home/*/autostart/

# 常见的米尔自启动位置:
sudo rm -f /etc/init.d/matrix-gui*        # TI/米尔 Matrix GUI
sudo rm -f /etc/profile.d/qt-env.sh       # Qt 环境变量
sudo rm -f /usr/share/applications/*demo*
sudo rm -rf /opt/myir/
sudo rm -rf /home/root/launcher/
sudo rm -rf /usr/bin/mxapp*              # 米尔示例应用

# 3. 检查并清理 .bashrc / .profile 中的自动启动命令
grep -n -i -E 'app|demo|gui|launcher|myir' /root/.bashrc /root/.profile /etc/profile 2>/dev/null
# 用 sed 或手动 vi 删除相关行

# 4. 杀掉正在运行的图形进程
sudo pkill -9 -f myir
sudo pkill -9 -f weston
sudo pkill -9 -f demo
sudo pkill -9 -f launcher

# 5. 确认 /dev/dri/card0 已释放
fuser -v /dev/dri/card0
# 应该无输出
```

### 2.3 释放 DRM 主节点

```bash
# eglfs 需要独占 DRM 主节点 (card0)
# 清理可能占用 DRM 的内核模块
lsmod | grep -E 'mali|gpu|drm'
# 确认只有 mali 或 panfrost 在, 没有其他显示驱动冲突

# 如果之前有 weston/compositor 的 systemd 服务, 也要停掉:
sudo systemctl stop weston.service 2>/dev/null
sudo systemctl disable weston.service 2>/dev/null
```

---

## 3. Mali-G31 GPU 驱动配置

### 3.1 验证 GPU 硬件

```bash
# RZ/G2L 的 Mali-G31 应出现在设备树
ls -la /sys/class/drm/
# 预期: card0/  card0-LVDS-1/  renderD128/  version

cat /sys/class/drm/card0/device/gpuinfo 2>/dev/null || \
  dmesg | grep -i -E 'mali|panfrost|gpu|g31'
# 预期输出含 "Mali-G31"

# 查看 DRM 设备
ls -la /dev/dri/
# 预期: card0  renderD128
```

### 3.2 安装 Mali 用户态驱动

RZ/G2L 使用 ARM 官方 Mali 用户态 blob (`libmali`) 或开源 `panfrost`:

```bash
# === 方案 A: 使用 Renesas BSP 自带的 Mali blob (推荐) ===
# 米尔 BSP 通常已安装, 验证:
find /usr/lib -name "libmali*" -o -name "libEGL*" -o -name "libGLES*" 2>/dev/null

# 若缺失, 从米尔 SDK 安装:
# (将 SDK 中的 .deb 包传到 RZ/G2L)
sudo dpkg -i libmali-rzg2l*.deb

# === 方案 B: Panfrost 开源驱动 (需较新内核) ===
# 检查内核版本 (panfrost 需要 ≥ 5.2, 最好 ≥ 5.10)
uname -r

# 安装 panfrost 用户态
sudo apt-get update
sudo apt-get install -y mesa-utils-egl libegl1-mesa libgles2-mesa libgbm1

# 加载 panfrost 内核模块
sudo modprobe panfrost
dmesg | grep panfrost
```

### 3.3 验证 EGL/GLES 可用性

```bash
# 测试 EGL 初始化
sudo apt-get install -y mesa-utils 2>/dev/null || true

# 使用 es2_info / es2gears 验证 GPU 渲染
es2_info 2>&1 | head -20
# 预期: GL_VENDOR: ARM 或 Mesa/Panfrost
#       GL_RENDERER: Mali-G31 或 Panfrost

# 若没有 es2 工具, 用 Python 脚本快速验证:
python3 -c "
import ctypes, os
os.environ['DISPLAY'] = ''
lib = ctypes.CDLL('libEGL.so.1')
dpy = lib.eglGetDisplay(0)
print(f'EGL Display: {hex(dpy)}')
print('EGL OK' if dpy else 'EGL FAILED')
"
```

### 3.4 DRM 权限配置

```bash
# 创建 udev 规则: 允许 render group 访问 DRM
sudo tee /etc/udev/rules.d/99-drm.rules << 'UDEV'
KERNEL=="card[0-9]*", GROUP="video", MODE="0660"
KERNEL=="renderD*", GROUP="video", MODE="0666"
UDEV

# 确保运行用户属于 video 组
sudo usermod -a -G video root
sudo usermod -a -G video $USER 2>/dev/null || true

# 重新加载 udev
sudo udevadm control --reload-rules
sudo udevadm trigger
```

---

## 4. Qt 6 ARM64 交叉编译

> **编译机**: x86_64 Ubuntu 20.04/22.04 (至少 8 核, 30 GB 空闲磁盘)
> **目标机**: RZ/G2L ARM64, Ubuntu 20.04

### 4.1 准备交叉编译工具链

```bash
# === 在 x86_64 编译机上执行 ===

# 安装 ARM64 交叉编译器
sudo apt-get update
sudo apt-get install -y \
    gcc-aarch64-linux-gnu \
    g++-aarch64-linux-gnu \
    binutils-aarch64-linux-gnu \
    pkg-config-aarch64-linux-gnu

# 验证
aarch64-linux-gnu-g++ --version
# 预期: aarch64-linux-gnu-g++ (Ubuntu 9.4.0-...) 9.4.0
```

### 4.2 获取 RZ/G2L sysroot

```bash
# 从 RZ/G2L 板上拉取 sysroot (包含 Mali 库、libdrm 等)

# === 在 RZ/G2L 上 ===
# 安装 rsync (若没有)
sudo apt-get install -y rsync

# === 在 x86_64 编译机上 ===
SYSROOT_DIR="$HOME/rzg2l-sysroot"
mkdir -p "$SYSROOT_DIR"

# 拉取完整 sysroot (约 300-500 MB)
# 注意: --exclude 跳过不需要的目录以节省空间
rsync -avz --delete \
    --exclude=/proc --exclude=/sys --exclude=/dev \
    --exclude=/tmp --exclude=/run --exclude=/mnt \
    --exclude=/var/cache --exclude=/var/log \
    --exclude=/usr/share/doc --exclude=/usr/share/man \
    --exclude=/usr/src --exclude=/lib/modules \
    root@<rzg2l-ip>:/ "$SYSROOT_DIR/"

# 修正 sysroot 中的符号链接
# Qt configure 需要 sysroot 中的库路径为绝对路径
find "$SYSROOT_DIR/usr/lib" -name "*.so*" -type l -exec sh -c '
    target=$(readlink "$1")
    case "$target" in
        /*) ln -snf "'"$SYSROOT_DIR"'"$target" "$1" ;;
    esac
' _ {} \;
```

### 4.3 编译 Qt 6.5 LTS

```bash
# === 在 x86_64 编译机上 ===

# 下载 Qt 6.5 LTS 源码
cd /tmp
wget https://download.qt.io/official_releases/qt/6.5/6.5.3/single/qt-everywhere-src-6.5.3.tar.xz
tar xf qt-everywhere-src-6.5.3.tar.xz
cd qt-everywhere-src-6.5.3

# 创建 ARM64 交叉编译配置
# Qt 已内置 aarch64 交叉编译 mkspec:
# linux-aarch64-gnu-g++  (针对 ARMv8-A 基线)
# 我们需要为 Cortex-A55 调优, 复制一份:
cp -r qtbase/mkspecs/linux-aarch64-gnu-g++ qtbase/mkspecs/linux-aarch64-cortexa55-g++
```

**修改 qmake.conf 启用 NEON 优化:**

```bash
cat > qtbase/mkspecs/linux-aarch64-cortexa55-g++/qmake.conf << 'QMAKE'
#
# qmake configuration for RZ/G2L Cortex-A55 + ARM NEON
#

include(../common/linux_device_post.conf)

MAKEFILE_GENERATOR      = UNIX
CONFIG                 += incremental
QMAKE_INCREMENTAL_STYLE = sublib

# Compiler
QMAKE_CC                = aarch64-linux-gnu-gcc
QMAKE_CXX               = aarch64-linux-gnu-g++
QMAKE_LINK              = aarch64-linux-gnu-g++
QMAKE_LINK_SHLIB        = aarch64-linux-gnu-g++

QMAKE_CFLAGS_RELEASE   += -march=armv8.2-a+fp16+dotprod -mtune=cortex-a55
QMAKE_CXXFLAGS_RELEASE += -march=armv8.2-a+fp16+dotprod -mtune=cortex-a55

# Device options
DISTRO_OPTS            += hard-float

# EGL / OpenGL ES
QMAKE_INCDIR_EGL        =
QMAKE_LIBDIR_EGL        =
QMAKE_LIBS_EGL          = -lEGL

QMAKE_INCDIR_OPENGL_ES2 =
QMAKE_LIBDIR_OPENGL_ES2 =
QMAKE_LIBS_OPENGL_ES2   = -lGLESv2

# DRM (for eglfs)
QMAKE_LIBS_DRM          = -ldrm

load(qt_config)
QMAKE
```

**配置并编译:**

```bash
SYSROOT="$HOME/rzg2l-sysroot"
INSTALL_PREFIX="/opt/qt6-rzg2l"

./configure \
    -prefix "$INSTALL_PREFIX" \
    -extprefix "$INSTALL_PREFIX" \
    -sysroot "$SYSROOT" \
    -release \
    -opensource \
    -confirm-license \
    -xplatform linux-aarch64-cortexa55-g++ \
    -nomake tests \
    -nomake examples \
    -no-feature-accessibility \
    -no-dbus \
    -no-ssl \
    -no-cups \
    -no-gui \
    -widgets \
    -qt-libpng \
    -qt-libjpeg \
    -qt-harfbuzz \
    -qt-pcre \
    -fontconfig \
    -opengl es2 \
    -eglfs \
    -kms \
    -libinput \
    -tslib \
    -skip qt3d \
    -skip qt5compat \
    -skip qtactiveqt \
    -skip qtcharts \
    -skip qtcoap \
    -skip qtconnectivity \
    -skip qtdatavis3d \
    -skip qtgraphs \
    -skip qtgrpc \
    -skip qthttpserver \
    -skip qtlanguageserver \
    -skip qtlocation \
    -skip qtlottie \
    -skip qtmultimedia \
    -skip qtnetworkauth \
    -skip qtopcua \
    -skip qtscxml \
    -skip qtsensors \
    -skip qtserialbus \
    -skip qtspeech \
    -skip qtvirtualkeyboard \
    -skip qtwayland \
    -skip qtwebchannel \
    -skip qtwebengine \
    -skip qtwebsockets \
    -skip qtwebview \
    2>&1 | tee configure.log

# 编译 (建议 -j 不超过 CPU 核心数)
make -j$(nproc)
make install

# 验证产物
ls "$INSTALL_PREFIX/bin/qmake"
ls "$INSTALL_PREFIX/lib/libQt6Core.so"
ls "$INSTALL_PREFIX/plugins/platforms/"   # 应包含 libqeglfs.so

echo "Qt 6.5 installed to: $INSTALL_PREFIX"
```

### 4.4 部署 Qt 到 RZ/G2L

```bash
# 打包 Qt 库 (只带需要的模块)
cd "$INSTALL_PREFIX"

# 精简: 删除头文件、静态库、cmake 配置 (目标机不需要)
rm -rf include/ doc/ mkspecs/
find lib/ -name "*.a" -delete
find lib/ -name "*.la" -delete
find lib/ -name "*.prl" -delete

# 只保留需要的 .so
REQUIRED_LIBS="
    libQt6Core.so* libQt6Gui.so* libQt6Quick.so*
    libQt6Qml.so* libQt6QuickControls2.so* libQt6QuickTemplates2.so*
    libQt6OpenGL.so* libQt6EglFsDeviceIntegration.so*
    libQt6Network.so* libQt6Bundled*.so*
    libQt6DBus.so* libQt6XcbQpa.so* libQt6FontDatabase*
"
# 注意: 保留上述需要的 .so, 删除不需要的:
# (根据需要调整, 尽量精简以节省 eMMC 空间)

# 打包
tar czf /tmp/qt6-rzg2l-deploy.tar.gz -C "$INSTALL_PREFIX" .

# 传到 RZ/G2L
scp /tmp/qt6-rzg2l-deploy.tar.gz root@<rzg2l-ip>:/opt/

# === 在 RZ/G2L 上 ===
cd /opt
sudo tar xzf qt6-rzg2l-deploy.tar.gz
sudo ldconfig /opt/lib

# 验证 Qt 库可用
/opt/bin/qmake --version
# 输出: QMake version 3.1 ... Using Qt version 6.5.3
```

---

## 5. GUI 应用完整源码

### 5.1 目录结构

```
battery_inference/
├── include/
│   └── battery_inference.h          ← 已有 (推理引擎公共头文件)
├── src/
│   ├── battery_inference.cpp        ← 已有 (推理引擎实现)
│   └── main.cpp                     ← 已有 (CLI 入口)
├── gui/                             ← ★ 新增
│   ├── CMakeLists.txt
│   ├── src/
│   │   ├── main.cpp                 ← eglfs 入口
│   │   ├── batterydashboard.h       ← QObject 后端
│   │   └── batterydashboard.cpp     ← 后端实现
│   └── qml/
│       ├── MainView.qml             ← 主视图
│       ├── SohGauge.qml             ← SOH 圆环表盘
│       ├── StageBadge.qml           ← 阶段状态标签
│       ├── IcCurveView.qml          ← IC 曲线图 (Canvas)
│       └── HistoryTable.qml         ← 历史记录表
├── CMakeLists.txt                   ← 已有 (需加 gui 子目录)
├── scalers/                         ← 已有
└── models/                          ← 已有
```

### 5.2 `gui/src/batterydashboard.h` — C++ QObject 后端

```cpp
#ifndef BATTERY_DASHBOARD_H
#define BATTERY_DASHBOARD_H

#include <QObject>
#include <QVector>
#include <QDateTime>
#include <QTimer>
#include <memory>
#include <deque>
#include <mutex>

// 引入推理引擎 (使用已有 PIMPL 头文件)
#include "battery_inference.h"

/**
 * @brief QObject wrapper around the C++ inference engine.
 *
 * Exposes inference results as Qt properties for QML binding.
 * All inference runs happen on background threads via QtConcurrent.
 *
 * Usage from QML:
 *   BatteryDashboard {
 *       id: dashboard
 *       onSohChanged: sohGauge.value = dashboard.soh
 *   }
 */
class BatteryDashboard : public QObject
{
    Q_OBJECT

    // ── QML 可绑定属性 ──
    Q_PROPERTY(float    soh          READ soh          NOTIFY sohChanged)
    Q_PROPERTY(int      stage        READ stage        NOTIFY stageChanged)
    Q_PROPERTY(QString  stageName    READ stageName    NOTIFY stageChanged)
    Q_PROPERTY(float    rul          READ rul          NOTIFY rulChanged)
    Q_PROPERTY(bool     running      READ running      NOTIFY runningChanged)
    Q_PROPERTY(QString  lastError    READ lastError    NOTIFY lastErrorChanged)

public:
    struct HistoryEntry {
        QDateTime timestamp;
        float soh;
        int stage;
        float rul;
        QVector<double> icCurve;
    };

    explicit BatteryDashboard(QObject *parent = nullptr);
    ~BatteryDashboard() override;

    // ── 属性 getters ──
    float    soh()       const { return soh_; }
    int      stage()     const { return stage_; }
    QString  stageName() const { return stageName_; }
    float    rul()       const { return rul_; }
    bool     running()   const { return running_; }
    QString  lastError() const { return lastError_; }

    // ── QML 可调用方法 ──
    Q_INVOKABLE void runPINN(const QVector<double> &features132);
    Q_INVOKABLE void runCNN(const QVector<double> &icCurve128);
    Q_INVOKABLE void runDemo();
    Q_INVOKABLE void clearHistory();

    // ── 历史数据 ──
    Q_INVOKABLE QVector<QVector<QVariant>> getHistory() const;

signals:
    void sohChanged();
    void stageChanged();
    void rulChanged();
    void runningChanged();
    void lastErrorChanged();
    void inferenceComplete();
    void errorOccurred(const QString &message);

private:
    void setRunning(bool v);
    void setError(const QString &msg);

    // 推理引擎实例 (PIMPL, 线程安全)
    std::unique_ptr<battery::PINNInference> pinn_;
    std::unique_ptr<battery::CNNInference>  cnn_;
    bool modelsLoaded_ = false;

    // 当前推理结果
    float soh_   = 0.0f;
    int stage_   = 0;
    QString stageName_ = "Unknown";
    float rul_   = 0.0f;
    bool running_ = false;
    QString lastError_;

    // 历史记录 (最近 100 条)
    mutable std::mutex historyMutex_;
    std::deque<HistoryEntry> history_;
    static constexpr size_t kMaxHistory = 100;

    // Demo 模式数据
    int demoCounter_ = 0;
};

#endif // BATTERY_DASHBOARD_H
```

### 5.3 `gui/src/batterydashboard.cpp` — 后端实现

```cpp
#include "batterydashboard.h"
#include <QtConcurrent/QtConcurrent>
#include <QFutureWatcher>
#include <algorithm>
#include <cmath>

// ────────────────────────────────────────────────────────────
// 辅助: 生成 demo 数据
// ────────────────────────────────────────────────────────────
static QVector<double> makeDemoFeatures132(int seed) {
    // 模拟一个逐渐衰老的电池 (以 seed 模拟循环数)
    QVector<double> f(132, 0.0);
    double sohTrend = 1.0 - seed * 0.002;  // 每循环衰减 0.2%
    sohTrend = std::max(0.5, sohTrend);

    // IC 曲线部分 (索引 0-127): 生成一个典型峰
    for (int i = 0; i < 128; ++i) {
        double x = (i - 64.0) / 20.0;
        f[i] = 2.5 * sohTrend * std::exp(-x * x * 0.5) + (seed % 17) * 0.02;
    }
    // 温度 (索引 128)
    f[128] = 25.0f + (seed % 10) * 0.3f;
    // log_cycle (索引 129)
    f[129] = std::log10(std::max(1.0, static_cast<double>(seed + 1)));
    // dV (索引 130)
    f[130] = -0.05f - seed * 0.001f;
    // capacity (索引 131)
    f[131] = 1.0f + seed * 0.0005f;
    return f;
}

static QVector<double> makeDemoIC128(int seed) {
    QVector<double> ic(128, 0.0);
    double sohTrend = 1.0 - seed * 0.002;
    sohTrend = std::max(0.5, sohTrend);
    double peakShift = seed * 0.05;  // 峰值随老化漂移
    for (int i = 0; i < 128; ++i) {
        double x = (i - 64.0 - peakShift) / 18.0;
        ic[i] = 2.2 * sohTrend * std::exp(-x * x * 0.5)
              + 0.08 * std::sin(x * 3.0) + (seed % 13) * 0.015;
    }
    return ic;
}

// ────────────────────────────────────────────────────────────
// BatteryDashboard 实现
// ────────────────────────────────────────────────────────────

BatteryDashboard::BatteryDashboard(QObject *parent)
    : QObject(parent)
{
    // 初始化推理引擎
    try {
        // PINN 配置
        battery::PINNConfig pinnCfg;
        pinnCfg.model_path = "../models/battery_pinn_int8.onnx";
        pinnCfg.scaler_mean_path = "../scalers/pinn_mean.bin";
        pinnCfg.scaler_std_path  = "../scalers/pinn_std.bin";
        pinnCfg.intra_op_threads = 2;
        pinn_ = std::make_unique<battery::PINNInference>(pinnCfg);

        // CNN 配置
        battery::CNNConfig cnnCfg;
        cnnCfg.model_path = "../models/battery_cnn_int8.onnx";
        cnnCfg.ic_scaler_mean_path = "../scalers/cnn_ic_scaler_mean.bin";
        cnnCfg.ic_scaler_std_path  = "../scalers/cnn_ic_scaler_std.bin";
        cnnCfg.ig_scaler_mean_path = "../scalers/cnn_ig_scaler_mean.bin";
        cnnCfg.ig_scaler_std_path  = "../scalers/cnn_ig_scaler_std.bin";
        cnnCfg.intra_op_threads = 2;
        cnn_ = std::make_unique<battery::CNNInference>(cnnCfg);

        modelsLoaded_ = true;
    } catch (const std::exception &e) {
        setError(QString("Failed to load models: %1").arg(e.what()));
    }
}

BatteryDashboard::~BatteryDashboard() = default;

// ── QML-callable slots ──

void BatteryDashboard::runPINN(const QVector<double> &features132)
{
    if (!modelsLoaded_ || running_) return;
    setRunning(true);
    setError("");

    // 在后台线程执行推理, 避免阻塞 UI
    auto *watcher = new QFutureWatcher<float>(this);
    connect(watcher, &QFutureWatcher<float>::finished, this,
        [this, watcher]() {
            if (watcher->future().isCanceled()) {
                setRunning(false);
                return;
            }
            try {
                float result = watcher->result();
                soh_ = std::clamp(result, 0.0f, 1.0f);
                emit sohChanged();

                // 添加到历史
                {
                    std::lock_guard<std::mutex> lk(historyMutex_);
                    history_.push_front({QDateTime::currentDateTime(), soh_, -1, -1.0f, {}});
                    if (history_.size() > kMaxHistory) history_.pop_back();
                }
            } catch (const std::exception &e) {
                setError(QString("PINN inference failed: %1").arg(e.what()));
            }
            setRunning(false);
            emit inferenceComplete();
        });

    QFuture<float> future = QtConcurrent::run(
        [this, f = features132.toStdVector()]() -> float {
            return pinn_->PredictSOH(f);
        });
    watcher->setFuture(future);
}

void BatteryDashboard::runCNN(const QVector<double> &icCurve128)
{
    if (!modelsLoaded_ || running_) return;
    setRunning(true);
    setError("");

    auto *watcher = new QFutureWatcher<battery::CNNResult>(this);
    connect(watcher, &QFutureWatcher<battery::CNNResult>::finished, this,
        [this, watcher]() {
            if (watcher->future().isCanceled()) {
                setRunning(false);
                return;
            }
            try {
                battery::CNNResult r = watcher->result();
                stage_ = static_cast<int>(r.stage);
                switch (r.stage) {
                    case battery::BatteryStage::Healthy:   stageName_ = "Healthy";   break;
                    case battery::BatteryStage::Degrading: stageName_ = "Degrading"; break;
                    case battery::BatteryStage::EOL:       stageName_ = "EOL";       break;
                    default:                               stageName_ = "Unknown";   break;
                }
                rul_ = std::clamp(r.rul, 0.0f, 1.0f);
                emit stageChanged();
                emit rulChanged();

                {
                    std::lock_guard<std::mutex> lk(historyMutex_);
                    history_.push_front({
                        QDateTime::currentDateTime(), -1.0f, stage_, rul_,
                        QVector<double>{}
                    });
                    if (history_.size() > kMaxHistory) history_.pop_back();
                }
            } catch (const std::exception &e) {
                setError(QString("CNN inference failed: %1").arg(e.what()));
            }
            setRunning(false);
            emit inferenceComplete();
        });

    QFuture<battery::CNNResult> future = QtConcurrent::run(
        [this, c = icCurve128.toStdVector()]() -> battery::CNNResult {
            return cnn_->Predict(c);
        });
    watcher->setFuture(future);
}

void BatteryDashboard::runDemo()
{
    if (running_) return;

    // 同时运行 PINN 和 CNN (demo 模式)
    // 先运行 CNN (带 IC 曲线显示), 再运行 PINN
    QVector<double> ic = makeDemoIC128(demoCounter_);
    QVector<double> feat = makeDemoFeatures132(demoCounter_);

    // 更新 demo 计数
    demoCounter_ = (demoCounter_ + 1) % 500;

    // 运行 CNN (获得 stage + RUL)
    // 然后运行 PINN (获得 SOH)
    setRunning(true);
    setError("");

    auto *watcher = new QFutureWatcher<std::pair<float, battery::CNNResult>>(this);
    connect(watcher, &QFutureWatcher<std::pair<float, battery::CNNResult>>::finished,
        this, [this, watcher, ic]() {
            if (watcher->future().isCanceled()) {
                setRunning(false);
                return;
            }
            try {
                auto [soh, cnnResult] = watcher->result();
                soh_ = std::clamp(soh, 0.0f, 1.0f);
                stage_ = static_cast<int>(cnnResult.stage);
                switch (cnnResult.stage) {
                    case battery::BatteryStage::Healthy:   stageName_ = "Healthy";   break;
                    case battery::BatteryStage::Degrading: stageName_ = "Degrading"; break;
                    case battery::BatteryStage::EOL:       stageName_ = "EOL";       break;
                    default:                               stageName_ = "Unknown";   break;
                }
                rul_ = std::clamp(cnnResult.rul, 0.0f, 1.0f);
                emit sohChanged();
                emit stageChanged();
                emit rulChanged();

                {
                    std::lock_guard<std::mutex> lk(historyMutex_);
                    history_.push_front({
                        QDateTime::currentDateTime(), soh_, stage_, rul_, ic
                    });
                    if (history_.size() > kMaxHistory) history_.pop_back();
                }
            } catch (const std::exception &e) {
                setError(QString("Demo failed: %1").arg(e.what()));
            }
            setRunning(false);
            emit inferenceComplete();
        });

    QFuture<std::pair<float, battery::CNNResult>> future = QtConcurrent::run(
        [this, f = feat.toStdVector(), c = ic.toStdVector()]()
            -> std::pair<float, battery::CNNResult> {
            float soh = pinn_->PredictSOH(f);
            battery::CNNResult r = cnn_->Predict(c);
            return {soh, r};
        });
    watcher->setFuture(future);
}

void BatteryDashboard::clearHistory()
{
    std::lock_guard<std::mutex> lk(historyMutex_);
    history_.clear();
}

QVector<QVector<QVariant>> BatteryDashboard::getHistory() const
{
    QVector<QVector<QVariant>> result;
    std::lock_guard<std::mutex> lk(historyMutex_);
    result.reserve(history_.size());
    for (const auto &e : history_) {
        QVector<QVariant> row;
        row.append(e.timestamp.toString("HH:mm:ss"));
        row.append(e.soh >= 0 ? QString::number(e.soh, 'f', 4) : "-");
        row.append(e.stage >= 0 ? e.stageName : "-");
        row.append(e.rul >= 0 ? QString::number(e.rul, 'f', 4) : "-");
        result.append(row);
    }
    return result;
}

// ── 私有辅助 ──

void BatteryDashboard::setRunning(bool v)
{
    if (running_ != v) {
        running_ = v;
        emit runningChanged();
    }
}

void BatteryDashboard::setError(const QString &msg)
{
    lastError_ = msg;
    emit lastErrorChanged();
    if (!msg.isEmpty())
        emit errorOccurred(msg);
}
```

### 5.4 `gui/src/main.cpp` — eglfs 入口

```cpp
/**
 * RZ/G2L Battery SOH Assessment — Qt 6 eglfs GUI
 *
 * 启动方式:
 *   QT_QPA_PLATFORM=eglfs ./battery_gui
 *
 * 环境变量:
 *   QT_QPA_EGLFS_KMS_CONFIG=kms.conf     (多屏 / 强制分辨率)
 *   QT_QPA_EGLFS_INTEGRATION=eglfs_mali  (Mali GPU 后端)
 *   QT_QPA_EGLFS_ALWAYS_SET_MODE=1       (强制 KMS 模式)
 *   QT_QPA_EVDEV_TOUCHSCREEN_PARAMETERS  (触摸屏配置, 若有)
 */
#include <QGuiApplication>
#include <QQmlApplicationEngine>
#include <QQmlContext>
#include <QIcon>
#include <QDir>
#include <QStandardPaths>

#include "batterydashboard.h"

int main(int argc, char *argv[])
{
    // ── eglfs 专用环境变量 ──
    // (也可在启动脚本中设置, 这里作为 fallback)
    if (qEnvironmentVariableIsEmpty("QT_QPA_PLATFORM"))
        qputenv("QT_QPA_PLATFORM", "eglfs");

    // 禁用光标 (触摸屏场景)
    if (qEnvironmentVariableIsEmpty("QT_QPA_EGLFS_HIDECURSOR"))
        qputenv("QT_QPA_EGLFS_HIDECURSOR", "1");

    // Mali GPU 集成 (若使用 Mali blob 驱动)
    // 使用 panfrost 时清空此变量
    if (qEnvironmentVariableIsEmpty("QT_QPA_EGLFS_INTEGRATION"))
        qputenv("QT_QPA_EGLFS_INTEGRATION", "eglfs_mali");

    // 强制设置 KMS 模式 (防止分辨率检测失败)
    if (qEnvironmentVariableIsEmpty("QT_QPA_EGLFS_ALWAYS_SET_MODE"))
        qputenv("QT_QPA_EGLFS_ALWAYS_SET_MODE", "1");

    // OpenGL ES 2.0 (Mali-G31 支持 ES 2.0/3.0, 选 2.0 最稳)
    if (qEnvironmentVariableIsEmpty("QT_QUICK_BACKEND"))
        qputenv("QT_QUICK_BACKEND", "software"); // 纯 QML 控件可用 software
    // Qt Quick 场景图后端 (选 es2 以利用 Mali GPU)
    QQuickWindow::setGraphicsApi(QSGRendererInterface::OpenGL);

    QGuiApplication app(argc, argv);
    app.setApplicationName("Battery SOH");
    app.setApplicationVersion("1.0.0");
    app.setOrganizationName("BatteryTeam");

    // ── 注册 C++ 类型到 QML ──
    qmlRegisterType<BatteryDashboard>("Battery.App", 1, 0, "BatteryDashboard");

    // ── 加载 QML ──
    QQmlApplicationEngine engine;

    // 设置 QML 搜索路径
    engine.addImportPath(QCoreApplication::applicationDirPath() + "/../qml");

    const QUrl url(QStringLiteral("qrc:/qml/MainView.qml"));

    QObject::connect(&engine, &QQmlApplicationEngine::objectCreationFailed,
        &app, []() { QCoreApplication::exit(-1); },
        Qt::QueuedConnection);

    engine.load(url);

    if (engine.rootObjects().isEmpty())
        return -1;

    return app.exec();
}
```

### 5.5 `gui/qml/MainView.qml` — 主视图

```qml
import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import Battery.App 1.0

ApplicationWindow {
    id: root
    visible: true
    visibility: ApplicationWindow.FullScreen

    // ── 深色工业主题 ──
    color: "#1a1a2e"

    BatteryDashboard {
        id: dashboard
        onErrorOccurred: (msg) => statusLabel.text = msg
        onInferenceComplete: statusLabel.text = "Ready"
    }

    // ── 顶部状态栏 ──
    Rectangle {
        id: topBar
        anchors { top: parent.top; left: parent.left; right: parent.right }
        height: 64
        color: "#16213e"

        RowLayout {
            anchors { fill: parent; margins: 12 }
            Text {
                text: "🔋 Battery SOH Assessment"
                color: "#e0e0e0"
                font.pixelSize: 26
                font.bold: true
                Layout.fillWidth: true
            }

            // 状态指示灯
            Rectangle {
                id: statusDot
                width: 12; height: 12; radius: 6
                color: dashboard.running ? "#ffb300" : "#4caf50"
                Behavior on color { ColorAnimation { duration: 300 } }
            }
            Text {
                id: statusLabel
                text: "Ready"
                color: "#a0a0a0"
                font.pixelSize: 16
            }
            Item { width: 20 }

            // 设置按钮
            Button {
                text: "⚙"
                font.pixelSize: 22
                flat: true
                onClicked: settingsDrawer.open()
            }
        }
    }

    // ── 主内容区 ──
    RowLayout {
        anchors {
            top: topBar.bottom; bottom: footerBar.top
            left: parent.left; right: parent.right
            margins: 20
        }
        spacing: 20

        // ── 左侧: SOH 表盘 ──
        SohGauge {
            id: sohGauge
            soh: dashboard.soh
            Layout.preferredWidth: 300
            Layout.preferredHeight: 350
        }

        // ── 中间: 阶段状态 + IC 曲线 ──
        ColumnLayout {
            Layout.fillWidth: true
            Layout.fillHeight: true
            spacing: 16

            // 阶段状态卡片
            StageBadge {
                id: stageBadge
                stage: dashboard.stage
                stageName: dashboard.stageName
                rul: dashboard.rul
                Layout.fillWidth: true
                Layout.preferredHeight: 100
            }

            // IC 曲线视图
            IcCurveView {
                id: icCurveView
                Layout.fillWidth: true
                Layout.fillHeight: true
            }
        }

        // ── 右侧: 历史记录 ──
        HistoryTable {
            id: historyTable
            Layout.preferredWidth: 300
            Layout.fillHeight: true
        }
    }

    // ── 底部操作栏 ──
    Rectangle {
        id: footerBar
        anchors { bottom: parent.bottom; left: parent.left; right: parent.right }
        height: 72
        color: "#16213e"

        RowLayout {
            anchors { fill: parent; margins: 12 }
            spacing: 16

            Button {
                text: dashboard.running ? "⏳ Running..." : "▶ Run PINN"
                enabled: !dashboard.running
                font.pixelSize: 18
                onClicked: dashboard.runDemo()
                Layout.fillWidth: true
            }
            Button {
                text: "🗑 Clear History"
                font.pixelSize: 18
                onClicked: {
                    dashboard.clearHistory()
                    historyTable.refresh()
                }
                Layout.fillWidth: true
            }
            Button {
                text: "⏻ Exit"
                font.pixelSize: 18
                onClicked: Qt.quit()
                Layout.fillWidth: true
            }
        }
    }

    // ── 历史数据刷新定时器 ──
    Timer {
        interval: 500
        running: true
        repeat: true
        onTriggered: historyTable.refresh()
    }
}
```

### 5.6 `gui/qml/SohGauge.qml` — SOH 圆环表盘

```qml
import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

/**
 * 圆形 SOH 表盘 (Canvas 绘制)
 *
 * 颜色渐变: 绿 (≥82%) → 黄 (70-82%) → 红 (<70%)
 */
Item {
    id: gauge
    property double soh: 0.0

    implicitWidth: 280
    implicitHeight: 300

    // 计算颜色
    function gaugeColor(value) {
        if (value >= 0.82) return "#4caf50"       // 绿色: 健康
        if (value >= 0.70) return "#ff9800"       // 橙色: 衰退
        return "#f44336"                           // 红色: EOL
    }

    Canvas {
        id: bgCanvas
        anchors.centerIn: parent
        width: 240; height: 240
        onPaint: {
            var ctx = getContext("2d")
            ctx.clearRect(0, 0, width, height)
            var cx = width / 2, cy = height / 2, r = cx - 12

            // 背景轨道
            ctx.beginPath()
            ctx.arc(cx, cy, r, Math.PI * 0.75, Math.PI * 2.25, false)
            ctx.lineWidth = 18
            ctx.strokeStyle = "#2a2a4a"
            ctx.lineCap = "round"
            ctx.stroke()

            // 填充弧
            var sweep = gauge.soh * Math.PI * 1.5  // 270° 弧度范围
            ctx.beginPath()
            ctx.arc(cx, cy, r, Math.PI * 0.75, Math.PI * 0.75 + sweep, false)
            ctx.lineWidth = 18
            ctx.strokeStyle = gaugeColor(gauge.soh)
            ctx.lineCap = "round"
            ctx.stroke()
        }
    }

    // 百分比数字
    Text {
        anchors.centerIn: bgCanvas
        text: (gauge.soh * 100).toFixed(1) + "%"
        color: gaugeColor(gauge.soh)
        font.pixelSize: 48
        font.bold: true
        horizontalAlignment: Text.AlignHCenter
    }
    Text {
        anchors { top: bgCanvas.verticalCenter; topMargin: 52
                  horizontalCenter: bgCanvas.horizontalCenter }
        text: "SOH"
        color: "#8888aa"
        font.pixelSize: 18
        font.bold: true
    }

    // 刻度标签
    // 0.82 和 0.70 阈值标记
    Repeater {
        model: [
            { value: 0.0,  label: "0",   angle: 135 },
            { value: 0.25, label: "25",  angle: 202.5 },
            { value: 0.50, label: "50",  angle: 270 },
            { value: 0.70, label: "70",  angle: 337.5, color: "#ff9800" },
            { value: 0.82, label: "82",  angle: 365.5, color: "#4caf50" },
            { value: 1.0,  label: "100", angle: 405 },
        ]
        delegate: Text {
            x: gauge.width / 2 + Math.cos(modelData.angle * Math.PI / 180) * bgCanvas.width / 2 * 0.78
               - width / 2 + 4
            y: gauge.height / 2 + Math.sin(modelData.angle * Math.PI / 180) * bgCanvas.height / 2 * 0.78
               - height / 2 + 4
            text: modelData.label
            color: modelData.color || "#666688"
            font.pixelSize: modelData.color ? 14 : 11
            font.bold: modelData.color !== undefined
        }
    }

    // 重新绘制当 soh 变化
    Connections {
        target: gauge
        function onSohChanged() { bgCanvas.requestPaint() }
    }
}
```

### 5.7 `gui/qml/StageBadge.qml` — 阶段状态卡片

```qml
import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

Item {
    id: badge
    property int stage: -1
    property string stageName: ""
    property double rul: 0.0

    function stageColor(s) {
        switch (s) {
            case 0: return "#4caf50"   // Healthy
            case 1: return "#ff9800"   // Degrading
            case 2: return "#f44336"   // EOL
            default: return "#555577"  // Unknown
        }
    }

    Rectangle {
        anchors.fill: parent
        radius: 12
        color: "#16213e"
        border { width: 2; color: badge.stageColor(badge.stage) }

        RowLayout {
            anchors { fill: parent; margins: 16 }
            spacing: 20

            // 大圆点: 阶段指示
            Rectangle {
                width: 56; height: 56; radius: 28
                color: badge.stageColor(badge.stage)
                Layout.alignment: Qt.AlignVCenter

                Text {
                    anchors.centerIn: parent
                    text: ({
                        0: "H",  1: "D",  2: "EOL"
                    })[badge.stage] || "?"
                    color: "white"
                    font.pixelSize: 24
                    font.bold: true
                }
            }

            ColumnLayout {
                Layout.fillWidth: true
                spacing: 4

                Text {
                    text: badge.stageName || "No Data"
                    color: "#e0e0e0"
                    font.pixelSize: 28
                    font.bold: true
                }

                // RUL 进度条
                RowLayout {
                    spacing: 8
                    Text {
                        text: "RUL:"
                        color: "#8888aa"
                        font.pixelSize: 16
                    }
                    Rectangle {
                        width: 200; height: 14; radius: 7
                        color: "#2a2a4a"
                        Rectangle {
                            width: parent.width * badge.rul
                            height: parent.height
                            radius: 7
                            color: badge.rul > 0.5 ? "#4caf50" :
                                   (badge.rul > 0.3 ? "#ff9800" : "#f44336")
                            Behavior on width { NumberAnimation { duration: 400 } }
                        }
                    }
                    Text {
                        text: (badge.rul * 100).toFixed(0) + "%"
                        color: "#e0e0e0"
                        font.pixelSize: 16
                        font.bold: true
                    }
                }
            }

            // 阶段文字说明
            Text {
                text: ({
                    0: "Battery is\nin good condition",
                    1: "Performance\ndeclining",
                    2: "Battery reached\nend of life"
                })[badge.stage] || "No assessment yet"
                color: "#8888aa"
                font.pixelSize: 14
                horizontalAlignment: Text.AlignRight
                Layout.alignment: Qt.AlignVCenter
            }
        }
    }
}
```

### 5.8 `gui/qml/IcCurveView.qml` — IC 曲线图 (Canvas)

```qml
import QtQuick
import QtQuick.Controls

Rectangle {
    id: view
    color: "#16213e"
    radius: 12

    property var curveData: []   // QVector<double> → JS array

    Canvas {
        id: canvas
        anchors { fill: parent; margins: 8 }
        onPaint: {
            var ctx = getContext("2d")
            var w = width, h = height
            ctx.clearRect(0, 0, w, h)

            // 坐标轴
            ctx.strokeStyle = "#333355"
            ctx.lineWidth = 1
            ctx.beginPath()
            ctx.moveTo(40, 10);     ctx.lineTo(40, h - 30)   // Y 轴
            ctx.moveTo(40, h - 30); ctx.lineTo(w - 10, h - 30)  // X 轴
            ctx.stroke()

            // 标签
            ctx.fillStyle = "#666688"
            ctx.font = "12px sans-serif"
            ctx.fillText("dQ/dV", 2, 14)
            ctx.fillText("Voltage", w - 50, h - 8)

            // 曲线
            if (!view.curveData || view.curveData.length < 2) {
                ctx.fillStyle = "#444466"
                ctx.font = "16px sans-serif"
                ctx.textAlign = "center"
                ctx.fillText("No IC data — press Run PINN / Demo", w / 2, h / 2 - 10)
                return
            }

            var data = view.curveData
            var n = data.length
            var xScale = (w - 60) / (n - 1)
            var yMin = Math.min(...data), yMax = Math.max(...data)
            var yRange = Math.max(yMax - yMin, 0.01)
            var yScale = (h - 50) / yRange

            // IC 曲线
            ctx.strokeStyle = "#00bcd4"
            ctx.lineWidth = 2.5
            ctx.beginPath()
            for (var i = 0; i < n; i++) {
                var x = 40 + i * xScale
                var y = h - 30 - (data[i] - yMin) * yScale
                if (i === 0) ctx.moveTo(x, y)
                else ctx.lineTo(x, y)
            }
            ctx.stroke()

            // 填充
            ctx.lineTo(40 + (n - 1) * xScale, h - 30)
            ctx.lineTo(40, h - 30)
            ctx.closePath()
            ctx.fillStyle = "rgba(0, 188, 212, 0.08)"
            ctx.fill()
        }
    }

    // 标题
    Text {
        anchors { top: parent.top; horizontalCenter: parent.horizontalCenter; topMargin: 8 }
        text: "IC Curve (dQ/dV)"
        color: "#8888aa"
        font.pixelSize: 14
        font.bold: true
    }

    // 图例
    Row {
        anchors { bottom: parent.bottom; right: parent.right; margins: 8 }
        spacing: 6
        Rectangle { width: 16; height: 3; color: "#00bcd4"; anchors.verticalCenter: parent.verticalCenter }
        Text { text: "IC"; color: "#8888aa"; font.pixelSize: 11 }
    }
}
```

### 5.9 `gui/qml/HistoryTable.qml` — 历史记录表

```qml
import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import Battery.App 1.0

Rectangle {
    id: root
    color: "#16213e"
    radius: 12

    property var historyData: []

    function stageEmoji(s) {
        switch (s) { case 0: return "🟢"; case 1: return "🟠"; case 2: return "🔴"; default: return "⚪" }
    }

    function refresh() {
        // 从 C++ backend 拉取最新历史数据
        var raw = dashboard.getHistory()
        historyData = raw
    }

    ColumnLayout {
        anchors { fill: parent; margins: 8 }
        spacing: 4

        Text {
            text: "History"
            color: "#e0e0e0"
            font.pixelSize: 18
            font.bold: true
            Layout.alignment: Qt.AlignHCenter
        }

        // 表头
        Rectangle {
            Layout.fillWidth: true
            height: 28
            color: "#0f3460"
            radius: 4
            RowLayout {
                anchors.fill: parent
                Text { text: "Time"; color: "#aaa"; font.pixelSize: 13; Layout.preferredWidth: 80; Layout.leftMargin: 8 }
                Text { text: "SOH"; color: "#aaa"; font.pixelSize: 13; Layout.preferredWidth: 65 }
                Text { text: "Stage"; color: "#aaa"; font.pixelSize: 13; Layout.preferredWidth: 55 }
                Text { text: "RUL"; color: "#aaa"; font.pixelSize: 13; Layout.fillWidth: true }
            }
        }

        // 历史行
        ListView {
            id: listView
            Layout.fillWidth: true
            Layout.fillHeight: true
            clip: true
            model: root.historyData
            delegate: Rectangle {
                width: listView.width
                height: 30
                color: index % 2 === 0 ? "transparent" : "#1a1a3e"
                radius: 2
                RowLayout {
                    anchors.fill: parent
                    Text { text: modelData[0]; color: "#ddd"; font.pixelSize: 12; Layout.preferredWidth: 80; Layout.leftMargin: 8 }
                    Text { text: modelData[1]; color: "#ddd"; font.pixelSize: 12; Layout.preferredWidth: 65; font.bold: true }
                    Text { text: modelData[2]; color: "#ddd"; font.pixelSize: 12; Layout.preferredWidth: 55 }
                    Text { text: modelData[3]; color: "#ddd"; font.pixelSize: 12; Layout.fillWidth: true }
                }
            }
        }
    }
}
```

---

## 6. CMake 构建配置

### 6.1 `gui/CMakeLists.txt`

```cmake
cmake_minimum_required(VERSION 3.16)
project(battery_gui LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -march=armv8.2-a+fp16+dotprod -mtune=cortex-a55")

# ── 查找 Qt 6 (使用交叉编译的 Qt) ──
# 通过 CMAKE_PREFIX_PATH 指向 Qt 安装位置
set(CMAKE_PREFIX_PATH "/opt/qt6-rzg2l/lib/cmake" ${CMAKE_PREFIX_PATH})

find_package(Qt6 REQUIRED COMPONENTS
    Core
    Gui
    Quick
    Qml
    QuickControls2
    OpenGL
)

qt6_add_resources(QML_RESOURCES
    qml/qml.qrc
)

# ── GUI 可执行文件 ──
add_executable(battery_gui
    src/main.cpp
    src/batterydashboard.cpp
    ${QML_RESOURCES}
)

# 链接 Qt
target_link_libraries(battery_gui PRIVATE
    Qt6::Core
    Qt6::Gui
    Qt6::Quick
    Qt6::Qml
    Qt6::QuickControls2
    Qt6::OpenGL
)

# 链接推理引擎
target_link_libraries(battery_gui PRIVATE
    battery_inference     # 已有的推理库
)

# EGL / GLES (Mali GPU)
target_link_libraries(battery_gui PRIVATE
    EGL
    GLESv2
    drm
)

# 确保 rpath 指向本地 Qt 库 (部署时)
set_target_properties(battery_gui PROPERTIES
    INSTALL_RPATH "\$ORIGIN/../lib"
    BUILD_RPATH "/opt/qt6-rzg2l/lib"
)
```

### 6.2 `gui/qml/qml.qrc` — QML 资源文件

```xml
<!DOCTYPE RCC>
<RCC version="1.0">
    <qresource prefix="/qml">
        <file>MainView.qml</file>
        <file>SohGauge.qml</file>
        <file>StageBadge.qml</file>
        <file>IcCurveView.qml</file>
        <file>HistoryTable.qml</file>
    </qresource>
</RCC>
```

### 6.3 更新顶层 `CMakeLists.txt`

在已有的顶层 `CMakeLists.txt` 中追加:

```cmake
# 已有部分不变...

# ── GUI 子项目 (可选, 需要 Qt 6) ──
option(BUILD_GUI "Build Qt 6 eglfs GUI" OFF)

if(BUILD_GUI)
    # 检查 Qt 6 是否可用
    find_package(Qt6 QUIET COMPONENTS Core)
    if(Qt6_FOUND)
        add_subdirectory(gui)
        message(STATUS "GUI target: battery_gui (Qt ${Qt6_VERSION})")
    else()
        message(WARNING "Qt 6 not found — GUI build disabled."
                        " Set CMAKE_PREFIX_PATH to Qt 6 install location.")
    endif()
endif()
```

---

## 7. 部署到 RZ/G2L

### 7.1 交叉编译 GUI

```bash
# === 在 x86_64 编译机上 ===

# 注: 推理引擎 (libbattery_inference.so) 也需要交叉编译
# 详见 RZG2L_CPP_DEPLOY.md 第 8-9 章

cd /path/to/battery_inference

mkdir -p build-arm64 && cd build-arm64

cmake .. \
    -DCMAKE_TOOLCHAIN_FILE=../toolchain.aarch64.cmake \
    -DCMAKE_BUILD_TYPE=Release \
    -DCMAKE_PREFIX_PATH="/opt/qt6-rzg2l/lib/cmake" \
    -DONNX_RUNTIME_ROOT="/opt/onnxruntime-rzg2l" \
    -DBUILD_GUI=ON

make -j$(nproc)

# 产物:
#   build-arm64/libbattery_inference.so
#   build-arm64/gui/battery_gui
```

### 7.2 打包部署

```bash
# 打包所需全部文件
DEPLOY_DIR="/tmp/battery_deploy"
mkdir -p "$DEPLOY_DIR"/{bin,lib,models,scalers,qml}

# 可执行文件
cp build-arm64/gui/battery_gui "$DEPLOY_DIR/bin/"

# 推理库
cp build-arm64/libbattery_inference.so "$DEPLOY_DIR/lib/"

# ONNX 模型
cp models/battery_pinn_int8.onnx "$DEPLOY_DIR/models/"
cp models/battery_cnn_int8.onnx "$DEPLOY_DIR/models/"

# Scaler 参数
cp scalers/*.bin "$DEPLOY_DIR/scalers/"

# 创建启动脚本
cat > "$DEPLOY_DIR/bin/start_gui.sh" << 'STARTUP'
#!/bin/bash
# Battery SOH GUI — RZ/G2L Launch Script

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
APP_DIR="$(dirname "$SCRIPT_DIR")"

export LD_LIBRARY_PATH="$APP_DIR/lib:/opt/lib:$LD_LIBRARY_PATH"

# eglfs 配置
export QT_QPA_PLATFORM=eglfs
export QT_QPA_EGLFS_INTEGRATION=eglfs_mali
export QT_QPA_EGLFS_HIDECURSOR=1
export QT_QPA_EGLFS_ALWAYS_SET_MODE=1

# Qt Quick 场景图
export QSG_RENDER_LOOP=basic        # basic/threaded — basic 更稳
export QT_QUICK_CONTROLS_STYLE=Material
export QT_QUICK_CONTROLS_MATERIAL_THEME=Dark

# 日志
export QT_LOGGING_RULES="qt.qpa.eglfs*=true"

# 启动
exec "$SCRIPT_DIR/battery_gui" "$@"
STARTUP
chmod +x "$DEPLOY_DIR/bin/start_gui.sh"

# 打包
tar czf /tmp/battery_deploy.tar.gz -C "$DEPLOY_DIR" .

# 传输到 RZ/G2L
scp /tmp/battery_deploy.tar.gz root@<rzg2l-ip>:/home/root/
```

### 7.3 在 RZ/G2L 上部署

```bash
# === 在 RZ/G2L 上 ===

# 解压
cd /home/root
tar xzf battery_deploy.tar.gz

# 安装到 /opt
sudo mkdir -p /opt/battery-gui
sudo cp -r battery_deploy/* /opt/battery-gui/

# 验证库依赖
ldd /opt/battery-gui/bin/battery_gui
# 确认所有 .so 都能找到, 尤其:
#   libbattery_inference.so → /opt/battery-gui/lib/
#   libQt6*.so              → /opt/lib/
#   libonnxruntime.so       → 系统路径或 /opt/lib/

# 手动测试启动
cd /opt/battery-gui
QT_QPA_PLATFORM=eglfs \
QT_QPA_EGLFS_INTEGRATION=eglfs_mali \
LD_LIBRARY_PATH=/opt/battery-gui/lib:/opt/lib \
  ./bin/battery_gui

# 按 Ctrl+C 退出, 或用触摸屏/鼠标操作 Exit 按钮
```

---

## 8. 上电自启 (systemd)

```bash
# === 在 RZ/G2L 上 ===

sudo tee /etc/systemd/system/battery-gui.service << 'SYSTEMD'
[Unit]
Description=Battery SOH Assessment GUI
Documentation=https://github.com/your-team/battery-inference
After=network.target multi-user.target
Wants=network.target
Conflicts=getty@tty1.service

[Service]
Type=simple
User=root
Group=video
WorkingDirectory=/opt/battery-gui

# 环境变量
Environment=LD_LIBRARY_PATH=/opt/battery-gui/lib:/opt/lib
Environment=QT_QPA_PLATFORM=eglfs
Environment=QT_QPA_EGLFS_INTEGRATION=eglfs_mali
Environment=QT_QPA_EGLFS_HIDECURSOR=1
Environment=QT_QPA_EGLFS_ALWAYS_SET_MODE=1
Environment=QSG_RENDER_LOOP=basic
Environment=QT_QUICK_CONTROLS_STYLE=Material
Environment=QT_QUICK_CONTROLS_MATERIAL_THEME=Dark

# 若使用触摸屏, 添加:
# Environment=QT_QPA_EVDEV_TOUCHSCREEN_PARAMETERS=/dev/input/event0:rotate=0

ExecStart=/opt/battery-gui/bin/battery_gui

# 崩溃自动重启
Restart=on-failure
RestartSec=3

# 确保 tty1 空闲 (eglfs 需要)
StandardOutput=journal
StandardError=journal
TTYPath=/dev/tty1
TTYReset=yes
TTYVHangup=yes

[Install]
WantedBy=multi-user.target
SYSTEMD

# 启用自启
sudo systemctl daemon-reload
sudo systemctl enable battery-gui.service

# 立即启动
sudo systemctl start battery-gui.service

# 查看状态
sudo systemctl status battery-gui.service

# 查看日志
journalctl -u battery-gui.service -f

# 如果要临时停止 (调试用)
# sudo systemctl stop battery-gui.service
```

---

## 9. UI 自定义指南

### 9.1 修改配色方案

QML 文件中所有颜色集中在几处, 全局替换即可:

```qml
// 主背景色
color: "#1a1a2e"   // 深蓝 → 改为 "#1e1e1e" 即纯黑

// 卡片色
color: "#16213e"   // 深紫蓝 → 改为 "#2d2d2d" 即深灰

// Healthy / Degrading / EOL 颜色
"#4caf50"  // 绿  → 自定义
"#ff9800"  // 橙  → 自定义
"#f44336"  // 红  → 自定义

// IC 曲线颜色
"#00bcd4"  // 青色 → 自定义
```

### 9.2 适配不同分辨率

```bash
# 启动前设置环境变量强制分辨率:
export QT_QPA_EGLFS_PHYSICAL_WIDTH=155    # 屏幕物理宽 mm
export QT_QPA_EGLFS_PHYSICAL_HEIGHT=86    # 屏幕物理高 mm

# 或者: kms.conf 文件指定模式
cat > /opt/battery-gui/kms.conf << 'KMS'
{
  "device": "/dev/dri/card0",
  "outputs": [
    { "name": "LVDS-1", "mode": "1024x600" }
  ]
}
KMS
export QT_QPA_EGLFS_KMS_CONFIG=/opt/battery-gui/kms.conf
```

### 9.3 接入真实数据源

修改 `BatteryDashboard` 中的数据入口即可 — QML UI 层不需要改动:

```cpp
// batterydashboard.cpp — 将 demo 数据替换为真实采集

// 示例: 从串口 / SPI / 共享内存读取 RA8 采集数据
void BatteryDashboard::onNewDataArrived(const SensorData &data) {
    // RA8 采集的原始数据
    QVector<double> features132 = {
        // data.ic_curve (128 points)
        ...,
        // data.temperature, data.log_cycle, data.dv, data.capacity
    };

    // 运行 PINN 推理
    runPINN(features132);

    // 同时运行 CNN (使用 IC 曲线)
    runCNN(data.ic_curve.toQVector());
}
```

### 9.4 添加触摸屏支持

```bash
# 查找触摸屏输入设备
ls -la /dev/input/by-path/ | grep -i touch
# 或 evtest (交互式测试)
sudo apt-get install -y evtest
sudo evtest

# 配置 Qt 使用触摸屏:
export QT_QPA_EVDEV_TOUCHSCREEN_PARAMETERS="/dev/input/event0:rotate=0:invertx=0:inverty=0"
export QT_QPA_EGLFS_DISABLE_INPUT=0

# 若使用 libinput (推荐, 支持多点触控):
export QT_QPA_EGLFS_KMS_CONFIG=kms.conf  # 自动通过 libinput 接管
```

---

## 10. 故障排查

### 10.1 eglfs 无法启动 — "Could not open DRM device"

```bash
# 症状:
#   Could not open DRM device /dev/dri/card0
#   qt.qpa.eglfs: Unable to open DRM device

# 排查:
# 1. 检查 DRM 设备是否存在
ls -la /dev/dri/card0

# 2. 检查权限
sudo chmod 0666 /dev/dri/card0 /dev/dri/renderD128

# 3. 检查是否有其他进程占用
fuser -v /dev/dri/card0
sudo fuser -k /dev/dri/card0  # 杀掉占用进程

# 4. 确认 Mali/panfrost 模块加载
lsmod | grep -E 'mali|panfrost'
dmesg | grep -i 'mali\|panfrost\|drm'

# 5. 若模块未加载:
sudo modprobe panfrost  # 或 sudo modprobe mali
```

### 10.2 EGL 初始化失败

```bash
# 症状:
#   qt.qpa.eglfs: EGL initialization failed
#   Could not initialize EGL display

# 排查:
# 1. 检查 libEGL 和 libGLESv2 是否存在
find /usr/lib /opt/lib -name "libEGL*" -o -name "libGLESv2*"

# 2. 检查 EGL 能否独立工作
python3 -c "
import ctypes
dll = ctypes.CDLL('libEGL.so')
dpy = dll.eglGetDisplay(0)
print(f'EGL Display: {hex(dpy)}')
"

# 3. 如果 eglGetDisplay 返回 0, 说明 Mali 驱动未正确安装
#    尝试重新安装 Mali 用户态库
sudo dpkg -l | grep -i mali

# 4. 或切换到 panfrost:
sudo apt-get install -y libegl1-mesa libgles2-mesa
sudo modprobe panfrost
```

### 10.3 QML 渲染异常 — 白屏 / 黑屏

```bash
# 症状:
#   程序启动但屏幕全白或全黑

# 排查:
# 1. 检查 Qt Quick 场景图后端
export QSG_INFO=1
./battery_gui 2>&1 | grep -i 'render\|scene\|backend'

# 2. 若 Mali GPU 渲染有问题, 切换到 software 后端:
export QT_QUICK_BACKEND=software
# 或只改场景图:
export QSG_RENDER_LOOP=basic

# 3. 检查 OpenGL ES 版本
export QT_OPENGL=software
# 然后重试

# 4. 验证 Mali 是否支持 OpenGL ES:
es2_info | grep -i version
# 期望: GL_VERSION: OpenGL ES 2.0 ...
```

### 10.4 推理引擎加载失败

```bash
# 症状:
#   "Failed to load models: ..."
#   或 libbattery_inference.so not found

# 排查:
# 1. 确认 LD_LIBRARY_PATH 包含推理库路径
echo $LD_LIBRARY_PATH
ldd /opt/battery-gui/bin/battery_gui | grep "not found"

# 2. 确认模型文件存在
ls -la /opt/battery-gui/models/
# 应包含: battery_pinn_int8.onnx  battery_cnn_int8.onnx

# 3. 确认 scaler 文件存在
ls -la /opt/battery-gui/scalers/
# 应包含 6 个 .bin 文件

# 4. 如果模型路径不对, 修改 batterydashboard.cpp 中的路径:
#    pinnCfg.model_path = "/opt/battery-gui/models/battery_pinn_int8.onnx";
```

### 10.5 启动后无触摸/键盘输入

```bash
# 排查:
# 1. 检查输入设备
ls -la /dev/input/
cat /proc/bus/input/devices

# 2. 使用 evtest 验证:
sudo evtest
# 选择一个 event 设备, 触摸屏幕看是否有事件

# 3. 配置 Qt 输入:
export QT_QPA_EVDEV_KEYBOARD_PARAMETERS="/dev/input/event1:grab=1"
export QT_QPA_EVDEV_TOUCHSCREEN_PARAMETERS="/dev/input/event0"
export QT_QPA_EGLFS_DISABLE_INPUT=0

# 4. 或使用 libinput (推荐):
export QT_QPA_EGLFS_USE_LIBINPUT=1
```

---

## 附录 A: 完整文件清单

```
battery_inference/
│
├── RZG2L_CPP_DEPLOY.md           ← 已有: C++ 推理引擎部署教程
├── RZG2L_GUI_DEPLOY.md           ← 本文件: Qt 6 GUI 部署教程
├── export_scalers.py             ← 已有: Scaler 导出脚本
│
├── include/
│   └── battery_inference.h       ← 已有: 推理引擎 PIMPL 头文件
│
├── src/
│   ├── battery_inference.cpp     ← 已有: 推理引擎实现
│   └── main.cpp                  ← 已有: CLI 工具入口
│
├── gui/                          ← ★ 新增: Qt 6 GUI
│   ├── CMakeLists.txt
│   ├── src/
│   │   ├── main.cpp
│   │   ├── batterydashboard.h
│   │   └── batterydashboard.cpp
│   └── qml/
│       ├── qml.qrc
│       ├── MainView.qml
│       ├── SohGauge.qml
│       ├── StageBadge.qml
│       ├── IcCurveView.qml
│       └── HistoryTable.qml
│
├── CMakeLists.txt                ← 已有: 更新以支持 BUILD_GUI
├── toolchain.aarch64.cmake       ← 已有: 交叉编译工具链
│
├── models/
│   ├── battery_pinn_int8.onnx
│   └── battery_cnn_int8.onnx
│
└── scalers/
    ├── pinn_mean.bin
    ├── pinn_std.bin
    ├── cnn_ic_scaler_mean.bin
    ├── cnn_ic_scaler_std.bin
    ├── cnn_ig_scaler_mean.bin
    └── cnn_ig_scaler_std.bin
```

## 附录 B: 快速参考卡

```bash
# ====== 启动/停止 ======
sudo systemctl start battery-gui     # 启动 GUI
sudo systemctl stop battery-gui      # 停止 GUI
sudo systemctl status battery-gui    # 查看状态
journalctl -u battery-gui -f         # 实时日志

# ====== 手动启动 (调试用) ======
cd /opt/battery-gui
QT_QPA_PLATFORM=eglfs LD_LIBRARY_PATH=./lib:/opt/lib ./bin/battery_gui

# ====== 切换到 tty ======
# Ctrl+Alt+F2  → tty2 (纯文本)
# Ctrl+Alt+F1  → tty1 (GUI 应用)

# ====== 检查 GPU ======
ls /dev/dri/card0                    # DRM 设备
fuser -v /dev/dri/card0              # 谁在用 GPU
dmesg | grep -i 'mali\|panfrost'     # GPU 驱动日志

# ====== 性能分析 ======
export QSG_RENDER_TIMING=1           # Qt Quick 渲染计时
export QT_LOGGING_RULES="qt.qpa.eglfs*=true"  # eglfs 详细日志

# ====== 完全恢复旧显示 (调试时) ======
sudo systemctl stop battery-gui
# 重新启用 console:
sudo systemctl start getty@tty1
```
