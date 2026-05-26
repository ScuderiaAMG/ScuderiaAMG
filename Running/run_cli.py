#!/usr/bin/env python3
"""
华中大体育 GPS 跑步模拟器 — 纯命令行模式
零第三方依赖，适合 SSH 远程操作 / headless 服务器

约束: 每次最少 3.5 km, 配速 4:00-10:00 min/km

用法:
  python run_cli.py                          # 默认配速 5:00, 自动圈数(>=3.5km)
  python run_cli.py -p 6.5                   # 配速 6:30 min/km
  python run_cli.py -p 5.0 -l 2              # 配速 5:00, 指定跑 2 圈
  python run_cli.py -p 4.5 -t 1800           # 配速 4:30, 最多跑 30 分钟
  python run_cli.py -s 3.33                  # 直接用速度 (m/s) 控制
  python run_cli.py --dry-run                # 仅预览轨迹, 不连设备
  python run_cli.py --list                   # 列出可用路线
"""

import argparse
import json
import math
import random
import signal
import subprocess
import sys
import time
from pathlib import Path

# ── 约束常量 ────────────────────────────────────────────

MIN_DISTANCE_M = 3500       # 每次最少 3.5 km
MIN_PACE = 4.0              # 最快配速 4:00 min/km
MAX_PACE = 10.0             # 最慢配速 10:00 min/km

# ── 工具函数 ────────────────────────────────────────────

def clamp_pace(pace):
    return max(MIN_PACE, min(MAX_PACE, pace))


def min_laps_for_distance(wps):
    dist = route_distance(wps)
    if dist <= 0:
        return 1
    return max(1, int(MIN_DISTANCE_M / dist + 0.999))

def haversine(lat1, lng1, lat2, lng2):
    R = 6371000
    dlat = math.radians(lat2 - lat1)
    dlng = math.radians(lng2 - lng1)
    a = (math.sin(dlat / 2) ** 2 +
         math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) *
         math.sin(dlng / 2) ** 2)
    return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))


def fmt_pace(mps):
    if mps <= 0:
        return "--:--"
    sec = round(1000 / mps)
    return f"{int(sec // 60)}:{int(sec % 60):02d}"


def fmt_dist(m):
    return f"{m / 1000:.2f} km" if m >= 1000 else f"{m:.0f} m"


