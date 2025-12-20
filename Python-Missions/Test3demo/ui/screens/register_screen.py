"""
ui/screens/register_screen.py

显示注册界面。
"""
import pygame
from config import WINDOW_WIDTH, WINDOW_HEIGHT, WINDOW_TITLE, DEFAULT_BG_COLOR, MIN_PASSWORD_LENGTH, PASSWORD_REQUIRE_UPPERCASE, PASSWORD_REQUIRE_LOWERCASE, PASSWORD_REQUIRE_DIGIT, PASSWORD_REQUIRE_SPECIAL
from utils.input_handler import handle_text_input, reset_input_state
from utils.file_handler import load_user_data, save_user_data
from models.user import User
from utils.logger import logger
import re

def is_valid_password(password: str) -> bool:
    """
    验证密码是否符合要求。
    """
    if len(password) < MIN_PASSWORD_LENGTH:
        return False
    if PASSWORD_REQUIRE_UPPERCASE and not re.search(r'[A-Z]', password):
        return False
    if PASSWORD_REQUIRE_LOWERCASE and not re.search(r'[a-z]', password):
        return False
    if PASSWORD_REQUIRE_DIGIT and not re.search(r'\d', password):
        return False
    if PASSWORD_REQUIRE_SPECIAL and not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
        return False
    return True

def show_register_screen():
    """
    显示注册界面，处理用户输入和注册逻辑。
    Returns:
        bool: 注册是否成功。
    """
    pygame.init()
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    pygame.display.set_caption(f"{WINDOW_TITLE} - 注册")

    clock = pygame.time.Clock()
    font = pygame.font.SysFont(None, 32)
    small_font = pygame.font.SysFont(None, 24)

    username_input = ""
    password_input = ""
    confirm_password_input = ""
    username_active = False
    password_active = False
    confirm_password_active = False
    message = ""

    input_boxes = {
        'username': pygame.Rect(400, 180, 400, 40),
        'password': pygame.Rect(400, 260, 400, 40),
        'confirm_password': pygame.Rect(400, 340, 400, 40)
    }

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                return False

            if event.type == pygame.MOUSEBUTTONDOWN:
                if input_boxes['username'].collidepoint(event.pos):
                    username_active = True
                    password_active = False
                    confirm_password_active = False
                    reset_input_state()
                elif input_boxes['password'].collidepoint(event.pos):
                    username_active = False
                    password_active = True
                    confirm_password_active = False
                    reset_input_state()
                elif input_boxes['confirm_password'].collidepoint(event.pos):
                    username_active = False
                    password_active = False
                    confirm_password_active = True
                    reset_input_state()
                else:
                    username_active = False
                    password_active = False
                    confirm_password_active = False

            if event.type == pygame.KEYDOWN:
                if username_active:
                    username_input = handle_text_input(event, username_input, max_length=20)
                elif password_active:
                    password_input = handle_text_input(event, password_input, max_length=20)
                elif confirm_password_active:
                    confirm_password_input = handle_text_input(event, confirm_password_input, max_length=20)

            if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
                # 按回车尝试注册
                if not username_input:
                    message = "请输入用户名！"
                elif load_user_data(username_input): # 检查用户是否已存在
                    message = "用户名已存在！"
                elif not is_valid_password(password_input):
                    message = f"密码不符合要求！至少 {MIN_PASSWORD_LENGTH} 位，"
                    if PASSWORD_REQUIRE_UPPERCASE: message += "含大写字母, "
                    if PASSWORD_REQUIRE_LOWERCASE: message += "含小写字母, "
                    if PASSWORD_REQUIRE_DIGIT: message += "含数字, "
                    if PASSWORD_REQUIRE_SPECIAL: message += "含特殊字符。"
                elif password_input != confirm_password_input:
                    message = "两次输入的密码不一致！"
                else:
                    # 创建新用户并保存
                    try:
                        new_user = User.create(username_input, password_input)
                        new_user.save()
                        logger.info(f"新用户 {username_input} 注册成功。")
                        message = "注册成功！"
                        # 可以选择在这里短暂显示成功信息后返回 True
                        # 或者等待用户点击按钮
                    except Exception as e:
                        logger.error(f"注册用户 {username_input} 失败: {e}")
                        message = "注册失败，请稍后重试。"


        screen.fill(DEFAULT_BG_COLOR)

        # 绘制输入框
        for name, rect in input_boxes.items():
            color = (200, 200, 255) if (name == 'username' and username_active) or (name == 'password' and password_active) or (name == 'confirm_password' and confirm_password_active) else (220, 220, 220)
            pygame.draw.rect(screen, color, rect, 2)
            input_text = locals()[f"{name}_input"]
            if name == 'password' or name == 'confirm_password':
                input_text = '*' * len(input_text) # 显示星号
            text_surface = font.render(input_text, True, (0, 0, 0))
            screen.blit(text_surface, (rect.x + 5, rect.y + 5))

        # 绘制标签
        username_label = small_font.render("用户名:", True, (0, 0, 0))
        password_label = small_font.render("密码:", True, (0, 0, 0))
        confirm_password_label = small_font.render("确认密码:", True, (0, 0, 0))
        screen.blit(username_label, (input_boxes['username'].x, input_boxes['username'].y - 30))
        screen.blit(password_label, (input_boxes['password'].x, input_boxes['password'].y - 30))
        screen.blit(confirm_password_label, (input_boxes['confirm_password'].x, input_boxes['confirm_password'].y - 30))

        # 绘制注册按钮
        button_rect = pygame.Rect(500, 420, 200, 50)
        pygame.draw.rect(screen, (0, 150, 0), button_rect)
        button_text = font.render("注册", True, (255, 255, 255))
        screen.blit(button_text, button_text.get_rect(center=button_rect.center))

        # 绘制消息
        if message:
            msg_surface = small_font.render(message, True, (255, 0, 0) if "失败" in message or "错误" in message else (0, 150, 0))
            screen.blit(msg_surface, (WINDOW_WIDTH // 2 - msg_surface.get_width() // 2, 480))

        pygame.display.flip()
        clock.tick(30)

    pygame.quit()
    return True # 如果循环正常结束，返回 True (虽然实际逻辑在回车事件里)