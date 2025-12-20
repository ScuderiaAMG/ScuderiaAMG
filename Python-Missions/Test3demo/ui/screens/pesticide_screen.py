"""
ui/screens/pesticide_screen.py

显示农药配置页面。
"""
import pygame
from config import WINDOW_WIDTH, WINDOW_HEIGHT, WINDOW_TITLE, DEFAULT_BG_COLOR
from utils.input_handler import handle_text_input, reset_input_state
from utils.file_handler import save_pesticide_data, load_pesticide_data
from models.pesticide import Pesticide
from utils.logger import logger

def show_pesticide_screen(current_user):
    """
    显示农药管理界面。
    Args:
        current_user (User): 当前登录的用户对象。
    """
    pygame.init()
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    pygame.display.set_caption(f"{WINDOW_TITLE} - 农药管理")

    clock = pygame.time.Clock()
    font = pygame.font.SysFont(None, 32)
    small_font = pygame.font.SysFont(None, 24)

    # 输入字段
    name_input = ""
    type_input = ""
    notes_input = ""
    incompatible_input = ""
    input_active = None

    input_boxes = {
        'name': pygame.Rect(200, 100, 300, 40),
        'type': pygame.Rect(200, 180, 300, 40),
        'notes': pygame.Rect(200, 260, 500, 80), # 多行输入
        'incompatible': pygame.Rect(200, 380, 500, 40) # 逗号分隔列表
    }

    message = ""

    # 按钮
    button_width, button_height = 150, 40
    button_margin = 10
    save_button = pygame.Rect(200, 460, button_width, button_height)
    list_button = pygame.Rect(200 + button_width + button_margin, 460, button_width, button_height)

    running = True
    while running:
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
                        name = name_input
                        pesticide_type = type_input
                        notes = notes_input
                        # 解析不兼容列表
                        incompatible_list = [item.strip() for item in incompatible_input.split(',') if item.strip()]
                        if name and pesticide_type: # 基本验证
                            new_pesticide = Pesticide(name, pesticide_type, notes, incompatible_list)
                            # 加载现有农药列表
                            current_pesticides = load_pesticide_data(current_user.username)
                            # 检查是否已存在同名农药
                            existing_index = next((i for i, p in enumerate(current_pesticides) if p.name == name), -1)
                            if existing_index != -1:
                                current_pesticides[existing_index] = new_pesticide # 更新
                            else:
                                current_pesticides.append(new_pesticide) # 添加
                            # 保存农药列表
                            save_pesticide_data(current_user.username, current_pesticides)
                            message = f"农药 {name} 保存成功！"
                        else:
                            message = "请填写农药名称和类型！"
                    except Exception as e:
                        logger.error(f"保存农药失败: {e}")
                        message = "保存失败，请稍后重试。"

                elif list_button.collidepoint(event.pos):
                    user_pesticides = load_pesticide_data(current_user.username)
                    logger.info(f"用户 {current_user.username} 的农药列表: {[p.name for p in user_pesticides]}")
                    # 简化为打印
                    print("用户农药列表:", [p.name for p in user_pesticides])


            if event.type == pygame.KEYDOWN and input_active:
                if input_active == 'name':
                    name_input = handle_text_input(event, name_input, max_length=20)
                elif input_active == 'type':
                    type_input = handle_text_input(event, type_input, max_length=20)
                elif input_active == 'notes':
                    notes_input = handle_text_input(event, notes_input, max_length=200) # 增加长度
                elif input_active == 'incompatible':
                    incompatible_input = handle_text_input(event, incompatible_input, max_length=100)


        screen.fill(DEFAULT_BG_COLOR)

        # 绘制输入框
        for name, rect in input_boxes.items():
            color = (200, 200, 255) if name == input_active else (220, 220, 220)
            pygame.draw.rect(screen, color, rect, 2)
            input_text = locals()[f"{name}_input"]
            if name == 'notes':
                # 多行文本需要特殊处理，这里简化为单行显示
                text_surface = small_font.render(input_text, True, (0, 0, 0))
            else:
                text_surface = font.render(input_text, True, (0, 0, 0))
            screen.blit(text_surface, (rect.x + 5, rect.y + 5))

        # 绘制标签
        name_label = small_font.render("农药名称:", True, (0, 0, 0))
        type_label = small_font.render("类型:", True, (0, 0, 0))
        notes_label = small_font.render("注意事项/混合比例:", True, (0, 0, 0))
        incompatible_label = small_font.render("不兼容农药 (逗号分隔):", True, (0, 0, 0))
        screen.blit(name_label, (input_boxes['name'].x, input_boxes['name'].y - 30))
        screen.blit(type_label, (input_boxes['type'].x, input_boxes['type'].y - 30))
        screen.blit(notes_label, (input_boxes['notes'].x, input_boxes['notes'].y - 30))
        screen.blit(incompatible_label, (input_boxes['incompatible'].x, input_boxes['incompatible'].y - 30))

        # 绘制按钮
        pygame.draw.rect(screen, (0, 150, 0), save_button)
        pygame.draw.rect(screen, (0, 0, 150), list_button)
        save_text = font.render("保存", True, (255, 255, 255))
        list_text = font.render("列出", True, (255, 255, 255))
        screen.blit(save_text, save_text.get_rect(center=save_button.center))
        screen.blit(list_text, list_text.get_rect(center=list_button.center))

        # 绘制消息
        if message:
            msg_surface = small_font.render(message, True, (0, 150, 0))
            screen.blit(msg_surface, (200, 520))

        pygame.display.flip()
        clock.tick(30)

    pygame.quit()