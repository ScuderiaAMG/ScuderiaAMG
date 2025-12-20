import pygame
import sys
import json
import time
from pygame.locals import *
from auth import AuthSystem
from animation import AnimationSystem
from drone import Drone
from field import Field
from pesticide import PesticideManager
from path_planning import PathPlanner

class FarmDroneApp:
    def __init__(self):
        pygame.init()
        self.screen_width, self.screen_height = 1000, 700
        self.screen = pygame.display.set_mode((self.screen_width, self.screen_height))
        pygame.display.set_caption("农田无人机喷洒农药模拟系统")
        
        self.clock = pygame.time.Clock()
        self.fps = 60
        
        self.auth_system = AuthSystem()
        self.animation_system = AnimationSystem(self.screen)
        
        self.current_user = None
        self.current_state = "welcome"  # welcome, login, register, main, exit
        
        # 主界面组件
        self.field = None
        self.drone = None
        self.pesticide_manager = PesticideManager()
        self.path_planner = PathPlanner()
        
        self.buttons = {}
        self.font = pygame.font.SysFont("simhei", 24)
        self.title_font = pygame.font.SysFont("simhei", 36)
        
    def run(self):
        self.animation_system.play_welcome_animation()
        self.current_state = "login"
        
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == QUIT:
                    running = False
                self.handle_event(event)
            
            self.update()
            self.render()
            
            pygame.display.flip()
            self.clock.tick(self.fps)
        
        self.animation_system.play_exit_animation()
        pygame.quit()
        sys.exit()
    
    def handle_event(self, event):
        if self.current_state == "login":
            self.auth_system.handle_login_event(event, self)
        elif self.current_state == "register":
            self.auth_system.handle_register_event(event, self)
        elif self.current_state == "main":
            self.handle_main_events(event)
    
    def handle_main_events(self, event):
        if event.type == MOUSEBUTTONDOWN:
            mouse_pos = pygame.mouse.get_pos()
            for button_name, button_rect in self.buttons.items():
                if button_rect.collidepoint(mouse_pos):
                    self.handle_button_click(button_name)
    
    def handle_button_click(self, button_name):
        if button_name == "logout":
            self.current_user = None
            self.current_state = "login"
        elif button_name == "exit":
            self.current_state = "exit"
        elif button_name == "field_new":
            self.field = Field.generate_random_field()
        elif button_name == "drone_deploy":
            if self.field:
                self.drone = Drone(self.field)
        elif button_name == "pesticide_mix":
            if self.drone:
                self.drone.pesticide = self.pesticide_manager.create_custom_mix()
        elif button_name == "plan_path":
            if self.drone and self.field:
                path = self.path_planner.plan_path(self.field)
                self.drone.set_path(path)
        elif button_name == "start_spray":
            if self.drone and self.drone.path:
                self.drone.start_spraying()
    
    def update(self):
        if self.current_state == "main" and self.drone:
            self.drone.update()
    
    def render(self):
        if self.current_state == "login":
            self.auth_system.render_login(self.screen)
        elif self.current_state == "register":
            self.auth_system.render_register(self.screen)
        elif self.current_state == "main":
            self.render_main_screen()
    
    def render_main_screen(self):
        # 绘制背景
        self.screen.fill((240, 255, 240))
        
        # 绘制标题
        title = self.title_font.render("农田无人机喷洒农药模拟系统", True, (0, 100, 0))
        self.screen.blit(title, (self.screen_width//2 - title.get_width()//2, 20))
        
        # 绘制用户信息
        user_text = self.font.render(f"用户: {self.current_user}", True, (0, 0, 0))
        self.screen.blit(user_text, (20, 20))
        
        # 绘制农田和无人机
        if self.field:
            self.field.draw(self.screen, 100, 100)
        
        if self.drone:
            self.drone.draw(self.screen, 100, 100)
        
        # 绘制控制按钮
        self.draw_buttons()
        
        # 绘制状态信息
        status = self.get_status_text()
        status_text = self.font.render(status, True, (0, 0, 0))
        self.screen.blit(status_text, (20, 60))
    
    def draw_buttons(self):
        button_y = 500
        button_width, button_height = 150, 40
        button_margin = 20
        
        buttons = [
            ("field_new", "新建农田"),
            ("drone_deploy", "部署无人机"),
            ("pesticide_mix", "配置农药"),
            ("plan_path", "规划路径"),
            ("start_spray", "开始喷洒"),
            ("logout", "退出登录"),
            ("exit", "退出系统")
        ]
        
        self.buttons = {}
        for i, (name, text) in enumerate(buttons):
            x = 100 + i * (button_width + button_margin)
            if x + button_width > self.screen_width - 100:
                x = 100
                button_y += button_height + button_margin
            
            button_rect = pygame.Rect(x, button_y, button_width, button_height)
            pygame.draw.rect(self.screen, (0, 150, 0), button_rect, border_radius=5)
            pygame.draw.rect(self.screen, (0, 100, 0), button_rect, 2, border_radius=5)
            
            button_text = self.font.render(text, True, (255, 255, 255))
            text_rect = button_text.get_rect(center=button_rect.center)
            self.screen.blit(button_text, text_rect)
            
            self.buttons[name] = button_rect
    
    def get_status_text(self):
        if not self.field:
            return "状态: 请先创建农田"
        if not self.drone:
            return "状态: 请部署无人机"
        if not self.drone.pesticide:
            return "状态: 请配置农药"
        if not self.drone.path:
            return "状态: 请规划路径"
        if self.drone.spraying:
            return "状态: 喷洒中..."
        return "状态: 就绪，可以开始喷洒"