def fmt_time(s):
    h = int(s // 3600)
    m = int((s % 3600) // 60)
    sec = int(s % 60)
    return f"{h:02d}:{m:02d}:{sec:02d}" if h else f"{m:02d}:{sec:02d}"


# ── 路线 ────────────────────────────────────────────────

def load_route(name):
    path = Path(__file__).parent / "routes" / f"{name}.json"
    if not path.exists():
        print(f"[ERROR] 路线文件不存在: {path}")
        sys.exit(1)
    return json.loads(path.read_text(encoding="utf-8"))


def route_distance(wps):
    total = 0.0
    for i in range(len(wps)):
        p1, p2 = wps[i], wps[(i + 1) % len(wps)]
        total += haversine(p1["lat"], p1["lng"], p2["lat"], p2["lng"])
    return total


# ── 轨迹生成 ─────────────────────────────────────────────

JITTER = 0.00001


def generate_trajectory(waypoints, speed_mps, interval, lap_count, max_duration_s):
    step_dist = speed_mps * interval
    all_coords = []

    for _ in range(lap_count):
        for i in range(len(waypoints)):
            p1 = waypoints[i]
            p2 = waypoints[(i + 1) % len(waypoints)]
            dist = haversine(p1["lat"], p1["lng"], p2["lat"], p2["lng"])
            steps = max(1, int(dist / step_dist))
            for s in range(steps):
                t = s / steps
                all_coords.append((
                    p1["lat"] + (p2["lat"] - p1["lat"]) * t,
                    p1["lng"] + (p2["lng"] - p1["lng"]) * t,
                ))

    if max_duration_s:
        all_coords = all_coords[:int(max_duration_s / interval)]
    return all_coords


# ── GPX 导出 ─────────────────────────────────────────────

def export_gpx(coords, speed_mps, output_path):
    import zipfile
    from datetime import datetime, timedelta, timezone
    tz_utc = timezone.utc
    start = datetime.now(tz_utc).replace(microsecond=0)

    lines = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        '<gpx version="1.1" creator="HUST-Runner"',
        '     xmlns="http://www.topografix.com/GPX/1/1">',
        '  <trk>',
        '    <name>HUST Running</name>',
        '    <trkseg>',
    ]
    for i, (lat, lng) in enumerate(coords):
        t = (start + timedelta(seconds=i)).isoformat()
        lines.append(f'      <trkpt lat="{lat:.8f}" lon="{lng:.8f}">')
        lines.append(f'        <ele>0</ele>')
        lines.append(f'        <time>{t}</time>')
        lines.append(f'      </trkpt>')
    lines.append('    </trkseg>')
    lines.append('  </trk>')
    lines.append('</gpx>')

    gpx_content = "\n".join(lines)

    out_path = Path(output_path)
    if out_path.suffix == '.gpx':
        zip_path = out_path.with_suffix('.zip')
    elif out_path.suffix != '.zip':
        zip_path = out_path.with_suffix('.zip')
    else:
        zip_path = out_path

    gpx_name = out_path.stem + ".gpx"
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zf:
        zf.writestr(gpx_name, gpx_content)

    return str(zip_path)


# ── ADB 操作 ─────────────────────────────────────────────

_ADB_COMMON_DIRS = [
    r"D:\Applications\platform-tools",
    r"C:\platform-tools",
    r"C:\adb",
    r"D:\adb",
]

_ADB_PATH = "adb"


def _find_adb():
    global _ADB_PATH
    # 先试 PATH
    r = subprocess.run(["where", "adb"], capture_output=True, text=True, shell=True)
    if r.returncode == 0 and r.stdout.strip():
        _ADB_PATH = "adb"
        return

    # 搜索常见目录
    for d in _ADB_COMMON_DIRS:
        p = Path(d) / "adb.exe"
        if p.is_file():
            _ADB_PATH = str(p)
            return

    # 搜索 LOCALAPPDATA
    base = os.environ.get("LOCALAPPDATA", "")
    if base:
        p = Path(base) / "platform-tools" / "adb.exe"
        if p.is_file():
            _ADB_PATH = str(p)
            return


def adb(*args):
    return subprocess.run([_ADB_PATH] + list(args), capture_output=True, text=True,
                          encoding="utf-8", errors="replace")



def adb_setup():
    print("[*] 配置 Mock GPS 环境...")

    # 1. 系统级 mock 开关
    before = adb("shell", "settings", "get", "secure", "mock_location").stdout.strip()
    if before == "0":
        print("[*] secure.mock_location=0, 正在设为 1...")
        adb("shell", "settings", "put", "secure", "mock_location", "1")

    # 2. Shell 权限
    adb("shell", "appops", "set", "com.android.shell",
        "android:mock_location", "allow")

    # 3. 强制开 GPS
    adb("shell", "settings", "put", "secure", "location_mode", "3")

    # 4. 启用定位服务
    adb("shell", "cmd", "location", "set-location-enabled", "true")

    # 5. 重建 gps + network 双 provider
    for p in ["gps", "network"]:
        adb("shell", "cmd", "location", "providers", "remove-test-provider", p)

    r_gps = adb("shell", "cmd", "location", "providers", "add-test-provider", "gps")
    r_net = adb("shell", "cmd", "location", "providers", "add-test-provider", "network")
    if r_gps.returncode != 0 and r_net.returncode != 0:
        err = (r_gps.stderr or r_gps.stdout or "").strip()
        print(f"[ERROR] 无法添加 test provider: {err}")
        print("[*] 该设备可能不支持 cmd location test provider")
        sys.exit(1)

    # 6. 启用
    for p in ["gps", "network"]:
        adb("shell", "cmd", "location", "providers",
            "set-test-provider-enabled", p, "true")

    # 7. 初始定位 + 验证
    adb("shell", "cmd", "location", "providers",
        "set-test-provider-location", "gps",
        "--location", "30.508800,114.411500",
        "--accuracy", "5")
    adb("shell", "cmd", "location", "providers",
        "set-test-provider-location", "network",
        "--location", "30.508800,114.411500",
        "--accuracy", "5")

    verify = adb("shell", "cmd", "location", "providers",
                  "get-test-provider-location", "gps")
    if "30.508" in verify.stdout and "114.411" in verify.stdout:
        print("[OK] Mock GPS 环境就绪（gps 已验证）")
    else:
        print("[OK] Mock GPS 环境就绪")
        print(f"    gps 回读: {verify.stdout.strip()[:120]}")


def adb_send(lat, lng):
    for p in ["gps", "network"]:
        adb("shell", "cmd", "location", "providers",
            "set-test-provider-location", p,
            "--location", f"{lat},{lng}",
            "--accuracy", "5")


def adb_teardown():
    print("\n[*] 清理 Mock GPS 环境...")
    for provider in ["gps", "network"]:
        adb("shell", "cmd", "location", "providers",
            "set-test-provider-enabled", provider, "false")
        adb("shell", "cmd", "location", "providers",
            "remove-test-provider", provider)
    print("[OK] 清理完成")


# ── 模式: diagnose ─────────────────────────────────────

def cmd_diagnose():
    print("=" * 60)
    print("  定位诊断报告")
    print("=" * 60)

    # 设备信息
    print("\n── 设备信息 ──")
    for prop in ["ro.product.brand", "ro.product.model", "ro.build.version.release"]:
        r = adb("shell", "getprop", prop)
        print(f"  {prop.rsplit('.',1)[-1]}: {r.stdout.strip()}")

    # Mock 权限
    print("\n── Mock 权限 ──")
    for perm in ["mock_location"]:
        r = adb("shell", "appops", "get", "com.android.shell",
                f"android:{perm}")
        print(f"  shell {perm}: {r.stdout.strip()}")

    r = adb("shell", "settings", "get", "secure", "mock_location")
    print(f"  secure.mock_location: {r.stdout.strip()}")

    # GPS 状态
    print("\n── GPS / 定位状态 ──")
    mode = adb("shell", "settings", "get", "secure", "location_mode").stdout.strip()
    mode_map = {"0": "关闭", "1": "仅GPS", "2": "仅网络", "3": "高精度"}
    print(f"  location_mode: {mode} ({mode_map.get(mode, '未知')})")

    for provider in ["gps", "network"]:
        pos = adb("shell", "cmd", "location", "providers",
                   "get-test-provider-location", provider)
        print(f"  test-{provider}: {pos.stdout.strip()[:120]}")

    print("\n── 诊断结论 ──")
    if mode == "0":
        print("  ⚠ GPS 处于关闭状态！请手动打开手机 GPS")
    pos_gps = adb("shell", "cmd", "location", "providers",
                   "get-test-provider-location", "gps").stdout.strip()
    if "null" in pos_gps.lower() or not pos_gps:
        print("  ⚠ gps test provider 未设置有效位置")
    else:
        print(f"  ✓ gps test provider 坐标已注入: {pos_gps[:80]}")
        print("  → 若 App 里程仍不增加，需换用 Mock GPS App（参考 README）")
    print("=" * 60)


# ── 模式: dry-run ───────────────────────────────────────

def cmd_dry_run(args):
    data = load_route(args.route)
    wps = data["waypoints"]
    speed = args.speed
    dist = route_distance(wps)
    coords = generate_trajectory(wps, speed, 1.0, args.laps, args.max_time)

    print("=" * 55)
    print("  Dry-Run 模式 — 仅预览，不连接设备")
    print("=" * 55)
    print(f"  路线:    {data['name']} — {data.get('description', '')}")
    print(f"  航点:    {len(wps)} 个  |  环路: {'是' if data.get('loop', True) else '否'}"
          f"  |  单圈: ~{fmt_dist(dist)}")
    print(f"  配速:    {fmt_pace(speed)} min/km  |  速度: {speed:.2f} m/s")
    print(f"  圈数:    {args.laps}  |  模拟距离: ~{fmt_dist(len(coords) * speed)}")
    print(f"  坐标点:  {len(coords)}  |  预计用时: {fmt_time(len(coords))}")
    print()
    print(f"  坐标预览（前 5 + 后 3）:")
    print(f"  {'#':>5s}  {'纬度':>12s}  {'经度':>12s}")
    print(f"  {'-'*5}  {'-'*12}  {'-'*12}")
    for i, c in enumerate(coords[:5]):
        print(f"  {i + 1:>5d}  {c[0]:>12.6f}  {c[1]:>12.6f}")
    if len(coords) > 8:
        print(f"  {'...':>5s}  {'...':>12s}  {'...':>12s}")
        for i in range(len(coords) - 3, len(coords)):
            print(f"  {i + 1:>5d}  {coords[i][0]:>12.6f}  {coords[i][1]:>12.6f}")
    print(f"\n[OK] 轨迹生成正常，共 {len(coords)} 个坐标点")


# ── 模式: live ──────────────────────────────────────────

def cmd_live(args):
    # 检查 ADB
    _find_adb()
    if adb("version").returncode != 0:
        print("[ERROR] 未找到 ADB，请先安装 Android SDK Platform Tools 并加入 PATH")
        print("  如果已安装但此处找不到，请尝试：")
        print("  1. 重新打开终端（PATH 变更后需重启终端）")
        print(f"  2. 或将 adb.exe 放到: {_ADB_COMMON_DIRS[0]}")
        for d in _ADB_COMMON_DIRS[1:]:
            print(f"     {d}")
        sys.exit(1)

    # 检查设备
    r = adb("devices")
    lines = [l for l in r.stdout.strip().split("\n")[1:] if "\tdevice" in l]
    if not lines:
        print("[ERROR] 未检测到已连接的设备")
        print("  1. USB 线连接手机和电脑")
        print("  2. 手机上开启 USB 调试")
        print("  3. 手机上点「允许」USB 调试授权")
        sys.exit(1)
    device = lines[0].split("\t")[0]
    print(f"[OK] 已连接设备: {device}")

    # 加载路线 & 生成轨迹
    data = load_route(args.route)
    wps = data["waypoints"]
    speed = args.speed
    dist = route_distance(wps)
    coords = generate_trajectory(wps, speed, 1.0, args.laps, args.max_time)

    print("=" * 55)
    print(f"  路线:    {data['name']} — {data.get('description', '')}")
    print(f"  总距离:  {fmt_dist(dist * args.laps)}  |  圈数: {args.laps}")
    print(f"  配速:    {fmt_pace(speed)} min/km ({speed:.2f} m/s)")
    print(f"  预计:    {fmt_time(len(coords))}  |  {len(coords)} 个坐标点")
    print("=" * 55)

    if not args.yes:
        resp = input("\n开始模拟? [Y/n]: ").strip().lower()
        if resp and resp != 'y':
            print("取消")
            return

    adb_setup()

    print()
    print("=" * 55)
    print("  跑步进行中...  按 Ctrl+C 停止")
    print("=" * 55)
    print()

    start = time.time()
    dist_done = 0.0
    prev = None
    stopped = False

    def on_sigint(sig, frame):
        nonlocal stopped
        stopped = True
    signal.signal(signal.SIGINT, on_sigint)

    try:
        for i, (lat, lng) in enumerate(coords):
            if stopped:
                break

            lat_j = lat + random.uniform(-JITTER, JITTER)
            lng_j = lng + random.uniform(-JITTER, JITTER)

            if prev:
                dist_done += haversine(prev[0], prev[1], lat, lng)
            prev = (lat, lng)

            adb_send(lat_j, lng_j)

            elapsed = time.time() - start
            pct = (i + 1) / len(coords) * 100
            cur_pace = (elapsed / 60) / (dist_done / 1000) if dist_done > 0 else 0

            if (i + 1) % 10 == 0 or i == 0:
                bar_w = 25
                filled = int(bar_w * (i + 1) / len(coords))
                bar = "|" + "#" * filled + "-" * (bar_w - filled) + "|"
                line = (f"\r{bar} {pct:5.1f}%  "
                        f"├ {fmt_dist(dist_done)}  "
                        f"├ {fmt_time(elapsed)}  "
                        f"├ {fmt_pace(cur_pace * 60)}/km  "
                        f"├ ({lat_j:.5f},{lng_j:.5f})")
                sys.stdout.write(line)
                sys.stdout.flush()

            time.sleep(1.0)

        sys.stdout.write("\n")

    except KeyboardInterrupt:
        pass
    finally:
        adb_teardown()
        elapsed = time.time() - start
        print(f"\n[DONE] 用时: {fmt_time(elapsed)}  |  距离: {fmt_dist(dist_done)}")


# ── 模式: list ──────────────────────────────────────────

def cmd_list():
    routes_dir = Path(__file__).parent / "routes"
    for f in sorted(routes_dir.glob("*.json")):
        data = json.loads(f.read_text(encoding="utf-8"))
        wps = data["waypoints"]
        d = route_distance(wps)
        min_laps = min_laps_for_distance(wps)
        print(f"  {f.stem:20s}  {len(wps):2d} 点  "
              f"~{fmt_dist(d):>8s}/圈  最少 {min_laps} 圈 (>= {fmt_dist(MIN_DISTANCE_M)})  "
              f"{data.get('description', '')}")


# ── 入口 ────────────────────────────────────────────────

def main():
    p = argparse.ArgumentParser(
        description="华中大体育 GPS 跑步模拟器 (纯 CLI)\n约束: 每次最少 3.5km, 配速 4:00-10:00 min/km",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  python run_cli.py                       默认配速 5:00, 自动圈数(>=3.5km)
  python run_cli.py -p 6.5                配速 6:30
  python run_cli.py -p 5.0 -l 2           配速 5:00, 指定跑 2 圈
  python run_cli.py -p 4.5 -t 1800        配速 4:30, 最多 30 分钟
  python run_cli.py -s 2.78               速度 2.78 m/s
  python run_cli.py --dry-run             仅预览
  python run_cli.py --list                列出路线
        """,
    )
    p.add_argument("-p", "--pace", type=float,
                   help=f"配速 (min/km), 范围 {MIN_PACE:.0f}-{MAX_PACE:.0f}")
    p.add_argument("-s", "--speed", type=float,
                   help="速度 (m/s), 如 3.33 (仅未指定 -p 时生效)")
    p.add_argument("-r", "--route", default="hust_campus",
                   help="路线名称 (默认 hust_campus)")
    p.add_argument("-l", "--laps", type=int, default=0,
                   help="圈数 (0=自动满足最低 3.5km)")
    p.add_argument("-t", "--max-time", type=int, default=0,
                   help="最长跑步时间 秒 (0=不限)")
    p.add_argument("--dry-run", action="store_true",
                   help="仅预览轨迹")
    p.add_argument("-y", "--yes", action="store_true",
                   help="跳过开始确认，直接运行")
    p.add_argument("--list", action="store_true",
                   help="列出所有可用路线")
    p.add_argument("--diagnose", action="store_true",
                   help="诊断手机定位状态")
    p.add_argument("--gpx", type=str, default=None,
                   help="导出 GPX 到 ZIP 包，例如 --gpx route")

    args = p.parse_args()

    if args.diagnose:
        _find_adb()
        if adb("version").returncode != 0:
            print("[ERROR] 未找到 ADB")
            sys.exit(1)
        r = adb("devices")
        lines = [l for l in r.stdout.strip().split("\n")[1:] if "\tdevice" in l]
        if not lines:
            print("[ERROR] 未检测到设备")
            sys.exit(1)
        cmd_diagnose()
        return

    if args.list:
        cmd_list()
        return

    # 配速: --pace > --speed > 默认 5:00, 限幅到 [MIN_PACE, MAX_PACE]
    pace_used = "--pace" in sys.argv or "-p" in sys.argv
    speed_used = "--speed" in sys.argv or "-s" in sys.argv

    if args.pace is not None and pace_used:
        if args.pace < MIN_PACE or args.pace > MAX_PACE:
            print(f"[WARN] 配速 {args.pace:.1f} 超出范围，已调整为 {clamp_pace(args.pace):.1f}")
        args.speed = 1000 / (clamp_pace(args.pace) * 60)
    elif args.speed is not None and speed_used:
        pace_val = (1000 / args.speed) / 60
        if pace_val < MIN_PACE or pace_val > MAX_PACE:
            print(f"[WARN] 速度对应配速 {pace_val:.1f} 超出范围，已调整")
            pace_val = clamp_pace(pace_val)
            args.speed = 1000 / (pace_val * 60)
    else:
        args.speed = 1000 / (5.0 * 60)

    # 圈数: 自动计算或校验满足 3.5km
    data = load_route(args.route)
    wps = data["waypoints"]
    min_laps = min_laps_for_distance(wps)
    if args.laps <= 0:
        args.laps = min_laps
        print(f"[INFO] 自动设置圈数: {min_laps} (满足最低 {fmt_dist(MIN_DISTANCE_M)})")
    elif args.laps < min_laps:
        print(f"[WARN] {args.laps} 圈不足 {fmt_dist(MIN_DISTANCE_M)}，已调整为 {min_laps} 圈")
        args.laps = min_laps

    if args.gpx:
        wps = data["waypoints"]
        speed = args.speed
        coords = generate_trajectory(wps, speed, 1.0, args.laps, args.max_time)
        zip_path = export_gpx(coords, speed, args.gpx)
        total_dist = len(coords) * speed
        print(f"[OK] GPX 已打包导出: {zip_path}")
        print(f"     坐标点: {len(coords)}  |  距离: ~{fmt_dist(total_dist)}  |  "
              f"用时: {fmt_time(len(coords))}")
        print(f"     传到手机后解压，用 Mock GPS App 导入 GPX")
        return

    if args.dry_run:
        cmd_dry_run(args)
    else:
        cmd_live(args)


if __name__ == "__main__":
    main()
