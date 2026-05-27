#!/usr/bin/env python3
"""
深度诊断：分析华中大体育 App 的定位逻辑链路
需要：手机通过 USB 连接，ADB 可用

用法：
  python analyze_app.py                # 自动搜包名 + 全面诊断
  python analyze_app.py --package <pkg> # 指定包名
  python analyze_app.py --live          # 实时监控定位请求（开跑后运行）
"""

import argparse
import html
import os
import subprocess
import sys
import time
from pathlib import Path
from xml.etree import ElementTree

# ── ADB 工具 ──────────────────────────────────────────────

ADB = "adb"


def find_adb():
    global ADB
    r = subprocess.run(["where", "adb"], capture_output=True, text=True, shell=True)
    if r.returncode == 0 and r.stdout.strip():
        return
    for d in [
        r"D:\Applications\platform-tools",
        r"C:\platform-tools",
        r"C:\adb",
        r"D:\adb",
    ]:
        p = Path(d) / "adb.exe"
        if p.is_file():
            ADB = str(p)
            return
    base = os.environ.get("LOCALAPPDATA", "")
    if base:
        p = Path(base) / "platform-tools" / "adb.exe"
        if p.is_file():
            ADB = str(p)
            return


def sh(*args):
    """执行 ADB 命令，返回 stdout"""
    r = subprocess.run([ADB] + list(args), capture_output=True, text=True,
                       encoding="utf-8", errors="replace")
    return r.stdout.strip(), r.stderr.strip(), r.returncode


def sh_ok(*args):
    """执行，返回是否成功"""
    _, _, rc = sh(*args)
    return rc == 0


# ── 包名搜索 ──────────────────────────────────────────────

# 常见高校跑步 App 的包名关键词
CANDIDATE_KEYWORDS = [
    "hust", "华中大", "华中科技", "huazhong",
    "sports", "体育", "running", "跑步",
    "campus", "校园", "exercise", "锻炼",
    "fitness", "健康", "health",
]


def find_package():
    """自动搜索可能的包名"""
    print("── 搜索候选包名 ──")

    # 方法1: 搜索已安装包名中包含关键词的
    out, _, _ = sh("shell", "pm", "list", "packages")
    all_packages = [l.replace("package:", "").strip() for l in out.split("\n") if l.strip()]

    candidates = []
    for pkg in all_packages:
        pkg_lower = pkg.lower()
        for kw in CANDIDATE_KEYWORDS:
            if kw.lower() in pkg_lower:
                candidates.append(pkg)
                break

    # 方法2: 用 dumpsys 找前台/最近运行过的 app
    out, _, _ = sh("shell", "dumpsys", "activity", "activities")
    # 从 topResumedActivity / realActivity 中提取包名
    for line in out.split("\n"):
        if "realActivity" in line or "topResumedActivity" in line:
            for token in line.split():
                if "/" in token and "." in token and not token.startswith("."):
                    pkg = token.split("/")[0].strip()
                    if pkg and pkg not in candidates:
                        candidates.append(pkg)

    # 方法3: 用 dumpsys 查看最近的任务栈
    out, _, _ = sh("shell", "dumpsys", "activity", "recents")
    for line in out.split("\n"):
        for token in line.split():
            if token.startswith("com.") or token.startswith("cn."):
                token = token.split("/")[0].strip()
                if token.count(".") >= 2 and token not in candidates:
                    candidates.append(token)

    if not candidates:
        print("  ⚠ 未自动找到，尝试常见命名模式...")
        for prefix in ["com", "cn"]:
            for kw in ["hust", "running", "sport", "health", "campus"]:
                pattern = f"{prefix}.{kw}"
                for pkg in all_packages:
                    if pattern in pkg.lower():
                        candidates.append(pkg)

    if not candidates:
        print("  ❌ 未能自动识别 App 包名")
        print("  请手动运行: adb shell pm list packages | findstr <关键词>")
        print("  然后: python analyze_app.py --package <包名>")
        sys.exit(1)

    # 去重 + 展示
    candidates = list(dict.fromkeys(candidates))
    print(f"  找到 {len(candidates)} 个候选:")
    for i, c in enumerate(candidates):
        # 获取 app label
        label = ""
        out, _, _ = sh("shell", "dumpsys", "package", c)
        for line in out.split("\n"):
            if "com.android.packageinstaller" not in line and "labelRes" in line:
                break
        print(f"  [{i + 1}] {c}")

    if len(candidates) == 1:
        return candidates[0]

    print()
    choice = input("选择序号 (默认 1): ").strip()
    try:
        idx = int(choice) - 1 if choice else 0
        return candidates[idx]
    except (ValueError, IndexError):
        return candidates[0]


