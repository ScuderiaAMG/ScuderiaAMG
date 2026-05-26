# 华中大体育 GPS 跑步模拟器

通过 USB 连接 Android 手机，利用 ADB 向手机注入模拟 GPS 坐标，沿华科校园路线模拟跑步轨迹，完成"华中大体育"App 的课外跑步打卡。

**约束规则：每次跑步最少 3.5 km，配速范围 4:00 - 10:00 min/km。**

---

## 目录

- [前置环境](#前置环境)
- [第一步：安装 Python](#第一步安装-python)
- [第二步：安装 ADB](#第二步安装-adb)
- [第三步：手机端设置](#第三步手机端设置)
- [第四步：连接手机到电脑](#第四步连接手机到电脑)
- [第五步：安装 Python 依赖](#第五步安装-python-依赖)
- [第六步：预览轨迹（不连手机）](#第六步预览轨迹不连手机)
- [第七步：开始模拟跑步](#第七步开始模拟跑步)
- [第八步：纯命令行模式（SSH / 远程）](#第八步纯命令行模式ssh--远程)
- [第九步：远程部署方案](#第九步远程部署方案)
- [命令行参数速查](#命令行参数速查)
- [常见问题排查](#常见问题排查)
- [自定义路线](#自定义路线)

---

## 前置环境

你需要准备好以下三样东西：

| 序号 | 物品 | 用途 |
|------|------|------|
| 1 | 一台 Windows 电脑 | 运行模拟脚本 |
| 2 | 一根 USB 数据线 | 连接手机和电脑（**必须支持数据传输**，不能是只充电的线） |
| 3 | 你的小米 14 Pro | 被模拟 GPS 的设备 |

整个首次配置过程大约需要 **15-20 分钟**。

---

## 第一步：安装 Python

### 1.1 检查是否已安装

打开 **命令提示符（CMD）** 或 **PowerShell**，输入：

```bash
python --version
```

如果显示 `Python 3.x.x` 说明已安装，可跳到下一步。

### 1.2 下载安装

1. 浏览器打开 https://www.python.org/downloads/
2. 点击黄色 **Download Python** 按钮下载最新版
3. 运行下载的 `.exe` 安装程序
4. **关键步骤**：安装界面第一页，务必勾选底部的 **"Add Python to PATH"**
5. 点击 **Install Now**，等待安装完成
6. 重新打开 CMD，输入 `python --version` 确认安装成功

> 如果忘记了勾选 "Add Python to PATH"，可以重新运行安装程序，选择 "Modify" 来补上。

---

## 第二步：安装 ADB

ADB（Android Debug Bridge）是电脑和 Android 手机通信的桥梁工具。

### 2.1 下载

1. 浏览器打开 https://developer.android.com/tools/releases/platform-tools
2. 找到 **"Download SDK Platform-Tools for Windows"** 链接并点击下载
3. 你会得到一个 `platform-tools-latest-windows.zip` 文件

### 2.2 解压

1. 将下载的 zip 文件解压
2. 把解压出来的 `platform-tools` 文件夹放到一个固定的位置，例如：
   ```
   C:\platform-tools
   ```
   （不要放在桌面或临时文件夹，以后还要用）

### 2.3 添加到系统 PATH

1. 按键盘 **Win 键**，输入 **"环境变量"**，点击 **"编辑系统环境变量"**
2. 在弹出的"系统属性"窗口中，点击右下角 **"环境变量(N)..."**
3. 在下方"系统变量"区域，找到并双击 **Path**
4. 点击右侧 **"新建"**，输入你的 platform-tools 文件夹路径，例如：
   ```
   C:\platform-tools
   ```
5. 依次点击 **"确定"** 关闭所有窗口

### 2.4 验证安装

重新打开一个新的 CMD 窗口，输入：

```bash
adb version
```

如果看到类似 `Android Debug Bridge version 1.0.41` 的输出，说明安装成功。

---

## 第三步：手机端设置

> 以下操作在小米 14 Pro 上进行，系统为 HyperOS（Android 14）。

### 3.1 开启开发者选项

1. 打开手机 **设置**
2. 进入 **我的设备**（或"关于手机"）
3. 找到 **全部参数与信息**
4. 连续快速点击 **"MIUI 版本"**（或"OS 版本"）**7 次**
5. 系统会提示"您已处于开发者模式"或要求输入锁屏密码确认

### 3.2 开启 USB 调试

1. 回到 **设置** 主页面
2. 进入 **更多设置**（或"系统与设备"）
3. 进入 **开发者选项**（新出现的菜单项）
4. 找到并打开以下开关：
   - ✅ **USB 调试**
   - ✅ **USB 安装**（如果有）
   - ✅ **USB 调试（安全设置）**（如果有这个选项也要打开）

5. 在开发者选项中找到 **"选择模拟位置信息应用"**，如果能看到这个选项即可，**不需要选择任何应用**

> 找不到"开发者选项"？去设置顶部搜索"开发者"三个字即可定位。

---

## 第四步：连接手机到电脑

1. 用 **USB 数据线** 将手机连接到电脑
2. 手机屏幕上会弹出 **"允许 USB 调试吗？"** 的对话框
3. 勾选 **"一律允许使用这台计算机进行调试"**
4. 点击 **"允许"**

### 验证连接

在电脑 CMD 中输入：

```bash
adb devices
```

正常输出应该类似：

```
List of devices attached
abc12345        device
```

如果显示 `unauthorized`，说明手机上还没点"允许"。
如果显示 `offline`，拔掉数据线重新插一下。
如果什么都没有，检查 USB 线是否支持数据传输。

---

## 第五步：安装 Python 依赖

打开 CMD，进入本项目目录：

```bash
cd Running
```

安装依赖包：

```bash
pip install -r requirements.txt
```

或者手动安装：

```bash
pip install rich click
```

---

## 第六步：预览轨迹（不连手机）

在正式跑之前，建议先预览一下模拟轨迹是否正常：

```bash
# 查看有哪些路线可用
python run.py --list-routes

# 预览默认路线和配速
python run.py --dry-run

# 预览自定义配速
python run.py --dry-run --pace 6.0
```

你会看到：
- 路线名称、航点数量、是否为环路
- 配速、总距离、预计用时
- 生成的 GPS 坐标点预览

这一步**不需要连接手机**，纯本地计算验证。

---

## 第七步：开始模拟跑步

### 7.1 准备工作

在开始之前，确认以下几点：

- [ ] 手机已通过 USB 连接到电脑
- [ ] `adb devices` 能看到设备
- [ ] 手机上的"华中大体育"App 已经打开
- [ ] App 已经进入跑步页面，等待 GPS 定位

### 7.2 基础使用

> 程序会自动计算最小圈数满足 3.5 km 底线，也接受手动指定圈数。

```bash
# 默认配速 5:00 min/km，自动跑 2 圈（约 4.8 km，满足 3.5 km），约 24 分钟
python run.py

# 配速 6:30 min/km（慢跑，自动 2 圈约 32 分钟）
python run.py --pace 6.5

# 手指定跑 3 圈（约 7.3 km）
python run.py --laps 3

# 配速 4:30 + 跑 2 圈
python run.py --pace 4.5 --laps 2

# 最多跑 30 分钟，不管跑了几圈
python run.py --max-time 1800
```

### 7.3 运行过程

程序启动后会依次执行：

```
📱 检测设备...                   # 查找连接的手机
✅ 已连接设备: abc12345

🔧 正在配置模拟定位环境...        # 设置手机的 Mock GPS
✅ 模拟定位环境配置完成

🏃 开始跑步模拟... 按 Ctrl+C 停止

[████████████░░░░░░░░░░░] 65.3%  ├ 1.56 km  ├ 07:48  ├ 配速 5:00  ├ (30.513, 114.416)
```

进度条会实时显示：
- 完成百分比
- 已跑距离
- 已用时间
- 当前配速
- 当前 GPS 坐标

### 7.4 停止模拟

- **正常完成**：跑完设定的圈数后自动停止
- **手动停止**：按 **Ctrl + C** 安全退出，会自动清理手机上的模拟环境
- 无论哪种方式，程序退出时都会自动清理 Mock GPS 设置

---

## 第八步：纯命令行模式（SSH / 远程）

如果你需要通过 SSH 远程控制，或者运行在没有显示器的服务器上，可以使用纯 CLI 脚本 `run_cli.py`。

### 与交互版的区别

| | `run.py` (交互版) | `run_cli.py` (CLI 版) |
|---|---|---|
| 依赖 | 需要 `rich` + `click` | **零依赖**，仅 Python 标准库 |
| 界面 | 彩色进度条、面板 | ASCII 进度条，纯文本输出 |
| 适用场景 | 本地终端 | SSH、tmux、headless、脚本自动化 |
| 参数风格 | `--pace 5.5 --laps 2` | `-p 5.5 -l 2` |

### CLI 版用法

```bash
# 默认配速 5:00 min/km，自动圈数 (满足 3.5 km)
python run_cli.py

# 指定配速（短参数）
python run_cli.py -p 6.5          # 配速 6:30 min/km

# 配速 + 圈数
python run_cli.py -p 5.0 -l 3     # 配速 5:00, 跑 3 圈

# 配速 + 时间上限（30 分钟）
python run_cli.py -p 4.5 -t 1800

# 直接用速度值
python run_cli.py -s 3.33         # 3.33 m/s

# 预览轨迹
python run_cli.py --dry-run

# 列出可用路线
python run_cli.py --list
```

### 运行效果

```
[OK] 已连接设备: abc12345
=======================================================
  路线:    hust_campus — 华科主校区跑步路线
  总距离:  2.44 km  |  圈数: 1
  配速:    5:00 min/km (3.33 m/s)
  预计:    12:14  |  735 个坐标点
=======================================================

开始模拟? [Y/n]: y
[*] 配置 Mock GPS 环境...
[OK] Mock GPS 环境就绪

=======================================================
  跑步进行中...  按 Ctrl+C 停止
=======================================================

|##########---------------| 43.5%  ├ 1.06 km  ├ 05:18  ├ 5:00/km  ├ (30.51342,114.41618)
```

### SSH 远程部署

1. 将整个 `Running/` 目录上传到远程机器：
   ```bash
   scp -r Running/ user@remote-host:/home/user/
   ```

2. 远程机器上仍需安装 Python 3 和 ADB（参考第一步和第二步）

3. SSH 上去直接跑——CLI 版无需 pip install：
   ```bash
   ssh user@remote-host
   cd /home/user/Running
   python run_cli.py -p 5.0 -l 1
   ```

4. 远程机器的 USB 口需要插手机，`adb devices` 能看到设备即可

### 后台运行（不占用终端）

在 SSH 里用 `nohup` 或 `tmux` 可让模拟在后台持续运行：

```bash
# 方式 A: nohup + -y（跳过确认，跑完自动退出）
nohup python3 run_cli.py -p 5.5 -l 2 -y > run.log 2>&1 &

# 方式 B: tmux（随时切回来看进度）
tmux new -s run
python run_cli.py -p 5.5 -l 2
# Ctrl+B, D 断开, tmux attach -t run 重连
```

> **提示**：nohup 后台运行时，用 `-y` 参数跳过确认提示：`nohup python3 run_cli.py -p 5.5 -l 2 -y > run.log 2>&1 &`

---

## 第九步：远程部署方案

核心约束：**跑脚本的机器必须通过 USB 插着手机**。云服务器（阿里云/腾讯云/AWS）做不到这一点。以下是两种可行方案。

### 9.1 方案 A：本地服务器（推荐）

找一台闲置设备放在宿舍/家里，24 小时开机，手机一直插在上面。你从任何地方 SSH 上去控制。

```
你 (任何地方)  ──SSH──>  本地服务器 (宿舍)  ──USB──>  手机
```

**适合的设备：**

| 设备 | 成本 | 功耗 | 推荐度 |
|------|------|------|--------|
| 旧笔记本（装 Linux） | 0 | ~15W | ★★★★★ |
| 树莓派 4B/5 | ~200元 | ~5W | ★★★★ |
| 香橙派/其他 SBC | ~100元 | ~5W | ★★★ |
| 安卓手机 + Termux | 0 | ~3W | ★★（配置复杂） |

**部署步骤（以 Debian/Ubuntu 为例）：**

```bash
# ─── 1. 服务器端安装依赖 ───

# 安装 ADB
sudo apt update
sudo apt install adb -y

# 确认 Python 3 可用（系统自带）
python3 --version

# ─── 2. 从本机上传项目 ───

# 在你自己的电脑上执行：
scp -r Running user@192.168.1.100:~/

# ─── 3. 服务器上验证 ───

ssh user@192.168.1.100
cd ~/Running

# 手机插上 USB，检查设备
adb devices
# 预期输出: xxxxxx  device

# 预览轨迹（不连手机也行）
python3 run_cli.py --dry-run -p 5.0

# ─── 4. 开始模拟 ───

python3 run_cli.py -p 5.5 -l 2 -y
```

**防止 USB 休眠丢连接：**

```bash
# 添加 crontab 定期保活，每 15 分钟 ping 一次 adb
crontab -e
# 加入这一行:
*/15 * * * * /usr/bin/adb devices > /dev/null 2>&1
```

**保持手机不锁屏：**

```bash
# 方法 1: 通过 ADB 开启充电常亮（临时生效）
adb shell svc power stayon true

# 方法 2: 手机设置里手动打开
# 开发者选项 → 开启「不锁定屏幕」（充电时屏幕不会休眠）
```

> **注意**：即使开着"不锁定屏幕"，长时间闲置后手机的 HyperOS 息屏策略可能仍然会断开 ADB。建议额外在手机 **设置 → 锁屏 → 自动锁屏 → 设置为"永不"**。

**配合 tmux 实现持久会话：**

```bash
# 创建会话
tmux new -s runner

# 运行模拟
python3 run_cli.py -p 5.5 -l 2 -y

# 按 Ctrl+B 然后按 D 断开（模拟继续在后台跑）
# 退出 SSH 也完全不影响

# 下次 SSH 进来重新查看：
tmux attach -t runner
```

---

### 9.2 方案 B：Windows 本机开 SSH 服务

你的 Windows 电脑本身就是"服务器"。开启自带 SSH 服务后，同一局域网内的手机/平板就能远程控制它。

```
手机/平板 (同 WiFi)  ──SSH──>  你的 Windows 电脑  ──USB──>  手机
```

> 此场景适用于：跑步时手机插电脑，你在平板或另一台手机上 SSH 过来控制。

**在 Windows 上安装 OpenSSH Server（管理员 PowerShell）：**

```powershell
# 安装
Add-WindowsCapability -Online -Name OpenSSH.Server~~~~0.0.1.0

# 启动
Start-Service sshd

# 设为开机自启
Set-Service -Name sshd -StartupType 'Automatic'

# 确认防火墙放行端口 22
New-NetFirewallRule -Name sshd -DisplayName 'OpenSSH Server' `
    -Enabled True -Direction Inbound -Protocol TCP -Action Allow -LocalPort 22
```

**从其他设备 SSH 进来：**

```bash
# 先确认 Windows 电脑的局域网 IP
# Windows 上执行: ipconfig  → 找到 IPv4 地址，如 192.168.1.105

# 从手机/平板/其他电脑 SSH 连接：
ssh 你的Windows用户名@192.168.1.105

# 进入项目目录开跑
cd Running
python run_cli.py -p 5.5 -l 2
```

> Windows 用户名为登录时的英文名（不是中文名）。不确定的话在 CMD 里 `echo %USERNAME%` 看。SSH 登录密码就是 Windows 锁屏密码/PIN 码。

---

### 9.3 手机端参考（JuiceSSH）

Android 手机/平板推荐使用 **JuiceSSH**（Play Store 免费），连接后可以随时远程控制 Windows 电脑上的跑步脚本。

操作流程：
1. 平板安装 JuiceSSH → 新建连接 → 填 Windows IP、用户名、密码
2. 点击连接 → `cd Running`
3. `python run_cli.py -p 5.5` → 开始跑
4. 断开 JuiceSSH 不影响（会话会断，所以建议配合 Windows 端的 tmux 或者用 PowerShell 的进程）

---

## 命令行参数速查

### 交互版 `run.py`

| 参数 | 说明 | 示例 |
|------|------|------|
| `--pace` | 跑步配速 (min/km), 范围 4-10 | `--pace 5.5`（5 分 30 秒每公里） |
| `--speed` | 跑步速度（m/s） | `--speed 3.33`（等价于 5:00 配速） |
| `--route` | 路线名称 | `--route hust_campus` |
| `--laps` | 跑几圈（默认自动满足 3.5km） | `--laps 2` |
| `--max-time` | 最长跑多久（秒） | `--max-time 1800`（30 分钟） |
| `--dry-run` | 仅预览轨迹 | `--dry-run` |
| `--list-routes` | 列出所有路线 | `--list-routes` |

### CLI 版 `run_cli.py`

| 参数 | 说明 | 示例 |
|------|------|------|
| `-p`, `--pace` | 跑步配速（min/km） | `-p 5.5` |
| `-s`, `--speed` | 跑步速度（m/s） | `-s 3.33` |
| `-r`, `--route` | 路线名称 | `-r hust_campus` |
| `-l`, `--laps` | 跑几圈（0=自动满足 3.5km） | `-l 2` |
| `-t`, `--max-time` | 最长跑多久（秒） | `-t 1800` |
| `-y`, `--yes` | 跳过确认，直接运行 | `-y` |
| `--dry-run` | 仅预览轨迹 | `--dry-run` |
| `--list` | 列出所有路线 | `--list` |

> 如果同时指定 `--pace` 和 `--speed`，`--pace` 优先。

### 配速参考表

| 场景 | 配速 (min/km) | 速度 (m/s) | 2 圈用时 (~4.9km) |
|------|--------------|-----------|-------------------|
| 快跑 | 4:00 | 4.17 | ~20 分钟 |
| 偏快 | 4:30 | 3.70 | ~22 分钟 |
| 正常慢跑 | 5:00 | 3.33 | ~24 分钟 |
| 慢跑 | 6:00 | 2.78 | ~29 分钟 |
| 很慢 | 7:00 | 2.38 | ~34 分钟 |
| 快走 | 8:00 | 2.08 | ~39 分钟 |
| 散步 | 9:00 | 1.85 | ~44 分钟 |
| 极慢 | 10:00 | 1.67 | ~49 分钟 |

---

## 常见问题排查

### Q: `adb devices` 看不到设备

1. 检查 USB 线是否支持数据传输（换一根线试试）
2. 换一个电脑 USB 口（优先用机箱后面的口）
3. 检查手机 USB 调试开关是否打开
4. 手机重新插拔后注意看屏幕是否有授权弹窗
5. 在手机上撤销并重新授权：开发者选项 → 撤销 USB 调试授权

### Q: 运行脚本时报 "未找到 ADB"

说明 ADB 没有正确添加到 PATH。解决方法：
- 直接使用完整路径：`C:\platform-tools\adb.exe devices`
- 或重新执行第二步中的"添加到系统 PATH"操作，然后**重新打开 CMD 窗口**

### Q: Mock Location 设置失败

1. 确认开发者选项中 **USB 调试** 是开启状态
2. 确认手机上弹出的授权对话框点了"允许"
3. 尝试在开发者选项中手动找到"选择模拟位置信息应用"，看看是否有选项

### Q: 华中大体育 App 没有检测到位置变化

1. 确保在开跑前 App 已经打开了跑步页面
2. 确保手机没有同时打开其他需要定位的 App（如高德地图、百度地图）——它们会占用定位
3. 尝试关闭 App 的省电策略：设置 → 应用设置 → 华中大体育 → 省电策略 → 无限制
4. 关闭手机省电模式

### Q: 定位点不在华科校园？

默认路线坐标基于华科主校区。如果你的跑步路线要求不同的区域，可以自定义路线（见下文）。

### Q: 可以一边模拟跑步一边做其他事吗？

可以。模拟跑步期间你可以正常使用手机，GPS 模拟在后台运行。但不要在手机上打开地图 App 验证位置——这可能导致华中大体育 App 被挤掉 GPS 信号。

### Q: 是否支持 WiFi 连接（不用 USB）？

可以。先用 USB 连接一次，然后在 CMD 中输入：

```bash
adb tcpip 5555
```

之后拔掉 USB，用 WiFi 连接：

```bash
adb connect <手机IP地址>:5555
```

手机 IP 地址在：设置 → WiFi → 点击已连接的 WiFi → 查看 IP 地址。

但 USB 连接更稳定，**推荐始终使用 USB**。

---

## 自定义路线

你可以在 `routes/` 目录下创建自己的路线 JSON 文件。

### 格式说明

```json
{
  "name": "路线名称",
  "description": "路线描述",
  "loop": true,
  "waypoints": [
    {"name": "起点", "lat": 30.50880, "lng": 114.41150},
    {"name": "中途点1", "lat": 30.51020, "lng": 114.41280},
    {"name": "中途点2", "lat": 30.51180, "lng": 114.41550},
    {"name": "终点", "lat": 30.50950, "lng": 114.41100}
  ]
}
```

### 如何获取 GPS 坐标

1. 打开 https://lbs.amap.com/tools/picker （高德坐标拾取器）
2. 在地图上点击你要经过的位置点
3. 复制该点的经纬度坐标
4. 添加到 JSON 文件的 waypoints 数组中

### 使用自定义路线

假设你创建了 `routes/my_route.json`：

```bash
python run.py --route my_route
```

---

## 安全提醒

- 本工具仅供个人学习研究使用
- 请在规则允许的范围内合理使用
- 模拟速度已限制在 4:00-10:00 min/km 范围内，超出会被自动调整。更窄的安全区间建议 5:00-7:00（正常跑步速度），避免被后台异常检测识别
- 使用完毕后程序会自动清理 Mock GPS 环境，无需手动操作手机
