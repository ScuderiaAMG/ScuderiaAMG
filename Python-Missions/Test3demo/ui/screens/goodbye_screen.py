"""
ui/screens/goodbye_screen.py

显示程序结束动画。
"""
import pygame
import time
from config import WINDOW_WIDTH, WINDOW_HEIGHT, WINDOW_TITLE, DEFAULT_BG_COLOR

def show_goodbye_animation():
    """
    显示结束动画。
    """
    pygame.init()
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    pygame.display.set_caption(f"{WINDOW_TITLE} - 再见")

    clock = pygame.time.Clock()
    font = pygame.font.SysFont(None, 48)
    text = font.render("感谢使用，再见！", True, (0, 0, 0))
    text_rect = text.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2))

    running = True
    start_time = time.time()
    duration = 2 # 结束动画持续2秒

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        screen.fill(DEFAULT_BG_COLOR)
        screen.blit(text, text_rect)
        pygame.display.flip()

        clock.tick(30)

        if time.time() - start_time >= duration:
            running = False

    pygame.quit()