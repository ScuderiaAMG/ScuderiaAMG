import pygame
import time

class AnimationSystem:
    def __init__(self, screen):
        self.screen = screen
        self.font = pygame.font.SysFont("simhei", 36)
    
    def play_welcome_animation(self):
        # 简单的欢迎动画
        for i in range(100):
            self.screen.fill((0, 0, 0))
            
            # 渐入效果
            alpha = i * 2.55
            welcome_text = self.font.render("欢迎使用农田无人机喷洒系统", True, (255, 255, 255))
            welcome_text.set_alpha(alpha)
            
            text_rect = welcome_text.get_rect(center=self.screen.get_rect().center)
            self.screen.blit(welcome_text, text_rect)
            
            pygame.display.flip()
            pygame.time.delay(30)
        
        pygame.time.delay(1000)
    
    def play_exit_animation(self):
        # 简单的退出动画
        for i in range(100, 0, -1):
            self.screen.fill((0, 0, 0))
            
            # 渐出效果
            alpha = i * 2.55
            exit_text = self.font.render("谢谢使用，再见！", True, (255, 255, 255))
            exit_text.set_alpha(alpha)
            
            text_rect = exit_text.get_rect(center=self.screen.get_rect().center)
            self.screen.blit(exit_text, text_rect)
            
            pygame.display.flip()
            pygame.time.delay(30)