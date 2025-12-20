import pygame
import numpy as np
import math
import random
import sys

# --- 全局常量设置 ---
SCREEN_WIDTH = 1000
SCREEN_HEIGHT = 700
FPS = 60

# 树相关常量
TREE_HEIGHT = 350
TRUNK_HEIGHT = 40
BASE_RADIUS = 140

# 颜色定义
BLACK = (0, 0, 0)
GREEN = (34, 139, 34)  # 圣诞树绿色
RED = (255, 0, 0)
YELLOW = (255, 255, 0)
BLUE = (0, 0, 255)
PURPLE = (128, 0, 128)
ORANGE = (255, 165, 0)
GOLD = (255, 215, 0)
SILVER = (192, 192, 192)
WHITE = (255, 255, 255)
PINK = (255, 192, 203)
CYAN = (0, 255, 255)
HEART_COLOR = (255, 105, 180) # 粉红色爱心
GROUND_COLOR = (240, 248, 255) # 地面粒子颜色 (类似 AliceBlue)

# 粒子颜色列表 - 更丰富的颜色
TREE_PARTICLE_COLORS = [GREEN, RED, YELLOW, BLUE, PURPLE, ORANGE, GOLD, SILVER, PINK, CYAN]
BACKGROUND_PARTICLE_COLORS_FAR = [WHITE, (200, 200, 200), (150, 150, 150)] # 后方背景粒子
BACKGROUND_PARTICLE_COLORS_NEAR = [(230, 230, 250), (240, 248, 255), (255, 250, 240)] # 前方背景粒子 (更亮)

# --- 3D 粒子类定义 ---
class Particle3D:
    def __init__(self, x, y, z, color, size, is_decoration=False):
        self.initial_pos = np.array([x, y, z, 1])  # 齐次坐标
        self.color = color
        self.size = size
        self.current_pos = self.initial_pos.copy()
        self.is_decoration = is_decoration
        # 为装饰球添加闪烁效果的参数
        if is_decoration:
            self.original_color = color
            self.blink_speed = random.uniform(0.02, 0.05)
            self.blink_phase = random.uniform(0, 2 * math.pi)

    def rotate_y(self, angle):
        """绕 Y 轴旋转"""
        cos_a = math.cos(angle)
        sin_a = math.sin(angle)
        rotation_matrix = np.array([
            [cos_a,  0, sin_a, 0],
            [0,      1, 0,     0],
            [-sin_a, 0, cos_a, 0],
            [0,      0, 0,     1]
        ])
        self.current_pos = rotation_matrix @ self.initial_pos

    def update(self, time):
        """更新粒子状态，例如装饰球的闪烁"""
        if self.is_decoration:
            # 简单的亮度闪烁效果
            intensity = 0.7 + 0.3 * math.sin(time * self.blink_speed + self.blink_phase)
            r = min(255, max(0, int(self.original_color[0] * intensity)))
            g = min(255, max(0, int(self.original_color[1] * intensity)))
            b = min(255, max(0, int(self.original_color[2] * intensity)))
            self.color = (r, g, b)

    def project_to_2d(self, screen_width, screen_height, fov=320):
        """将3D坐标投影到2D屏幕"""
        x = self.current_pos[0]
        y = self.current_pos[1]
        z = self.current_pos[2]

        # 透视投影
        factor = fov / (fov + z)
        x_proj = x * factor + screen_width / 2
        y_proj = -y * factor + screen_height / 2 # -y 是因为屏幕Y轴向下
        return (int(x_proj), int(y_proj)), int(self.size * factor)

