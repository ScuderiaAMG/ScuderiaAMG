import pygame
import random

class Field:
    def __init__(self, width, height, x=0, y=0):
        self.width = width
        self.height = height
        self.x = x
        self.y = y
        self.crops = []
        self.disease_level = random.uniform(0.1, 0.5)  # 病害程度
        self.generate_crops()
    
    def generate_crops(self):
        # 生成作物布局
        spacing = 20
        for x in range(self.x + 10, self.x + self.width - 10, spacing):
            for y in range(self.y + 10, self.y + self.height - 10, spacing):
                # 根据病害程度决定作物健康状况
                health = 1.0 - random.random() * self.disease_level
                self.crops.append({
                    'x': x,
                    'y': y,
                    'health': health,
                    'sprayed': False
                })
    
    @staticmethod
    def generate_random_field():
        width = random.randint(300, 500)
        height = random.randint(200, 400)
        return Field(width, height)
    
    def draw(self, screen, offset_x=0, offset_y=0):
        # 绘制农田背景
        pygame.draw.rect(screen, (210, 180, 140), (offset_x + self.x, offset_y + self.y, self.width, self.height))
        pygame.draw.rect(screen, (139, 115, 85), (offset_x + self.x, offset_y + self.y, self.width, self.height), 2)
        
        # 绘制作物
        for crop in self.crops:
            # 根据健康状况决定颜色
            if crop['sprayed']:
                color = (50, 200, 50)  # 已喷洒的颜色
            else:
                health = crop['health']
                if health > 0.7:
                    color = (0, 200, 0)  # 健康
                elif health > 0.4:
                    color = (200, 200, 0)  # 一般
                else:
                    color = (200, 0, 0)  # 不健康
            
            pygame.draw.circle(screen, color, (offset_x + crop['x'], offset_y + crop['y']), 3)