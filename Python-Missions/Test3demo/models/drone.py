"""
models/drone.py

定义 Drone 类，用于表示无人机。
包含型号、飞行时间、喷嘴大小等属性。
"""
from typing import Dict, Any
from utils.logger import logger

class Drone:
    """
    表示一架无人机。
    """
    def __init__(self, model: str, flight_time: float, spray_width: int, name: str = "NewDrone"):
        """
        初始化无人机对象。
        Args:
            model (str): 无人机型号。
            flight_time (float): 飞行时间（分钟）。
            spray_width (int): 喷洒宽度（覆盖的网格单元格数量）。
            name (str): 无人机名称（用于用户自定义）。
        """
        self.name = name
        self.model = model
        self.flight_time = flight_time
        self.spray_width = spray_width

    def to_dict(self) -> Dict[str, Any]:
        """
        将无人机对象转换为字典，用于 JSON 序列化。
        Returns:
            dict: 包含无人机信息的字典。
        """
        return {
            'name': self.name,
            'model': self.model,
            'flight_time': self.flight_time,
            'spray_width': self.spray_width
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]):
        """
        从字典创建无人机对象，用于 JSON 反序列化。
        Args:
            data (dict): 包含无人机信息的字典。
        Returns:
            Drone: 无人机对象。
        """
        return cls(
            model=data['model'],
            flight_time=data['flight_time'],
            spray_width=data['spray_width'],
            name=data.get('name', data['model']) # 如果没有name，使用model作为name
        )

    def __repr__(self):
        return f"Drone(name='{self.name}', model='{self.model}', flight_time={self.flight_time}, spray_width={self.spray_width})"
