"""
ui/graphics_engine.py

封装底层图形绘制逻辑，用于绘制农田、无人机、路径等。
"""
import pygame
from config import GRID_CELL_SIZE_PX, DEFAULT_GRID_COLOR
from models.field import Field
from utils.logger import logger

def draw_field_grid(screen, field: Field, offset_x: int, offset_y: int):
    """
    绘制农田网格。
    Args:
        screen (pygame.Surface): Pygame 屏幕表面。
        field (Field): 农田对象。
        offset_x (int): 绘制区域的 X 偏移。
        offset_y (int): 绘制区域的 Y 偏移。
    """
    cell_size = GRID_CELL_SIZE_PX
    for y in range(field.height):
        for x in range(field.width):
            rect = pygame.Rect(offset_x + x * cell_size, offset_y + y * cell_size, cell_size, cell_size)
            cell_type = field.get_cell(x, y)
            if cell_type == Field.EMPTY:
                color = (255, 255, 255) # 白色
            elif cell_type == Field.CROP:
                color = (0, 255, 0) # 绿色
            elif cell_type == Field.OBSTACLE:
                color = (139, 69, 19) # 棕色
            elif cell_type == Field.DRONE_START:
                color = (0, 0, 255) # 蓝色
            else:
                color = (255, 255, 255) # 默认白色

            pygame.draw.rect(screen, color, rect)
            pygame.draw.rect(screen, DEFAULT_GRID_COLOR, rect, 1) # 绘制网格线

def draw_path(screen, path: list, offset_x: int, offset_y: int, color=(255, 0, 0)):
    """
    绘制路径。
    Args:
        screen (pygame.Surface): Pygame 屏幕表面。
        path (list): 路径坐标列表 [(x1, y1), ...]。
        offset_x (int): 绘制区域的 X 偏移。
        offset_y (int): 绘制区域的 Y 偏移。
        color (tuple): 路径颜色 (R, G, B)。
    """
    if len(path) < 2:
        return
    points = [(offset_x + x * GRID_CELL_SIZE_PX + GRID_CELL_SIZE_PX//2, offset_y + y * GRID_CELL_SIZE_PX + GRID_CELL_SIZE_PX//2) for x, y in path]
    pygame.draw.lines(screen, color, False, points, 3) # 画线

def draw_drone(screen, pos: list, offset_x: int, offset_y: int, color=(255, 165, 0), size=10):
    """
    绘制无人机。
    Args:
        screen (pygame.Surface): Pygame 屏幕表面。
        pos (list): 无人机当前位置 [x, y]。
        offset_x (int): 绘制区域的 X 偏移。
        offset_y (int): 绘制区域的 Y 偏移。
        color (tuple): 无人机颜色 (R, G, B)。
        size (int): 无人机大小 (半径)。
    """
    center_x = offset_x + pos[0] * GRID_CELL_SIZE_PX + GRID_CELL_SIZE_PX // 2
    center_y = offset_y + pos[1] * GRID_CELL_SIZE_PX + GRID_CELL_SIZE_PX // 2
    pygame.draw.circle(screen, color, (center_x, center_y), size)
    # 可以添加更多细节，如方向指示器
    pygame.draw.line(screen, (0, 0, 0), (center_x, center_y), (center_x + size, center_y), 2) # 简单的方向指示
