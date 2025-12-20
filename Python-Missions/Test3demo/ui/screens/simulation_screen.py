"""
ui/screens/simulation_screen.py

显示无人机喷洒模拟页面。
"""
import pygame
import time
from config import WINDOW_WIDTH, WINDOW_HEIGHT, WINDOW_TITLE, DEFAULT_BG_COLOR, GRID_CELL_SIZE_PX, SIMULATION_TIMESTEP, ANIMATION_FPS
from ui.graphics_engine import draw_field_grid, draw_drone, draw_path
from models.field import Field
from models.drone import Drone
from models.pesticide import Pesticide
from models.simulation import SimulationEnvironment
from algorithms.pathfinding.a_star import AStarPlanner
from algorithms.pathfinding.tsp import TSPPlanner
from algorithms.spraying.coverage_calculator import calculate_coverage
from utils.file_handler import list_user_fields, load_field_data, list_user_drones, load_drone_data, load_pesticide_data
from utils.logger import logger

def show_simulation(current_user):
    """
    显示模拟主界面。
    Args:
        current_user (User): 当前登录的用户对象。
    """
    pygame.init()
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    pygame.display.set_caption(f"{WINDOW_TITLE} - 模拟")

    clock = pygame.time.Clock()
    font = pygame.font.SysFont(None, 24)

    # 加载用户数据
    user_fields = list_user_fields(current_user.username)
    user_drones = list_user_drones(current_user.username)
    user_pesticides = load_pesticide_data(current_user.username)

    if not user_fields:
        logger.warning("用户没有农田，无法开始模拟。")
        print("错误: 用户没有保存的农田，请先创建农田。")
        pygame.quit()
        return

    # 简化：选择第一个农田、无人机和农药
    field_name = user_fields[0]
    drone_name = user_drones[0] if user_drones else "DefaultDrone"
    pesticide = user_pesticides[0] if user_pesticides else Pesticide("Generic", "General")

    field = load_field_data(current_user.username, field_name)
    drone = load_drone_data(current_user.username, drone_name) if drone_name != "DefaultDrone" else Drone("SimulatedDrone", 30.0, 2, "SimulatedDrone")

    if not field or not drone:
        logger.error("加载农田或无人机数据失败。")
        print("错误: 加载农田或无人机数据失败。")
        pygame.quit()
        return

    # 路径规划
    planner = TSPPlanner(field) # 也可以选择 AStarPlanner
    # targets = field.crop_positions # 使用农田中的庄稼位置作为目标
    # 简化：如果庄稼位置为空，使用几个示例位置
    targets = field.crop_positions if field.crop_positions else [(2,2), (5,5), (8,3)]
    planned_path = planner.plan_path(field.start_position, targets)
    logger.info(f"规划路径长度: {len(planned_path)}, 路径: {planned_path}")

    # 模拟变量
    drone_pos = list(field.start_position) # 无人机当前位置
    path_index = 0 # 当前路径索引
    simulating = False
    animation_speed = 1 # 控制动画速度 (帧/步)

    # 绘制区域
    draw_area_x = 50
    draw_area_y = 50
    draw_area_width = field.width * GRID_CELL_SIZE_PX
    draw_area_height = field.height * GRID_CELL_SIZE_PX
    draw_area_rect = pygame.Rect(draw_area_x, draw_area_y, draw_area_width, draw_area_height)

    # 按钮
    button_width, button_height = 120, 40
    button_margin = 10
    start_button = pygame.Rect(WINDOW_WIDTH - button_width - button_margin, 50, button_width, button_height)
    stop_button = pygame.Rect(WINDOW_WIDTH - button_width - button_margin, 50 + button_height + button_margin, button_width, button_height)
    # reset_button = pygame.Rect(WINDOW_WIDTH - button_width - button_margin, 50 + 2*(button_height + button_margin), button_width, button_height)

    running = True
    frame_count = 0
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if event.type == pygame.MOUSEBUTTONDOWN:
                if start_button.collidepoint(event.pos) and not simulating:
                    simulating = True
                elif stop_button.collidepoint(event.pos) and simulating:
                    simulating = False
                # elif reset_button.collidepoint(event.pos):
                #     drone_pos = list(field.start_position)
                #     path_index = 0
                #     simulating = False


        screen.fill(DEFAULT_BG_COLOR)

        # 绘制农田和路径
        draw_field_grid(screen, field, draw_area_x, draw_area_y)
        if planned_path:
            draw_path(screen, planned_path, draw_area_x, draw_area_y)
        draw_drone(screen, drone_pos, draw_area_x, draw_area_y)

        # 模拟无人机移动
        if simulating and path_index < len(planned_path):
            frame_count += 1
            if frame_count >= animation_speed:
                frame_count = 0
                target_pos = planned_path[path_index]
                # 简单移动逻辑 (曼哈顿距离)
                if drone_pos[0] < target_pos[0]:
                    drone_pos[0] += 1
                elif drone_pos[0] > target_pos[0]:
                    drone_pos[0] -= 1
                elif drone_pos[1] < target_pos[1]:
                    drone_pos[1] += 1
                elif drone_pos[1] > target_pos[1]:
                    drone_pos[1] -= 1

                # 如果到达目标点，移动到下一个
                if drone_pos == list(target_pos):
                    path_index += 1

        # 绘制按钮
        start_color = (0, 150, 0) if not simulating else (100, 100, 100)
        stop_color = (150, 0, 0) if simulating else (100, 100, 100)
        pygame.draw.rect(screen, start_color, start_button)
        pygame.draw.rect(screen, stop_color, stop_button)
        # pygame.draw.rect(screen, (100, 100, 100), reset_button)
        start_text = font.render("开始", True, (255, 255, 255))
        stop_text = font.render("停止", True, (255, 255, 255))
        # reset_text = font.render("重置", True, (255, 255, 255))
        screen.blit(start_text, start_text.get_rect(center=start_button.center))
        screen.blit(stop_text, stop_text.get_rect(center=stop_button.center))
        # screen.blit(reset_text, reset_text.get_rect(center=reset_button.center))

        # 绘制状态信息
        status_text = f"状态: {'模拟中' if simulating else '已停止'} | 位置: {drone_pos} | 路径进度: {path_index}/{len(planned_path)}"
        status_surface = font.render(status_text, True, (0, 0, 0))
        screen.blit(status_surface, (draw_area_x, draw_area_y + draw_area_height + 10))

        # 计算并显示覆盖率
        if planned_path:
            coverage = calculate_coverage(field, planned_path[:path_index+1], drone) # 计算已走路径的覆盖率
            coverage_text = f"覆盖率: {coverage:.2%}"
            coverage_surface = font.render(coverage_text, True, (0, 0, 0))
            screen.blit(coverage_surface, (draw_area_x, draw_area_y + draw_area_height + 40))

        pygame.display.flip()
        clock.tick(ANIMATION_FPS)

    pygame.quit()