# --- 3D 爱心类定义 ---
class Heart3D:
    def __init__(self, scale=8, y_offset=0):
        self.particles = []
        self.generate_heart(scale, y_offset)

    def generate_heart(self, scale, y_offset):
        """生成3D爱心形状的点云"""
        num_points = 400 # 减少粒子数，因为心形变小了
        t_values = np.linspace(0, 2 * np.pi, 100) # 参数 t
        u_values = np.linspace(-np.pi, np.pi, 100) # 参数 u (用于生成体积)

        # 使用参数方程生成3D爱心点云
        # x = 16 * sin(t)^3
        # y = 13 * cos(t) - 5 * cos(2t) - 2 * cos(3t) - cos(4t)
        # z = 16 * sin(t)^3 * sin(u) (用于厚度)
        for _ in range(num_points):
            t = random.uniform(0, 2 * math.pi)
            u = random.uniform(-math.pi, math.pi)

            # 计算参数方程坐标
            x_param = 16 * (math.sin(t) ** 3)
            y_param = 13 * math.cos(t) - 5 * math.cos(2 * t) - 2 * math.cos(3 * t) - math.cos(4 * t)
            z_param = 16 * (math.sin(t) ** 3) * math.sin(u) # 添加厚度

            # 应用缩放和偏移
            x = x_param * scale
            y = y_param * scale + y_offset # 应用 Y 轴偏移
            z = z_param * scale * 0.5 # 缩小 Z 轴厚度

            color = HEART_COLOR
            size = random.randint(2, 3) # 减小心形粒子大小
            is_decoration = True # 爱心也算作装饰
            self.particles.append(Particle3D(x, y, z, color, size, is_decoration))

    def rotate_y(self, angle):
        """对爱心上的所有粒子绕 Y 轴旋转"""
        for p in self.particles:
            p.rotate_y(angle)

    def update(self, time):
        """更新爱心上粒子的状态"""
        for p in self.particles:
            p.update(time)

    def draw(self, screen):
        """绘制爱心上的所有粒子"""
        for p in self.particles:
            pos_2d, size_2d = p.project_to_2d(SCREEN_WIDTH, SCREEN_HEIGHT)
            if size_2d > 0:
                pygame.draw.circle(screen, p.color, pos_2d, max(1, size_2d))

# --- 银河地面类定义 ---
class GalaxyGround:
    def __init__(self, radius=400, num_particles=2000, y_offset=0): # 添加 y_offset 参数
        self.particles = []
        self.y_offset = y_offset # 保存偏移量
        self.generate_ground(radius, num_particles)

    def generate_ground(self, radius, num_particles):
        """生成一个类似银河的地面粒子盘"""
        for _ in range(num_particles):
            # 使用极坐标生成点，模拟银河盘
            r = random.uniform(0, radius)
            # 为了模拟旋臂，让角度与半径有关
            # theta = random.uniform(0, 2 * math.pi) # 均匀分布
            # 旋臂模拟 (简单版本)
            spiral_tightness = 0.2 # 螺旋的紧密度
            num_arms = 2 # 旋臂数量
            arm_offset = (2 * math.pi / num_arms) * random.randint(0, num_arms - 1)
            theta = arm_offset + spiral_tightness * r + random.uniform(-0.5, 0.5) # 添加随机扰动

            x = r * math.cos(theta)
            z = r * math.sin(theta)
            y = 0 + self.y_offset # 应用 Y 轴偏移，与树干底部对齐

            # 根据距离中心的远近调整粒子大小和亮度
            distance_factor = max(0.1, 1 - r / radius) # 距离越远，值越小
            size = max(1, int(2 * distance_factor + random.randint(0, 1))) # 中心稍大
            # 颜色也可以根据距离调整，这里保持白色系
            color_variance = random.randint(-20, 20)
            color = (
                max(220, min(255, GROUND_COLOR[0] + color_variance)),
                max(220, min(255, GROUND_COLOR[1] + color_variance)),
                max(240, min(255, GROUND_COLOR[2] + color_variance))
            )

            self.particles.append(Particle3D(x, y, z, color, size, is_decoration=False))

    def rotate_y(self, angle):
        """对地面上的所有粒子绕 Y 轴旋转"""
        for p in self.particles:
            p.rotate_y(angle)

    def draw(self, screen):
        """绘制地面上的所有粒子"""
        for p in self.particles:
            pos_2d, size_2d = p.project_to_2d(SCREEN_WIDTH, SCREEN_HEIGHT)
            if size_2d > 0:
                pygame.draw.circle(screen, p.color, pos_2d, max(1, size_2d))

