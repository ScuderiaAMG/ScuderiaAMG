import json
import math
import random
from pathlib import Path
from typing import Iterator

from .models import Route, Waypoint


def haversine(lat1: float, lng1: float, lat2: float, lng2: float) -> float:
    """返回两点间距离（米）"""
    R = 6371000
    dlat = math.radians(lat2 - lat1)
    dlng = math.radians(lng2 - lng1)
    a = (math.sin(dlat / 2) ** 2 +
         math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) *
         math.sin(dlng / 2) ** 2)
    return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))


def load_route(name: str) -> Route:
    route_path = Path(__file__).parent.parent / "routes" / f"{name}.json"
    if not route_path.exists():
        raise FileNotFoundError(f"路线文件不存在: {route_path}")

    data = json.loads(route_path.read_text(encoding="utf-8"))
    waypoints = [Waypoint(name=w["name"], lat=w["lat"], lng=w["lng"])
                 for w in data["waypoints"]]
    return Route(
        name=data["name"],
        waypoints=waypoints,
        loop=data.get("loop", True),
        description=data.get("description", ""),
    )


def route_total_distance(route: Route) -> float:
    total = 0.0
    for i in range(len(route.waypoints)):
        p1 = route.waypoints[i]
        p2 = route.waypoints[(i + 1) % len(route.waypoints)]
        total += haversine(p1.lat, p1.lng, p2.lat, p2.lng)
    return total


def _interpolate_waypoints(p1: Waypoint, p2: Waypoint, steps: int) -> list[tuple[float, float]]:
    points = []
    for i in range(steps):
        t = i / steps
        lat = p1.lat + (p2.lat - p1.lat) * t
        lng = p1.lng + (p2.lng - p1.lng) * t
        points.append((lat, lng))
    return points


class RunSimulator:
    def __init__(self, route: Route, speed_mps: float = 3.33,
                 update_interval: float = 1.0, jitter: float = 0.00001):
        self.route = route
        self.speed_mps = speed_mps
        self.update_interval = update_interval
        self.jitter = jitter

    @property
    def pace_min_per_km(self) -> float:
        if self.speed_mps <= 0:
            return float("inf")
        return (1000 / self.speed_mps) / 60

    @staticmethod
    def pace_to_speed(pace_min_per_km: float) -> float:
        if pace_min_per_km <= 0:
            raise ValueError("配速必须大于 0")
        return 1000 / (pace_min_per_km * 60)

    def _build_full_waypoint_cycle(self, lap_count: int) -> list[tuple[float, float]]:
        """生成所有航点对之间的插值点，形成一个完整的连续轨迹"""
        waypoints = self.route.waypoints
        step_distance = self.speed_mps * self.update_interval

        all_coords: list[tuple[float, float]] = []

        for _ in range(lap_count):
            for i in range(len(waypoints)):
                p1 = waypoints[i]
                p2 = waypoints[(i + 1) % len(waypoints)]
                dist = haversine(p1.lat, p1.lng, p2.lat, p2.lng)
                steps = max(1, int(dist / step_distance))
                segment = _interpolate_waypoints(p1, p2, steps)
                all_coords.extend(segment)

        # 如果是环路，添加最后一个点回到第一个点
        if not self.route.loop:
            p_last = waypoints[-1]
            all_coords.append((p_last.lat, p_last.lng))

        return all_coords

    def generate_trajectory(self, lap_count: int = 1,
                            max_duration_s: float = None) -> list[tuple[float, float]]:
        full = self._build_full_waypoint_cycle(lap_count)
        if max_duration_s is not None:
            max_points = int(max_duration_s / self.update_interval)
            full = full[:max_points]
        return full

    def iter_run(self, lap_count: int = 1,
                 max_duration_s: float = None) -> Iterator[tuple[float, float]]:
        coords = self.generate_trajectory(lap_count, max_duration_s)
        total = len(coords)
        for i, (lat, lng) in enumerate(coords):
            jittered_lat = lat + random.uniform(-self.jitter, self.jitter)
            jittered_lng = lng + random.uniform(-self.jitter, self.jitter)
            yield (jittered_lat, jittered_lng)

            if i < total - 1:
                dist_to_next = haversine(lat, lng, coords[i + 1][0], coords[i + 1][1])
                actual_interval = dist_to_next / self.speed_mps if self.speed_mps > 0 else 1.0
            else:
                actual_interval = self.update_interval
            yield ("wait", actual_interval)
