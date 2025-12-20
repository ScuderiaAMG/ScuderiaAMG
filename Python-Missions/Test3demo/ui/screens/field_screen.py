"""
ui/screens/field_screen.py

显示农田创建/编辑页面。
"""
import pygame
from config import WINDOW_WIDTH, WINDOW_HEIGHT, WINDOW_TITLE, DEFAULT_BG_COLOR, DEFAULT_GRID_COLOR, GRID_CELL_SIZE_PX
from utils.file_handler import save_field_data, load_field_data, list_user_fields
from models.field import Field
from utils.logger import logger
from ui.graphics_engine import draw_field_grid

def show_field_screen(current_user):
    """
    显示农田编辑界面。
    Args:
        current_user (User): 当前登录的用户对象。
    """
    pygame.init()
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    pygame.display.set_caption(f"{WINDOW_TITLE} - 农田编辑")

    clock = pygame.time.Clock()
    font = pygame.font.SysFont(None, 24)

    # 初始化一个默认农田
    field = Field(10, 10, "DefaultField")

    # 按钮区域
    button_width, button_height = 120, 40
    button_margin = 10
    button_y_start = 50
    clear_button = pygame.Rect(WINDOW_WIDTH - button_width - button_margin, button_y_start, button_width, button_height)
    save_button = pygame.Rect(WINDOW_WIDTH - button_width - button_margin, button_y_start + button_height + button_margin, button_width, button_height)
    load_button = pygame.Rect(WINDOW_WIDTH - button_width - button_margin, button_y_start + 2*(button_height + button_margin), button_width, button_height)

    # 绘制区域
    draw_area_x = 50
    draw_area_y = 50
    draw_area_width = field.width * GRID_CELL_SIZE_PX
    draw_area_height = field.height * GRID_CELL_SIZE_PX
    draw_area_rect = pygame.Rect(draw_area_x, draw_area_y, draw_area_width, draw_area_height)

    # 工具选择
    tool = "crop" # 'crop', 'obstacle', 'start', 'select' (select 用于取消)

    running = True
    while running:
        mouse_pos = pygame.mouse.get_pos()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if event.type == pygame.MOUSEBUTTONDOWN:
                if clear_button.collidepoint(event.pos):
                    field.clear()
                elif save_button.collidepoint(event.pos):
                    # 获取农田名称
                    field_name = input("请输入农田名称: ") # 这里简化处理，实际UI应有输入框
                    if field_name:
                        save_field_data(current_user.username, field_name, field)
                        current_user.add_field_name(field_name)
                        current_user.save() # 保存用户信息
                elif load_button.collidepoint(event):
                    # 列出用户农田并让用户选择
                    user_fields = list_user_fields(current_user.username)
                    if user_fields:
                        # 这里简化处理，实际UI应有列表选择
                        field_name = user_fields[0] if len(user_fields) == 1 else input(f"请输入要加载的农田名称 {user_fields}: ")
                        if field_name in user_fields:
                            loaded_field = load_field_data(current_user.username, field_name)
                            if loaded_field:
                                field = loaded_field
                    else:
                        logger.info("用户没有保存的农田。")
                elif draw_area_rect.collidepoint(event.pos):
                    # 计算点击的网格坐标
                    grid_x = (mouse_pos[0] - draw_area_x) // GRID_CELL_SIZE_PX
                    grid_y = (mouse_pos[1] - draw_area_y) // GRID_CELL_SIZE_PX
                    if 0 <= grid_x < field.width and 0 <= grid_y < field.height:
                        # 根据工具设置单元格类型
                        if tool == "crop":
                            field.set_cell(grid_x, grid_y, Field.CROP)
                        elif tool == "obstacle":
                            field.set_cell(grid_x, grid_y, Field.OBSTACLE)
                        elif tool == "start":
                            # 先清除旧的起点
                            old_start_x, old_start_y = field.start_position
                            field.set_cell(old_start_x, old_start_y, Field.EMPTY)
                            # 设置新的起点
                            field.set_cell(grid_x, grid_y, Field.DRONE_START)
                            field.start_position = (grid_x, grid_y)
                        elif tool == "select":
                            # 取消选择，可以清除作物或障碍物
                            current_type = field.get_cell(grid_x, grid_y)
                            if current_type in [Field.CROP, Field.OBSTACLE]:
                                field.set_cell(grid_x, grid_y, Field.EMPTY)

        # 检查工具切换按键 (例如 1, 2, 3, 4)
        keys = pygame.key.get_pressed()
        if keys[pygame.K_1]:
            tool = "crop"
        elif keys[pygame.K_2]:
            tool = "obstacle"
        elif keys[pygame.K_3]:
            tool = "start"
        elif keys[pygame.K_4]:
            tool = "select"

        screen.fill(DEFAULT_BG_COLOR)

        # 绘制农田网格
        draw_field_grid(screen, field, draw_area_x, draw_area_y)

        # 绘制按钮
        pygame.draw.rect(screen, (200, 0, 0), clear_button)
        pygame.draw.rect(screen, (0, 200, 0), save_button)
        pygame.draw.rect(screen, (0, 0, 200), load_button)
        clear_text = font.render("清除", True, (255, 255, 255))
        save_text = font.render("保存", True, (255, 255, 255))
        load_text = font.render("加载", True, (255, 255, 255))
        screen.blit(clear_text, clear_text.get_rect(center=clear_button.center))
        screen.blit(save_text, save_text.get_rect(center=save_button.center))
        screen.blit(load_text, load_text.get_rect(center=load_button.center))

        # 绘制工具提示
        tool_text = font.render(f"当前工具: {tool.upper()}", True, (0, 0, 0))
        screen.blit(tool_text, (draw_area_x, draw_area_y + draw_area_height + 20))

        # 绘制快捷键提示
        key_text = font.render("1-作物 2-障碍 3-起点 4-选择", True, (0, 0, 0))
        screen.blit(key_text, (draw_area_x, draw_area_y + draw_area_height + 50))

        pygame.display.flip()
        clock.tick(30)

    pygame.quit()