# ── 详细诊断 ──────────────────────────────────────────────

def analyze_app(package):
    print()
    print("=" * 65)
    print(f"  定位逻辑深度分析: {package}")
    print("=" * 65)

    # ============================================================
    # 1. App 基本信息 + 权限清单
    # ============================================================
    print("\n── [1] App 基本信息 ──")
    out, _, _ = sh("shell", "dumpsys", "package", package)

    # 解析 version / targetSdk
    version_name = "?"
    target_sdk = "?"
    for line in out.split("\n"):
        if "versionName=" in line:
            version_name = line.split("versionName=")[1].split()[0].strip()
        if "targetSdk=" in line:
            target_sdk = line.split("targetSdk=")[1].split()[0].strip()

    print(f"  versionName: {version_name}")
    print(f"  targetSdk:   {target_sdk}")

    # 权限
    print("\n  位置相关权限:")
    location_perms = []
    for line in out.split("\n"):
        stripped = line.strip()
        for perm in ["ACCESS_FINE_LOCATION", "ACCESS_COARSE_LOCATION",
                     "ACCESS_BACKGROUND_LOCATION", "ACCESS_MOCK_LOCATION",
                     "LOCATION_HARDWARE", "HIGH_SAMPLING_RATE_SENSORS",
                     "ACTIVITY_RECOGNITION"]:
            if perm in stripped:
                location_perms.append(perm)

    for p in location_perms:
        print(f"    ✓ {p}")
    if not location_perms:
        print("    ⚠ 未声明标准位置权限（可能通过服务间接获取）")

    # ============================================================
    # 2. ContentProvider 分析 (是否有自定义定位 Provider)
    # ============================================================
    print("\n── [2] ContentProvider / 自定义组件 ──")
    providers = []
    in_provider = False
    for line in out.split("\n"):
        if "Provider{" in line:
            in_provider = True
            providers.append(line.strip())
        elif in_provider and "}" in line:
            in_provider = False
    if providers:
        for prov in providers[:10]:
            print(f"    {prov[:120]}")
    else:
        print("    (无自定义 Provider)")

    # ============================================================
    # 3. dumpsys location — 核心：当前谁在请求定位？
    # ============================================================
    print("\n── [3] 系统定位服务状态 (dumpsys location) ──")

    loc_out, _, _ = sh("shell", "dumpsys", "location")

    # 提取 activity 报告
    # HyperOS 用不同的 location stack，dumpsys location 可能较短
    print(f"    输出长度: {len(loc_out)} 字符")

    # 找 LocationManagerService 中的注册信息
    for section in ["Registered", "register", "receivers", "listeners",
                    "Location Request", "requested", "provider", "Client"]:
        found = False
        for line in loc_out.split("\n"):
            if section.lower() in line.lower().strip()[:30]:
                if not found:
                    print(f"  --- 含 '{section}' 的行 ---")
                    found = True
                print(f"    {line.strip()[:130]}")

    # 完整 dump providers 部分
    print("\n  --- 当前 Provider 状态 ---")
    for provider in ["gps", "network", "fused", "passive"]:
        grep_out, _, _ = sh("shell", "dumpsys", "location", "--", provider)
        if grep_out and "No such" not in grep_out:
            print(f"  [{provider}]")
            for line in grep_out.split("\n")[:15]:
                print(f"    {line.strip()[:130]}")

    # ============================================================
    # 4. Google Play Services / Fused Location
    # ============================================================
    print("\n── [4] Fused Location Provider (GMS) ──")
    gms_out, _, _ = sh("shell", "dumpsys", "location", "--", "fused")
    if "No such" in gms_out or not gms_out:
        print("    fused provider 不可用 (非 GMS 设备或未启用)")
    else:
        for line in gms_out.split("\n")[:20]:
            print(f"    {line.strip()[:130]}")

    # GMS 相关服务
    print("\n  GMS 定位服务:")
    for svc in ["com.google.android.gms", "com.google.android.location"]:
        svc_out, _, _ = sh("shell", "dumpsys", "activity", "services", svc)
        if svc_out and len(svc_out) > 50:
            print(f"    ✓ {svc} 存在 ({len(svc_out)} 字符)")
        else:
            print(f"    ✗ {svc} 不存在或未运行")

    # ============================================================
    # 5. App 的定位调用方式判断
    # ============================================================
    print("\n── [5] 定位 SDK 调用链推断 ──")

    # 看 dumpsys package 中的 uses-library / meta-data
    for line in out.split("\n"):
        if any(k in line.lower() for k in ["amap", "高德", "baidu", "百度",
                                              "tencent", "腾讯", "googlemap",
                                              "location", "lbs"]):
            print(f"    {line.strip()[:130]}")

    # 检查 APK 中包含的 SDK (搜索 so 库)
    print("\n  Native 库 (.so):")
    app_path = ""
    for line in out.split("\n"):
        if "codePath=" in line:
            app_path = line.split("codePath=")[1].split()[0].strip()
            break

    if app_path:
        lib_out, _, _ = sh("shell", "find", app_path + "/lib", "-name", "*.so", "-type", "f")
        libs = [l.strip() for l in lib_out.split("\n") if l.strip()]
        # 只展示定位相关的
        location_libs = [l for l in libs if any(k in l.lower()
                         for k in ["locat", "lbs", "map", "gnss", "gps", "navigat", "geo"])]
        if location_libs:
            for lib in location_libs:
                print(f"    {Path(lib).name}")
        else:
            print(f"    ({len(libs)} 个 .so 文件，无显然的定位相关库名)")
    else:
        print("    无法获取 APK 路径")

    # ============================================================
    # 6. 反 Mock 检测机制分析
    # ============================================================
    print("\n── [6] 反 Mock 检测线索 ──")

    # 6a. 检查 App 是否调用了 isFromMockProvider()
    for line in loc_out.split("\n"):
        if "mock" in line.lower() and len(line.strip()) > 10:
            print(f"    dumpsys: {line.strip()[:130]}")

    # 6b. 检查是否有多余的 provider 注册
    providers_out, _, _ = sh("shell", "cmd", "location", "providers",
                              "get-test-provider-location", "gps")
    print(f"    gps test-provider 当前值: {providers_out[:100]}")

    # 6c. 检查开发者选项中「选择模拟位置信息应用」
    mock_app, _, _ = sh("shell", "settings", "get", "secure",
                        "mock_location_app")
    print(f"    mock_location_app 系统设置: {mock_app}")

    # 6d. 查看是否 App 直接读 GNSS (绕过 Android LocationManager)
    #    如果有 android.hardware.location 权限则属此类
    for line in out.split("\n"):
        if "LOCATION_HARDWARE" in line:
            print(f"    ⚠ 检测到 LOCATION_HARDWARE 权限 — App 可能直接访问 GNSS 硬件!")

    # ============================================================
    # 7. 网络请求 — App 是否有服务端位置校验
    # ============================================================
    print("\n── [7] 运行时网络 + 缓存检查 ──")

    # 检查 App 数据目录中的 shared_prefs (可能存位置信息)
    data_dir = ""
    for line in out.split("\n"):
        if "dataDir=" in line:
            data_dir = line.split("dataDir=")[1].split()[0].strip()
            break

    if data_dir:
        pref_out, _, _ = sh("shell", "ls", "-la", data_dir + "/shared_prefs")
        if pref_out and "No such" not in pref_out:
            print(f"    SharedPrefs 文件:")
            for line in pref_out.split("\n")[:20]:
                print(f"      {line.strip()[:130]}")
        else:
            print(f"    (无 shared_prefs 目录或不可读)")

        # 数据库文件
        db_out, _, _ = sh("shell", "ls", "-la", data_dir + "/databases")
        if db_out and "No such" not in db_out:
            print(f"    Databases:")
            for line in db_out.split("\n")[:10]:
                print(f"      {line.strip()[:130]}")

    print()
    print("=" * 65)
    print("  诊断完成。接下来:")
    print("  1. python analyze_app.py --live  → 实时监控定位调用")
    print("  2. 打开华中大体育 App，进入跑步页面，观察 logcat 输出")
    print("=" * 65)


