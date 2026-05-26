#!/usr/bin/env python3
"""
华中大体育 GPS 跑步模拟器 — 纯命令行模式
零第三方依赖，适合 SSH 远程操作 / headless 服务器

用法:
  python run_cli.py                          # 默认配速 5:00, 跑 1 圈 (~2.4km)
  python run_cli.py -p 6.5                   # 配速 6:30 min/km
  python run_cli.py -p 5.0 -l 2              # 配速 5:00, 跑 2 圈
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

# ── 工具函数 ────────────────────────────────────────────

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
    sec = 1000 / mps
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


# ── ADB 操作 ─────────────────────────────────────────────

def adb(*args):
    return subprocess.run(["adb"] + list(args), capture_output=True, text=True)


def adb_setup():
    print("[*] 配置 Mock GPS 环境...")
    adb("shell", "appops", "set", "com.android.shell",
        "android:mock_location", "allow")
    adb("shell", "cmd", "location", "providers", "remove-test-provider", "gps")
    r = adb("shell", "cmd", "location", "providers", "add-test-provider", "gps")
    if r.returncode != 0:
        print(f"[ERROR] 无法添加 test provider:\n{r.stderr}")
        print("[*] 请在手机 开发者选项 中确认 USB 调试已开启")
        sys.exit(1)
    print("[OK] Mock GPS 环境就绪")


def adb_send(lat, lng):
    adb("shell", "cmd", "location", "providers",
        "set-test-provider-location", "gps", "--location", f"{lat},{lng}")


def adb_teardown():
    print("\n[*] 清理 Mock GPS 环境...")
    adb("shell", "cmd", "location", "providers", "remove-test-provider", "gps")
    print("[OK] 清理完成")


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
    if adb("version").returncode != 0:
        print("[ERROR] 未找到 ADB，请先安装 Android SDK Platform Tools 并加入 PATH")
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
        d = route_distance(data["waypoints"])
        print(f"  {f.stem:20s}  {len(data['waypoints']):2d} 点  "
              f"~{fmt_dist(d):>8s}  {data.get('description', '')}")


# ── 入口 ────────────────────────────────────────────────

def main():
    p = argparse.ArgumentParser(
        description="华中大体育 GPS 跑步模拟器 (纯 CLI)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  python run_cli.py                       默认配速 5min/km, 跑 1 圈
  python run_cli.py -p 6.5                配速 6:30
  python run_cli.py -p 5.0 -l 2           配速 5:00, 跑 2 圈
  python run_cli.py -p 4.5 -t 1800        配速 4:30, 最多 30 分钟
  python run_cli.py -s 2.78               速度 2.78 m/s
  python run_cli.py --dry-run             仅预览
  python run_cli.py --list                列出路线
        """,
    )
    p.add_argument("-p", "--pace", type=float,
                   help="配速 (min/km), 如 5.0 = 5分/km")
    p.add_argument("-s", "--speed", type=float,
                   help="速度 (m/s), 如 3.33 (仅未指定 -p 时生效)")
    p.add_argument("-r", "--route", default="hust_campus",
                   help="路线名称 (默认 hust_campus)")
    p.add_argument("-l", "--laps", type=int, default=1,
                   help="圈数 (默认 1)")
    p.add_argument("-t", "--max-time", type=int, default=0,
                   help="最长跑步时间 秒 (0=不限)")
    p.add_argument("--dry-run", action="store_true",
                   help="仅预览轨迹")
    p.add_argument("--list", action="store_true",
                   help="列出所有可用路线")

    args = p.parse_args()

    if args.list:
        cmd_list()
        return

    # 速度: --pace 优先, 否则用 --speed, 再否则默认 pace=5.0
    pace_used = "--pace" in sys.argv or "-p" in sys.argv
    speed_used = "--speed" in sys.argv or "-s" in sys.argv

    if args.pace is not None and pace_used:
        args.speed = 1000 / (args.pace * 60)
    elif args.speed is not None and speed_used:
        args.speed = args.speed  # 保持不变
    else:
        args.speed = 1000 / (5.0 * 60)  # 默认 5:00 配速

    if args.dry_run:
        cmd_dry_run(args)
    else:
        cmd_live(args)


if __name__ == "__main__":
    main()
