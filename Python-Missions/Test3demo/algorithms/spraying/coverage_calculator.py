"""
algorithms/spraying/coverage_calculator.py

计算无人机喷洒的覆盖率。
"""
from typing import List, Tuple, Set
from models.field import Field
from models.drone import Drone
from utils.logger import logger

def calculate_coverage(field: Field, path: List[Tuple[int, int]], drone: Drone) -> float:
    """
    计算给定路径和无人机喷洒宽度下的覆盖率。
    Args:
        field (Field): 农田对象。
        path (list): 无人机飞行路径 [(x1, y1), ...]。
        drone (Drone): 无人机对象。
    Returns:
        float: 覆盖率 (0.0 到 1.0)。
    """
    if not path:
        return 0.0

    # 获取所有需要被喷洒的地块 (例如，庄稼地块)
    target_cells = set(field.crop_positions)
    total_target_area = len(target_cells)
    if total_target_area == 0:
        logger.info("农田中没有需要喷洒的地块 (庄稼)，覆盖率定义为 100%。")
        return 1.0 # 没有目标，认为覆盖完成

    # 计算喷洒覆盖到的目标地块
    covered_cells: Set[Tuple[int, int]] = set()
    spray_width = drone.spray_width
    half_width = spray_width // 2
    is_even_width = spray_width % 2 == 0

    for x, y in path:
        # 计算当前位置的喷洒区域
        start_x = x - half_width
        end_x = x + half_width + (1 if not is_even_width else 0) # 奇数宽度时，右侧多一格
        start_y = y - half_width
        end_y = y + half_width + (1 if not is_even_width else 0)

        for sx in range(start_x, end_x):
            for sy in range(start_y, end_y):
                if (sx, sy) in target_cells:
                    covered_cells.add((sx, sy))

    covered_area = len(covered_cells)
    coverage_ratio = covered_area / total_target_area if total_target_area > 0 else 0.0

    logger.info(f"喷洒路径计算: 总目标区域 {total_target_area}, 覆盖区域 {covered_area}, 覆盖率 {coverage_ratio:.2%}")
    return coverage_ratio
