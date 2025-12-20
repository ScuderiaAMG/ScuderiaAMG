"""
algorithms/pathfinding/base_planner.py

定义路径规划器的基类。
所有具体的路径规划算法都应继承此类。
"""
from abc import ABC, abstractmethod
from typing import List, Tuple
from models.field import Field

class BasePathPlanner(ABC):
    """
    路径规划器的抽象基类。
    """
    def __init__(self, field: Field):
        """
        初始化规划器。
        Args:
            field (Field): 农田对象。
        """
        self.field = field
        # 将农田的障碍物信息转换为更方便处理的格式 (例如集合)
        self.obstacles = set(self.field.obstacle_positions)

    @abstractmethod
    def plan_path(self, start: Tuple[int, int], targets: List[Tuple[int, int]]) -> List[Tuple[int, int]]:
        """
        规划从起点到所有目标点的路径。
        Args:
            start (tuple): 起点坐标 (x, y)。
            targets (list): 目标点坐标列表 [(x1, y1), (x2, y2), ...]。
        Returns:
            list: 路径坐标列表 [(x1, y1), (x2, y2), ...]。
        """
        pass

    def is_valid_position(self, x: int, y: int) -> bool:
        """
        检查坐标是否在农田范围内且不是障碍物。
        Args:
            x (int): X坐标。
            y (int): Y坐标。
        Returns:
            bool: 如果有效返回 True，否则返回 False。
        """
        if 0 <= x < self.field.width and 0 <= y < self.field.height:
            return (x, y) not in self.obstacles
        return False

    def get_neighbors(self, x: int, y: int) -> List[Tuple[int, int]]:
        """
        获取指定坐标点的邻居节点 (上下左右)。
        Args:
            x (int): X坐标。
            y (int): Y坐标。
        Returns:
            list: 邻居坐标列表 [(x1, y1), ...]。
        """
        neighbors = []
        for dx, dy in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
            nx, ny = x + dx, y + dy
            if self.is_valid_position(nx, ny):
                neighbors.append((nx, ny))
        return neighbors