# --- 圣诞树生成函数 ---
def generate_tree_points(num_layers=9, points_per_layer=320, y_offset=-140):
    """生成分层的圣诞树形状的3D点云"""
    points = []
    total_points = num_layers * points_per_layer

    # 使用全局常量
    tree_height = TREE_HEIGHT
    trunk_height = TRUNK_HEIGHT
    base_radius = BASE_RADIUS

    layer_height = (tree_height - trunk_height) / num_layers

    for layer_idx in range(num_layers):
        # 计算当前层的 Y 坐标范围 (从下往上)
        layer_bottom_y = trunk_height + layer_idx * layer_height
        layer_top_y = trunk_height + (layer_idx + 1) * layer_height
        layer_center_y = (layer_bottom_y + layer_top_y) / 2

        # 计算当前层的半径 (从下往上递减)
        layer_radius = base_radius * (1 - layer_idx / num_layers)

        for _ in range(points_per_layer):
            # 在当前层的圆环内随机生成点
            r = random.uniform(0.55 * layer_radius, layer_radius) # 调整内部空隙，使其更饱满
            theta = random.uniform(0, 2 * math.pi)
            x = r * math.cos(theta)
            z = r * math.sin(theta)

            # Y 坐标在当前层高度范围内随机
            y = random.uniform(layer_bottom_y, layer_top_y)
            
            # 应用 Y 轴偏移，使整棵树向下移动
            y += y_offset 

            # 选择颜色
            color = random.choice(TREE_PARTICLE_COLORS)
            size = random.randint(2, 4) # 增大基本粒子大小
            is_decoration = False
            # 有一定概率生成较大的装饰球
            if random.random() < 0.025:  # 2.5% 概率
                color = random.choice([RED, YELLOW, BLUE, GOLD, SILVER, PINK, CYAN])
                size = random.randint(6, 10) # 增大装饰球大小
                is_decoration = True

            points.append(Particle3D(x, y, z, color, size, is_decoration))

    # 添加树干 - 同样应用偏移
    trunk_points = 300 # 增大树干粒子数
    trunk_radius = 20 # 增大树干半径
    trunk_top_y = trunk_height
    for _ in range(trunk_points):
        r = random.uniform(0, trunk_radius)
        theta = random.uniform(0, 2 * math.pi)
        x = r * math.cos(theta)
        z = r * math.sin(theta)
        y = random.uniform(0, trunk_top_y)
        y += y_offset # 对树干也应用偏移
        points.append(Particle3D(x, y, z, (139, 69, 19), random.randint(2, 3), False)) # 棕色树干

    return points

# --- 背景粒子生成函数 ---
def generate_background_particles(num_particles_far=600, num_particles_near=300):
    """生成3D背景粒子，分为远近两层"""
    particles_far = []
    particles_near = []
    
    # 远方背景粒子
    bg_distance_far = 600
    for _ in range(num_particles_far):
        r = random.uniform(bg_distance_far - 150, bg_distance_far + 150)
        theta = random.uniform(0, 2 * math.pi)
        phi = random.uniform(0, math.pi)
        x = r * math.sin(phi) * math.cos(theta)
        # 使用全局常量 TREE_HEIGHT 来计算 Y 坐标
        y = r * math.cos(phi) + 175 - 140 # 应用 Y 轴偏移
        z = r * math.sin(phi) * math.sin(theta)
        color = random.choice(BACKGROUND_PARTICLE_COLORS_FAR)
        size = random.randint(1, 2) # 减小远方粒子大小
        particles_far.append(Particle3D(x, y, z, color, size, False))

    # 近方背景粒子 (在圣诞树和观察者之间)
    bg_distance_near = 200
    for _ in range(num_particles_near):
        # 分布在圣诞树周围的近处空间
        x = random.uniform(-250, 250)
        # 使用全局常量 TREE_HEIGHT 来计算 Y 坐标范围
        y = random.uniform(-50, TREE_HEIGHT + 50 - 140) # 应用 Y 轴偏移
        z = random.uniform(-250, 250)
        # 确保 Z 坐标在观察者和圣诞树之间 (Z < 0)
        if z > 0:
             z = random.uniform(-250, 0) # 确保 z 在负半轴
        color = random.choice(BACKGROUND_PARTICLE_COLORS_NEAR)
        size = random.randint(1, 2) # 减小近方粒子大小
        particles_near.append(Particle3D(x, y, z, color, size, False))
        
    return particles_far, particles_near