# ── 实时监控模式 ──────────────────────────────────────────

def live_monitor(package=None):
    """实时监控 App 的定位调用"""
    print("实时监控定位调用 (Ctrl+C 退出)")
    print("请打开华中大体育 App → 进入跑步页面")
    print()

    # 清空 logcat 缓冲区
    sh("logcat", "-c")

    # 构建过滤条件
    filter_spec = "LocationManager:GpsStatusListener:GnssLocationProvider:*"

    print("开始捕获...")
    print("-" * 60)

    try:
        proc = subprocess.Popen(
            [ADB, "logcat", "-v", "time"],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            encoding="utf-8",
            errors="replace",
        )

        keywords = [
            "location", "Location", "LOCATION",
            "gps", "GPS", "Gnss", "GNSS",
            "mock", "Mock", "MOCK",
            "provider", "Provider",
            "fused", "FusedLocation",
            "lat", "lng", "LatLng",
            "高德", "百度", "腾讯",
            "AMap", "Baidu", "Tencent",
            "amap", "baidu", "tencent",
            "hust", "sport", "running",
        ]
        if package:
            keywords.insert(0, package)

        for line in proc.stdout:
            line = line.strip()
            if not line:
                continue
            for kw in keywords:
                if kw in line:
                    print(line[:200])
                    break

    except KeyboardInterrupt:
        print("\n已停止")
        proc.terminate()


