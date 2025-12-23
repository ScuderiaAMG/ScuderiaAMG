import pygame
import numpy as np
import math
import random
import sys

SCREEN_WIDTH = 1000
SCREEN_HEIGHT = 700
FPS = 60

TREE_HEIGHT = 350
TRUNK_HEIGHT = 40
BASE_RADIUS = 140

BLACK = (0, 0, 0)
GREEN = (34, 139, 34)
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
HEART_COLOR = (255, 105, 180)
GROUND_COLOR = (240, 248, 255)
TREE_PARTICLE_COLORS = [GREEN, RED, YELLOW, BLUE, PURPLE, ORANGE, GOLD, SILVER, PINK, CYAN]
BACKGROUND_PARTICLE_COLORS_FAR = [WHITE, (200, 200, 200), (150, 150, 150)]
BACKGROUND_PARTICLE_COLORS_NEAR = [(230, 230, 250), (240, 248, 255), (255, 250, 240)]


class Particle3D:
    def __init__(self, x, y, z, color, size, is_decoration=False):
        self.initial_pos = np.array([x, y, z, 1])
        self.color = color
        self.size = size
        self.current_pos = self.initial_pos.copy()
        self.is_decoration = is_decoration
        if is_decoration:
            self.original_color = color
            self.blink_speed = random.uniform(0.02, 0.05)
            self.blink_phase = random.uniform(0, 2 * math.pi)

    def rotate_y(self, angle):
        cos_a = math.cos(angle)
        sin_a = math.sin(angle)
        rotation_matrix = np.array([
            [cos_a, 0, sin_a, 0],
            [0, 1, 0, 0],
            [-sin_a, 0, cos_a, 0],
            [0, 0, 0, 1]
        ])
        self.current_pos = rotation_matrix @ self.initial_pos

    def update(self, time):
        if self.is_decoration:
            intensity = 0.7 + 0.3 * math.sin(time * self.blink_speed + self.blink_phase)
            r = min(255, max(0, int(self.original_color[0] * intensity)))
            g = min(255, max(0, int(self.original_color[1] * intensity)))
            b = min(255, max(0, int(self.original_color[2] * intensity)))
            self.color = (r, g, b)

    def project_to_2d(self, screen_width, screen_height, fov=320):
        x = self.current_pos[0]
        y = self.current_pos[1]
        z = self.current_pos[2]
        factor = fov / (fov + z)
        x_proj = x * factor + screen_width / 2
        y_proj = -y * factor + screen_height / 2
        return (int(x_proj), int(y_proj)), int(self.size * factor)


class Heart3D:
    def __init__(self, scale=8, y_offset=0):
        self.particles = []
        self.generate_heart(scale, y_offset)

    def generate_heart(self, scale, y_offset):
        num_points = 400
        for _ in range(num_points):
            t = random.uniform(0, 2 * math.pi)
            u = random.uniform(-math.pi, math.pi)
            x_param = 16 * (math.sin(t) ** 3)
            y_param = 13 * math.cos(t) - 5 * math.cos(2 * t) - 2 * math.cos(3 * t) - math.cos(4 * t)
            z_param = 16 * (math.sin(t) ** 3) * math.sin(u)
            x = x_param * scale
            y = y_param * scale + y_offset
            z = z_param * scale * 0.5
            color = HEART_COLOR
            size = random.randint(2, 3)
            is_decoration = True
            self.particles.append(Particle3D(x, y, z, color, size, is_decoration))

    def rotate_y(self, angle):
        for p in self.particles:
            p.rotate_y(angle)

    def update(self, time):
        for p in self.particles:
            p.update(time)

    def draw(self, screen):
        for p in self.particles:
            pos_2d, size_2d = p.project_to_2d(SCREEN_WIDTH, SCREEN_HEIGHT)
            if size_2d > 0:
                pygame.draw.circle(screen, p.color, pos_2d, max(1, size_2d))


class GalaxyGround:
    def __init__(self, radius=400, num_particles=2000, y_offset=0):
        self.particles = []
        self.y_offset = y_offset
        self.generate_ground(radius, num_particles)

    def generate_ground(self, radius, num_particles):
        for _ in range(num_particles):
            r = random.uniform(0, radius)
            spiral_tightness = 0.2
            num_arms = 2
            arm_offset = (2 * math.pi / num_arms) * random.randint(0, num_arms - 1)
            theta = arm_offset + spiral_tightness * r + random.uniform(-0.5, 0.5)
            x = r * math.cos(theta)
            z = r * math.sin(theta)
            y = 0 + self.y_offset
            distance_factor = max(0.1, 1 - r / radius)
            size = max(1, int(2 * distance_factor + random.randint(0, 1)))
            color_variance = random.randint(-20, 20)
            color = (
                max(220, min(255, GROUND_COLOR[0] + color_variance)),
                max(220, min(255, GROUND_COLOR[1] + color_variance)),
                max(240, min(255, GROUND_COLOR[2] + color_variance))
            )
            self.particles.append(Particle3D(x, y, z, color, size, is_decoration=False))

    def rotate_y(self, angle):
        for p in self.particles:
            p.rotate_y(angle)

    def draw(self, screen):
        for p in self.particles:
            pos_2d, size_2d = p.project_to_2d(SCREEN_WIDTH, SCREEN_HEIGHT)
            if size_2d > 0:
                pygame.draw.circle(screen, p.color, pos_2d, max(1, size_2d))


