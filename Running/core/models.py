from dataclasses import dataclass, field
from typing import Optional


@dataclass
class Waypoint:
    name: str
    lat: float
    lng: float


@dataclass
class Route:
    name: str
    waypoints: list[Waypoint]
    loop: bool = True
    description: str = ""


@dataclass
class RunConfig:
    speed_mps: float = 3.33
    route_name: str = "hust_campus"
    lap_count: int = 1
    update_interval: float = 1.0
    jitter: float = 0.00001
    max_duration_s: Optional[float] = None