# ── 入口 ──────────────────────────────────────────────────

def main():
    p = argparse.ArgumentParser(description="深度分析华中大体育 App 定位逻辑")
    p.add_argument("--package", help="App 包名（自动检测如不指定）")
    p.add_argument("--live", action="store_true", help="实时监控定位调用")
    p.add_argument("--list-packages", action="store_true",
                   help="列出所有可能相关的包")
    args = p.parse_args()

    find_adb()

    # 验证 ADB + 设备
    if not sh_ok("version"):
        print("[ERROR] ADB 不可用")
        sys.exit(1)

    out, _, _ = sh("devices")
    if len([l for l in out.split("\n") if "\tdevice" in l]) == 0:
        print("[ERROR] 未检测到已连接的设备")
        sys.exit(1)

    if args.list_packages:
        out, _, _ = sh("shell", "pm", "list", "packages")
        for line in out.split("\n"):
            pkg = line.replace("package:", "").strip()
            if pkg:
                for kw in CANDIDATE_KEYWORDS:
                    if kw.lower() in pkg.lower():
                        print(f"  {pkg}")
                        break
        return

    pkg = args.package or find_package()
    print(f"\n目标包名: {pkg}")

    if args.live:
        live_monitor(pkg)
    else:
        analyze_app(pkg)


if __name__ == "__main__":
    main()
