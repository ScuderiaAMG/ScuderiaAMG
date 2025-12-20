"""
models/simulation.py

定义 Simulation 类，用于表示模拟环境。
包含气象条件、地形变化等环境因素。
"""
from typing import Dict, Any
from utils.logger import logger

class SimulationEnvironment:
    """
    表示模拟的环境因素。
    """
    def __init__(self, weather: str = "sunny", wind_speed: float = 0.0, terrain_elevation: float = 0.0):
        """
        初始化模拟环境对象。
        Args:
            weather (str): 天气状况 (例如: sunny, cloudy, rainy)。
            wind_speed (float): 风速 (m/s)。
            terrain_elevation (float): 地形海拔变化 (m)。
        """
        self.weather = weather
        self.wind_speed = wind_speed
        self.terrain_elevation = terrain_elevation

    def to_dict(self) -> Dict[str, Any]:
        """
        将环境对象转换为字典，用于 JSON 序列化。
        Returns:
            dict: 包含环境信息的字典。
        """
        return {
            'weather': self.weather,
            'wind_speed': self.wind_speed,
            'terrain_elevation': self.terrain_elevation
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]):
        """
        从字典创建环境对象，用于 JSON 反序列化。
        Args:
            data (dict): 包含环境信息的字典。
        Returns:
            SimulationEnvironment: 环境对象。
        """
        return cls(
            weather=data.get('weather', 'sunny'),
            wind_speed=data.get('wind_speed', 0.0),
            terrain_elevation=data.get('terrain_elevation', 0.0)
        )

    def __repr__(self):
        return f"SimulationEnvironment(weather='{self.weather}', wind_speed={self.wind_speed}, terrain_elevation={self.terrain_elevation})"
