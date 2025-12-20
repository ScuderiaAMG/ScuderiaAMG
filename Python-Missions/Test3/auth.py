import pygame
import json
import os
from pygame.locals import *

class AuthSystem:
    def __init__(self):
        self.data_file = "data/users.json"
        self.users = self.load_users()
        
        self.login_input = {"username": "", "password": ""}
        self.register_input = {"username": "", "password": "", "confirm": ""}
        self.active_field = None
        self.error_message = ""
        
        self.font = pygame.font.SysFont("simhei", 24)
        self.title_font = pygame.font.SysFont("simhei", 36)
    
    def load_users(self):
        if os.path.exists(self.data_file):
            try:
                with open(self.data_file, 'r') as f:
                    return json.load(f)
            except:
                return {}
        return {}
    
    def save_users(self):
        os.makedirs(os.path.dirname(self.data_file), exist_ok=True)
        with open(self.data_file, 'w') as f:
            json.dump(self.users, f)
    
    def handle_login_event(self, event, app):
        if event.type == KEYDOWN:
            if event.key == K_TAB:
                self.active_field = "username" if self.active_field != "username" else "password"
            elif event.key == K_RETURN:
                self.login(app)
            elif self.active_field:
                if event.key == K_BACKSPACE:
                    self.login_input[self.active_field] = self.login_input[self.active_field][:-1]
                else:
                    self.login_input[self.active_field] += event.unicode
        elif event.type == MOUSEBUTTONDOWN:
            mouse_pos = pygame.mouse.get_pos()
            # 检查用户名输入框
            if pygame.Rect(350, 250, 300, 40).collidepoint(mouse_pos):
                self.active_field = "username"
            # 检查密码输入框
            elif pygame.Rect(350, 320, 300, 40).collidepoint(mouse_pos):
                self.active_field = "password"
            # 检查登录按钮
            elif pygame.Rect(350, 400, 120, 40).collidepoint(mouse_pos):
                self.login(app)
            # 检查注册按钮
            elif pygame.Rect(530, 400, 120, 40).collidepoint(mouse_pos):
                app.current_state = "register"
        
        elif event.type == MOUSEMOTION:
            self.active_field = None
            mouse_pos = pygame.mouse.get_pos()
            if pygame.Rect(350, 250, 300, 40).collidepoint(mouse_pos):
                self.active_field = "username"
            elif pygame.Rect(350, 320, 300, 40).collidepoint(mouse_pos):
                self.active_field = "password"
    
    def handle_register_event(self, event, app):
        if event.type == KEYDOWN:
            if event.key == K_TAB:
                if self.active_field == "username":
                    self.active_field = "password"
                elif self.active_field == "password":
                    self.active_field = "confirm"
                else:
                    self.active_field = "username"
            elif event.key == K_RETURN:
                self.register(app)
            elif event.key == K_ESCAPE:
                app.current_state = "login"
            elif self.active_field:
                if event.key == K_BACKSPACE:
                    self.register_input[self.active_field] = self.register_input[self.active_field][:-1]
                else:
                    self.register_input[self.active_field] += event.unicode
        elif event.type == MOUSEBUTTONDOWN:
            mouse_pos = pygame.mouse.get_pos()
            # 检查用户名输入框
            if pygame.Rect(350, 200, 300, 40).collidepoint(mouse_pos):
                self.active_field = "username"
            # 检查密码输入框
            elif pygame.Rect(350, 270, 300, 40).collidepoint(mouse_pos):
                self.active_field = "password"
            # 检查确认密码输入框
            elif pygame.Rect(350, 340, 300, 40).collidepoint(mouse_pos):
                self.active_field = "confirm"
            # 检查注册按钮
            elif pygame.Rect(350, 420, 120, 40).collidepoint(mouse_pos):
                self.register(app)
            # 检查返回按钮
            elif pygame.Rect(530, 420, 120, 40).collidepoint(mouse_pos):
                app.current_state = "login"
        
        elif event.type == MOUSEMOTION:
            self.active_field = None
            mouse_pos = pygame.mouse.get_pos()
            if pygame.Rect(350, 200, 300, 40).collidepoint(mouse_pos):
                self.active_field = "username"
            elif pygame.Rect(350, 270, 300, 40).collidepoint(mouse_pos):
                self.active_field = "password"
            elif pygame.Rect(350, 340, 300, 40).collidepoint(mouse_pos):
                self.active_field = "confirm"
    
    def login(self, app):
        username = self.login_input["username"]
        password = self.login_input["password"]
        
        if not username or not password:
            self.error_message = "用户名和密码不能为空"
            return
        
        if username in self.users and self.users[username] == password:
            app.current_user = username
            app.current_state = "main"
            self.error_message = ""
            self.login_input = {"username": "", "password": ""}
        else:
            self.error_message = "用户名或密码错误"
    
    def register(self, app):
        username = self.register_input["username"]
        password = self.register_input["password"]
        confirm = self.register_input["confirm"]
        
        if not username or not password:
            self.error_message = "用户名和密码不能为空"
            return
        
        if password != confirm:
            self.error_message = "两次输入的密码不一致"
            return
        
        if username in self.users:
            self.error_message = "用户名已存在"
            return
        
        self.users[username] = password
        self.save_users()
        self.error_message = "注册成功，请登录"
        app.current_state = "login"
        self.register_input = {"username": "", "password": "", "confirm": ""}
    
    def render_login(self, screen):
        screen.fill((240, 255, 240))
        
        # 绘制标题
        title = self.title_font.render("农田无人机喷洒系统 - 登录", True, (0, 100, 0))
        screen.blit(title, (screen.get_width()//2 - title.get_width()//2, 100))
        
        # 绘制输入框和标签
        username_label = self.font.render("用户名:", True, (0, 0, 0))
        screen.blit(username_label, (250, 250))
        
        password_label = self.font.render("密码:", True, (0, 0, 0))
        screen.blit(password_label, (250, 320))
        
        # 输入框
        pygame.draw.rect(screen, (255, 255, 255), (350, 250, 300, 40))
        pygame.draw.rect(screen, (0, 150, 0) if self.active_field == "username" else (0, 100, 0), 
                         (350, 250, 300, 40), 2)
        
        pygame.draw.rect(screen, (255, 255, 255), (350, 320, 300, 40))
        pygame.draw.rect(screen, (0, 150, 0) if self.active_field == "password" else (0, 100, 0), 
                         (350, 320, 300, 40), 2)
        
        # 输入文本
        username_text = self.font.render(self.login_input["username"], True, (0, 0, 0))
        screen.blit(username_text, (360, 260))
        
        # 密码显示为星号
        password_text = self.font.render("*" * len(self.login_input["password"]), True, (0, 0, 0))
        screen.blit(password_text, (360, 330))
        
        # 按钮
        pygame.draw.rect(screen, (0, 150, 0), (350, 400, 120, 40), border_radius=5)
        login_text = self.font.render("登录", True, (255, 255, 255))
        screen.blit(login_text, (390, 410))
        
        pygame.draw.rect(screen, (0, 150, 0), (530, 400, 120, 40), border_radius=5)
        register_text = self.font.render("注册", True, (255, 255, 255))
        screen.blit(register_text, (570, 410))
        
        # 错误信息
        if self.error_message:
            error_text = self.font.render(self.error_message, True, (255, 0, 0))
            screen.blit(error_text, (350, 360))
    
    def render_register(self, screen):
        screen.fill((240, 255, 240))
        
        # 绘制标题
        title = self.title_font.render("农田无人机喷洒系统 - 注册", True, (0, 100, 0))
        screen.blit(title, (screen.get_width()//2 - title.get_width()//2, 100))
        
        # 绘制输入框和标签
        labels = [
            ("用户名:", 200),
            ("密码:", 270),
            ("确认密码:", 340)
        ]
        
        for text, y in labels:
            label = self.font.render(text, True, (0, 0, 0))
            screen.blit(label, (250, y))
        
        # 输入框
        for i, y in enumerate([200, 270, 340]):
            field_name = list(self.register_input.keys())[i]
            pygame.draw.rect(screen, (255, 255, 255), (350, y, 300, 40))
            pygame.draw.rect(screen, (0, 150, 0) if self.active_field == field_name else (0, 100, 0), 
                             (350, y, 300, 40), 2)
            
            # 输入文本 (密码显示为星号)
            display_text = self.register_input[field_name]
            if field_name != "username":
                display_text = "*" * len(display_text)
                
            field_text = self.font.render(display_text, True, (0, 0, 0))
            screen.blit(field_text, (360, y + 10))
        
        # 按钮
        pygame.draw.rect(screen, (0, 150, 0), (350, 420, 120, 40), border_radius=5)
        register_text = self.font.render("注册", True, (255, 255, 255))
        screen.blit(register_text, (390, 430))
        
        pygame.draw.rect(screen, (0, 150, 0), (530, 420, 120, 40), border_radius=5)
        back_text = self.font.render("返回", True, (255, 255, 255))
        screen.blit(back_text, (570, 430))
        
        # 错误信息
        if self.error_message:
            error_text = self.font.render(self.error_message, True, (255, 0, 0))
            screen.blit(error_text, (350, 380))