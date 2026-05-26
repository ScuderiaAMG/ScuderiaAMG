# 华中大体育 GPS 跑步模拟器

沿华科校园路线生成模拟跑步 GPS 轨迹，完成"华中大体育"App 的课外跑步打卡。

**约束规则：每次跑步最少 3.5 km，配速范围 4:00 - 10:00 min/km。**

---

## 两种使用方式

| 方式 | 原理 | 适用设备 | 推荐度 |
|------|------|----------|--------|
| **GPX 导出** (推荐) | 导出轨迹文件 → 手机 Mock GPS App 导入播放 | 所有 Android 设备 | ★★★★★ |
| **ADB 实时模拟** | PC 通过 USB 每秒向手机注入 GPS 坐标 | 仅部分 ROM 支持 | ★★ |

> **HyperOS / Android 14+ 用户请用 GPX 导出方式。** `cmd location` test provider 在新版系统中不被完整支持。运行 `python run.py --diagnose` 可检测你的设备是否兼容 ADB 方式。

---

## 方式一：GPX 导出（推荐，全设备通用）

不依赖 ADB 实时注入。PC 端预先生成 GPX 轨迹文件，传到手机上用 Mock GPS App 播放。**所有 Android 设备通用。**

### 第一步：安装 Python

终端输入 `python --version`，显示 `3.x` 即可。否则去 https://www.python.org/downloads/ 下载安装（勾选 "Add Python to PATH"）。

### 第二步：导出 GPX 文件

```bash
cd Running

# 交互版（需要先 pip install rich click）
python run.py --gpx route.gpx

# CLI 版（零依赖，直接跑）
python run_cli.py -p 5.5 -l 2 --gpx route.gpx
```

可选参数：`--pace 5.0`（配速）、`--laps 2`（圈数）、`--max-time 1800`（限时）。

### 第三步：手机端操作

1. **安装 Mock GPS App**：手机应用商店或浏览器搜索下载 **"Fake GPS Location"**
2. **传 GPX 文件到手机**：微信/QQ 文件传输、USB 拷贝、或 `adb push route.gpx /sdcard/` 均可
3. **配置开发者选项**：
   - 设置 → 我的设备 → 全部参数 → 连点 MIUI 版本 7 次
   - 设置 → 更多设置 → 开发者选项 → **"选择模拟位置信息应用"** → 选你装的 Mock GPS App
4. **在 Mock GPS App 中导入 GPX 文件**，设置播放速度，点击开始
5. 打开华中大体育 App，进入跑步页面，里程自动累计

> 不需要保持 USB 连接。GPX 文件一次性导出，手机上随时播放。

---

## 方式二：ADB 实时模拟（仅兼容设备）

PC 通过 USB 每秒向手机注入模拟 GPS 坐标，实时控制位置变化。

### 兼容性检测

```bash
python run.py --diagnose
# 或
python run_cli.py --diagnose
```

诊断报告会告诉你设备是否支持 `cmd location` test provider。如果显示 "test provider 创建失败"（HyperOS 常见情况），请改用方式一。

### 环境准备

1. **安装 ADB**：下载 [SDK Platform Tools](https://developer.android.com/tools/releases/platform-tools)，解压到 `C:\platform-tools`，加入系统 PATH
2. **手机设置**：
   - 设置 → 我的设备 → 全部参数 → 连点 MIUI 版本 7 次（开启开发者模式）
   - 设置 → 更多设置 → 开发者选项 → 开启 **USB 调试**
   - USB 连接电脑，手机上点"允许"授权
3. **验证连接**：`adb devices` 确认看到 `device`
4. **安装依赖**：`pip install rich click`

### 运行

```bash
# 预览轨迹
python run.py --dry-run

# 实际跑
python run.py --pace 5.0

# CLI 版
python run_cli.py -p 5.0 -y
```

按 Ctrl+C 安全退出，自动清理 Mock 环境。

---

## 纯命令行模式（SSH / 远程）

`run_cli.py` 零第三方依赖（仅需 Python 标准库），适合 SSH 远程操作：

```bash
# GPX 导出
python run_cli.py -p 5.5 --gpx route.gpx

# 实时模拟
python run_cli.py -p 5.5 -y

# 诊断
python run_cli.py --diagnose

# 后台运行
nohup python3 run_cli.py -p 5.5 -l 2 -y > run.log 2>&1 &
```

---

## 远程部署方案

核心约束：**跑脚本的机器必须 USB 连接手机**。云服务器做不到这点。

**方案 A：本地服务器（推荐）**
找台旧笔记本/树莓派装 Linux，手机插上面 24h 开机。从任何地方 SSH 上去控制。

```bash
# 服务器上装 ADB
sudo apt install adb -y

# 本机上传项目
scp -r Running user@192.168.1.100:~/

# SSH 上去跑
ssh user@192.168.1.100
cd ~/Running
python3 run_cli.py -p 5.5 -l 2 -y
```

**方案 B：Windows 开 SSH**
管理员 PowerShell 安装 OpenSSH Server，同 WiFi 下用平板 SSH 进来控制。

```powershell
Add-WindowsCapability -Online -Name OpenSSH.Server~~~~0.0.1.0
Start-Service sshd
Set-Service -Name sshd -StartupType 'Automatic'
```

---

## 命令行参数速查

| 参数 | `run.py` | `run_cli.py` | 说明 |
|------|----------|-------------|------|
| GPX 导出 | `--gpx route.gpx` | `--gpx route.gpx` | 导出轨迹文件（推荐） |
| 配速 | `--pace 5.5` | `-p 5.5` | min/km, 范围 4-10 |
| 速度 | `--speed 3.33` | `-s 3.33` | m/s |
| 路线 | `--route hust_campus` | `-r hust_campus` | 路线名称 |
| 圈数 | `--laps 2` | `-l 2` | 默认自动满足 3.5km |
| 限时 | `--max-time 1800` | `-t 1800` | 秒 |
| 预览 | `--dry-run` | `--dry-run` | 不连设备 |
| 诊断 | `--diagnose` | `--diagnose` | 检测 mock 兼容性 |
| 列表 | `--list-routes` | `--list` | 列出可用路线 |

### 配速参考

| 场景 | 配速 | 2 圈 (~4.8km) |
|------|------|--------------|
| 快跑 | 4:00 | ~20 min |
| 慢跑 | 5:00 | ~24 min |
| 很慢 | 6:00 | ~29 min |
| 快走 | 8:00 | ~39 min |
| 极慢 | 10:00 | ~49 min |

---

## 常见问题排查

**Q: GPX 导入后 App 位置无变化？**
1. 确认 Mock GPS App 已被设为"选择模拟位置信息应用"
2. 部分 App 要求 Mock GPS App 保持**前台运行**
3. 重启手机再试

**Q: ADB 实时模拟里程不增加？**
大概率 HyperOS 不支持。运行 `--diagnose`，如显示 test provider 失败请改用 GPX 方式。

**Q: 如何自定义路线？**
在 `routes/` 目录下创建 JSON 文件，格式参见 `hust_campus.json`。GPS 坐标可用高德坐标拾取器获取：https://lbs.amap.com/tools/picker

---

## 安全提醒

- 本工具仅供个人学习研究使用
- 请在规则允许的范围内合理使用
- 配速已限制在 4:00-10:00 min/km，自动满足 3.5km 最低距离
- GPX 方式无需 USB 常连，使用更方便且无兼容性问题
