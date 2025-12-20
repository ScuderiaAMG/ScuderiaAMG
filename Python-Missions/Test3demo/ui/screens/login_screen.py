"""
ui/screens/login_screen.py

显示登录界面。
"""
import pygame
from config import WINDOW_WIDTH, WINDOW_HEIGHT, WINDOW_TITLE, DEFAULT_BG_COLOR
from utils.input_handler import handle_text_input, reset_input_state
from utils.file_handler import load_user_data
from models.user import User
from utils.logger import logger

def show_login_screen():
    """
    显示登录界面，处理用户输入和登录验证。
    Returns:
        User: 登录成功的用户对象，如果失败则返回 None。
    """
    pygame.init()
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    pygame.display.set_caption(f"{WINDOW_TITLE} - 登录")

    clock = pygame.time.Clock()
    font = pygame.font.SysFont(None, 32)
    small_font = pygame.font.SysFont(None, 24)

    username_input = ""
    password_input = ""
    username_active = False
    password_active = False
    message = ""

    input_boxes = {
        'username': pygame.Rect(400, 200, 400, 40),
        'password': pygame.Rect(400, 280, 400, 40)
    }

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                return None

            if event.type == pygame.MOUSEBUTTONDOWN:
                # 检查点击了哪个输入框
                if input_boxes['username'].collidepoint(event.pos):
                    username_active = True
                    password_active = False
                    reset_input_state() # 重置输入状态
                elif input_boxes['password'].collidepoint(event.pos):
                    password_active = True
                    username_active = False
                    reset_input_state()
                else:
                    username_active = False
                    password_active = False

            if event.type == pygame.KEYDOWN:
                if username_active:
                    username_input = handle_text_input(event, username_input, max_length=20)
                elif password_active:
                    # 对密码输入也进行处理，但显示为星号
                    password_input = handle_text_input(event, password_input, max_length=20)

            if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
                # 按回车尝试登录
                user = load_user_data(username_input)
                if user and user.check_password(password_input):
                    logger.info(f"用户 {username_input} 登录成功。")
                    running = False
                    return user
                else:
                    message = "用户名或密码错误！"
                    logger.warning(f"登录失败: 用户名 '{username_input}'")


        screen.fill(DEFAULT_BG_COLOR)

        # 绘制输入框
        for name, rect in input_boxes.items():
            color = (200, 200, 255) if (name == 'username' and username_active) or (name == 'password' and password_active) else (220, 220, 220)
            pygame.draw.rect(screen, color, rect, 2)
            text_surface = font.render(locals()[f"{name}_input"], True, (0, 0, 0))
            screen.blit(text_surface, (rect.x + 5, rect.y + 5))
            if name == 'password':
                # 显示星号
                masked_text = '*' * len(password_input)
                text_surface = font.render(masked_text, True, (0, 0, 0))
                screen.blit(text_surface, (rect.x + 5, rect.y + 5))

        # 绘制标签
        username_label = small_font.render("用户名:", True, (0, 0, 0))
        password_label = small_font.render("密码:", True, (0, 0, 0))
        screen.blit(username_label, (input_boxes['username'].x, input_boxes['username'].y - 30))
        screen.blit(password_label, (input_boxes['password'].x, input_boxes['password'].y - 30))

        # 绘制登录按钮
        button_rect = pygame.Rect(500, 360, 200, 50)
        pygame.draw.rect(screen, (0, 100, 200), button_rect)
        button_text = font.render("登录", True, (255, 255, 255))
        screen.blit(button_text, button_text.get_rect(center=button_rect.center))

        # 绘制消息
        if message:
            msg_surface = small_font.render(message, True, (255, 0, 0))
            screen.blit(msg_surface, (WINDOW_WIDTH // 2 - msg_surface.get_width() // 2, 420))

        pygame.display.flip()
        clock.tick(30)

    pygame.quit()
    return None