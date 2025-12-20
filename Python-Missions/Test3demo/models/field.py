"""
models/field.py

定义 Field 类，用于表示农田。
包含农田的网格大小、地块信息、障碍物、庄稼位置、无人机起点等。
"""
from typing import List, Tuple, Dict, Any
import json
from utils.logger import logger

class Field:
    """
    表示一块农田。
    """
    # 常量定义地块类型
    EMPTY = 0
    CROP = 1
    OBSTACLE = 2
    DRONE_START = 3

    def __init__(self, width: int, height: int, name: str = "NewField"):
        """
        初始化农田对象。
        Args:
            width (int): 农田网格宽度。
            height (int): 农田网格高度。
            name (str): 农田名称。
        """
        self.name = name
        self.width = width
        self.height = height
        # 使用二维列表存储地块状态
        self.grid: List[List[int]] = [[self.EMPTY for _ in range(width)] for _ in range(height)]
        self.start_position: Tuple[int, int] = (0, 0) # 无人机起点
        self.crop_positions: List[Tuple[int, int]] = [] # 庄稼位置列表
        self.obstacle_positions: List[Tuple[int, int]] = [] # 障碍物位置列表

    def set_cell(self, x: int, y: int, cell_type: int):
        """
        设置指定坐标地块的类型。
        Args:
            x (int): X坐标。
            y (int): Y坐标。
            cell_type (int): 地块类型 (EMPTY, CROP, OBSTACLE, DRONE_START)。
        """
        if 0 <= x < self.width and 0 <= y < self.height:
            self.grid[y][x] = cell_type
            # 更新位置列表
            if cell_type == self.CROP and (x, y) not in self.crop_positions:
                self.crop_positions.append((x, y))
            elif cell_type == self.OBSTACLE and (x, y) not in self.obstacle_positions:
                self.obstacle_positions.append((x, y))
            elif cell_type == self.DRONE_START:
                self.start_position = (x, y)
        else:
            logger.warning(f"尝试设置超出农田边界的单元格 ({x}, {y})")

    def get_cell(self, x: int, y: int) -> int:
        """
        获取指定坐标地块的类型。
        Args:
            x (int): X坐标。
            y (int): Y坐标。
        Returns:
            int: 地块类型。
        """
        if 0 <= x < self.width and 0 <= y < self.height:
            return self.grid[y][x]
        else:
            logger.warning(f"尝试获取超出农田边界的单元格 ({x}, {y}) 类型")
            return self.OBSTACLE # 超出边界视为障碍物

    def clear(self):
        """清空农田，将所有地块设置为空。"""
        self.grid = [[self.EMPTY for _ in range(self.width)] for _ in range(self.height)]
        self.start_position = (0, 0)
        self.crop_positions = []
        self.obstacle_positions = []

    def to_dict(self) -> Dict[str, Any]:
        """
        将农田对象转换为字典，用于 JSON 序列化。
        Returns:
            dict: 包含农田信息的字典。
        """
        return {
            'name': self.name,
            'width': self.width,
            'height': self.height,
            'grid': self.grid, # 二维列表可以直接序列化
            'start_position': list(self.start_position), # 转换为列表
            'crop_positions': self.crop_positions,
            'obstacle_positions': self.obstacle_positions
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]):
        """
        从字典创建农田对象，用于 JSON 反序列化。
        Args:
            data (dict): 包含农田信息的字典。
        Returns:
            Field: 农田对象。
        """
        field = cls(data['width'], data['height'], data['name'])
        field.grid = data['grid']
        field.start_position = tuple(data['start_position'])
        field.crop_positions = data.get('crop_positions', [])
        field.obstacle_positions = data.get('obstacle_positions', [])
        return field

    def __repr__(self):
        return f"Field(name='{self.name}', size=({self.width}x{self.height}))"
