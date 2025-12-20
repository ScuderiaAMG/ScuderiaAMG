"""
ui/screens/welcome_screen.py

显示开机欢迎动画。
"""
import pygame
import time
from config import WINDOW_WIDTH, WINDOW_HEIGHT, WINDOW_TITLE, DEFAULT_BG_COLOR

def show_welcome_animation():
    """
    显示欢迎动画。
    """
    pygame.init()
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    pygame.display.set_caption(f"{WINDOW_TITLE} - 欢迎")

    clock = pygame.time.Clock()
    font = pygame.font.SysFont(None, 48)
    text = font.render("欢迎使用 农田无人机喷洒模拟系统", True, (0, 0, 0))
    text_rect = text.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2))

    running = True
    start_time = time.time()
    duration = 3 # 欢迎动画持续3秒

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        screen.fill(DEFAULT_BG_COLOR)
        screen.blit(text, text_rect)
        pygame.display.flip()

        clock.tick(30) # 30 FPS

        # 持续时间到后自动退出
        if time.time() - start_time >= duration:
            running = False

    pygame.quit()

# # 如果需要更复杂的动画，可以添加更多绘图逻辑
# def show_welcome_animation_advanced():
#     pygame.init()
#     screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
#     pygame.display.set_caption(f"{WINDOW_TITLE} - 欢迎")
#     clock = pygame.time.Clock()
#     font = pygame.font.SysFont(None, 48)
#     title_text = "欢迎使用 农田无人机喷洒模拟系统"
#     title_surface = font.render(title_text, True, (0, 0, 0))
#     title_rect = title_surface.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2))
#     alpha = 0
#     fade_in = True
#     start_time = time.time()
#     duration = 5
#     while time.time() - start_time < duration:
#         for event in pygame.event.get():
#             if event.type == pygame.QUIT:
#                 pygame.quit()
#                 return
#         screen.fill(DEFAULT_BG_COLOR)
#         if fade_in:
#             alpha = min(255, alpha + 5)
#             if alpha == 255:
#                 fade_in = False
#         else:
#             alpha = max(0, alpha - 5)
#         title_surface.set_alpha(alpha)
#         screen.blit(title_surface, title_rect)
#         pygame.display.flip()
#         clock.tick(30)
#     pygame.quit()