# --- 主程序 ---
def main():
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Python 3D 超炫旋转粒子圣诞树 & 爱心 & 银河地面")
    clock = pygame.time.Clock()

    # 定义偏移量
    y_offset = -140 # 统一的 Y 轴偏移量

    # 生成圣诞树点云 (向下移动 140 个单位)
    tree_points = generate_tree_points(num_layers=10, points_per_layer=300, y_offset=y_offset)

    # 生成爱心 (放在树顶，Y 坐标大约是树高 + y_offset，放置在树尖)
    # 树的最高点是 TREE_HEIGHT + y_offset，爱心中心需要再往上一点
    heart_y_offset = TREE_HEIGHT + y_offset + 25 # 调整 25 使其更精确地位于树尖
    heart = Heart3D(scale=6, y_offset=heart_y_offset) # 进一步缩小 scale

    # 生成地面 (应用相同的 Y 轴偏移量，使其与树干底部对齐)
    ground = GalaxyGround(radius=450, num_particles=2500, y_offset=y_offset) # 创建地面对象，并传入偏移量

    # 生成背景粒子
    bg_particles_far, bg_particles_near = generate_background_particles(600, 300) # 分别生成远近粒子

    # 旋转角度
    angle = 0
    rotation_speed = 0.0025 # 弧度/帧, 进一步降低速度
    time_counter = 0 # 用于装饰球闪烁计时

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        # --- 更新 ---
        # 更新旋转角度
        angle += rotation_speed
        if angle > 2 * math.pi:
            angle -= 2 * math.pi
        time_counter += 1

        # 旋转所有圣诞树粒子
        for point in tree_points:
            point.rotate_y(angle)
            point.update(time_counter) # 更新装饰球闪烁

        # 旋转爱心
        heart.rotate_y(angle)
        heart.update(time_counter)

        # 旋转地面
        ground.rotate_y(angle) # 地面同速旋转

        # 旋转所有背景粒子
        for point in bg_particles_far:
             point.rotate_y(angle)
        for point in bg_particles_near:
             point.rotate_y(angle) # 近处粒子也旋转，保持与场景一致

        # --- 绘制 ---
        screen.fill(BLACK)  # 填充黑色背景

        # 绘制远方背景粒子 (最先绘制)
        for point in bg_particles_far:
            pos_2d, size_2d = point.project_to_2d(SCREEN_WIDTH, SCREEN_HEIGHT)
            if size_2d > 0:
                 pygame.draw.circle(screen, point.color, pos_2d, max(1, size_2d))

        # 绘制圣诞树粒子 (后绘制，覆盖在远背景上)
        for point in tree_points:
            pos_2d, size_2d = point.project_to_2d(SCREEN_WIDTH, SCREEN_HEIGHT)
            if size_2d > 0:
                pygame.draw.circle(screen, point.color, pos_2d, max(1, size_2d))

        # 绘制爱心 (与树同一层级，或稍前)
        heart.draw(screen)

        # 绘制地面 (在树和近处粒子之间)
        ground.draw(screen)

        # 绘制近方背景粒子 (最后绘制，覆盖在所有物体前面)
        for point in bg_particles_near:
            pos_2d, size_2d = point.project_to_2d(SCREEN_WIDTH, SCREEN_HEIGHT)
            if size_2d > 0:
                 pygame.draw.circle(screen, point.color, pos_2d, max(1, size_2d))


        # --- 更新显示 ---
        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()