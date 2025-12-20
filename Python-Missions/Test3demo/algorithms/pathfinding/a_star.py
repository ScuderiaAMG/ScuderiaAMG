"""
algorithms/pathfinding/a_star.py

实现 A* 路径规划算法。
用于在农田中找到从一个点到另一个点的最短路径。
"""
import heapq
from typing import List, Tuple, Dict, Optional
from .base_planner import BasePathPlanner
from models.field import Field
from utils.logger import logger

class AStarPlanner(BasePathPlanner):
    """
    A* 算法实现。
    """
    def __init__(self, field: Field):
        super().__init__(field)

    def heuristic(self, a: Tuple[int, int], b: Tuple[int, int]) -> float:
        """
        计算启发式距离 (曼哈顿距离)。
        Args:
            a (tuple): 坐标 (x1, y1)。
            b (tuple): 坐标 (x2, y2)。
        Returns:
            float: 启发式距离。
        """
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    def plan_path_single(self, start: Tuple[int, int], goal: Tuple[int, int]) -> Optional[List[Tuple[int, int]]]:
        """
        规划从单一起点到单个终点的路径。
        Args:
            start (tuple): 起点坐标 (x, y)。
            goal (tuple): 终点坐标 (x, y)。
        Returns:
            list: 路径坐标列表 [(x1, y1), (x2, y2), ...] 或 None (如果无路径)。
        """
        if not self.is_valid_position(*start) or not self.is_valid_position(*goal):
            logger.warning(f"A* 无法规划路径: 起点 {start} 或终点 {goal} 无效。")
            return None

        if start == goal:
            return [start]

        open_set = [(0, start)] # 优先队列，存储 (f_score, (x, y))
        came_from: Dict[Tuple[int, int], Tuple[int, int]] = {}
        g_score: Dict[Tuple[int, int], float] = {start: 0}
        f_score: Dict[Tuple[int, int], float] = {start: self.heuristic(start, goal)}

        while open_set:
            current = heapq.heappop(open_set)[1]

            if current == goal:
                # 重建路径
                path = []
                while current in came_from:
                    path.append(current)
                    current = came_from[current]
                path.append(start)
                path.reverse()
                return path

            for neighbor in self.get_neighbors(*current):
                tentative_g_score = g_score[current] + 1 # 每一步代价为1

                if neighbor not in g_score or tentative_g_score < g_score[neighbor]:
                    came_from[neighbor] = current
                    g_score[neighbor] = tentative_g_score
                    f_score[neighbor] = tentative_g_score + self.heuristic(neighbor, goal)
                    heapq.heappush(open_set, (f_score[neighbor], neighbor))

        logger.warning(f"A* 无法找到从 {start} 到 {goal} 的路径。")
        return None # 未找到路径

    def plan_path(self, start: Tuple[int, int], targets: List[Tuple[int, int]]) -> List[Tuple[int, int]]:
        """
        规划从起点到所有目标点的完整路径 (通过依次连接子路径)。
        注意: 这个简单的实现是依次访问目标点，不是解决 TSP 问题。
        Args:
            start (tuple): 起点坐标 (x, y)。
            targets (list): 目标点坐标列表 [(x1, y1), (x2, y2), ...]。
        Returns:
            list: 完整路径坐标列表。
        """
        full_path = []
        current_pos = start

        for target in targets:
            path_segment = self.plan_path_single(current_pos, target)
            if path_segment is None:
                logger.error(f"无法规划从 {current_pos} 到目标 {target} 的路径，返回部分路径。")
                # 可以选择跳过该目标或返回已找到的路径
                break # 这里选择中断规划
            if full_path: # 如果不是第一个路径段，去掉起点以避免重复
                full_path.extend(path_segment[1:])
            else:
                full_path.extend(path_segment)
            current_pos = target # 更新当前位置为上一段路径的终点

        return full_path
