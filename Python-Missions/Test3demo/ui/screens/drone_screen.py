"""
ui/screens/drone_screen.py

显示无人机信息录入页面。
"""
import pygame
from config import WINDOW_WIDTH, WINDOW_HEIGHT, WINDOW_TITLE, DEFAULT_BG_COLOR
from utils.input_handler import handle_text_input, reset_input_state
from utils.file_handler import save_drone_data, load_drone_data, list_user_drones, load_default_drones
from models.drone import Drone
from utils.logger import logger

def show_drone_screen(current_user):
    """
    显示无人机管理界面。
    Args:
        current_user (User): 当前登录的用户对象。
    """
    pygame.init()
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    pygame.display.set_caption(f"{WINDOW_TITLE} - 无人机管理")

    clock = pygame.time.Clock()
    font = pygame.font.SysFont(None, 32)
    small_font = pygame.font.SysFont(None, 24)

    # 输入字段
    drone_name_input = ""
    drone_model_input = ""
    drone_flight_time_input = ""
    drone_spray_width_input = ""
    input_active = None # 记录当前激活的输入框

    input_boxes = {
        'name': pygame.Rect(200, 100, 300, 40),
        'model': pygame.Rect(200, 180, 300, 40),
        'flight_time': pygame.Rect(200, 260, 300, 40),
        'spray_width': pygame.Rect(200, 340, 300, 40)
    }

    message = ""

    # 按钮
    button_width, button_height = 150, 40
    button_margin = 10
    save_button = pygame.Rect(200, 420, button_width, button_height)
    list_button = pygame.Rect(200 + button_width + button_margin, 420, button_width, button_height)
    load_defaults_button = pygame.Rect(200, 420 + button_height + button_margin, button_width, button_height)

    running = True
    while running:
        mouse_pos = pygame.mouse.get_pos()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if event.type == pygame.MOUSEBUTTONDOWN:
                clicked_input = None
                for name, rect in input_boxes.items():
                    if rect.collidepoint(event.pos):
                        clicked_input = name
                        break
                input_active = clicked_input
                reset_input_state()

                if save_button.collidepoint(event.pos):
                    try:
                        name = drone_name_input if drone_name_input else drone_model_input # 如果没填name，用model
                        model = drone_model_input
                        flight_time = float(drone_flight_time_input) if drone_flight_time_input else 0.0
                        spray_width = int(drone_spray_width_input) if drone_spray_width_input else 1
                        new_drone = Drone(model, flight_time, spray_width, name)
                        save_drone_data(current_user.username, name, new_drone)
                        current_user.add_drone_name(name)
                        current_user.save()
                        message = f"无人机 {name} 保存成功！"
                    except ValueError:
                        message = "飞行时间或喷洒宽度格式错误！"
                    except Exception as e:
                        logger.error(f"保存无人机失败: {e}")
                        message = "保存失败，请稍后重试。"

                elif list_button.collidepoint(event.pos):
                    user_drones = list_user_drones(current_user.username)
                    logger.info(f"用户 {current_user.username} 的无人机列表: {user_drones}")
                    # 这里可以弹出一个列表窗口让用户选择加载，简化为打印
                    print("用户无人机列表:", user_drones)

                elif load_defaults_button.collidepoint(event.pos):
                    default_drones = load_default_drones()
                    for drone in default_drones:
                        save_drone_data(current_user.username, drone.name, drone)
                        current_user.add_drone_name(drone.name)
                    current_user.save()
                    message = f"加载了 {len(default_drones)} 个默认无人机配置。"


            if event.type == pygame.KEYDOWN and input_active:
                if input_active == 'name':
                    drone_name_input = handle_text_input(event, drone_name_input, max_length=20)
                elif input_active == 'model':
                    drone_model_input = handle_text_input(event, drone_model_input, max_length=20)
                elif input_active == 'flight_time':
                    drone_flight_time_input = handle_text_input(event, drone_flight_time_input, max_length=10)
                elif input_active == 'spray_width':
                    drone_spray_width_input = handle_text_input(event, drone_spray_width_input, max_length=10)


        screen.fill(DEFAULT_BG_COLOR)

        # 绘制输入框
        for name, rect in input_boxes.items():
            color = (200, 200, 255) if name == input_active else (220, 220, 220)
            pygame.draw.rect(screen, color, rect, 2)
            input_text = locals()[f"drone_{name}_input"]
            text_surface = font.render(input_text, True, (0, 0, 0))
            screen.blit(text_surface, (rect.x + 5, rect.y + 5))

        # 绘制标签
        name_label = small_font.render("无人机名称 (可选):", True, (0, 0, 0))
        model_label = small_font.render("型号:", True, (0, 0, 0))
        flight_time_label = small_font.render("飞行时间 (分钟):", True, (0, 0, 0))
        spray_width_label = small_font.render("喷洒宽度 (格):", True, (0, 0, 0))
        screen.blit(name_label, (input_boxes['name'].x, input_boxes['name'].y - 30))
        screen.blit(model_label, (input_boxes['model'].x, input_boxes['model'].y - 30))
        screen.blit(flight_time_label, (input_boxes['flight_time'].x, input_boxes['flight_time'].y - 30))
        screen.blit(spray_width_label, (input_boxes['spray_width'].x, input_boxes['spray_width'].y - 30))

        # 绘制按钮
        pygame.draw.rect(screen, (0, 150, 0), save_button)
        pygame.draw.rect(screen, (0, 0, 150), list_button)
        pygame.draw.rect(screen, (150, 150, 0), load_defaults_button)
        save_text = font.render("保存", True, (255, 255, 255))
        list_text = font.render("列出", True, (255, 255, 255))
        load_defaults_text = font.render("加载默认", True, (255, 255, 255))
        screen.blit(save_text, save_text.get_rect(center=save_button.center))
        screen.blit(list_text, list_text.get_rect(center=list_button.center))
        screen.blit(load_defaults_text, load_defaults_text.get_rect(center=load_defaults_button.center))

        # 绘制消息
        if message:
            msg_surface = small_font.render(message, True, (0, 150, 0))
            screen.blit(msg_surface, (200, 500))

        pygame.display.flip()
        clock.tick(30)

    pygame.quit()