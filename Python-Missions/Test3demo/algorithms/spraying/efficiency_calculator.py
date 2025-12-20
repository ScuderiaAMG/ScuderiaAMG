"""
algorithms/spraying/efficiency_calculator.py

计算无人机喷洒的效率。
"""
from typing import List, Tuple
from models.field import Field
from models.drone import Drone
from utils.logger import logger

def calculate_efficiency(path: List[Tuple[int, int]], drone: Drone, flight_time_used: float, total_area_to_cover: int) -> float:
    """
    计算喷洒效率。这里可以定义多种效率指标。
    例如: 单位时间覆盖面积，单位时间喷洒农药量 (如果农药信息也传入)。
    Args:
        path (list): 无人机飞行路径。
        drone (Drone): 无人机对象。
        flight_time_used (float): 实际使用的飞行时间 (分钟)。
        total_area_to_cover (int): 总共需要覆盖的区域数量。
    Returns:
        float: 效率值 (例如，单位时间覆盖面积)。
    """
    if flight_time_used <= 0:
        logger.warning("计算效率时飞行时间 <= 0，返回 0。")
        return 0.0

    path_length = len(path)
    # 效率可以定义为: 总覆盖面积 / 总飞行时间
    # 这里简单地使用覆盖的单元格数量 / 时间
    # 如果需要考虑无人机喷洒宽度，可以计算总的喷洒面积 (path_length * spray_width)
    efficiency = total_area_to_cover / flight_time_used
    logger.info(f"喷洒效率计算: 总覆盖面积 {total_area_to_cover}, 飞行时间 {flight_time_used} 分钟, 效率为 {efficiency:.2f} 单元格/分钟")
    return efficiency