def generate_tree_points(num_layers=9, points_per_layer=320, y_offset=-140):
    points = []
    tree_height = TREE_HEIGHT
    trunk_height = TRUNK_HEIGHT
    base_radius = BASE_RADIUS
    layer_height = (tree_height - trunk_height) / num_layers
    for layer_idx in range(num_layers):
        layer_bottom_y = trunk_height + layer_idx * layer_height
        layer_top_y = trunk_height + (layer_idx + 1) * layer_height
        layer_radius = base_radius * (1 - layer_idx / num_layers)
        for _ in range(points_per_layer):
            r = random.uniform(0.55 * layer_radius, layer_radius)
            theta = random.uniform(0, 2 * math.pi)
            x = r * math.cos(theta)
            z = r * math.sin(theta)
            y = random.uniform(layer_bottom_y, layer_top_y)
            y += y_offset
            color = random.choice(TREE_PARTICLE_COLORS)
            size = random.randint(2, 4)
            is_decoration = False
            if random.random() < 0.025:
                color = random.choice([RED, YELLOW, BLUE, GOLD, SILVER, PINK, CYAN])
                size = random.randint(6, 10)
                is_decoration = True
            points.append(Particle3D(x, y, z, color, size, is_decoration))
    trunk_points = 300
    trunk_radius = 20
    trunk_top_y = trunk_height
    for _ in range(trunk_points):
        r = random.uniform(0, trunk_radius)
        theta = random.uniform(0, 2 * math.pi)
        x = r * math.cos(theta)
        z = r * math.sin(theta)
        y = random.uniform(0, trunk_top_y)
        y += y_offset
        points.append(Particle3D(x, y, z, (139, 69, 19), random.randint(2, 3), False))
    return points


def generate_background_particles(num_particles_far=600, num_particles_near=300):
    particles_far = []
    particles_near = []
    bg_distance_far = 600
    for _ in range(num_particles_far):
        r = random.uniform(bg_distance_far - 150, bg_distance_far + 150)
        theta = random.uniform(0, 2 * math.pi)
        phi = random.uniform(0, math.pi)
        x = r * math.sin(phi) * math.cos(theta)
        y = r * math.cos(phi) + 175 - 140
        z = r * math.sin(phi) * math.sin(theta)
        color = random.choice(BACKGROUND_PARTICLE_COLORS_FAR)
        size = random.randint(1, 2)
        particles_far.append(Particle3D(x, y, z, color, size, False))
    bg_distance_near = 200
    for _ in range(num_particles_near):
        x = random.uniform(-250, 250)
        y = random.uniform(-50, TREE_HEIGHT + 50 - 140)
        z = random.uniform(-250, 250)
        if z > 0:
            z = random.uniform(-250, 0)
        color = random.choice(BACKGROUND_PARTICLE_COLORS_NEAR)
        size = random.randint(1, 2)
        particles_near.append(Particle3D(x, y, z, color, size, False))
    return particles_far, particles_near


def main():
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Python 3D 超炫旋转粒子圣诞树 & 爱心 & 银河地面")
    clock = pygame.time.Clock()
    y_offset = -140
    tree_points = generate_tree_points(num_layers=10, points_per_layer=300, y_offset=y_offset)
    heart_y_offset = TREE_HEIGHT + y_offset + 25
    heart = Heart3D(scale=6, y_offset=heart_y_offset)
    ground = GalaxyGround(radius=450, num_particles=2500, y_offset=y_offset)
    bg_particles_far, bg_particles_near = generate_background_particles(600, 300)
    angle = 0
    rotation_speed = 0.0025
    time_counter = 0
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
        angle += rotation_speed
        if angle > 2 * math.pi:
            angle -= 2 * math.pi
        time_counter += 1
        for point in tree_points:
            point.rotate_y(angle)
            point.update(time_counter)
        heart.rotate_y(angle)
        heart.update(time_counter)
        ground.rotate_y(angle)
        for point in bg_particles_far:
            point.rotate_y(angle)
        for point in bg_particles_near:
            point.rotate_y(angle)
        screen.fill(BLACK)
        for point in bg_particles_far:
            pos_2d, size_2d = point.project_to_2d(SCREEN_WIDTH, SCREEN_HEIGHT)
            if size_2d > 0:
                pygame.draw.circle(screen, point.color, pos_2d, max(1, size_2d))
        for point in tree_points:
            pos_2d, size_2d = point.project_to_2d(SCREEN_WIDTH, SCREEN_HEIGHT)
            if size_2d > 0:
                pygame.draw.circle(screen, point.color, pos_2d, max(1, size_2d))
        heart.draw(screen)
        ground.draw(screen)
        for point in bg_particles_near:
            pos_2d, size_2d = point.project_to_2d(SCREEN_WIDTH, SCREEN_HEIGHT)
            if size_2d > 0:
                pygame.draw.circle(screen, point.color, pos_2d, max(1, size_2d))
        pygame.display.flip()
        clock.tick(FPS)
    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()

