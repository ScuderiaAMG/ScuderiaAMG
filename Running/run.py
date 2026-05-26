import sys
import time
import signal
from pathlib import Path

import click
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TimeElapsedColumn
from rich.live import Live
from rich.layout import Layout
from rich.text import Text

sys.path.insert(0, str(Path(__file__).parent))

from core.models import RunConfig
from core.route_engine import (
    load_route,
    route_total_distance,
    RunSimulator,
    haversine,
    MIN_PACE,
    MAX_PACE,
    MIN_DISTANCE_M,
    clamp_pace,
    min_laps_for_distance,
)
from core.adb_controller import ADBController

console = Console()


def format_pace(mps: float) -> str:
    if mps <= 0:
        return "--:--"
    sec_per_km = round(1000 / mps)
    minutes = int(sec_per_km // 60)
    seconds = int(sec_per_km % 60)
    return f"{minutes}:{seconds:02d}"


def format_distance(meters: float) -> str:
    if meters >= 1000:
        return f"{meters / 1000:.2f} km"
    return f"{meters:.0f} m"


def format_duration(seconds: float) -> str:
    h = int(seconds // 3600)
    m = int((seconds % 3600) // 60)
    s = int(seconds % 60)
    if h > 0:
        return f"{h:02d}:{m:02d}:{s:02d}"
    return f"{m:02d}:{s:02d}"


def build_info_panel(config_info: dict) -> Panel:
    table = Table(show_header=False, box=None, padding=(0, 1))
    table.add_column("key", style="dim")
    table.add_column("value", style="bold")
    for k, v in config_info.items():
        table.add_row(k, str(v))
    return Panel(table, title="🚀 跑步模拟", border_style="green")


def do_dry_run(config: RunConfig):
    console.print("[bold cyan]🔍 Dry-Run 模式 — 仅预览轨迹，不连接设备[/]\n")

    route = load_route(config.route_name)
    simulator = RunSimulator(route, config.speed_mps,
                             config.update_interval, config.jitter)
    coords = simulator.generate_trajectory(config.lap_count, config.max_duration_s)
    total_dist = len(coords) * config.speed_mps * config.update_interval

    console.print(f"[dim]路线: {route.name} — {route.description}[/]")
    console.print(f"[dim]航点数: {len(route.waypoints)}  |  "
                  f"环路: {'是' if route.loop else '否'}[/]")
    console.print(f"[dim]配速: {format_pace(config.speed_mps)} min/km  |  "
                  f"速度: {config.speed_mps:.2f} m/s[/]")
    console.print(f"[dim]模拟距离: ~{format_distance(total_dist)}  |  "
                  f"圈数: {config.lap_count}  |  "
                  f"坐标点数: {len(coords)}[/]")
    console.print(f"[dim]预计用时: {format_duration(len(coords) * config.update_interval)}[/]\n")

    table = Table(title="轨迹预览（前 10 个 + 后 3 个坐标点）")
    table.add_column("#", style="dim")
    table.add_column("纬度 (lat)")
    table.add_column("经度 (lng)")

    preview = coords[:10] + coords[-3:] if len(coords) > 13 else coords
    for i, (lat, lng) in enumerate(preview):
        idx = str(i + 1) if i < 10 else str(len(coords) - (len(preview) - i) + 1)
        table.add_row(idx, f"{lat:.6f}", f"{lng:.6f}")

    console.print(table)
    console.print(f"\n[green]✅ 轨迹生成正常，共 {len(coords)} 个坐标点[/]")


def do_run(config: RunConfig):
    adb = ADBController()
    adb.check_or_die()

    console.print("[bold cyan]📱 检测设备...[/]")
    device = adb.check_device()
    console.print(f"[green]✅ 已连接设备: {device}[/]\n")

    route = load_route(config.route_name)
    route_dist = route_total_distance(route)
    simulator = RunSimulator(route, config.speed_mps,
                             config.update_interval, config.jitter)
    total_dist = route_dist * config.lap_count
    coords = simulator.generate_trajectory(config.lap_count, config.max_duration_s)
    total_time = len(coords) * config.update_interval

    config_info = [
        ("路线", f"{route.name} — {route.description}"),
        ("总距离", format_distance(total_dist)),
        ("配速", f"{format_pace(config.speed_mps)} min/km"),
        ("预计用时", format_duration(total_time)),
        ("坐标点", str(len(coords))),
        ("更新频率", f"{1 / config.update_interval:.0f} Hz"),
    ]

    console.print(build_info_panel({k: v for k, v in config_info}))

    if not click.confirm("\n是否开始模拟?", default=True):
        console.print("[dim]已取消[/]")
        return

    adb.setup_mock()
    console.print("\n[bold green]🏃 开始跑步模拟...[/] 按 Ctrl+C 停止\n")

    start_time = time.time()
    distance_covered = 0.0
    prev_lat, prev_lng = None, None
    coord_idx = 0

    def cleanup():
        adb.teardown()

    def on_sigint(signum, frame):
        console.print("\n[yellow]⏹ 正在停止...[/]")
        cleanup()
        elapsed = time.time() - start_time
        console.print(f"[dim]已用时: {format_duration(elapsed)}  |  "
                      f"已跑: {format_distance(distance_covered)}[/]")
        sys.exit(0)

    signal.signal(signal.SIGINT, on_sigint)

    try:
        for item in simulator.iter_run(config.lap_count, config.max_duration_s):
            if isinstance(item, tuple) and item[0] == "wait":
                time.sleep(item[1])
                continue

            lat, lng = item
            coord_idx += 1

            if prev_lat is not None:
                step_dist = haversine(prev_lat, prev_lng, lat, lng)
                distance_covered += step_dist

            prev_lat, prev_lng = lat, lng

            adb.send_location(lat, lng)

            elapsed = time.time() - start_time
            current_pace = (elapsed / 60) / (distance_covered / 1000) if distance_covered > 0 else 0

            # 每 5 个点更新一次显示
            if coord_idx % 5 == 0 or coord_idx == 1:
                pct = min(coord_idx / len(coords) * 100, 100)
                bar_width = 30
                filled = int(bar_width * coord_idx / len(coords))
                bar = "█" * filled + "░" * (bar_width - filled)
                status = (f"\r[{bar}] {pct:5.1f}%  "
                          f"├ {format_distance(distance_covered)}  "
                          f"├ {format_duration(elapsed)}  "
                          f"├ 配速 {format_pace(current_pace * 60)}  "
                          f"├ ({lat:.6f}, {lng:.6f})")
                sys.stdout.write(status)
                sys.stdout.flush()

        sys.stdout.write("\n")
        console.print("\n[bold green]✅ 跑步完成![/]")
    except Exception as e:
        console.print(f"\n[red]❌ 出错: {e}[/]")
    finally:
        cleanup()
        elapsed = time.time() - start_time
        console.print(f"[dim]总用时: {format_duration(elapsed)}  |  "
                      f"总距离: {format_distance(distance_covered)}[/]")


@click.command()
@click.option("--speed", type=float, default=None,
              help="跑步速度 (m/s)，例如 3.33")
@click.option("--pace", type=float, default=None,
              help=f"跑步配速 (min/km)，范围 {MIN_PACE:.0f}-{MAX_PACE:.0f}，默认 5.0")
@click.option("--route", type=str, default="hust_campus",
              help="路线名称 (对应 routes/ 目录下的 JSON 文件)")
@click.option("--laps", type=int, default=None,
              help="跑步圈数（默认自动计算以满足最低距离）")
@click.option("--max-time", type=float, default=None,
              help="最大跑步时间（秒）")
@click.option("--dry-run", is_flag=True, default=False,
              help="仅预览轨迹，不连接设备")
@click.option("--list-routes", is_flag=True, default=False,
              help="列出所有可用路线")
@click.option("--diagnose", is_flag=True, default=False,
              help="诊断手机定位状态，排查 mock 失败原因")
def main(speed, pace, route, laps, max_time, dry_run, list_routes, diagnose):
    """华中大体育 GPS 跑步模拟器

    每次跑步最少 3.5 km，配速范围 4:00 - 10:00 min/km。
    通过 USB 连接 Android 手机，模拟 GPS 位置变化来完成跑步打卡。
    """

    if diagnose:
        adb = ADBController()
        adb.check_or_die()
        adb.check_device()
        adb.diagnose()
        return

    if list_routes:
        routes_dir = Path(__file__).parent / "routes"
        json_files = list(routes_dir.glob("*.json"))
        if not json_files:
            console.print("[dim]没有找到路线文件[/]")
            return
        console.print("[bold]可用路线:[/]")
        for f in json_files:
            r = load_route(f.stem)
            dist = route_total_distance(r)
            min_laps = min_laps_for_distance(r)
            console.print(f"  • {f.stem} — {r.description}")
            console.print(f"    {len(r.waypoints)} 个航点, ~{format_distance(dist)}/圈, "
                          f"最少 {min_laps} 圈 (≥{format_distance(MIN_DISTANCE_M)})")
        return

    # 配速: --pace > --speed > 默认 5:00
    if pace is not None:
        pace_val = clamp_pace(pace)
        if pace_val != pace:
            console.print(f"[yellow]⚠ 配速 {pace:.1f} 超出范围，已调整为 {pace_val:.1f} min/km[/]")
        speed_mps = RunSimulator.pace_to_speed(pace_val)
    elif speed is not None:
        speed_mps = speed
        pace_val = (1000 / speed_mps) / 60
        if pace_val < MIN_PACE or pace_val > MAX_PACE:
            pace_val = clamp_pace(pace_val)
            speed_mps = RunSimulator.pace_to_speed(pace_val)
            console.print(f"[yellow]⚠ 速度超出配速范围，已调整为 {pace_val:.1f} min/km[/]")
    else:
        pace_val = 5.0
        speed_mps = RunSimulator.pace_to_speed(pace_val)

    # 圈数: 用户指定 > 自动计算满足 3.5km
    route_obj = load_route(route)
    min_laps = min_laps_for_distance(route_obj)
    if laps is None:
        laps = min_laps
        console.print(f"[dim]自动设置圈数: {laps} (满足最低 {format_distance(MIN_DISTANCE_M)})[/]")
    elif laps < min_laps:
        console.print(f"[yellow]⚠ {laps} 圈不足 {format_distance(MIN_DISTANCE_M)}，已调整为 {min_laps} 圈[/]")
        laps = min_laps

    config = RunConfig(
        speed_mps=speed_mps,
        route_name=route,
        lap_count=laps,
        max_duration_s=max_time,
    )

    if dry_run:
        do_dry_run(config)
    else:
        do_run(config)


if __name__ == "__main__":
    main()
