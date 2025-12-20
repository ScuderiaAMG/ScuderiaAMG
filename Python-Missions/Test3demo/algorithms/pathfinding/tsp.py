"""
algorithms/pathfinding/tsp.py

实现或调用 TSP (旅行商问题) 算法来规划访问多个目标点的最优路径。
这里使用一个近似算法 (如最近邻算法) 作为示例，实际项目中可能需要引入专门的库。
"""
from typing import List, Tuple
from .base_planner import BasePathPlanner
from .a_star import AStarPlanner
from models.field import Field
import random
from utils.logger import logger

class TSPPlanner(BasePathPlanner):
    """
    TSP 路径规划器。
    使用 A* 算法计算距离，然后应用近似算法（如最近邻）来规划访问顺序。
    """
    def __init__(self, field: Field):
        super().__init__(field)
        # 创建一个 A* 实例用于计算距离
        self.astar = AStarPlanner(field)

    def calculate_distance_matrix(self, points: List[Tuple[int, int]]) -> List[List[float]]:
        """
        计算点之间的距离矩阵 (使用 A* 计算实际路径距离)。
        Args:
            points (list): 点坐标列表。
        Returns:
            list: 距离矩阵。
        """
        n = len(points)
        dist_matrix = [[0.0 for _ in range(n)] for _ in range(n)]
        for i in range(n):
            for j in range(i + 1, n): # 只计算上三角矩阵
                path = self.astar.plan_path_single(points[i], points[j])
                distance = len(path) - 1 if path else float('inf') # 路径长度减1为步数
                dist_matrix[i][j] = distance
                dist_matrix[j][i] = distance # 距离矩阵是对称的
        return dist_matrix

    def nearest_neighbor_tsp(self, dist_matrix: List[List[float]], start_idx: int) -> List[int]:
        """
        使用最近邻算法求解 TSP (近似解)。
        Args:
            dist_matrix (list): 距离矩阵。
            start_idx (int): 起始点索引。
        Returns:
            list: 访问顺序的索引列表。
        """
        n = len(dist_matrix)
        unvisited = set(range(n))
        current_idx = start_idx
        tour = [current_idx]
        unvisited.remove(current_idx)

        while unvisited:
            nearest_idx = min(unvisited, key=lambda idx: dist_matrix[current_idx][idx])
            tour.append(nearest_idx)
            unvisited.remove(nearest_idx)
            current_idx = nearest_idx

        return tour

    def plan_path(self, start: Tuple[int, int], targets: List[Tuple[int, int]]) -> List[Tuple[int, int]]:
        """
        规划访问所有目标点的最优路径 (使用 TSP)。
        Args:
            start (tuple): 起点坐标 (x, y)。
            targets (list): 目标点坐标列表 [(x1, y1), (x2, y2), ...]。
        Returns:
            list: 完整路径坐标列表。
        """
        if not targets:
            return [start]

        # 将起点加入目标列表，以便规划一个完整的环路 (或从起点开始的路径)
        all_points = [start] + targets
        dist_matrix = self.calculate_distance_matrix(all_points)

        # 使用最近邻算法规划访问顺序
        # 从索引0 (即起点) 开始
        tour_indices = self.nearest_neighbor_tsp(dist_matrix, 0)

        # 重建完整路径
        full_path = []
        for i in range(len(tour_indices) - 1):
            current_point_idx = tour_indices[i]
            next_point_idx = tour_indices[i + 1]
            current_point = all_points[current_point_idx]
            next_point = all_points[next_point_idx]

            # 使用 A* 规划子路径
            path_segment = self.astar.plan_path_single(current_point, next_point)
            if path_segment is None:
                logger.error(f"TSP: 无法规划从 {current_point} 到 {next_point} 的子路径，返回部分路径。")
                break # 或者可以尝试其他方法
            if full_path: # 如果不是第一个路径段，去掉起点以避免重复
                full_path.extend(path_segment[1:])
            else:
                full_path.extend(path_segment)

        return full_path
