import pygame
import math

class Drone:
    def __init__(self, field):
        self.field = field
        self.x = field.x + 10
        self.y = field.y + 10
        self.speed = 3
        self.path = []
        self.current_target = 0
        self.spraying = False
        self.pesticide = None
        self.spray_radius = 20
        self.spray_cooldown = 10
        self.spray_timer = 0
        self.sprayed_areas = []
    
    def set_path(self, path):
        self.path = path
        self.current_target = 0
    
    def start_spraying(self):
        if self.path and self.pesticide:
            self.spraying = True
            self.current_target = 0
    
    def update(self):
        if not self.spraying or not self.path:
            return
        
        # 移动到当前目标点
        target_x, target_y = self.path[self.current_target]
        
        dx = target_x - self.x
        dy = target_y - self.y
        distance = math.sqrt(dx*dx + dy*dy)
        
        if distance < self.speed:
            self.x = target_x
            self.y = target_y
            self.current_target += 1
            
            # 检查是否到达路径终点
            if self.current_target >= len(self.path):
                self.spraying = False
                self.current_target = 0
        else:
            # 正常移动
            self.x += dx / distance * self.speed
            self.y += dy / distance * self.speed
        
        # 喷洒逻辑
        if self.spraying:
            self.spray_timer += 1
            if self.spray_timer >= self.spray_cooldown:
                self.spray_timer = 0
                self.sprayed_areas.append((self.x, self.y, self.spray_radius))
    
    def draw(self, screen, offset_x=0, offset_y=0):
        # 绘制喷洒区域
        for x, y, radius in self.sprayed_areas:
            pygame.draw.circle(screen, (0, 255, 0, 100), (offset_x + x, offset_y + y), radius, 1)
        
        # 绘制无人机
        drone_color = (0, 0, 255) if self.spraying else (100, 100, 255)
        pygame.draw.circle(screen, drone_color, (offset_x + self.x, offset_y + self.y), 8)
        
        # 绘制路径
        if self.path:
            for i in range(len(self.path) - 1):
                start_pos = (offset_x + self.path[i][0], offset_y + self.path[i][1])
                end_pos = (offset_x + self.path[i+1][0], offset_y + self.path[i+1][1])
                pygame.draw.line(screen, (200, 200, 200), start_pos, end_pos, 1)