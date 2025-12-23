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




# # # # # import pygame
# # # # # import numpy as np
# # # # # import math
# # # # # import random
# # # # # import sys

# # # # # SCREEN_WIDTH = 1200
# # # # # SCREEN_HEIGHT = 900
# # # # # FPS = 60

# # # # # TREE_HEIGHT = 400
# # # # # TRUNK_HEIGHT = 50
# # # # # BASE_RADIUS = 160

# # # # # BLACK = (0, 0, 0)
# # # # # GREEN = (34, 139, 34)
# # # # # RED = (255, 0, 0)
# # # # # YELLOW = (255, 255, 0)
# # # # # BLUE = (0, 0, 255)
# # # # # PURPLE = (128, 0, 128)
# # # # # ORANGE = (255, 165, 0)
# # # # # GOLD = (255, 215, 0)
# # # # # SILVER = (192, 192, 192)
# # # # # WHITE = (255, 255, 255)
# # # # # PINK = (255, 192, 203)
# # # # # CYAN = (0, 255, 255)
# # # # # HEART_COLOR = (255, 105, 180)
# # # # # HEART_COLOR_2 = (255, 20, 147)
# # # # # GROUND_COLOR = (240, 248, 255)
# # # # # SKY_COLOR = (5, 5, 25)
# # # # # TREE_PARTICLE_COLORS = [GREEN, RED, YELLOW, BLUE, PURPLE, ORANGE, GOLD, SILVER, PINK, CYAN]
# # # # # BACKGROUND_PARTICLE_COLORS_FAR = [(255, 255, 255), (200, 220, 255), (220, 200, 255), (200, 255, 200)]
# # # # # BACKGROUND_PARTICLE_COLORS_NEAR = [(230, 230, 250), (240, 248, 255), (255, 250, 240), (255, 245, 238)]

# # # # # class Particle3D:
# # # # #     def __init__(self, x, y, z, color, size, is_decoration=False, is_sparkle=False):
# # # # #         self.initial_pos = np.array([x, y, z, 1])
# # # # #         self.color = color
# # # # #         self.original_color = color
# # # # #         self.size = size
# # # # #         self.original_size = size
# # # # #         self.current_pos = self.initial_pos.copy()
# # # # #         self.is_decoration = is_decoration
# # # # #         self.is_sparkle = is_sparkle
# # # # #         self.rotation_speed = random.uniform(-0.01, 0.01)
# # # # #         self.rotation_angle = random.uniform(0, 2*math.pi)
# # # # #         self.float_speed = random.uniform(0.01, 0.03)
# # # # #         self.float_phase = random.uniform(0, 2*math.pi)
# # # # #         if is_decoration:
# # # # #             self.blink_speed = random.uniform(0.02, 0.08)
# # # # #             self.blink_phase = random.uniform(0, 2*math.pi)
# # # # #         if is_sparkle:
# # # # #             self.sparkle_speed = random.uniform(0.05, 0.1)
# # # # #             self.sparkle_phase = random.uniform(0, 2*math.pi)

# # # # #     def rotate_y(self, angle):
# # # # #         cos_a = math.cos(angle)
# # # # #         sin_a = math.sin(angle)
# # # # #         rotation_matrix = np.array([
# # # # #             [cos_a, 0, sin_a, 0],
# # # # #             [0, 1, 0, 0],
# # # # #             [-sin_a, 0, cos_a, 0],
# # # # #             [0, 0, 0, 1]
# # # # #         ])
# # # # #         self.current_pos = rotation_matrix @ self.initial_pos

# # # # #     def update(self, time):
# # # # #         if self.is_sparkle:
# # # # #             self.rotation_angle += self.rotation_speed
# # # # #             offset = math.sin(time * self.float_speed + self.float_phase) * 5
# # # # #             self.current_pos[1] = self.initial_pos[1] + offset
            
# # # # #             intensity = 0.6 + 0.4 * math.sin(time * self.sparkle_speed + self.sparkle_phase)
# # # # #             r = min(255, max(0, int(self.original_color[0] * intensity)))
# # # # #             g = min(255, max(0, int(self.original_color[1] * intensity)))
# # # # #             b = min(255, max(0, int(self.original_color[2] * intensity)))
# # # # #             self.color = (r, g, b)
# # # # #             self.size = self.original_size * (0.8 + 0.2 * intensity)
            
# # # # #         elif self.is_decoration:
# # # # #             intensity = 0.7 + 0.3 * math.sin(time * self.blink_speed + self.blink_phase)
# # # # #             r = min(255, max(0, int(self.original_color[0] * intensity)))
# # # # #             g = min(255, max(0, int(self.original_color[1] * intensity)))
# # # # #             b = min(255, max(0, int(self.original_color[2] * intensity)))
# # # # #             self.color = (r, g, b)
# # # # #             self.size = self.original_size * (0.9 + 0.1 * intensity)

# # # # #     def project_to_2d(self, screen_width, screen_height, fov=320):
# # # # #         x = self.current_pos[0]
# # # # #         y = self.current_pos[1]
# # # # #         z = self.current_pos[2]
# # # # #         factor = fov / (fov + z)
# # # # #         x_proj = x * factor + screen_width / 2
# # # # #         y_proj = -y * factor + screen_height / 2
# # # # #         return (int(x_proj), int(y_proj)), int(self.size * factor)


# # # # # class Heart3D:
# # # # #     def __init__(self, scale=10, y_offset=0):
# # # # #         self.particles = []
# # # # #         self.generate_heart(scale, y_offset)

# # # # #     def generate_heart(self, scale, y_offset):
# # # # #         num_points = 600
# # # # #         for _ in range(num_points):
# # # # #             t = random.uniform(0, 2 * math.pi)
# # # # #             u = random.uniform(-math.pi, math.pi)
# # # # #             x_param = 16 * (math.sin(t) ** 3)
# # # # #             y_param = 13 * math.cos(t) - 5 * math.cos(2 * t) - 2 * math.cos(3 * t) - math.cos(4 * t)
# # # # #             z_param = 16 * (math.sin(t) ** 3) * math.sin(u)
# # # # #             x = x_param * scale
# # # # #             y = y_param * scale + y_offset
# # # # #             z = z_param * scale * 0.5
# # # # #             if random.random() < 0.7:
# # # # #                 color = HEART_COLOR
# # # # #             else:
# # # # #                 color = HEART_COLOR_2
# # # # #             size = random.randint(2, 4)
# # # # #             is_decoration = True
# # # # #             self.particles.append(Particle3D(x, y, z, color, size, is_decoration))

# # # # #     def rotate_y(self, angle):
# # # # #         for p in self.particles:
# # # # #             p.rotate_y(angle)

# # # # #     def update(self, time):
# # # # #         for p in self.particles:
# # # # #             p.update(time)

# # # # #     def draw(self, screen):
# # # # #         for p in self.particles:
# # # # #             pos_2d, size_2d = p.project_to_2d(SCREEN_WIDTH, SCREEN_HEIGHT)
# # # # #             if size_2d > 0:
# # # # #                 pygame.draw.circle(screen, p.color, pos_2d, max(1, size_2d))
# # # # #                 if size_2d > 2:
# # # # #                     pygame.draw.circle(screen, (255, 255, 255), pos_2d, max(1, size_2d//2))


# # # # # class GalaxyGround:
# # # # #     def __init__(self, radius=500, num_particles=3000, y_offset=0):
# # # # #         self.particles = []
# # # # #         self.y_offset = y_offset
# # # # #         self.generate_ground(radius, num_particles)

# # # # #     def generate_ground(self, radius, num_particles):
# # # # #         for _ in range(num_particles):
# # # # #             r = random.uniform(0, radius)
# # # # #             spiral_tightness = 0.2
# # # # #             num_arms = 3
# # # # #             arm_offset = (2 * math.pi / num_arms) * random.randint(0, num_arms - 1)
# # # # #             theta = arm_offset + spiral_tightness * r + random.uniform(-0.3, 0.3)
# # # # #             x = r * math.cos(theta)
# # # # #             z = r * math.sin(theta)
# # # # #             y = 0 + self.y_offset
            
# # # # #             arm_index = int(arm_offset * num_arms / (2 * math.pi)) % 3
# # # # #             if arm_index == 0:
# # # # #                 base_color = (173, 216, 230)
# # # # #             elif arm_index == 1:
# # # # #                 base_color = (221, 160, 221)
# # # # #             else:
# # # # #                 base_color = (240, 248, 255)
            
# # # # #             distance_factor = max(0.1, 1 - r / radius)
# # # # #             color_variance = random.randint(-15, 15)
# # # # #             color = (
# # # # #                 max(180, min(255, base_color[0] + color_variance)),
# # # # #                 max(180, min(255, base_color[1] + color_variance)),
# # # # #                 max(200, min(255, base_color[2] + color_variance))
# # # # #             )
            
# # # # #             size = max(1, int(3 * distance_factor + random.randint(0, 2)))
# # # # #             is_sparkle = (random.random() < 0.1)
# # # # #             self.particles.append(Particle3D(x, y, z, color, size, is_decoration=False, is_sparkle=is_sparkle))

# # # # #     def rotate_y(self, angle):
# # # # #         for p in self.particles:
# # # # #             p.rotate_y(angle)

# # # # #     def update(self, time):
# # # # #         for p in self.particles:
# # # # #             p.update(time)

# # # # #     def draw(self, screen):
# # # # #         for p in self.particles:
# # # # #             pos_2d, size_2d = p.project_to_2d(SCREEN_WIDTH, SCREEN_HEIGHT)
# # # # #             if size_2d > 0:
# # # # #                 pygame.draw.circle(screen, p.color, pos_2d, max(1, size_2d))
# # # # #                 if p.is_sparkle and size_2d > 2:
# # # # #                     pygame.draw.circle(screen, (255, 255, 255), pos_2d, max(1, size_2d//2))


# # # # # class StarField:
# # # # #     def __init__(self, num_stars=800):
# # # # #         self.stars = []
# # # # #         self.generate_stars(num_stars)

# # # # #     def generate_stars(self, num_stars):
# # # # #         for _ in range(num_stars):
# # # # #             r = random.uniform(500, 1000)
# # # # #             theta = random.uniform(0, 2 * math.pi)
# # # # #             phi = random.uniform(0, math.pi)
# # # # #             x = r * math.sin(phi) * math.cos(theta)
# # # # #             y = r * math.cos(phi) + 200
# # # # #             z = r * math.sin(phi) * math.sin(theta)
            
# # # # #             brightness = random.uniform(0.3, 1.0)
# # # # #             color_value = int(200 + 55 * brightness)
# # # # #             color = (color_value, color_value, color_value)
# # # # #             size = random.randint(1, 3)
# # # # #             is_sparkle = (random.random() < 0.3)
# # # # #             self.stars.append(Particle3D(x, y, z, color, size, is_decoration=False, is_sparkle=is_sparkle))

# # # # #     def rotate_y(self, angle):
# # # # #         for star in self.stars:
# # # # #             star.rotate_y(angle)

# # # # #     def update(self, time):
# # # # #         for star in self.stars:
# # # # #             star.update(time)

# # # # #     def draw(self, screen):
# # # # #         for star in self.stars:
# # # # #             pos_2d, size_2d = star.project_to_2d(SCREEN_WIDTH, SCREEN_HEIGHT)
# # # # #             if size_2d > 0:
# # # # #                 pygame.draw.circle(screen, star.color, pos_2d, max(1, size_2d))
# # # # #                 if star.is_sparkle and size_2d > 1:
# # # # #                     pygame.draw.circle(screen, (255, 255, 255), pos_2d, max(1, size_2d//2))


# # # # # class FloatingParticles:
# # # # #     def __init__(self, num_particles=400):
# # # # #         self.particles = []
# # # # #         self.generate_particles(num_particles)

# # # # #     def generate_particles(self, num_particles):
# # # # #         for _ in range(num_particles):
# # # # #             x = random.uniform(-300, 300)
# # # # #             y = random.uniform(-100, TREE_HEIGHT + 100)
# # # # #             z = random.uniform(-300, -50)
# # # # #             color_choice = random.choice([(255, 182, 193), (173, 216, 230), (255, 250, 205), (230, 230, 250)])
# # # # #             color = color_choice
# # # # #             size = random.randint(2, 5)
# # # # #             is_sparkle = True
# # # # #             self.particles.append(Particle3D(x, y, z, color, size, is_decoration=False, is_sparkle=is_sparkle))

# # # # #     def rotate_y(self, angle):
# # # # #         for p in self.particles:
# # # # #             p.rotate_y(angle)

# # # # #     def update(self, time):
# # # # #         for p in self.particles:
# # # # #             p.update(time)

# # # # #     def draw(self, screen):
# # # # #         for p in self.particles:
# # # # #             pos_2d, size_2d = p.project_to_2d(SCREEN_WIDTH, SCREEN_HEIGHT)
# # # # #             if size_2d > 0:
# # # # #                 pygame.draw.circle(screen, p.color, pos_2d, max(1, size_2d))
# # # # #                 if size_2d > 2:
# # # # #                     pygame.draw.circle(screen, (255, 255, 255), pos_2d, max(1, size_2d//2))


# # # # # def generate_tree_points(num_layers=12, points_per_layer=350, y_offset=-140):
# # # # #     points = []
# # # # #     tree_height = TREE_HEIGHT
# # # # #     trunk_height = TRUNK_HEIGHT
# # # # #     base_radius = BASE_RADIUS
# # # # #     layer_height = (tree_height - trunk_height) / num_layers
# # # # #     for layer_idx in range(num_layers):
# # # # #         layer_bottom_y = trunk_height + layer_idx * layer_height
# # # # #         layer_top_y = trunk_height + (layer_idx + 1) * layer_height
# # # # #         layer_radius = base_radius * (1 - layer_idx / num_layers)
# # # # #         for _ in range(points_per_layer):
# # # # #             r = random.uniform(0.5 * layer_radius, layer_radius)
# # # # #             theta = random.uniform(0, 2 * math.pi)
# # # # #             x = r * math.cos(theta)
# # # # #             z = r * math.sin(theta)
# # # # #             y = random.uniform(layer_bottom_y, layer_top_y)
# # # # #             y += y_offset
# # # # #             color = random.choice(TREE_PARTICLE_COLORS)
# # # # #             size = random.randint(2, 4)
# # # # #             is_decoration = False
# # # # #             if random.random() < 0.06:
# # # # #                 color = random.choice([RED, YELLOW, GOLD, PINK, CYAN, (255, 215, 0), (255, 105, 180)])
# # # # #                 size = random.randint(8, 12)
# # # # #                 is_decoration = True
# # # # #             elif random.random() < 0.02:
# # # # #                 color = WHITE
# # # # #                 size = random.randint(6, 10)
# # # # #                 is_decoration = True
# # # # #             points.append(Particle3D(x, y, z, color, size, is_decoration))
    
# # # # #     trunk_points = 400
# # # # #     trunk_radius = 25
# # # # #     trunk_top_y = trunk_height
# # # # #     for _ in range(trunk_points):
# # # # #         r = random.uniform(0, trunk_radius)
# # # # #         theta = random.uniform(0, 2 * math.pi)
# # # # #         x = r * math.cos(theta)
# # # # #         z = r * math.sin(theta)
# # # # #         y = random.uniform(0, trunk_top_y)
# # # # #         y += y_offset
# # # # #         points.append(Particle3D(x, y, z, (139, 69, 19), random.randint(3, 4), False))
    
# # # # #     for _ in range(200):
# # # # #         r = random.uniform(trunk_radius + 10, trunk_radius + 30)
# # # # #         theta = random.uniform(0, 2 * math.pi)
# # # # #         x = r * math.cos(theta)
# # # # #         z = r * math.sin(theta)
# # # # #         y = random.uniform(0, trunk_top_y)
# # # # #         y += y_offset
# # # # #         color = random.choice([(160, 82, 45), (101, 67, 33)])
# # # # #         points.append(Particle3D(x, y, z, color, random.randint(2, 3), False))
    
# # # # #     return points


# # # # # def generate_background_particles(num_particles_far=800, num_particles_near=400):
# # # # #     particles_far = []
# # # # #     particles_near = []
# # # # #     bg_distance_far = 700
# # # # #     for _ in range(num_particles_far):
# # # # #         r = random.uniform(bg_distance_far - 200, bg_distance_far + 200)
# # # # #         theta = random.uniform(0, 2 * math.pi)
# # # # #         phi = random.uniform(0, math.pi)
# # # # #         x = r * math.sin(phi) * math.cos(theta)
# # # # #         y = r * math.cos(phi) + 200
# # # # #         z = r * math.sin(phi) * math.sin(theta)
# # # # #         color = random.choice(BACKGROUND_PARTICLE_COLORS_FAR)
# # # # #         size = random.randint(1, 3)
# # # # #         particles_far.append(Particle3D(x, y, z, color, size, False))
    
# # # # #     bg_distance_near = 300
# # # # #     for _ in range(num_particles_near):
# # # # #         x = random.uniform(-350, 350)
# # # # #         y = random.uniform(-80, TREE_HEIGHT + 80)
# # # # #         z = random.uniform(-350, 0)
# # # # #         color = random.choice(BACKGROUND_PARTICLE_COLORS_NEAR)
# # # # #         size = random.randint(2, 4)
# # # # #         particles_near.append(Particle3D(x, y, z, color, size, False))
    
# # # # #     return particles_far, particles_near


# # # # # def main():
# # # # #     pygame.init()
# # # # #     screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
# # # # #     pygame.display.set_caption("超炫3D圣诞树：银河之心")
# # # # #     clock = pygame.time.Clock()
    
# # # # #     y_offset = -140
# # # # #     tree_points = generate_tree_points(num_layers=12, points_per_layer=350, y_offset=y_offset)
# # # # #     heart_y_offset = TREE_HEIGHT + y_offset + 30
# # # # #     heart = Heart3D(scale=8, y_offset=heart_y_offset)
# # # # #     ground = GalaxyGround(radius=500, num_particles=3000, y_offset=y_offset)
# # # # #     starfield = StarField(num_stars=800)
# # # # #     floating = FloatingParticles(num_particles=400)
# # # # #     bg_particles_far, bg_particles_near = generate_background_particles(800, 400)
    
# # # # #     angle = 0
# # # # #     rotation_speed = 0.003
# # # # #     time_counter = 0
# # # # #     running = True
    
# # # # #     while running:
# # # # #         for event in pygame.event.get():
# # # # #             if event.type == pygame.QUIT:
# # # # #                 running = False
# # # # #             elif event.type == pygame.KEYDOWN:
# # # # #                 if event.key == pygame.K_UP:
# # # # #                     rotation_speed = min(0.01, rotation_speed + 0.0005)
# # # # #                 elif event.key == pygame.K_DOWN:
# # # # #                     rotation_speed = max(0.001, rotation_speed - 0.0005)
        
# # # # #         angle += rotation_speed
# # # # #         if angle > 2 * math.pi:
# # # # #             angle -= 2 * math.pi
        
# # # # #         time_counter += 1
        
# # # # #         for point in tree_points:
# # # # #             point.rotate_y(angle)
# # # # #             point.update(time_counter)
        
# # # # #         heart.rotate_y(angle)
# # # # #         heart.update(time_counter)
# # # # #         ground.rotate_y(angle)
# # # # #         ground.update(time_counter)
# # # # #         starfield.rotate_y(angle)
# # # # #         starfield.update(time_counter)
# # # # #         floating.rotate_y(angle)
# # # # #         floating.update(time_counter)
        
# # # # #         for point in bg_particles_far:
# # # # #             point.rotate_y(angle)
        
# # # # #         for point in bg_particles_near:
# # # # #             point.rotate_y(angle)
        
# # # # #         screen.fill(SKY_COLOR)
        
# # # # #         starfield.draw(screen)
        
# # # # #         for point in bg_particles_far:
# # # # #             pos_2d, size_2d = point.project_to_2d(SCREEN_WIDTH, SCREEN_HEIGHT)
# # # # #             if size_2d > 0:
# # # # #                 pygame.draw.circle(screen, point.color, pos_2d, max(1, size_2d))
        
# # # # #         ground.draw(screen)
        
# # # # #         for point in tree_points:
# # # # #             pos_2d, size_2d = point.project_to_2d(SCREEN_WIDTH, SCREEN_HEIGHT)
# # # # #             if size_2d > 0:
# # # # #                 pygame.draw.circle(screen, point.color, pos_2d, max(1, size_2d))
# # # # #                 if point.is_decoration and size_2d > 3:
# # # # #                     pygame.draw.circle(screen, (255, 255, 255), pos_2d, max(1, size_2d//3))
        
# # # # #         heart.draw(screen)
# # # # #         floating.draw(screen)
        
# # # # #         for point in bg_particles_near:
# # # # #             pos_2d, size_2d = point.project_to_2d(SCREEN_WIDTH, SCREEN_HEIGHT)
# # # # #             if size_2d > 0:
# # # # #                 pygame.draw.circle(screen, point.color, pos_2d, max(1, size_2d))
        
# # # # #         font = pygame.font.SysFont(None, 24)
# # # # #         info_text = f"旋转速度: {rotation_speed:.4f} (上下方向键调整)"
# # # # #         text_surface = font.render(info_text, True, (200, 200, 200))
# # # # #         screen.blit(text_surface, (10, 10))
        
# # # # #         pygame.display.flip()
# # # # #         clock.tick(FPS)
    
# # # # #     pygame.quit()
# # # # #     sys.exit()


# # # # # if __name__ == "__main__":
# # # # #     main()






# # # # import pygame
# # # # import numpy as np
# # # # import math
# # # # import random
# # # # import sys

# # # # SCREEN_WIDTH = 1200
# # # # SCREEN_HEIGHT = 900
# # # # FPS = 60

# # # # TREE_HEIGHT = 400
# # # # TRUNK_HEIGHT = 50
# # # # BASE_RADIUS = 160

# # # # BLACK = (0, 0, 0)
# # # # GREEN = (34, 139, 34)
# # # # RED = (255, 0, 0)
# # # # YELLOW = (255, 255, 0)
# # # # BLUE = (0, 0, 255)
# # # # PURPLE = (128, 0, 128)
# # # # ORANGE = (255, 165, 0)
# # # # GOLD = (255, 215, 0)
# # # # SILVER = (192, 192, 192)
# # # # WHITE = (255, 255, 255)
# # # # PINK = (255, 192, 203)
# # # # CYAN = (0, 255, 255)
# # # # HEART_COLOR = (255, 105, 180)
# # # # HEART_COLOR_2 = (255, 20, 147)
# # # # GROUND_COLOR = (240, 248, 255)
# # # # TREE_PARTICLE_COLORS = [GREEN, RED, YELLOW, BLUE, PURPLE, ORANGE, GOLD, SILVER, PINK, CYAN]
# # # # BACKGROUND_PARTICLE_COLORS_FAR = [(255, 255, 255), (200, 220, 255), (220, 200, 255), (200, 255, 200)]
# # # # BACKGROUND_PARTICLE_COLORS_NEAR = [(230, 230, 250), (240, 248, 255), (255, 250, 240), (255, 245, 238)]

# # # # class GradientBackground:
# # # #     def __init__(self, width, height):
# # # #         self.width = width
# # # #         self.height = height
# # # #         self.gradient_surface = self.create_gradient()
    
# # # #     def create_gradient(self):
# # # #         surface = pygame.Surface((self.width, self.height))
        
# # # #         top_color = (255, 240, 245)
# # # #         middle_color = (230, 230, 250)
# # # #         bottom_color = (220, 230, 255)
        
# # # #         for y in range(self.height):
# # # #             if y < self.height // 2:
# # # #                 ratio = y / (self.height // 2)
# # # #                 r = top_color[0] * (1 - ratio) + middle_color[0] * ratio
# # # #                 g = top_color[1] * (1 - ratio) + middle_color[1] * ratio
# # # #                 b = top_color[2] * (1 - ratio) + middle_color[2] * ratio
# # # #             else:
# # # #                 ratio = (y - self.height // 2) / (self.height // 2)
# # # #                 r = middle_color[0] * (1 - ratio) + bottom_color[0] * ratio
# # # #                 g = middle_color[1] * (1 - ratio) + bottom_color[1] * ratio
# # # #                 b = middle_color[2] * (1 - ratio) + bottom_color[2] * ratio
            
# # # #             color = (int(r), int(g), int(b))
# # # #             pygame.draw.line(surface, color, (0, y), (self.width, y))
        
# # # #         star_count = 50
# # # #         for _ in range(star_count):
# # # #             x = random.randint(0, self.width)
# # # #             y = random.randint(0, self.height)
# # # #             size = random.randint(1, 3)
# # # #             brightness = random.randint(180, 230)
# # # #             color = (brightness, brightness, brightness)
# # # #             pygame.draw.circle(surface, color, (x, y), size)
        
# # # #         return surface
    
# # # #     def draw(self, screen):
# # # #         screen.blit(self.gradient_surface, (0, 0))

# # # # class Particle3D:
# # # #     def __init__(self, x, y, z, color, size, is_decoration=False, is_sparkle=False):
# # # #         self.initial_pos = np.array([x, y, z, 1])
# # # #         self.color = color
# # # #         self.original_color = color
# # # #         self.size = size
# # # #         self.original_size = size
# # # #         self.current_pos = self.initial_pos.copy()
# # # #         self.is_decoration = is_decoration
# # # #         self.is_sparkle = is_sparkle
# # # #         self.rotation_speed = random.uniform(-0.01, 0.01)
# # # #         self.rotation_angle = random.uniform(0, 2*math.pi)
# # # #         self.float_speed = random.uniform(0.01, 0.03)
# # # #         self.float_phase = random.uniform(0, 2*math.pi)
# # # #         if is_decoration:
# # # #             self.blink_speed = random.uniform(0.02, 0.08)
# # # #             self.blink_phase = random.uniform(0, 2*math.pi)
# # # #         if is_sparkle:
# # # #             self.sparkle_speed = random.uniform(0.05, 0.1)
# # # #             self.sparkle_phase = random.uniform(0, 2*math.pi)

# # # #     def rotate_y(self, angle):
# # # #         cos_a = math.cos(angle)
# # # #         sin_a = math.sin(angle)
# # # #         rotation_matrix = np.array([
# # # #             [cos_a, 0, sin_a, 0],
# # # #             [0, 1, 0, 0],
# # # #             [-sin_a, 0, cos_a, 0],
# # # #             [0, 0, 0, 1]
# # # #         ])
# # # #         self.current_pos = rotation_matrix @ self.initial_pos

# # # #     def update(self, time):
# # # #         if self.is_sparkle:
# # # #             self.rotation_angle += self.rotation_speed
# # # #             offset = math.sin(time * self.float_speed + self.float_phase) * 5
# # # #             self.current_pos[1] = self.initial_pos[1] + offset
            
# # # #             intensity = 0.6 + 0.4 * math.sin(time * self.sparkle_speed + self.sparkle_phase)
# # # #             r = min(255, max(0, int(self.original_color[0] * intensity)))
# # # #             g = min(255, max(0, int(self.original_color[1] * intensity)))
# # # #             b = min(255, max(0, int(self.original_color[2] * intensity)))
# # # #             self.color = (r, g, b)
# # # #             self.size = self.original_size * (0.8 + 0.2 * intensity)
            
# # # #         elif self.is_decoration:
# # # #             intensity = 0.7 + 0.3 * math.sin(time * self.blink_speed + self.blink_phase)
# # # #             r = min(255, max(0, int(self.original_color[0] * intensity)))
# # # #             g = min(255, max(0, int(self.original_color[1] * intensity)))
# # # #             b = min(255, max(0, int(self.original_color[2] * intensity)))
# # # #             self.color = (r, g, b)
# # # #             self.size = self.original_size * (0.9 + 0.1 * intensity)

# # # #     def project_to_2d(self, screen_width, screen_height, fov=320):
# # # #         x = self.current_pos[0]
# # # #         y = self.current_pos[1]
# # # #         z = self.current_pos[2]
# # # #         factor = fov / (fov + z)
# # # #         x_proj = x * factor + screen_width / 2
# # # #         y_proj = -y * factor + screen_height / 2
# # # #         return (int(x_proj), int(y_proj)), int(self.size * factor)


# # # # class Heart3D:
# # # #     def __init__(self, scale=10, y_offset=0):
# # # #         self.particles = []
# # # #         self.generate_heart(scale, y_offset)

# # # #     def generate_heart(self, scale, y_offset):
# # # #         num_points = 600
# # # #         for _ in range(num_points):
# # # #             t = random.uniform(0, 2 * math.pi)
# # # #             u = random.uniform(-math.pi, math.pi)
# # # #             x_param = 16 * (math.sin(t) ** 3)
# # # #             y_param = 13 * math.cos(t) - 5 * math.cos(2 * t) - 2 * math.cos(3 * t) - math.cos(4 * t)
# # # #             z_param = 16 * (math.sin(t) ** 3) * math.sin(u)
# # # #             x = x_param * scale
# # # #             y = y_param * scale + y_offset
# # # #             z = z_param * scale * 0.5
# # # #             if random.random() < 0.7:
# # # #                 color = HEART_COLOR
# # # #             else:
# # # #                 color = HEART_COLOR_2
# # # #             size = random.randint(2, 4)
# # # #             is_decoration = True
# # # #             self.particles.append(Particle3D(x, y, z, color, size, is_decoration))

# # # #     def rotate_y(self, angle):
# # # #         for p in self.particles:
# # # #             p.rotate_y(angle)

# # # #     def update(self, time):
# # # #         for p in self.particles:
# # # #             p.update(time)

# # # #     def draw(self, screen):
# # # #         for p in self.particles:
# # # #             pos_2d, size_2d = p.project_to_2d(SCREEN_WIDTH, SCREEN_HEIGHT)
# # # #             if size_2d > 0:
# # # #                 pygame.draw.circle(screen, p.color, pos_2d, max(1, size_2d))
# # # #                 if size_2d > 2:
# # # #                     pygame.draw.circle(screen, (255, 255, 255), pos_2d, max(1, size_2d//2))


# # # # class GalaxyGround:
# # # #     def __init__(self, radius=500, num_particles=3000, y_offset=0):
# # # #         self.particles = []
# # # #         self.y_offset = y_offset
# # # #         self.generate_ground(radius, num_particles)

# # # #     def generate_ground(self, radius, num_particles):
# # # #         for _ in range(num_particles):
# # # #             r = random.uniform(0, radius)
# # # #             spiral_tightness = 0.2
# # # #             num_arms = 3
# # # #             arm_offset = (2 * math.pi / num_arms) * random.randint(0, num_arms - 1)
# # # #             theta = arm_offset + spiral_tightness * r + random.uniform(-0.3, 0.3)
# # # #             x = r * math.cos(theta)
# # # #             z = r * math.sin(theta)
# # # #             y = 0 + self.y_offset
            
# # # #             arm_index = int(arm_offset * num_arms / (2 * math.pi)) % 3
# # # #             if arm_index == 0:
# # # #                 base_color = (173, 216, 230)
# # # #             elif arm_index == 1:
# # # #                 base_color = (221, 160, 221)
# # # #             else:
# # # #                 base_color = (240, 248, 255)
            
# # # #             distance_factor = max(0.1, 1 - r / radius)
# # # #             color_variance = random.randint(-15, 15)
# # # #             color = (
# # # #                 max(180, min(255, base_color[0] + color_variance)),
# # # #                 max(180, min(255, base_color[1] + color_variance)),
# # # #                 max(200, min(255, base_color[2] + color_variance))
# # # #             )
            
# # # #             size = max(1, int(3 * distance_factor + random.randint(0, 2)))
# # # #             is_sparkle = (random.random() < 0.1)
# # # #             self.particles.append(Particle3D(x, y, z, color, size, is_decoration=False, is_sparkle=is_sparkle))

# # # #     def rotate_y(self, angle):
# # # #         for p in self.particles:
# # # #             p.rotate_y(angle)

# # # #     def update(self, time):
# # # #         for p in self.particles:
# # # #             p.update(time)

# # # #     def draw(self, screen):
# # # #         for p in self.particles:
# # # #             pos_2d, size_2d = p.project_to_2d(SCREEN_WIDTH, SCREEN_HEIGHT)
# # # #             if size_2d > 0:
# # # #                 pygame.draw.circle(screen, p.color, pos_2d, max(1, size_2d))
# # # #                 if p.is_sparkle and size_2d > 2:
# # # #                     pygame.draw.circle(screen, (255, 255, 255), pos_2d, max(1, size_2d//2))


# # # # class StarField:
# # # #     def __init__(self, num_stars=800):
# # # #         self.stars = []
# # # #         self.generate_stars(num_stars)

# # # #     def generate_stars(self, num_stars):
# # # #         for _ in range(num_stars):
# # # #             r = random.uniform(500, 1000)
# # # #             theta = random.uniform(0, 2 * math.pi)
# # # #             phi = random.uniform(0, math.pi)
# # # #             x = r * math.sin(phi) * math.cos(theta)
# # # #             y = r * math.cos(phi) + 200
# # # #             z = r * math.sin(phi) * math.sin(theta)
            
# # # #             brightness = random.uniform(0.3, 1.0)
# # # #             color_value = int(200 + 55 * brightness)
# # # #             color = (color_value, color_value, color_value)
# # # #             size = random.randint(1, 3)
# # # #             is_sparkle = (random.random() < 0.3)
# # # #             self.stars.append(Particle3D(x, y, z, color, size, is_decoration=False, is_sparkle=is_sparkle))

# # # #     def rotate_y(self, angle):
# # # #         for star in self.stars:
# # # #             star.rotate_y(angle)

# # # #     def update(self, time):
# # # #         for star in self.stars:
# # # #             star.update(time)

# # # #     def draw(self, screen):
# # # #         for star in self.stars:
# # # #             pos_2d, size_2d = star.project_to_2d(SCREEN_WIDTH, SCREEN_HEIGHT)
# # # #             if size_2d > 0:
# # # #                 pygame.draw.circle(screen, star.color, pos_2d, max(1, size_2d))
# # # #                 if star.is_sparkle and size_2d > 1:
# # # #                     pygame.draw.circle(screen, (255, 255, 255), pos_2d, max(1, size_2d//2))


# # # # class FloatingParticles:
# # # #     def __init__(self, num_particles=400):
# # # #         self.particles = []
# # # #         self.generate_particles(num_particles)

# # # #     def generate_particles(self, num_particles):
# # # #         for _ in range(num_particles):
# # # #             x = random.uniform(-300, 300)
# # # #             y = random.uniform(-100, TREE_HEIGHT + 100)
# # # #             z = random.uniform(-300, -50)
# # # #             color_choice = random.choice([(255, 182, 193), (173, 216, 230), (255, 250, 205), (230, 230, 250)])
# # # #             color = color_choice
# # # #             size = random.randint(2, 5)
# # # #             is_sparkle = True
# # # #             self.particles.append(Particle3D(x, y, z, color, size, is_decoration=False, is_sparkle=is_sparkle))

# # # #     def rotate_y(self, angle):
# # # #         for p in self.particles:
# # # #             p.rotate_y(angle)

# # # #     def update(self, time):
# # # #         for p in self.particles:
# # # #             p.update(time)

# # # #     def draw(self, screen):
# # # #         for p in self.particles:
# # # #             pos_2d, size_2d = p.project_to_2d(SCREEN_WIDTH, SCREEN_HEIGHT)
# # # #             if size_2d > 0:
# # # #                 pygame.draw.circle(screen, p.color, pos_2d, max(1, size_2d))
# # # #                 if size_2d > 2:
# # # #                     pygame.draw.circle(screen, (255, 255, 255), pos_2d, max(1, size_2d//2))


# # # # def generate_tree_points(num_layers=12, points_per_layer=350, y_offset=-140):
# # # #     points = []
# # # #     tree_height = TREE_HEIGHT
# # # #     trunk_height = TRUNK_HEIGHT
# # # #     base_radius = BASE_RADIUS
# # # #     layer_height = (tree_height - trunk_height) / num_layers
# # # #     for layer_idx in range(num_layers):
# # # #         layer_bottom_y = trunk_height + layer_idx * layer_height
# # # #         layer_top_y = trunk_height + (layer_idx + 1) * layer_height
# # # #         layer_radius = base_radius * (1 - layer_idx / num_layers)
# # # #         for _ in range(points_per_layer):
# # # #             r = random.uniform(0.5 * layer_radius, layer_radius)
# # # #             theta = random.uniform(0, 2 * math.pi)
# # # #             x = r * math.cos(theta)
# # # #             z = r * math.sin(theta)
# # # #             y = random.uniform(layer_bottom_y, layer_top_y)
# # # #             y += y_offset
# # # #             color = random.choice(TREE_PARTICLE_COLORS)
# # # #             size = random.randint(2, 4)
# # # #             is_decoration = False
# # # #             if random.random() < 0.06:
# # # #                 color = random.choice([RED, YELLOW, GOLD, PINK, CYAN, (255, 215, 0), (255, 105, 180)])
# # # #                 size = random.randint(8, 12)
# # # #                 is_decoration = True
# # # #             elif random.random() < 0.02:
# # # #                 color = WHITE
# # # #                 size = random.randint(6, 10)
# # # #                 is_decoration = True
# # # #             points.append(Particle3D(x, y, z, color, size, is_decoration))
    
# # # #     trunk_points = 400
# # # #     trunk_radius = 25
# # # #     trunk_top_y = trunk_height
# # # #     for _ in range(trunk_points):
# # # #         r = random.uniform(0, trunk_radius)
# # # #         theta = random.uniform(0, 2 * math.pi)
# # # #         x = r * math.cos(theta)
# # # #         z = r * math.sin(theta)
# # # #         y = random.uniform(0, trunk_top_y)
# # # #         y += y_offset
# # # #         points.append(Particle3D(x, y, z, (139, 69, 19), random.randint(3, 4), False))
    
# # # #     for _ in range(200):
# # # #         r = random.uniform(trunk_radius + 10, trunk_radius + 30)
# # # #         theta = random.uniform(0, 2 * math.pi)
# # # #         x = r * math.cos(theta)
# # # #         z = r * math.sin(theta)
# # # #         y = random.uniform(0, trunk_top_y)
# # # #         y += y_offset
# # # #         color = random.choice([(160, 82, 45), (101, 67, 33)])
# # # #         points.append(Particle3D(x, y, z, color, random.randint(2, 3), False))
    
# # # #     return points


# # # # def generate_background_particles(num_particles_far=800, num_particles_near=400):
# # # #     particles_far = []
# # # #     particles_near = []
# # # #     bg_distance_far = 700
# # # #     for _ in range(num_particles_far):
# # # #         r = random.uniform(bg_distance_far - 200, bg_distance_far + 200)
# # # #         theta = random.uniform(0, 2 * math.pi)
# # # #         phi = random.uniform(0, math.pi)
# # # #         x = r * math.sin(phi) * math.cos(theta)
# # # #         y = r * math.cos(phi) + 200
# # # #         z = r * math.sin(phi) * math.sin(theta)
# # # #         color = random.choice(BACKGROUND_PARTICLE_COLORS_FAR)
# # # #         size = random.randint(1, 3)
# # # #         particles_far.append(Particle3D(x, y, z, color, size, False))
    
# # # #     bg_distance_near = 300
# # # #     for _ in range(num_particles_near):
# # # #         x = random.uniform(-350, 350)
# # # #         y = random.uniform(-80, TREE_HEIGHT + 80)
# # # #         z = random.uniform(-350, 0)
# # # #         color = random.choice(BACKGROUND_PARTICLE_COLORS_NEAR)
# # # #         size = random.randint(2, 4)
# # # #         particles_near.append(Particle3D(x, y, z, color, size, False))
    
# # # #     return particles_far, particles_near


# # # # def main():
# # # #     pygame.init()
# # # #     screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
# # # #     pygame.display.set_caption("?")
# # # #     clock = pygame.time.Clock()
    
# # # #     background = GradientBackground(SCREEN_WIDTH, SCREEN_HEIGHT)
    
# # # #     y_offset = -140
# # # #     tree_points = generate_tree_points(num_layers=12, points_per_layer=350, y_offset=y_offset)
# # # #     heart_y_offset = TREE_HEIGHT + y_offset + 30
# # # #     heart = Heart3D(scale=8, y_offset=heart_y_offset)
# # # #     ground = GalaxyGround(radius=500, num_particles=3000, y_offset=y_offset)
# # # #     starfield = StarField(num_stars=800)
# # # #     floating = FloatingParticles(num_particles=400)
# # # #     bg_particles_far, bg_particles_near = generate_background_particles(800, 400)
    
# # # #     angle = 0
# # # #     rotation_speed = 0.003
# # # #     time_counter = 0
# # # #     running = True
    
# # # #     while running:
# # # #         for event in pygame.event.get():
# # # #             if event.type == pygame.QUIT:
# # # #                 running = False
# # # #             elif event.type == pygame.KEYDOWN:
# # # #                 if event.key == pygame.K_UP:
# # # #                     rotation_speed = min(0.01, rotation_speed + 0.0005)
# # # #                 elif event.key == pygame.K_DOWN:
# # # #                     rotation_speed = max(0.001, rotation_speed - 0.0005)
# # # #                 elif event.key == pygame.K_SPACE:
# # # #                     rotation_speed = 0.003
        
# # # #         angle += rotation_speed
# # # #         if angle > 2 * math.pi:
# # # #             angle -= 2 * math.pi
        
# # # #         time_counter += 1
        
# # # #         for point in tree_points:
# # # #             point.rotate_y(angle)
# # # #             point.update(time_counter)
        
# # # #         heart.rotate_y(angle)
# # # #         heart.update(time_counter)
# # # #         ground.rotate_y(angle)
# # # #         ground.update(time_counter)
# # # #         starfield.rotate_y(angle)
# # # #         starfield.update(time_counter)
# # # #         floating.rotate_y(angle)
# # # #         floating.update(time_counter)
        
# # # #         for point in bg_particles_far:
# # # #             point.rotate_y(angle)
        
# # # #         for point in bg_particles_near:
# # # #             point.rotate_y(angle)
        
# # # #         background.draw(screen)
# # # #         starfield.draw(screen)
        
# # # #         for point in bg_particles_far:
# # # #             pos_2d, size_2d = point.project_to_2d(SCREEN_WIDTH, SCREEN_HEIGHT)
# # # #             if size_2d > 0:
# # # #                 pygame.draw.circle(screen, point.color, pos_2d, max(1, size_2d))
        
# # # #         ground.draw(screen)
        
# # # #         for point in tree_points:
# # # #             pos_2d, size_2d = point.project_to_2d(SCREEN_WIDTH, SCREEN_HEIGHT)
# # # #             if size_2d > 0:
# # # #                 pygame.draw.circle(screen, point.color, pos_2d, max(1, size_2d))
# # # #                 if point.is_decoration and size_2d > 3:
# # # #                     pygame.draw.circle(screen, (255, 255, 255), pos_2d, max(1, size_2d//3))
        
# # # #         heart.draw(screen)
# # # #         floating.draw(screen)
        
# # # #         for point in bg_particles_near:
# # # #             pos_2d, size_2d = point.project_to_2d(SCREEN_WIDTH, SCREEN_HEIGHT)
# # # #             if size_2d > 0:
# # # #                 pygame.draw.circle(screen, point.color, pos_2d, max(1, size_2d))
        
# # # #         font = pygame.font.SysFont(None, 24)
# # # #         info_text = f"旋转速度: {rotation_speed:.4f} (↑/↓方向键调整，空格重置)"
# # # #         text_surface = font.render(info_text, True, (80, 80, 120))
# # # #         screen.blit(text_surface, (10, 10))
        
# # # #         pygame.display.flip()
# # # #         clock.tick(FPS)
    
# # # #     pygame.quit()
# # # #     sys.exit()


# # # # if __name__ == "__main__":
# # # #     main()





# # # import pygame
# # # import numpy as np
# # # import math
# # # import random
# # # import sys

# # # SCREEN_WIDTH = 1200
# # # SCREEN_HEIGHT = 900
# # # FPS = 60

# # # TREE_HEIGHT = 400
# # # TRUNK_HEIGHT = 50
# # # BASE_RADIUS = 160

# # # BLACK = (0, 0, 0)
# # # GREEN = (34, 139, 34)
# # # RED = (255, 0, 0)
# # # YELLOW = (255, 255, 0)
# # # BLUE = (0, 0, 255)
# # # PURPLE = (128, 0, 128)
# # # ORANGE = (255, 165, 0)
# # # GOLD = (255, 215, 0)
# # # SILVER = (192, 192, 192)
# # # WHITE = (255, 255, 255)
# # # PINK = (255, 192, 203)
# # # CYAN = (0, 255, 255)
# # # HEART_COLOR = (255, 105, 180)
# # # HEART_COLOR_2 = (255, 20, 147)
# # # GROUND_COLOR = (240, 248, 255)
# # # TREE_PARTICLE_COLORS = [GREEN, RED, YELLOW, BLUE, PURPLE, ORANGE, GOLD, SILVER, PINK, CYAN]
# # # BACKGROUND_PARTICLE_COLORS_FAR = [(255, 255, 255), (200, 220, 255), (220, 200, 255), (200, 255, 200)]
# # # BACKGROUND_PARTICLE_COLORS_NEAR = [(230, 230, 250), (240, 248, 255), (255, 250, 240), (255, 245, 238)]

# # # class GradientBackground:
# # #     def __init__(self, width, height):
# # #         self.width = width
# # #         self.height = height
# # #         self.gradient_surface = self.create_gradient()
    
# # #     def create_gradient(self):
# # #         surface = pygame.Surface((self.width, self.height))
        
# # #         top_color = (255, 240, 245)
# # #         middle_color = (230, 230, 250)
# # #         bottom_color = (220, 230, 255)
        
# # #         for y in range(self.height):
# # #             if y < self.height // 2:
# # #                 ratio = y / (self.height // 2)
# # #                 r = top_color[0] * (1 - ratio) + middle_color[0] * ratio
# # #                 g = top_color[1] * (1 - ratio) + middle_color[1] * ratio
# # #                 b = top_color[2] * (1 - ratio) + middle_color[2] * ratio
# # #             else:
# # #                 ratio = (y - self.height // 2) / (self.height // 2)
# # #                 r = middle_color[0] * (1 - ratio) + bottom_color[0] * ratio
# # #                 g = middle_color[1] * (1 - ratio) + bottom_color[1] * ratio
# # #                 b = middle_color[2] * (1 - ratio) + bottom_color[2] * ratio
            
# # #             color = (int(r), int(g), int(b))
# # #             pygame.draw.line(surface, color, (0, y), (self.width, y))
        
# # #         star_count = 50
# # #         for _ in range(star_count):
# # #             x = random.randint(0, self.width)
# # #             y = random.randint(0, self.height)
# # #             size = random.randint(1, 3)
# # #             brightness = random.randint(180, 230)
# # #             color = (brightness, brightness, brightness)
# # #             pygame.draw.circle(surface, color, (x, y), size)
        
# # #         return surface
    
# # #     def draw(self, screen):
# # #         screen.blit(self.gradient_surface, (0, 0))

# # # class Particle3D:
# # #     def __init__(self, x, y, z, color, size, is_decoration=False, is_sparkle=False):
# # #         self.initial_pos = np.array([x, y, z, 1])
# # #         self.color = color
# # #         self.original_color = color
# # #         self.size = size
# # #         self.original_size = size
# # #         self.current_pos = self.initial_pos.copy()
# # #         self.is_decoration = is_decoration
# # #         self.is_sparkle = is_sparkle
# # #         self.rotation_speed = random.uniform(-0.01, 0.01)
# # #         self.rotation_angle = random.uniform(0, 2*math.pi)
# # #         self.float_speed = random.uniform(0.01, 0.03)
# # #         self.float_phase = random.uniform(0, 2*math.pi)
# # #         if is_decoration:
# # #             self.blink_speed = random.uniform(0.02, 0.08)
# # #             self.blink_phase = random.uniform(0, 2*math.pi)
# # #         if is_sparkle:
# # #             self.sparkle_speed = random.uniform(0.05, 0.1)
# # #             self.sparkle_phase = random.uniform(0, 2*math.pi)

# # #     def rotate_y(self, angle):
# # #         cos_a = math.cos(angle)
# # #         sin_a = math.sin(angle)
# # #         rotation_matrix = np.array([
# # #             [cos_a, 0, sin_a, 0],
# # #             [0, 1, 0, 0],
# # #             [-sin_a, 0, cos_a, 0],
# # #             [0, 0, 0, 1]
# # #         ])
# # #         self.current_pos = rotation_matrix @ self.initial_pos

# # #     def update(self, time):
# # #         if self.is_sparkle:
# # #             self.rotation_angle += self.rotation_speed
# # #             offset = math.sin(time * self.float_speed + self.float_phase) * 5
# # #             self.current_pos[1] = self.initial_pos[1] + offset
            
# # #             intensity = 0.6 + 0.4 * math.sin(time * self.sparkle_speed + self.sparkle_phase)
# # #             r = min(255, max(0, int(self.original_color[0] * intensity)))
# # #             g = min(255, max(0, int(self.original_color[1] * intensity)))
# # #             b = min(255, max(0, int(self.original_color[2] * intensity)))
# # #             self.color = (r, g, b)
# # #             self.size = self.original_size * (0.8 + 0.2 * intensity)
            
# # #         elif self.is_decoration:
# # #             intensity = 0.7 + 0.3 * math.sin(time * self.blink_speed + self.blink_phase)
# # #             r = min(255, max(0, int(self.original_color[0] * intensity)))
# # #             g = min(255, max(0, int(self.original_color[1] * intensity)))
# # #             b = min(255, max(0, int(self.original_color[2] * intensity)))
# # #             self.color = (r, g, b)
# # #             self.size = self.original_size * (0.9 + 0.1 * intensity)

# # #     def project_to_2d(self, screen_width, screen_height, fov=320):
# # #         x = self.current_pos[0]
# # #         y = self.current_pos[1]
# # #         z = self.current_pos[2]
# # #         factor = fov / (fov + z)
# # #         x_proj = x * factor + screen_width / 2
# # #         y_proj = -y * factor + screen_height / 2
# # #         return (int(x_proj), int(y_proj)), int(self.size * factor)


# # # class Heart3D:
# # #     def __init__(self, scale=10, y_offset=0):
# # #         self.particles = []
# # #         self.generate_heart(scale, y_offset)

# # #     def generate_heart(self, scale, y_offset):
# # #         num_points = 600
# # #         for _ in range(num_points):
# # #             t = random.uniform(0, 2 * math.pi)
# # #             u = random.uniform(-math.pi, math.pi)
# # #             x_param = 16 * (math.sin(t) ** 3)
# # #             y_param = 13 * math.cos(t) - 5 * math.cos(2 * t) - 2 * math.cos(3 * t) - math.cos(4 * t)
# # #             z_param = 16 * (math.sin(t) ** 3) * math.sin(u)
# # #             x = x_param * scale
# # #             y = y_param * scale + y_offset
# # #             z = z_param * scale * 0.5
# # #             if random.random() < 0.7:
# # #                 color = HEART_COLOR
# # #             else:
# # #                 color = HEART_COLOR_2
# # #             size = random.randint(2, 4)
# # #             is_decoration = True
# # #             self.particles.append(Particle3D(x, y, z, color, size, is_decoration))

# # #     def rotate_y(self, angle):
# # #         for p in self.particles:
# # #             p.rotate_y(angle)

# # #     def update(self, time):
# # #         for p in self.particles:
# # #             p.update(time)

# # #     def draw(self, screen):
# # #         for p in self.particles:
# # #             pos_2d, size_2d = p.project_to_2d(SCREEN_WIDTH, SCREEN_HEIGHT)
# # #             if size_2d > 0:
# # #                 pygame.draw.circle(screen, p.color, pos_2d, max(1, size_2d))
# # #                 if size_2d > 2:
# # #                     pygame.draw.circle(screen, (255, 255, 255), pos_2d, max(1, size_2d//2))


# # # class GalaxyGround:
# # #     def __init__(self, radius=500, num_particles=3000, y_offset=0):
# # #         self.particles = []
# # #         self.y_offset = y_offset
# # #         self.generate_ground(radius, num_particles)

# # #     def generate_ground(self, radius, num_particles):
# # #         for _ in range(num_particles):
# # #             r = random.uniform(0, radius)
# # #             spiral_tightness = 0.2
# # #             num_arms = 3
# # #             arm_offset = (2 * math.pi / num_arms) * random.randint(0, num_arms - 1)
# # #             theta = arm_offset + spiral_tightness * r + random.uniform(-0.3, 0.3)
# # #             x = r * math.cos(theta)
# # #             z = r * math.sin(theta)
# # #             y = 0 + self.y_offset
            
# # #             arm_index = int(arm_offset * num_arms / (2 * math.pi)) % 3
# # #             if arm_index == 0:
# # #                 base_color = (173, 216, 230)
# # #             elif arm_index == 1:
# # #                 base_color = (221, 160, 221)
# # #             else:
# # #                 base_color = (240, 248, 255)
            
# # #             distance_factor = max(0.1, 1 - r / radius)
# # #             color_variance = random.randint(-15, 15)
# # #             color = (
# # #                 max(180, min(255, base_color[0] + color_variance)),
# # #                 max(180, min(255, base_color[1] + color_variance)),
# # #                 max(200, min(255, base_color[2] + color_variance))
# # #             )
            
# # #             size = max(1, int(3 * distance_factor + random.randint(0, 2)))
# # #             is_sparkle = (random.random() < 0.1)
# # #             self.particles.append(Particle3D(x, y, z, color, size, is_decoration=False, is_sparkle=is_sparkle))

# # #     def rotate_y(self, angle):
# # #         for p in self.particles:
# # #             p.rotate_y(angle)

# # #     def update(self, time):
# # #         for p in self.particles:
# # #             p.update(time)

# # #     def draw(self, screen):
# # #         for p in self.particles:
# # #             pos_2d, size_2d = p.project_to_2d(SCREEN_WIDTH, SCREEN_HEIGHT)
# # #             if size_2d > 0:
# # #                 pygame.draw.circle(screen, p.color, pos_2d, max(1, size_2d))
# # #                 if p.is_sparkle and size_2d > 2:
# # #                     pygame.draw.circle(screen, (255, 255, 255), pos_2d, max(1, size_2d//2))


# # # class StarField:
# # #     def __init__(self, num_stars=800):
# # #         self.stars = []
# # #         self.generate_stars(num_stars)

# # #     def generate_stars(self, num_stars):
# # #         for _ in range(num_stars):
# # #             r = random.uniform(500, 1000)
# # #             theta = random.uniform(0, 2 * math.pi)
# # #             phi = random.uniform(0, math.pi)
# # #             x = r * math.sin(phi) * math.cos(theta)
# # #             y = r * math.cos(phi) + 200
# # #             z = r * math.sin(phi) * math.sin(theta)
            
# # #             brightness = random.uniform(0.3, 1.0)
# # #             color_value = int(200 + 55 * brightness)
# # #             color = (color_value, color_value, color_value)
# # #             size = random.randint(1, 3)
# # #             is_sparkle = (random.random() < 0.3)
# # #             self.stars.append(Particle3D(x, y, z, color, size, is_decoration=False, is_sparkle=is_sparkle))

# # #     def rotate_y(self, angle):
# # #         for star in self.stars:
# # #             star.rotate_y(angle)

# # #     def update(self, time):
# # #         for star in self.stars:
# # #             star.update(time)

# # #     def draw(self, screen):
# # #         for star in self.stars:
# # #             pos_2d, size_2d = star.project_to_2d(SCREEN_WIDTH, SCREEN_HEIGHT)
# # #             if size_2d > 0:
# # #                 pygame.draw.circle(screen, star.color, pos_2d, max(1, size_2d))
# # #                 if star.is_sparkle and size_2d > 1:
# # #                     pygame.draw.circle(screen, (255, 255, 255), pos_2d, max(1, size_2d//2))


# # # class FloatingParticles:
# # #     def __init__(self, num_particles=400):
# # #         self.particles = []
# # #         self.generate_particles(num_particles)

# # #     def generate_particles(self, num_particles):
# # #         for _ in range(num_particles):
# # #             x = random.uniform(-300, 300)
# # #             y = random.uniform(-100, TREE_HEIGHT + 100)
# # #             z = random.uniform(-300, -50)
# # #             color_choice = random.choice([(255, 182, 193), (173, 216, 230), (255, 250, 205), (230, 230, 250)])
# # #             color = color_choice
# # #             size = random.randint(2, 5)
# # #             is_sparkle = True
# # #             self.particles.append(Particle3D(x, y, z, color, size, is_decoration=False, is_sparkle=is_sparkle))

# # #     def rotate_y(self, angle):
# # #         for p in self.particles:
# # #             p.rotate_y(angle)

# # #     def update(self, time):
# # #         for p in self.particles:
# # #             p.update(time)

# # #     def draw(self, screen):
# # #         for p in self.particles:
# # #             pos_2d, size_2d = p.project_to_2d(SCREEN_WIDTH, SCREEN_HEIGHT)
# # #             if size_2d > 0:
# # #                 pygame.draw.circle(screen, p.color, pos_2d, max(1, size_2d))
# # #                 if size_2d > 2:
# # #                     pygame.draw.circle(screen, (255, 255, 255), pos_2d, max(1, size_2d//2))


# # # def generate_tree_points(num_layers=12, points_per_layer=350, y_offset=-140):
# # #     points = []
# # #     tree_height = TREE_HEIGHT
# # #     trunk_height = TRUNK_HEIGHT
# # #     base_radius = BASE_RADIUS
# # #     layer_height = (tree_height - trunk_height) / num_layers
# # #     for layer_idx in range(num_layers):
# # #         layer_bottom_y = trunk_height + layer_idx * layer_height
# # #         layer_top_y = trunk_height + (layer_idx + 1) * layer_height
# # #         layer_radius = base_radius * (1 - layer_idx / num_layers)
# # #         for _ in range(points_per_layer):
# # #             r = random.uniform(0.5 * layer_radius, layer_radius)
# # #             theta = random.uniform(0, 2 * math.pi)
# # #             x = r * math.cos(theta)
# # #             z = r * math.sin(theta)
# # #             y = random.uniform(layer_bottom_y, layer_top_y)
# # #             y += y_offset
# # #             color = random.choice(TREE_PARTICLE_COLORS)
# # #             size = random.randint(2, 4)
# # #             is_decoration = False
# # #             if random.random() < 0.06:
# # #                 color = random.choice([RED, YELLOW, GOLD, PINK, CYAN, (255, 215, 0), (255, 105, 180)])
# # #                 size = random.randint(8, 12)
# # #                 is_decoration = True
# # #             elif random.random() < 0.02:
# # #                 color = WHITE
# # #                 size = random.randint(6, 10)
# # #                 is_decoration = True
# # #             points.append(Particle3D(x, y, z, color, size, is_decoration))
    
# # #     trunk_points = 400
# # #     trunk_radius = 25
# # #     trunk_top_y = trunk_height
# # #     for _ in range(trunk_points):
# # #         r = random.uniform(0, trunk_radius)
# # #         theta = random.uniform(0, 2 * math.pi)
# # #         x = r * math.cos(theta)
# # #         z = r * math.sin(theta)
# # #         y = random.uniform(0, trunk_top_y)
# # #         y += y_offset
# # #         points.append(Particle3D(x, y, z, (139, 69, 19), random.randint(3, 4), False))
    
# # #     for _ in range(200):
# # #         r = random.uniform(trunk_radius + 10, trunk_radius + 30)
# # #         theta = random.uniform(0, 2 * math.pi)
# # #         x = r * math.cos(theta)
# # #         z = r * math.sin(theta)
# # #         y = random.uniform(0, trunk_top_y)
# # #         y += y_offset
# # #         color = random.choice([(160, 82, 45), (101, 67, 33)])
# # #         points.append(Particle3D(x, y, z, color, random.randint(2, 3), False))
    
# # #     return points


# # # def generate_background_particles(num_particles_far=800, num_particles_near=400):
# # #     particles_far = []
# # #     particles_near = []
# # #     bg_distance_far = 700
# # #     for _ in range(num_particles_far):
# # #         r = random.uniform(bg_distance_far - 200, bg_distance_far + 200)
# # #         theta = random.uniform(0, 2 * math.pi)
# # #         phi = random.uniform(0, math.pi)
# # #         x = r * math.sin(phi) * math.cos(theta)
# # #         y = r * math.cos(phi) + 200
# # #         z = r * math.sin(phi) * math.sin(theta)
# # #         color = random.choice(BACKGROUND_PARTICLE_COLORS_FAR)
# # #         size = random.randint(1, 3)
# # #         particles_far.append(Particle3D(x, y, z, color, size, False))
    
# # #     bg_distance_near = 300
# # #     for _ in range(num_particles_near):
# # #         x = random.uniform(-350, 350)
# # #         y = random.uniform(-80, TREE_HEIGHT + 80)
# # #         z = random.uniform(-350, 0)
# # #         color = random.choice(BACKGROUND_PARTICLE_COLORS_NEAR)
# # #         size = random.randint(2, 4)
# # #         particles_near.append(Particle3D(x, y, z, color, size, False))
    
# # #     return particles_far, particles_near


# # # def main():
# # #     pygame.init()
# # #     screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
# # #     pygame.display.set_caption("超炫3D圣诞树：银河之心")
# # #     clock = pygame.time.Clock()
    
# # #     background = GradientBackground(SCREEN_WIDTH, SCREEN_HEIGHT)
    
# # #     y_offset = -140
# # #     tree_points = generate_tree_points(num_layers=12, points_per_layer=350, y_offset=y_offset)
# # #     heart_y_offset = TREE_HEIGHT + y_offset + 30
# # #     heart = Heart3D(scale=8, y_offset=heart_y_offset)
# # #     ground = GalaxyGround(radius=500, num_particles=3000, y_offset=y_offset)
# # #     starfield = StarField(num_stars=800)
# # #     floating = FloatingParticles(num_particles=400)
# # #     bg_particles_far, bg_particles_near = generate_background_particles(800, 400)
    
# # #     angle = 0
# # #     rotation_speed = 0.003
# # #     time_counter = 0
# # #     running = True
    
# # #     while running:
# # #         for event in pygame.event.get():
# # #             if event.type == pygame.QUIT:
# # #                 running = False
# # #             elif event.type == pygame.KEYDOWN:
# # #                 if event.key == pygame.K_UP:
# # #                     rotation_speed = min(0.01, rotation_speed + 0.0005)
# # #                 elif event.key == pygame.K_DOWN:
# # #                     rotation_speed = max(0.001, rotation_speed - 0.0005)
# # #                 elif event.key == pygame.K_SPACE:
# # #                     rotation_speed = 0.003
        
# # #         angle += rotation_speed
# # #         if angle > 2 * math.pi:
# # #             angle -= 2 * math.pi
        
# # #         time_counter += 1
        
# # #         for point in tree_points:
# # #             point.rotate_y(angle)
# # #             point.update(time_counter)
        
# # #         heart.rotate_y(angle)
# # #         heart.update(time_counter)
# # #         ground.rotate_y(angle)
# # #         ground.update(time_counter)
# # #         starfield.rotate_y(angle)
# # #         starfield.update(time_counter)
# # #         floating.rotate_y(angle)
# # #         floating.update(time_counter)
        
# # #         for point in bg_particles_far:
# # #             point.rotate_y(angle)
        
# # #         for point in bg_particles_near:
# # #             point.rotate_y(angle)
        
# # #         background.draw(screen)
# # #         starfield.draw(screen)
        
# # #         for point in bg_particles_far:
# # #             pos_2d, size_2d = point.project_to_2d(SCREEN_WIDTH, SCREEN_HEIGHT)
# # #             if size_2d > 0:
# # #                 pygame.draw.circle(screen, point.color, pos_2d, max(1, size_2d))
        
# # #         ground.draw(screen)
        
# # #         for point in tree_points:
# # #             pos_2d, size_2d = point.project_to_2d(SCREEN_WIDTH, SCREEN_HEIGHT)
# # #             if size_2d > 0:
# # #                 pygame.draw.circle(screen, point.color, pos_2d, max(1, size_2d))
# # #                 if point.is_decoration and size_2d > 3:
# # #                     pygame.draw.circle(screen, (255, 255, 255), pos_2d, max(1, size_2d//3))
        
# # #         heart.draw(screen)
# # #         floating.draw(screen)
        
# # #         for point in bg_particles_near:
# # #             pos_2d, size_2d = point.project_to_2d(SCREEN_WIDTH, SCREEN_HEIGHT)
# # #             if size_2d > 0:
# # #                 pygame.draw.circle(screen, point.color, pos_2d, max(1, size_2d))
        
# # #         font = pygame.font.SysFont(None, 24)
# # #         info_text = f"旋转速度: {rotation_speed:.4f} (↑/↓方向键调整，空格重置)"
# # #         text_surface = font.render(info_text, True, (80, 80, 120))
# # #         screen.blit(text_surface, (10, 10))
        
# # #         pygame.display.flip()
# # #         clock.tick(FPS)
    
# # #     pygame.quit()
# # #     sys.exit()


# # # if __name__ == "__main__":
# # #     main()








# # import pygame
# # import numpy as np
# # import math
# # import random
# # import sys

# # SCREEN_WIDTH = 1200
# # SCREEN_HEIGHT = 900
# # FPS = 60

# # TREE_HEIGHT = 400
# # TRUNK_HEIGHT = 50
# # BASE_RADIUS = 160

# # BLACK = (0, 0, 0)
# # GREEN = (34, 139, 34)
# # RED = (255, 0, 0)
# # YELLOW = (255, 255, 0)
# # BLUE = (0, 0, 255)
# # PURPLE = (128, 0, 128)
# # ORANGE = (255, 165, 0)
# # GOLD = (255, 215, 0)
# # SILVER = (192, 192, 192)
# # WHITE = (255, 255, 255)
# # PINK = (255, 192, 203)
# # CYAN = (0, 255, 255)
# # HEART_COLOR = (255, 105, 180)
# # HEART_COLOR_2 = (255, 20, 147)
# # GROUND_COLOR = (50, 60, 120)
# # TREE_PARTICLE_COLORS = [GREEN, RED, YELLOW, BLUE, PURPLE, ORANGE, GOLD, SILVER, PINK, CYAN]
# # BACKGROUND_PARTICLE_COLORS_FAR = [(200, 220, 255), (220, 200, 255), (200, 255, 200)]
# # BACKGROUND_PARTICLE_COLORS_NEAR = [(150, 180, 220), (180, 200, 230), (200, 220, 240)]

# # class GradientBackground:
# #     def __init__(self, width, height):
# #         self.width = width
# #         self.height = height
# #         self.gradient_surface = self.create_gradient()
    
# #     def create_gradient(self):
# #         surface = pygame.Surface((self.width, self.height))
        
# #         top_color = (180, 200, 240)
# #         middle_color = (150, 170, 210)
# #         bottom_color = (120, 140, 180)
        
# #         for y in range(self.height):
# #             if y < self.height // 2:
# #                 ratio = y / (self.height // 2)
# #                 r = top_color[0] * (1 - ratio) + middle_color[0] * ratio
# #                 g = top_color[1] * (1 - ratio) + middle_color[1] * ratio
# #                 b = top_color[2] * (1 - ratio) + middle_color[2] * ratio
# #             else:
# #                 ratio = (y - self.height // 2) / (self.height // 2)
# #                 r = middle_color[0] * (1 - ratio) + bottom_color[0] * ratio
# #                 g = middle_color[1] * (1 - ratio) + bottom_color[1] * ratio
# #                 b = middle_color[2] * (1 - ratio) + bottom_color[2] * ratio
            
# #             color = (int(r), int(g), int(b))
# #             pygame.draw.line(surface, color, (0, y), (self.width, y))
        
# #         star_count = 50
# #         for _ in range(star_count):
# #             x = random.randint(0, self.width)
# #             y = random.randint(0, self.height)
# #             size = random.randint(1, 3)
# #             brightness = random.randint(180, 230)
# #             color = (brightness, brightness, brightness)
# #             pygame.draw.circle(surface, color, (x, y), size)
        
# #         return surface
    
# #     def draw(self, screen):
# #         screen.blit(self.gradient_surface, (0, 0))

# # class Particle3D:
# #     def __init__(self, x, y, z, color, size, is_decoration=False, is_sparkle=False):
# #         self.initial_pos = np.array([x, y, z, 1])
# #         self.color = color
# #         self.original_color = color
# #         self.size = size
# #         self.original_size = size
# #         self.current_pos = self.initial_pos.copy()
# #         self.is_decoration = is_decoration
# #         self.is_sparkle = is_sparkle
# #         self.rotation_speed = random.uniform(-0.01, 0.01)
# #         self.rotation_angle = random.uniform(0, 2*math.pi)
# #         self.float_speed = random.uniform(0.01, 0.03)
# #         self.float_phase = random.uniform(0, 2*math.pi)
# #         self.light_intensity = 1.0
# #         if is_decoration:
# #             self.blink_speed = random.uniform(0.02, 0.08)
# #             self.blink_phase = random.uniform(0, 2*math.pi)
# #         if is_sparkle:
# #             self.sparkle_speed = random.uniform(0.05, 0.1)
# #             self.sparkle_phase = random.uniform(0, 2*math.pi)
    
# #     def calculate_lighting(self, light_source):
# #         dx = self.current_pos[0] - light_source[0]
# #         dy = self.current_pos[1] - light_source[1]
# #         dz = self.current_pos[2] - light_source[2]
# #         distance = math.sqrt(dx*dx + dy*dy + dz*dz)
# #         intensity = 1.0 / (1.0 + distance * 0.001)
# #         self.light_intensity = min(1.5, max(0.3, intensity))

# #     def rotate_y(self, angle):
# #         cos_a = math.cos(angle)
# #         sin_a = math.sin(angle)
# #         rotation_matrix = np.array([
# #             [cos_a, 0, sin_a, 0],
# #             [0, 1, 0, 0],
# #             [-sin_a, 0, cos_a, 0],
# #             [0, 0, 0, 1]
# #         ])
# #         self.current_pos = rotation_matrix @ self.initial_pos

# #     def update(self, time):
# #         if self.is_sparkle:
# #             self.rotation_angle += self.rotation_speed
# #             offset = math.sin(time * self.float_speed + self.float_phase) * 5
# #             self.current_pos[1] = self.initial_pos[1] + offset
            
# #             intensity = 0.6 + 0.4 * math.sin(time * self.sparkle_speed + self.sparkle_phase)
# #             r = min(255, max(0, int(self.original_color[0] * intensity)))
# #             g = min(255, max(0, int(self.original_color[1] * intensity)))
# #             b = min(255, max(0, int(self.original_color[2] * intensity)))
# #             self.color = (r, g, b)
# #             self.size = self.original_size * (0.8 + 0.2 * intensity)
            
# #         elif self.is_decoration:
# #             intensity = 0.7 + 0.3 * math.sin(time * self.blink_speed + self.blink_phase)
# #             r = min(255, max(0, int(self.original_color[0] * intensity)))
# #             g = min(255, max(0, int(self.original_color[1] * intensity)))
# #             b = min(255, max(0, int(self.original_color[2] * intensity)))
# #             self.color = (r, g, b)
# #             self.size = self.original_size * (0.9 + 0.1 * intensity)
        
# #         if not self.is_decoration and not self.is_sparkle:
# #             r = min(255, max(0, int(self.original_color[0] * self.light_intensity)))
# #             g = min(255, max(0, int(self.original_color[1] * self.light_intensity)))
# #             b = min(255, max(0, int(self.original_color[2] * self.light_intensity)))
# #             self.color = (r, g, b)

# #     def project_to_2d(self, screen_width, screen_height, fov=320):
# #         x = self.current_pos[0]
# #         y = self.current_pos[1]
# #         z = self.current_pos[2]
# #         factor = fov / (fov + z)
# #         x_proj = x * factor + screen_width / 2
# #         y_proj = -y * factor + screen_height / 2
# #         return (int(x_proj), int(y_proj)), int(self.size * factor)


# # class Heart3D:
# #     def __init__(self, scale=6, y_offset=0):
# #         self.particles = []
# #         self.generate_heart(scale, y_offset)

# #     def generate_heart(self, scale, y_offset):
# #         num_points = 400
# #         for _ in range(num_points):
# #             t = random.uniform(0, 2 * math.pi)
# #             u = random.uniform(-math.pi, math.pi)
# #             x_param = 16 * (math.sin(t) ** 3)
# #             y_param = 13 * math.cos(t) - 5 * math.cos(2 * t) - 2 * math.cos(3 * t) - math.cos(4 * t)
# #             z_param = 16 * (math.sin(t) ** 3) * math.sin(u)
# #             x = x_param * scale
# #             y = y_param * scale + y_offset
# #             z = z_param * scale * 0.5
# #             if random.random() < 0.7:
# #                 color = HEART_COLOR
# #             else:
# #                 color = HEART_COLOR_2
# #             size = random.randint(1, 3)
# #             is_decoration = True
# #             self.particles.append(Particle3D(x, y, z, color, size, is_decoration))

# #     def calculate_lighting(self, light_source):
# #         for p in self.particles:
# #             p.calculate_lighting(light_source)

# #     def rotate_y(self, angle):
# #         for p in self.particles:
# #             p.rotate_y(angle)

# #     def update(self, time):
# #         for p in self.particles:
# #             p.update(time)

# #     def draw(self, screen):
# #         for p in self.particles:
# #             pos_2d, size_2d = p.project_to_2d(SCREEN_WIDTH, SCREEN_HEIGHT)
# #             if size_2d > 0:
# #                 pygame.draw.circle(screen, p.color, pos_2d, max(1, size_2d))
# #                 if size_2d > 2:
# #                     pygame.draw.circle(screen, (255, 255, 255), pos_2d, max(1, size_2d//2))


# # class GalaxyGround:
# #     def __init__(self, radius=500, num_particles=3000, y_offset=0):
# #         self.particles = []
# #         self.y_offset = y_offset
# #         self.generate_ground(radius, num_particles)

# #     def generate_ground(self, radius, num_particles):
# #         for _ in range(num_particles):
# #             r = random.uniform(0, radius)
# #             spiral_tightness = 0.2
# #             num_arms = 3
# #             arm_offset = (2 * math.pi / num_arms) * random.randint(0, num_arms - 1)
# #             theta = arm_offset + spiral_tightness * r + random.uniform(-0.3, 0.3)
# #             x = r * math.cos(theta)
# #             z = r * math.sin(theta)
# #             y = 0 + self.y_offset
            
# #             arm_index = int(arm_offset * num_arms / (2 * math.pi)) % 3
# #             if arm_index == 0:
# #                 base_color = (80, 100, 150)
# #             elif arm_index == 1:
# #                 base_color = (100, 80, 140)
# #             else:
# #                 base_color = (100, 120, 160)
            
# #             distance_factor = max(0.1, 1 - r / radius)
# #             color_variance = random.randint(-15, 15)
# #             color = (
# #                 max(70, min(200, base_color[0] + color_variance)),
# #                 max(70, min(200, base_color[1] + color_variance)),
# #                 max(90, min(220, base_color[2] + color_variance))
# #             )
            
# #             size = max(1, int(3 * distance_factor + random.randint(0, 2)))
# #             is_sparkle = (random.random() < 0.1)
# #             self.particles.append(Particle3D(x, y, z, color, size, is_decoration=False, is_sparkle=is_sparkle))

# #     def calculate_lighting(self, light_source):
# #         for p in self.particles:
# #             p.calculate_lighting(light_source)

# #     def rotate_y(self, angle):
# #         for p in self.particles:
# #             p.rotate_y(angle)

# #     def update(self, time):
# #         for p in self.particles:
# #             p.update(time)

# #     def draw(self, screen):
# #         for p in self.particles:
# #             pos_2d, size_2d = p.project_to_2d(SCREEN_WIDTH, SCREEN_HEIGHT)
# #             if size_2d > 0:
# #                 pygame.draw.circle(screen, p.color, pos_2d, max(1, size_2d))
# #                 if p.is_sparkle and size_2d > 2:
# #                     pygame.draw.circle(screen, (200, 200, 255), pos_2d, max(1, size_2d//2))


# # class StarField:
# #     def __init__(self, num_stars=800):
# #         self.stars = []
# #         self.generate_stars(num_stars)

# #     def generate_stars(self, num_stars):
# #         for _ in range(num_stars):
# #             r = random.uniform(500, 1000)
# #             theta = random.uniform(0, 2 * math.pi)
# #             phi = random.uniform(0, math.pi)
# #             x = r * math.sin(phi) * math.cos(theta)
# #             y = r * math.cos(phi) + 200
# #             z = r * math.sin(phi) * math.sin(theta)
            
# #             brightness = random.uniform(0.3, 1.0)
# #             color_value = int(150 + 105 * brightness)
# #             color = (color_value, color_value, color_value)
# #             size = random.randint(1, 3)
# #             is_sparkle = (random.random() < 0.3)
# #             self.stars.append(Particle3D(x, y, z, color, size, is_decoration=False, is_sparkle=is_sparkle))

# #     def calculate_lighting(self, light_source):
# #         for star in self.stars:
# #             star.calculate_lighting(light_source)

# #     def rotate_y(self, angle):
# #         for star in self.stars:
# #             star.rotate_y(angle)

# #     def update(self, time):
# #         for star in self.stars:
# #             star.update(time)

# #     def draw(self, screen):
# #         for star in self.stars:
# #             pos_2d, size_2d = star.project_to_2d(SCREEN_WIDTH, SCREEN_HEIGHT)
# #             if size_2d > 0:
# #                 pygame.draw.circle(screen, star.color, pos_2d, max(1, size_2d))
# #                 if star.is_sparkle and size_2d > 1:
# #                     pygame.draw.circle(screen, (220, 220, 255), pos_2d, max(1, size_2d//2))


# # class FloatingParticles:
# #     def __init__(self, num_particles=400):
# #         self.particles = []
# #         self.generate_particles(num_particles)

# #     def generate_particles(self, num_particles):
# #         for _ in range(num_particles):
# #             x = random.uniform(-300, 300)
# #             y = random.uniform(-100, TREE_HEIGHT + 100)
# #             z = random.uniform(-300, -50)
# #             color_choice = random.choice([(200, 150, 180), (130, 160, 200), (200, 200, 150), (180, 180, 210)])
# #             color = color_choice
# #             size = random.randint(2, 5)
# #             is_sparkle = True
# #             self.particles.append(Particle3D(x, y, z, color, size, is_decoration=False, is_sparkle=is_sparkle))

# #     def calculate_lighting(self, light_source):
# #         for p in self.particles:
# #             p.calculate_lighting(light_source)

# #     def rotate_y(self, angle):
# #         for p in self.particles:
# #             p.rotate_y(angle)

# #     def update(self, time):
# #         for p in self.particles:
# #             p.update(time)

# #     def draw(self, screen):
# #         for p in self.particles:
# #             pos_2d, size_2d = p.project_to_2d(SCREEN_WIDTH, SCREEN_HEIGHT)
# #             if size_2d > 0:
# #                 pygame.draw.circle(screen, p.color, pos_2d, max(1, size_2d))
# #                 if size_2d > 2:
# #                     pygame.draw.circle(screen, (220, 220, 240), pos_2d, max(1, size_2d//2))


# # class LightSource:
# #     def __init__(self, x=200, y=300, z=-200):
# #         self.x = x
# #         self.y = y
# #         self.z = z
# #         self.angle = 0
# #         self.speed = 0.002
        
# #     def update(self):
# #         self.angle += self.speed
# #         if self.angle > 2 * math.pi:
# #             self.angle -= 2 * math.pi
        
# #         radius = 300
# #         self.x = radius * math.cos(self.angle)
# #         self.z = radius * math.sin(self.angle)
        
# #     def get_position(self):
# #         return (self.x, self.y, self.z)
    
# #     def draw_glow(self, screen):
# #         screen_center_x = SCREEN_WIDTH // 2
# #         screen_center_y = SCREEN_HEIGHT // 2
        
# #         num_rings = 3
# #         for i in range(num_rings):
# #             radius = 30 + i * 10
# #             alpha = 30 - i * 10
# #             color = (255, 255, 200, alpha)
            
# #             glow_surf = pygame.Surface((radius*2, radius*2), pygame.SRCALPHA)
# #             pygame.draw.circle(glow_surf, color, (radius, radius), radius)
            
# #             light_x = screen_center_x + self.x * 0.5
# #             light_y = screen_center_y - self.y * 0.5
            
# #             screen.blit(glow_surf, (light_x - radius, light_y - radius), special_flags=pygame.BLEND_ALPHA_SDL2)


# # def generate_tree_points(num_layers=12, points_per_layer=350, y_offset=-140):
# #     points = []
# #     tree_height = TREE_HEIGHT
# #     trunk_height = TRUNK_HEIGHT
# #     base_radius = BASE_RADIUS
# #     layer_height = (tree_height - trunk_height) / num_layers
# #     for layer_idx in range(num_layers):
# #         layer_bottom_y = trunk_height + layer_idx * layer_height
# #         layer_top_y = trunk_height + (layer_idx + 1) * layer_height
# #         layer_radius = base_radius * (1 - layer_idx / num_layers)
# #         for _ in range(points_per_layer):
# #             r = random.uniform(0.5 * layer_radius, layer_radius)
# #             theta = random.uniform(0, 2 * math.pi)
# #             x = r * math.cos(theta)
# #             z = r * math.sin(theta)
# #             y = random.uniform(layer_bottom_y, layer_top_y)
# #             y += y_offset
# #             color = random.choice(TREE_PARTICLE_COLORS)
# #             size = random.randint(2, 4)
# #             is_decoration = False
# #             if random.random() < 0.06:
# #                 color = random.choice([RED, YELLOW, GOLD, PINK, CYAN, (255, 215, 0), (255, 105, 180)])
# #                 size = random.randint(8, 12)
# #                 is_decoration = True
# #             elif random.random() < 0.02:
# #                 color = (255, 255, 255)
# #                 size = random.randint(6, 10)
# #                 is_decoration = True
# #             points.append(Particle3D(x, y, z, color, size, is_decoration))
    
# #     trunk_points = 400
# #     trunk_radius = 25
# #     trunk_top_y = trunk_height
# #     for _ in range(trunk_points):
# #         r = random.uniform(0, trunk_radius)
# #         theta = random.uniform(0, 2 * math.pi)
# #         x = r * math.cos(theta)
# #         z = r * math.sin(theta)
# #         y = random.uniform(0, trunk_top_y)
# #         y += y_offset
# #         points.append(Particle3D(x, y, z, (90, 50, 30), random.randint(3, 4), False))
    
# #     for _ in range(200):
# #         r = random.uniform(trunk_radius + 10, trunk_radius + 30)
# #         theta = random.uniform(0, 2 * math.pi)
# #         x = r * math.cos(theta)
# #         z = r * math.sin(theta)
# #         y = random.uniform(0, trunk_top_y)
# #         y += y_offset
# #         color = random.choice([(70, 40, 25), (80, 50, 35)])
# #         points.append(Particle3D(x, y, z, color, random.randint(2, 3), False))
    
# #     return points


# # def generate_background_particles(num_particles_far=800, num_particles_near=400):
# #     particles_far = []
# #     particles_near = []
# #     bg_distance_far = 700
# #     for _ in range(num_particles_far):
# #         r = random.uniform(bg_distance_far - 200, bg_distance_far + 200)
# #         theta = random.uniform(0, 2 * math.pi)
# #         phi = random.uniform(0, math.pi)
# #         x = r * math.sin(phi) * math.cos(theta)
# #         y = r * math.cos(phi) + 200
# #         z = r * math.sin(phi) * math.sin(theta)
# #         color = random.choice(BACKGROUND_PARTICLE_COLORS_FAR)
# #         size = random.randint(1, 3)
# #         particles_far.append(Particle3D(x, y, z, color, size, False))
    
# #     bg_distance_near = 300
# #     for _ in range(num_particles_near):
# #         x = random.uniform(-350, 350)
# #         y = random.uniform(-80, TREE_HEIGHT + 80)
# #         z = random.uniform(-350, 0)
# #         color = random.choice(BACKGROUND_PARTICLE_COLORS_NEAR)
# #         size = random.randint(2, 4)
# #         particles_near.append(Particle3D(x, y, z, color, size, False))
    
# #     return particles_far, particles_near


# # def main():
# #     pygame.init()
# #     screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
# #     pygame.display.set_caption("超炫3D圣诞树：银河之心")
# #     clock = pygame.time.Clock()
    
# #     background = GradientBackground(SCREEN_WIDTH, SCREEN_HEIGHT)
    
# #     y_offset = -140
# #     tree_points = generate_tree_points(num_layers=12, points_per_layer=350, y_offset=y_offset)
# #     heart_y_offset = TREE_HEIGHT + y_offset + 30
# #     heart = Heart3D(scale=6, y_offset=heart_y_offset)
# #     ground = GalaxyGround(radius=500, num_particles=3000, y_offset=y_offset)
# #     starfield = StarField(num_stars=800)
# #     floating = FloatingParticles(num_particles=400)
# #     bg_particles_far, bg_particles_near = generate_background_particles(800, 400)
    
# #     angle = 0
# #     rotation_speed = 0.003
# #     time_counter = 0
# #     running = True
    
# #     light_source = LightSource(200, 300, -200)
    
# #     while running:
# #         for event in pygame.event.get():
# #             if event.type == pygame.QUIT:
# #                 running = False
# #             elif event.type == pygame.KEYDOWN:
# #                 if event.key == pygame.K_UP:
# #                     rotation_speed = min(0.01, rotation_speed + 0.0005)
# #                 elif event.key == pygame.K_DOWN:
# #                     rotation_speed = max(0.001, rotation_speed - 0.0005)
# #                 elif event.key == pygame.K_SPACE:
# #                     rotation_speed = 0.003
        
# #         angle += rotation_speed
# #         if angle > 2 * math.pi:
# #             angle -= 2 * math.pi
        
# #         time_counter += 1
        
# #         light_source.update()
# #         light_pos = light_source.get_position()
        
# #         for point in tree_points:
# #             point.rotate_y(angle)
# #             point.calculate_lighting(light_pos)
# #             point.update(time_counter)
        
# #         heart.calculate_lighting(light_pos)
# #         heart.rotate_y(angle)
# #         heart.update(time_counter)
# #         ground.calculate_lighting(light_pos)
# #         ground.rotate_y(angle)
# #         ground.update(time_counter)
# #         starfield.calculate_lighting(light_pos)
# #         starfield.rotate_y(angle)
# #         starfield.update(time_counter)
# #         floating.calculate_lighting(light_pos)
# #         floating.rotate_y(angle)
# #         floating.update(time_counter)
        
# #         for point in bg_particles_far:
# #             point.rotate_y(angle)
# #             point.calculate_lighting(light_pos)
        
# #         for point in bg_particles_near:
# #             point.rotate_y(angle)
# #             point.calculate_lighting(light_pos)
        
# #         background.draw(screen)
# #         starfield.draw(screen)
        
# #         for point in bg_particles_far:
# #             pos_2d, size_2d = point.project_to_2d(SCREEN_WIDTH, SCREEN_HEIGHT)
# #             if size_2d > 0:
# #                 pygame.draw.circle(screen, point.color, pos_2d, max(1, size_2d))
        
# #         ground.draw(screen)
        
# #         for point in tree_points:
# #             pos_2d, size_2d = point.project_to_2d(SCREEN_WIDTH, SCREEN_HEIGHT)
# #             if size_2d > 0:
# #                 pygame.draw.circle(screen, point.color, pos_2d, max(1, size_2d))
# #                 if point.is_decoration and size_2d > 3:
# #                     pygame.draw.circle(screen, (255, 255, 255), pos_2d, max(1, size_2d//3))
        
# #         heart.draw(screen)
# #         floating.draw(screen)
        
# #         for point in bg_particles_near:
# #             pos_2d, size_2d = point.project_to_2d(SCREEN_WIDTH, SCREEN_HEIGHT)
# #             if size_2d > 0:
# #                 pygame.draw.circle(screen, point.color, pos_2d, max(1, size_2d))
        
# #         light_source.draw_glow(screen)
        
# #         font = pygame.font.SysFont(None, 24)
# #         info_text = f"旋转速度: {rotation_speed:.4f} (↑/↓方向键调整，空格重置)"
# #         text_surface = font.render(info_text, True, (80, 80, 120))
# #         screen.blit(text_surface, (10, 10))
        
# #         pygame.display.flip()
# #         clock.tick(FPS)
    
# #     pygame.quit()
# #     sys.exit()


# # if __name__ == "__main__":
# #     main()


# import pygame
# import numpy as np
# import math
# import random
# import sys

# SCREEN_WIDTH = 1200
# SCREEN_HEIGHT = 900
# FPS = 60

# TREE_HEIGHT = 400
# TRUNK_HEIGHT = 50
# BASE_RADIUS = 160

# BLACK = (0, 0, 0)
# GREEN = (34, 139, 34)
# RED = (255, 0, 0)
# YELLOW = (255, 255, 0)
# BLUE = (0, 0, 255)
# PURPLE = (128, 0, 128)
# ORANGE = (255, 165, 0)
# GOLD = (255, 215, 0)
# SILVER = (192, 192, 192)
# WHITE = (255, 255, 255)
# PINK = (255, 192, 203)
# CYAN = (0, 255, 255)
# HEART_COLOR = (255, 105, 180)
# HEART_COLOR_2 = (255, 20, 147)
# GROUND_COLOR = (100, 120, 180)
# TREE_PARTICLE_COLORS = [GREEN, RED, YELLOW, BLUE, PURPLE, ORANGE, GOLD, SILVER, PINK, CYAN]
# BACKGROUND_PARTICLE_COLORS_FAR = [(250, 240, 250), (240, 240, 255), (255, 240, 240), (240, 255, 240)]
# BACKGROUND_PARTICLE_COLORS_NEAR = [(250, 230, 250), (240, 230, 255), (255, 230, 230), (230, 255, 230)]

# class GradientBackground:
#     def __init__(self, width, height):
#         self.width = width
#         self.height = height
#         self.gradient_surface = self.create_gradient()
    
#     def create_gradient(self):
#         surface = pygame.Surface((self.width, self.height))
        
#         top_color = (255, 245, 250)
#         middle_color = (250, 240, 245)
#         bottom_color = (245, 235, 240)
        
#         for y in range(self.height):
#             if y < self.height // 2:
#                 ratio = y / (self.height // 2)
#                 r = top_color[0] * (1 - ratio) + middle_color[0] * ratio
#                 g = top_color[1] * (1 - ratio) + middle_color[1] * ratio
#                 b = top_color[2] * (1 - ratio) + middle_color[2] * ratio
#             else:
#                 ratio = (y - self.height // 2) / (self.height // 2)
#                 r = middle_color[0] * (1 - ratio) + bottom_color[0] * ratio
#                 g = middle_color[1] * (1 - ratio) + bottom_color[1] * ratio
#                 b = middle_color[2] * (1 - ratio) + bottom_color[2] * ratio
            
#             color = (int(r), int(g), int(b))
#             pygame.draw.line(surface, color, (0, y), (self.width, y))
        
#         star_count = 40
#         for _ in range(star_count):
#             x = random.randint(0, self.width)
#             y = random.randint(0, self.height)
#             size = random.randint(1, 3)
#             brightness = random.randint(200, 240)
#             color = (brightness, brightness, brightness)
#             pygame.draw.circle(surface, color, (x, y), size)
        
#         return surface
    
#     def draw(self, screen):
#         screen.blit(self.gradient_surface, (0, 0))

# class Particle3D:
#     def __init__(self, x, y, z, color, size, is_decoration=False, is_sparkle=False):
#         self.initial_pos = np.array([x, y, z, 1])
#         self.color = color
#         self.original_color = color
#         self.size = size
#         self.original_size = size
#         self.current_pos = self.initial_pos.copy()
#         self.is_decoration = is_decoration
#         self.is_sparkle = is_sparkle
#         self.rotation_speed = random.uniform(-0.01, 0.01)
#         self.rotation_angle = random.uniform(0, 2*math.pi)
#         self.float_speed = random.uniform(0.01, 0.03)
#         self.float_phase = random.uniform(0, 2*math.pi)
#         self.light_intensity = 1.0
#         if is_decoration:
#             self.blink_speed = random.uniform(0.02, 0.08)
#             self.blink_phase = random.uniform(0, 2*math.pi)
#         if is_sparkle:
#             self.sparkle_speed = random.uniform(0.05, 0.1)
#             self.sparkle_phase = random.uniform(0, 2*math.pi)
    
#     def calculate_lighting(self, light_source):
#         dx = self.current_pos[0] - light_source[0]
#         dy = self.current_pos[1] - light_source[1]
#         dz = self.current_pos[2] - light_source[2]
#         distance = math.sqrt(dx*dx + dy*dy + dz*dz)
#         intensity = 1.0 / (1.0 + distance * 0.001)
#         self.light_intensity = min(1.5, max(0.4, intensity))

#     def rotate_y(self, angle):
#         cos_a = math.cos(angle)
#         sin_a = math.sin(angle)
#         rotation_matrix = np.array([
#             [cos_a, 0, sin_a, 0],
#             [0, 1, 0, 0],
#             [-sin_a, 0, cos_a, 0],
#             [0, 0, 0, 1]
#         ])
#         self.current_pos = rotation_matrix @ self.initial_pos

#     def update(self, time):
#         if self.is_sparkle:
#             self.rotation_angle += self.rotation_speed
#             offset = math.sin(time * self.float_speed + self.float_phase) * 5
#             self.current_pos[1] = self.initial_pos[1] + offset
            
#             intensity = 0.6 + 0.4 * math.sin(time * self.sparkle_speed + self.sparkle_phase)
#             r = min(255, max(0, int(self.original_color[0] * intensity)))
#             g = min(255, max(0, int(self.original_color[1] * intensity)))
#             b = min(255, max(0, int(self.original_color[2] * intensity)))
#             self.color = (r, g, b)
#             self.size = self.original_size * (0.8 + 0.2 * intensity)
            
#         elif self.is_decoration:
#             intensity = 0.7 + 0.3 * math.sin(time * self.blink_speed + self.blink_phase)
#             r = min(255, max(0, int(self.original_color[0] * intensity)))
#             g = min(255, max(0, int(self.original_color[1] * intensity)))
#             b = min(255, max(0, int(self.original_color[2] * intensity)))
#             self.color = (r, g, b)
#             self.size = self.original_size * (0.9 + 0.1 * intensity)
        
#         if not self.is_decoration and not self.is_sparkle:
#             r = min(255, max(0, int(self.original_color[0] * self.light_intensity)))
#             g = min(255, max(0, int(self.original_color[1] * self.light_intensity)))
#             b = min(255, max(0, int(self.original_color[2] * self.light_intensity)))
#             self.color = (r, g, b)

#     def project_to_2d(self, screen_width, screen_height, fov=320):
#         x = self.current_pos[0]
#         y = self.current_pos[1]
#         z = self.current_pos[2]
#         factor = fov / (fov + z)
#         x_proj = x * factor + screen_width / 2
#         y_proj = -y * factor + screen_height / 2
#         return (int(x_proj), int(y_proj)), int(self.size * factor)


# class Heart3D:
#     def __init__(self, scale=6, y_offset=0):
#         self.particles = []
#         self.generate_heart(scale, y_offset)

#     def generate_heart(self, scale, y_offset):
#         num_points = 400
#         for _ in range(num_points):
#             t = random.uniform(0, 2 * math.pi)
#             u = random.uniform(-math.pi, math.pi)
#             x_param = 16 * (math.sin(t) ** 3)
#             y_param = 13 * math.cos(t) - 5 * math.cos(2 * t) - 2 * math.cos(3 * t) - math.cos(4 * t)
#             z_param = 16 * (math.sin(t) ** 3) * math.sin(u)
#             x = x_param * scale
#             y = y_param * scale + y_offset
#             z = z_param * scale * 0.5
#             if random.random() < 0.7:
#                 color = HEART_COLOR
#             else:
#                 color = HEART_COLOR_2
#             size = random.randint(1, 3)
#             is_decoration = True
#             self.particles.append(Particle3D(x, y, z, color, size, is_decoration))

#     def calculate_lighting(self, light_source):
#         for p in self.particles:
#             p.calculate_lighting(light_source)

#     def rotate_y(self, angle):
#         for p in self.particles:
#             p.rotate_y(angle)

#     def update(self, time):
#         for p in self.particles:
#             p.update(time)

#     def draw(self, screen):
#         for p in self.particles:
#             pos_2d, size_2d = p.project_to_2d(SCREEN_WIDTH, SCREEN_HEIGHT)
#             if size_2d > 0:
#                 pygame.draw.circle(screen, p.color, pos_2d, max(1, size_2d))
#                 if size_2d > 2:
#                     pygame.draw.circle(screen, (255, 255, 255), pos_2d, max(1, size_2d//2))


# class GalaxyGround:
#     def __init__(self, radius=500, num_particles=3000, y_offset=0):
#         self.particles = []
#         self.y_offset = y_offset
#         self.generate_ground(radius, num_particles)

#     def generate_ground(self, radius, num_particles):
#         for _ in range(num_particles):
#             r = random.uniform(0, radius)
#             spiral_tightness = 0.2
#             num_arms = 3
#             arm_offset = (2 * math.pi / num_arms) * random.randint(0, num_arms - 1)
#             theta = arm_offset + spiral_tightness * r + random.uniform(-0.3, 0.3)
#             x = r * math.cos(theta)
#             z = r * math.sin(theta)
#             y = 0 + self.y_offset
            
#             arm_index = int(arm_offset * num_arms / (2 * math.pi)) % 3
#             if arm_index == 0:
#                 base_color = (180, 200, 240)
#             elif arm_index == 1:
#                 base_color = (220, 180, 230)
#             else:
#                 base_color = (200, 220, 250)
            
#             distance_factor = max(0.1, 1 - r / radius)
#             color_variance = random.randint(-15, 15)
#             color = (
#                 max(160, min(255, base_color[0] + color_variance)),
#                 max(160, min(255, base_color[1] + color_variance)),
#                 max(180, min(255, base_color[2] + color_variance))
#             )
            
#             size = max(1, int(3 * distance_factor + random.randint(0, 2)))
#             is_sparkle = (random.random() < 0.1)
#             self.particles.append(Particle3D(x, y, z, color, size, is_decoration=False, is_sparkle=is_sparkle))

#     def calculate_lighting(self, light_source):
#         for p in self.particles:
#             p.calculate_lighting(light_source)

#     def rotate_y(self, angle):
#         for p in self.particles:
#             p.rotate_y(angle)

#     def update(self, time):
#         for p in self.particles:
#             p.update(time)

#     def draw(self, screen):
#         for p in self.particles:
#             pos_2d, size_2d = p.project_to_2d(SCREEN_WIDTH, SCREEN_HEIGHT)
#             if size_2d > 0:
#                 pygame.draw.circle(screen, p.color, pos_2d, max(1, size_2d))
#                 if p.is_sparkle and size_2d > 2:
#                     pygame.draw.circle(screen, (240, 240, 255), pos_2d, max(1, size_2d//2))


# class StarField:
#     def __init__(self, num_stars=800):
#         self.stars = []
#         self.generate_stars(num_stars)

#     def generate_stars(self, num_stars):
#         for _ in range(num_stars):
#             r = random.uniform(500, 1000)
#             theta = random.uniform(0, 2 * math.pi)
#             phi = random.uniform(0, math.pi)
#             x = r * math.sin(phi) * math.cos(theta)
#             y = r * math.cos(phi) + 200
#             z = r * math.sin(phi) * math.sin(theta)
            
#             brightness = random.uniform(0.3, 1.0)
#             color_value = int(180 + 75 * brightness)
#             color = (color_value, color_value, color_value)
#             size = random.randint(1, 3)
#             is_sparkle = (random.random() < 0.3)
#             self.stars.append(Particle3D(x, y, z, color, size, is_decoration=False, is_sparkle=is_sparkle))

#     def calculate_lighting(self, light_source):
#         for star in self.stars:
#             star.calculate_lighting(light_source)

#     def rotate_y(self, angle):
#         for star in self.stars:
#             star.rotate_y(angle)

#     def update(self, time):
#         for star in self.stars:
#             star.update(time)

#     def draw(self, screen):
#         for star in self.stars:
#             pos_2d, size_2d = star.project_to_2d(SCREEN_WIDTH, SCREEN_HEIGHT)
#             if size_2d > 0:
#                 pygame.draw.circle(screen, star.color, pos_2d, max(1, size_2d))
#                 if star.is_sparkle and size_2d > 1:
#                     pygame.draw.circle(screen, (240, 240, 255), pos_2d, max(1, size_2d//2))


# class FloatingParticles:
#     def __init__(self, num_particles=400):
#         self.particles = []
#         self.generate_particles(num_particles)

#     def generate_particles(self, num_particles):
#         for _ in range(num_particles):
#             x = random.uniform(-300, 300)
#             y = random.uniform(-100, TREE_HEIGHT + 100)
#             z = random.uniform(-300, -50)
#             color_choice = random.choice([(255, 200, 220), (200, 220, 255), (255, 255, 200), (220, 200, 255)])
#             color = color_choice
#             size = random.randint(2, 5)
#             is_sparkle = True
#             self.particles.append(Particle3D(x, y, z, color, size, is_decoration=False, is_sparkle=is_sparkle))

#     def calculate_lighting(self, light_source):
#         for p in self.particles:
#             p.calculate_lighting(light_source)

#     def rotate_y(self, angle):
#         for p in self.particles:
#             p.rotate_y(angle)

#     def update(self, time):
#         for p in self.particles:
#             p.update(time)

#     def draw(self, screen):
#         for p in self.particles:
#             pos_2d, size_2d = p.project_to_2d(SCREEN_WIDTH, SCREEN_HEIGHT)
#             if size_2d > 0:
#                 pygame.draw.circle(screen, p.color, pos_2d, max(1, size_2d))
#                 if size_2d > 2:
#                     pygame.draw.circle(screen, (240, 240, 255), pos_2d, max(1, size_2d//2))


# class LightSource:
#     def __init__(self, x=200, y=300, z=-200):
#         self.x = x
#         self.y = y
#         self.z = z
#         self.angle = 0
#         self.speed = 0.002
        
#     def update(self):
#         self.angle += self.speed
#         if self.angle > 2 * math.pi:
#             self.angle -= 2 * math.pi
        
#         radius = 300
#         self.x = radius * math.cos(self.angle)
#         self.z = radius * math.sin(self.angle)
        
#     def get_position(self):
#         return (self.x, self.y, self.z)
    
#     def draw_glow(self, screen):
#         screen_center_x = SCREEN_WIDTH // 2
#         screen_center_y = SCREEN_HEIGHT // 2
        
#         num_rings = 3
#         for i in range(num_rings):
#             radius = 30 + i * 10
#             alpha = 30 - i * 10
#             color = (255, 255, 230, alpha)
            
#             glow_surf = pygame.Surface((radius*2, radius*2), pygame.SRCALPHA)
#             pygame.draw.circle(glow_surf, color, (radius, radius), radius)
            
#             light_x = screen_center_x + self.x * 0.5
#             light_y = screen_center_y - self.y * 0.5
            
#             screen.blit(glow_surf, (light_x - radius, light_y - radius), special_flags=pygame.BLEND_ALPHA_SDL2)


# def generate_tree_points(num_layers=12, points_per_layer=350, y_offset=-140):
#     points = []
#     tree_height = TREE_HEIGHT
#     trunk_height = TRUNK_HEIGHT
#     base_radius = BASE_RADIUS
#     layer_height = (tree_height - trunk_height) / num_layers
#     for layer_idx in range(num_layers):
#         layer_bottom_y = trunk_height + layer_idx * layer_height
#         layer_top_y = trunk_height + (layer_idx + 1) * layer_height
#         layer_radius = base_radius * (1 - layer_idx / num_layers)
#         for _ in range(points_per_layer):
#             r = random.uniform(0.5 * layer_radius, layer_radius)
#             theta = random.uniform(0, 2 * math.pi)
#             x = r * math.cos(theta)
#             z = r * math.sin(theta)
#             y = random.uniform(layer_bottom_y, layer_top_y)
#             y += y_offset
#             color = random.choice(TREE_PARTICLE_COLORS)
#             size = random.randint(2, 4)
#             is_decoration = False
#             if random.random() < 0.06:
#                 color = random.choice([RED, YELLOW, GOLD, PINK, CYAN, (255, 215, 0), (255, 105, 180)])
#                 size = random.randint(8, 12)
#                 is_decoration = True
#             elif random.random() < 0.02:
#                 color = (255, 255, 255)
#                 size = random.randint(6, 10)
#                 is_decoration = True
#             points.append(Particle3D(x, y, z, color, size, is_decoration))
    
#     trunk_points = 400
#     trunk_radius = 25
#     trunk_top_y = trunk_height
#     for _ in range(trunk_points):
#         r = random.uniform(0, trunk_radius)
#         theta = random.uniform(0, 2 * math.pi)
#         x = r * math.cos(theta)
#         z = r * math.sin(theta)
#         y = random.uniform(0, trunk_top_y)
#         y += y_offset
#         points.append(Particle3D(x, y, z, (120, 80, 50), random.randint(3, 4), False))
    
#     for _ in range(200):
#         r = random.uniform(trunk_radius + 10, trunk_radius + 30)
#         theta = random.uniform(0, 2 * math.pi)
#         x = r * math.cos(theta)
#         z = r * math.sin(theta)
#         y = random.uniform(0, trunk_top_y)
#         y += y_offset
#         color = random.choice([(100, 70, 50), (110, 80, 60)])
#         points.append(Particle3D(x, y, z, color, random.randint(2, 3), False))
    
#     return points


# def generate_background_particles(num_particles_far=800, num_particles_near=400):
#     particles_far = []
#     particles_near = []
#     bg_distance_far = 700
#     for _ in range(num_particles_far):
#         r = random.uniform(bg_distance_far - 200, bg_distance_far + 200)
#         theta = random.uniform(0, 2 * math.pi)
#         phi = random.uniform(0, math.pi)
#         x = r * math.sin(phi) * math.cos(theta)
#         y = r * math.cos(phi) + 200
#         z = r * math.sin(phi) * math.sin(theta)
#         color = random.choice(BACKGROUND_PARTICLE_COLORS_FAR)
#         size = random.randint(1, 3)
#         particles_far.append(Particle3D(x, y, z, color, size, False))
    
#     bg_distance_near = 300
#     for _ in range(num_particles_near):
#         x = random.uniform(-350, 350)
#         y = random.uniform(-80, TREE_HEIGHT + 80)
#         z = random.uniform(-350, 0)
#         color = random.choice(BACKGROUND_PARTICLE_COLORS_NEAR)
#         size = random.randint(2, 4)
#         particles_near.append(Particle3D(x, y, z, color, size, False))
    
#     return particles_far, particles_near


# def main():
#     pygame.init()
#     screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
#     pygame.display.set_caption("超炫3D圣诞树：银河之心")
#     clock = pygame.time.Clock()
    
#     background = GradientBackground(SCREEN_WIDTH, SCREEN_HEIGHT)
    
#     y_offset = -140
#     tree_points = generate_tree_points(num_layers=12, points_per_layer=350, y_offset=y_offset)
#     heart_y_offset = TREE_HEIGHT + y_offset + 30
#     heart = Heart3D(scale=6, y_offset=heart_y_offset)
#     ground = GalaxyGround(radius=500, num_particles=3000, y_offset=y_offset)
#     starfield = StarField(num_stars=800)
#     floating = FloatingParticles(num_particles=400)
#     bg_particles_far, bg_particles_near = generate_background_particles(800, 400)
    
#     angle = 0
#     rotation_speed = 0.003
#     time_counter = 0
#     running = True
    
#     light_source = LightSource(200, 300, -200)
    
#     while running:
#         for event in pygame.event.get():
#             if event.type == pygame.QUIT:
#                 running = False
#             elif event.type == pygame.KEYDOWN:
#                 if event.key == pygame.K_UP:
#                     rotation_speed = min(0.01, rotation_speed + 0.0005)
#                 elif event.key == pygame.K_DOWN:
#                     rotation_speed = max(0.001, rotation_speed - 0.0005)
#                 elif event.key == pygame.K_SPACE:
#                     rotation_speed = 0.003
        
#         angle += rotation_speed
#         if angle > 2 * math.pi:
#             angle -= 2 * math.pi
        
#         time_counter += 1
        
#         light_source.update()
#         light_pos = light_source.get_position()
        
#         for point in tree_points:
#             point.rotate_y(angle)
#             point.calculate_lighting(light_pos)
#             point.update(time_counter)
        
#         heart.calculate_lighting(light_pos)
#         heart.rotate_y(angle)
#         heart.update(time_counter)
#         ground.calculate_lighting(light_pos)
#         ground.rotate_y(angle)
#         ground.update(time_counter)
#         starfield.calculate_lighting(light_pos)
#         starfield.rotate_y(angle)
#         starfield.update(time_counter)
#         floating.calculate_lighting(light_pos)
#         floating.rotate_y(angle)
#         floating.update(time_counter)
        
#         for point in bg_particles_far:
#             point.rotate_y(angle)
#             point.calculate_lighting(light_pos)
        
#         for point in bg_particles_near:
#             point.rotate_y(angle)
#             point.calculate_lighting(light_pos)
        
#         background.draw(screen)
#         starfield.draw(screen)
        
#         for point in bg_particles_far:
#             pos_2d, size_2d = point.project_to_2d(SCREEN_WIDTH, SCREEN_HEIGHT)
#             if size_2d > 0:
#                 pygame.draw.circle(screen, point.color, pos_2d, max(1, size_2d))
        
#         ground.draw(screen)
        
#         for point in tree_points:
#             pos_2d, size_2d = point.project_to_2d(SCREEN_WIDTH, SCREEN_HEIGHT)
#             if size_2d > 0:
#                 pygame.draw.circle(screen, point.color, pos_2d, max(1, size_2d))
#                 if point.is_decoration and size_2d > 3:
#                     pygame.draw.circle(screen, (255, 255, 255), pos_2d, max(1, size_2d//3))
        
#         heart.draw(screen)
#         floating.draw(screen)
        
#         for point in bg_particles_near:
#             pos_2d, size_2d = point.project_to_2d(SCREEN_WIDTH, SCREEN_HEIGHT)
#             if size_2d > 0:
#                 pygame.draw.circle(screen, point.color, pos_2d, max(1, size_2d))
        
#         light_source.draw_glow(screen)
        
#         font = pygame.font.SysFont(None, 24)
#         info_text = f"旋转速度: {rotation_speed:.4f} (↑/↓方向键调整，空格重置)"
#         text_surface = font.render(info_text, True, (120, 100, 140))
#         screen.blit(text_surface, (10, 10))
        
#         pygame.display.flip()
#         clock.tick(FPS)
    
#     pygame.quit()
#     sys.exit()


# if __name__ == "__main__":
#     main()




# import pygame
# import numpy as np
# import math
# import random
# import sys

# SCREEN_WIDTH = 1200
# SCREEN_HEIGHT = 900
# FPS = 60

# TREE_HEIGHT = 400
# TRUNK_HEIGHT = 50
# BASE_RADIUS = 160

# BLACK = (0, 0, 0)
# GREEN = (100, 200, 100)
# RED = (255, 100, 100)
# YELLOW = (255, 255, 150)
# BLUE = (150, 200, 255)
# PURPLE = (200, 150, 255)
# ORANGE = (255, 200, 100)
# GOLD = (255, 220, 100)
# SILVER = (220, 220, 255)
# WHITE = (255, 255, 255)
# PINK = (255, 200, 220)
# CYAN = (150, 255, 255)
# HEART_COLOR = (255, 140, 200)
# HEART_COLOR_2 = (255, 80, 160)
# GROUND_COLOR = (150, 170, 230)
# TREE_PARTICLE_COLORS = [GREEN, RED, YELLOW, BLUE, PURPLE, ORANGE, GOLD, SILVER, PINK, CYAN]
# BACKGROUND_PARTICLE_COLORS_FAR = [(255, 245, 255), (245, 245, 255), (255, 245, 245), (245, 255, 245)]
# BACKGROUND_PARTICLE_COLORS_NEAR = [(255, 235, 255), (245, 235, 255), (255, 235, 235), (235, 255, 235)]

# class GradientBackground:
#     def __init__(self, width, height):
#         self.width = width
#         self.height = height
#         self.gradient_surface = self.create_gradient()
    
#     def create_gradient(self):
#         surface = pygame.Surface((self.width, self.height))
        
#         top_color = (255, 250, 255)
#         middle_color = (255, 245, 250)
#         bottom_color = (250, 240, 245)
        
#         for y in range(self.height):
#             if y < self.height // 2:
#                 ratio = y / (self.height // 2)
#                 r = top_color[0] * (1 - ratio) + middle_color[0] * ratio
#                 g = top_color[1] * (1 - ratio) + middle_color[1] * ratio
#                 b = top_color[2] * (1 - ratio) + middle_color[2] * ratio
#             else:
#                 ratio = (y - self.height // 2) / (self.height // 2)
#                 r = middle_color[0] * (1 - ratio) + bottom_color[0] * ratio
#                 g = middle_color[1] * (1 - ratio) + bottom_color[1] * ratio
#                 b = middle_color[2] * (1 - ratio) + bottom_color[2] * ratio
            
#             color = (int(r), int(g), int(b))
#             pygame.draw.line(surface, color, (0, y), (self.width, y))
        
#         star_count = 40
#         for _ in range(star_count):
#             x = random.randint(0, self.width)
#             y = random.randint(0, self.height)
#             size = random.randint(1, 3)
#             brightness = random.randint(220, 250)
#             color = (brightness, brightness, brightness)
#             pygame.draw.circle(surface, color, (x, y), size)
        
#         return surface
    
#     def draw(self, screen):
#         screen.blit(self.gradient_surface, (0, 0))

# class Particle3D:
#     def __init__(self, x, y, z, color, size, is_decoration=False, is_sparkle=False):
#         self.initial_pos = np.array([x, y, z, 1])
#         self.color = color
#         self.original_color = color
#         self.size = size
#         self.original_size = size
#         self.current_pos = self.initial_pos.copy()
#         self.is_decoration = is_decoration
#         self.is_sparkle = is_sparkle
#         self.rotation_speed = random.uniform(-0.01, 0.01)
#         self.rotation_angle = random.uniform(0, 2*math.pi)
#         self.float_speed = random.uniform(0.01, 0.03)
#         self.float_phase = random.uniform(0, 2*math.pi)
#         self.light_intensity = 1.0
#         if is_decoration:
#             self.blink_speed = random.uniform(0.02, 0.08)
#             self.blink_phase = random.uniform(0, 2*math.pi)
#         if is_sparkle:
#             self.sparkle_speed = random.uniform(0.05, 0.1)
#             self.sparkle_phase = random.uniform(0, 2*math.pi)
    
#     def calculate_lighting(self, light_source):
#         dx = self.current_pos[0] - light_source[0]
#         dy = self.current_pos[1] - light_source[1]
#         dz = self.current_pos[2] - light_source[2]
#         distance = math.sqrt(dx*dx + dy*dy + dz*dz)
#         intensity = 1.0 / (1.0 + distance * 0.001)
#         self.light_intensity = min(1.5, max(0.5, intensity))

#     def rotate_y(self, angle):
#         cos_a = math.cos(angle)
#         sin_a = math.sin(angle)
#         rotation_matrix = np.array([
#             [cos_a, 0, sin_a, 0],
#             [0, 1, 0, 0],
#             [-sin_a, 0, cos_a, 0],
#             [0, 0, 0, 1]
#         ])
#         self.current_pos = rotation_matrix @ self.initial_pos

#     def update(self, time):
#         if self.is_sparkle:
#             self.rotation_angle += self.rotation_speed
#             offset = math.sin(time * self.float_speed + self.float_phase) * 5
#             self.current_pos[1] = self.initial_pos[1] + offset
            
#             intensity = 0.7 + 0.3 * math.sin(time * self.sparkle_speed + self.sparkle_phase)
#             r = min(255, max(0, int(self.original_color[0] * intensity)))
#             g = min(255, max(0, int(self.original_color[1] * intensity)))
#             b = min(255, max(0, int(self.original_color[2] * intensity)))
#             self.color = (r, g, b)
#             self.size = self.original_size * (0.8 + 0.2 * intensity)
            
#         elif self.is_decoration:
#             intensity = 0.8 + 0.2 * math.sin(time * self.blink_speed + self.blink_phase)
#             r = min(255, max(0, int(self.original_color[0] * intensity)))
#             g = min(255, max(0, int(self.original_color[1] * intensity)))
#             b = min(255, max(0, int(self.original_color[2] * intensity)))
#             self.color = (r, g, b)
#             self.size = self.original_size * (0.9 + 0.1 * intensity)
        
#         if not self.is_decoration and not self.is_sparkle:
#             r = min(255, max(0, int(self.original_color[0] * self.light_intensity)))
#             g = min(255, max(0, int(self.original_color[1] * self.light_intensity)))
#             b = min(255, max(0, int(self.original_color[2] * self.light_intensity)))
#             self.color = (r, g, b)

#     def project_to_2d(self, screen_width, screen_height, fov=320):
#         x = self.current_pos[0]
#         y = self.current_pos[1]
#         z = self.current_pos[2]
#         factor = fov / (fov + z)
#         x_proj = x * factor + screen_width / 2
#         y_proj = -y * factor + screen_height / 2
#         return (int(x_proj), int(y_proj)), int(self.size * factor)


# class Heart3D:
#     def __init__(self, scale=6, y_offset=0):
#         self.particles = []
#         self.generate_heart(scale, y_offset)

#     def generate_heart(self, scale, y_offset):
#         num_points = 400
#         for _ in range(num_points):
#             t = random.uniform(0, 2 * math.pi)
#             u = random.uniform(-math.pi, math.pi)
#             x_param = 16 * (math.sin(t) ** 3)
#             y_param = 13 * math.cos(t) - 5 * math.cos(2 * t) - 2 * math.cos(3 * t) - math.cos(4 * t)
#             z_param = 16 * (math.sin(t) ** 3) * math.sin(u)
#             x = x_param * scale
#             y = y_param * scale + y_offset
#             z = z_param * scale * 0.5
#             if random.random() < 0.7:
#                 color = HEART_COLOR
#             else:
#                 color = HEART_COLOR_2
#             size = random.randint(1, 3)
#             is_decoration = True
#             self.particles.append(Particle3D(x, y, z, color, size, is_decoration))

#     def calculate_lighting(self, light_source):
#         for p in self.particles:
#             p.calculate_lighting(light_source)

#     def rotate_y(self, angle):
#         for p in self.particles:
#             p.rotate_y(angle)

#     def update(self, time):
#         for p in self.particles:
#             p.update(time)

#     def draw(self, screen):
#         for p in self.particles:
#             pos_2d, size_2d = p.project_to_2d(SCREEN_WIDTH, SCREEN_HEIGHT)
#             if size_2d > 0:
#                 pygame.draw.circle(screen, p.color, pos_2d, max(1, size_2d))
#                 if size_2d > 2:
#                     pygame.draw.circle(screen, (255, 255, 255), pos_2d, max(1, size_2d//2))


# class GalaxyGround:
#     def __init__(self, radius=500, num_particles=3000, y_offset=0):
#         self.particles = []
#         self.y_offset = y_offset
#         self.generate_ground(radius, num_particles)

#     def generate_ground(self, radius, num_particles):
#         for _ in range(num_particles):
#             r = random.uniform(0, radius)
#             spiral_tightness = 0.2
#             num_arms = 3
#             arm_offset = (2 * math.pi / num_arms) * random.randint(0, num_arms - 1)
#             theta = arm_offset + spiral_tightness * r + random.uniform(-0.3, 0.3)
#             x = r * math.cos(theta)
#             z = r * math.sin(theta)
#             y = 0 + self.y_offset
            
#             arm_index = int(arm_offset * num_arms / (2 * math.pi)) % 3
#             if arm_index == 0:
#                 base_color = (200, 220, 255)
#             elif arm_index == 1:
#                 base_color = (240, 200, 255)
#             else:
#                 base_color = (220, 240, 255)
            
#             distance_factor = max(0.1, 1 - r / radius)
#             color_variance = random.randint(-10, 10)
#             color = (
#                 max(180, min(255, base_color[0] + color_variance)),
#                 max(180, min(255, base_color[1] + color_variance)),
#                 max(200, min(255, base_color[2] + color_variance))
#             )
            
#             size = max(1, int(3 * distance_factor + random.randint(0, 2)))
#             is_sparkle = (random.random() < 0.1)
#             self.particles.append(Particle3D(x, y, z, color, size, is_decoration=False, is_sparkle=is_sparkle))

#     def calculate_lighting(self, light_source):
#         for p in self.particles:
#             p.calculate_lighting(light_source)

#     def rotate_y(self, angle):
#         for p in self.particles:
#             p.rotate_y(angle)

#     def update(self, time):
#         for p in self.particles:
#             p.update(time)

#     def draw(self, screen):
#         for p in self.particles:
#             pos_2d, size_2d = p.project_to_2d(SCREEN_WIDTH, SCREEN_HEIGHT)
#             if size_2d > 0:
#                 pygame.draw.circle(screen, p.color, pos_2d, max(1, size_2d))
#                 if p.is_sparkle and size_2d > 2:
#                     pygame.draw.circle(screen, (250, 250, 255), pos_2d, max(1, size_2d//2))


# class StarField:
#     def __init__(self, num_stars=800):
#         self.stars = []
#         self.generate_stars(num_stars)

#     def generate_stars(self, num_stars):
#         for _ in range(num_stars):
#             r = random.uniform(500, 1000)
#             theta = random.uniform(0, 2 * math.pi)
#             phi = random.uniform(0, math.pi)
#             x = r * math.sin(phi) * math.cos(theta)
#             y = r * math.cos(phi) + 200
#             z = r * math.sin(phi) * math.sin(theta)
            
#             brightness = random.uniform(0.5, 1.0)
#             color_value = int(200 + 55 * brightness)
#             color = (color_value, color_value, color_value)
#             size = random.randint(1, 3)
#             is_sparkle = (random.random() < 0.3)
#             self.stars.append(Particle3D(x, y, z, color, size, is_decoration=False, is_sparkle=is_sparkle))

#     def calculate_lighting(self, light_source):
#         for star in self.stars:
#             star.calculate_lighting(light_source)

#     def rotate_y(self, angle):
#         for star in self.stars:
#             star.rotate_y(angle)

#     def update(self, time):
#         for star in self.stars:
#             star.update(time)

#     def draw(self, screen):
#         for star in self.stars:
#             pos_2d, size_2d = star.project_to_2d(SCREEN_WIDTH, SCREEN_HEIGHT)
#             if size_2d > 0:
#                 pygame.draw.circle(screen, star.color, pos_2d, max(1, size_2d))
#                 if star.is_sparkle and size_2d > 1:
#                     pygame.draw.circle(screen, (245, 245, 255), pos_2d, max(1, size_2d//2))


# class FloatingParticles:
#     def __init__(self, num_particles=400):
#         self.particles = []
#         self.generate_particles(num_particles)

#     def generate_particles(self, num_particles):
#         for _ in range(num_particles):
#             x = random.uniform(-300, 300)
#             y = random.uniform(-100, TREE_HEIGHT + 100)
#             z = random.uniform(-300, -50)
#             color_choice = random.choice([(255, 210, 230), (210, 230, 255), (255, 255, 210), (230, 210, 255)])
#             color = color_choice
#             size = random.randint(2, 5)
#             is_sparkle = True
#             self.particles.append(Particle3D(x, y, z, color, size, is_decoration=False, is_sparkle=is_sparkle))

#     def calculate_lighting(self, light_source):
#         for p in self.particles:
#             p.calculate_lighting(light_source)

#     def rotate_y(self, angle):
#         for p in self.particles:
#             p.rotate_y(angle)

#     def update(self, time):
#         for p in self.particles:
#             p.update(time)

#     def draw(self, screen):
#         for p in self.particles:
#             pos_2d, size_2d = p.project_to_2d(SCREEN_WIDTH, SCREEN_HEIGHT)
#             if size_2d > 0:
#                 pygame.draw.circle(screen, p.color, pos_2d, max(1, size_2d))
#                 if size_2d > 2:
#                     pygame.draw.circle(screen, (245, 245, 255), pos_2d, max(1, size_2d//2))


# class LightSource:
#     def __init__(self, x=200, y=300, z=-200):
#         self.x = x
#         self.y = y
#         self.z = z
#         self.angle = 0
#         self.speed = 0.002
        
#     def update(self):
#         self.angle += self.speed
#         if self.angle > 2 * math.pi:
#             self.angle -= 2 * math.pi
        
#         radius = 300
#         self.x = radius * math.cos(self.angle)
#         self.z = radius * math.sin(self.angle)
        
#     def get_position(self):
#         return (self.x, self.y, self.z)
    
#     def draw_glow(self, screen):
#         screen_center_x = SCREEN_WIDTH // 2
#         screen_center_y = SCREEN_HEIGHT // 2
        
#         num_rings = 3
#         for i in range(num_rings):
#             radius = 30 + i * 10
#             alpha = 30 - i * 10
#             color = (255, 255, 240, alpha)
            
#             glow_surf = pygame.Surface((radius*2, radius*2), pygame.SRCALPHA)
#             pygame.draw.circle(glow_surf, color, (radius, radius), radius)
            
#             light_x = screen_center_x + self.x * 0.5
#             light_y = screen_center_y - self.y * 0.5
            
#             screen.blit(glow_surf, (light_x - radius, light_y - radius), special_flags=pygame.BLEND_ALPHA_SDL2)


# def generate_tree_points(num_layers=12, points_per_layer=350, y_offset=-140):
#     points = []
#     tree_height = TREE_HEIGHT
#     trunk_height = TRUNK_HEIGHT
#     base_radius = BASE_RADIUS
#     layer_height = (tree_height - trunk_height) / num_layers
#     for layer_idx in range(num_layers):
#         layer_bottom_y = trunk_height + layer_idx * layer_height
#         layer_top_y = trunk_height + (layer_idx + 1) * layer_height
#         layer_radius = base_radius * (1 - layer_idx / num_layers)
#         for _ in range(points_per_layer):
#             r = random.uniform(0.5 * layer_radius, layer_radius)
#             theta = random.uniform(0, 2 * math.pi)
#             x = r * math.cos(theta)
#             z = r * math.sin(theta)
#             y = random.uniform(layer_bottom_y, layer_top_y)
#             y += y_offset
#             color = random.choice(TREE_PARTICLE_COLORS)
#             size = random.randint(2, 4)
#             is_decoration = False
#             if random.random() < 0.06:
#                 color = random.choice([RED, YELLOW, GOLD, PINK, CYAN, (255, 220, 100), (255, 140, 200)])
#                 size = random.randint(8, 12)
#                 is_decoration = True
#             elif random.random() < 0.02:
#                 color = (255, 255, 255)
#                 size = random.randint(6, 10)
#                 is_decoration = True
#             points.append(Particle3D(x, y, z, color, size, is_decoration))
    
#     trunk_points = 400
#     trunk_radius = 25
#     trunk_top_y = trunk_height
#     for _ in range(trunk_points):
#         r = random.uniform(0, trunk_radius)
#         theta = random.uniform(0, 2 * math.pi)
#         x = r * math.cos(theta)
#         z = r * math.sin(theta)
#         y = random.uniform(0, trunk_top_y)
#         y += y_offset
#         points.append(Particle3D(x, y, z, (150, 100, 70), random.randint(3, 4), False))
    
#     for _ in range(200):
#         r = random.uniform(trunk_radius + 10, trunk_radius + 30)
#         theta = random.uniform(0, 2 * math.pi)
#         x = r * math.cos(theta)
#         z = r * math.sin(theta)
#         y = random.uniform(0, trunk_top_y)
#         y += y_offset
#         color = random.choice([(130, 90, 70), (140, 100, 80)])
#         points.append(Particle3D(x, y, z, color, random.randint(2, 3), False))
    
#     return points


# def generate_background_particles(num_particles_far=800, num_particles_near=400):
#     particles_far = []
#     particles_near = []
#     bg_distance_far = 700
#     for _ in range(num_particles_far):
#         r = random.uniform(bg_distance_far - 200, bg_distance_far + 200)
#         theta = random.uniform(0, 2 * math.pi)
#         phi = random.uniform(0, math.pi)
#         x = r * math.sin(phi) * math.cos(theta)
#         y = r * math.cos(phi) + 200
#         z = r * math.sin(phi) * math.sin(theta)
#         color = random.choice(BACKGROUND_PARTICLE_COLORS_FAR)
#         size = random.randint(1, 3)
#         particles_far.append(Particle3D(x, y, z, color, size, False))
    
#     bg_distance_near = 300
#     for _ in range(num_particles_near):
#         x = random.uniform(-350, 350)
#         y = random.uniform(-80, TREE_HEIGHT + 80)
#         z = random.uniform(-350, 0)
#         color = random.choice(BACKGROUND_PARTICLE_COLORS_NEAR)
#         size = random.randint(2, 4)
#         particles_near.append(Particle3D(x, y, z, color, size, False))
    
#     return particles_far, particles_near


# def main():
#     pygame.init()
#     screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
#     pygame.display.set_caption("超炫3D圣诞树：银河之心")
#     clock = pygame.time.Clock()
    
#     background = GradientBackground(SCREEN_WIDTH, SCREEN_HEIGHT)
    
#     y_offset = -140
#     tree_points = generate_tree_points(num_layers=12, points_per_layer=350, y_offset=y_offset)
#     heart_y_offset = TREE_HEIGHT + y_offset + 30
#     heart = Heart3D(scale=6, y_offset=heart_y_offset)
#     ground = GalaxyGround(radius=500, num_particles=3000, y_offset=y_offset)
#     starfield = StarField(num_stars=800)
#     floating = FloatingParticles(num_particles=400)
#     bg_particles_far, bg_particles_near = generate_background_particles(800, 400)
    
#     angle = 0
#     rotation_speed = 0.003
#     time_counter = 0
#     running = True
    
#     light_source = LightSource(200, 300, -200)
    
#     while running:
#         for event in pygame.event.get():
#             if event.type == pygame.QUIT:
#                 running = False
        
#         angle += rotation_speed
#         if angle > 2 * math.pi:
#             angle -= 2 * math.pi
        
#         time_counter += 1
        
#         light_source.update()
#         light_pos = light_source.get_position()
        
#         for point in tree_points:
#             point.rotate_y(angle)
#             point.calculate_lighting(light_pos)
#             point.update(time_counter)
        
#         heart.calculate_lighting(light_pos)
#         heart.rotate_y(angle)
#         heart.update(time_counter)
#         ground.calculate_lighting(light_pos)
#         ground.rotate_y(angle)
#         ground.update(time_counter)
#         starfield.calculate_lighting(light_pos)
#         starfield.rotate_y(angle)
#         starfield.update(time_counter)
#         floating.calculate_lighting(light_pos)
#         floating.rotate_y(angle)
#         floating.update(time_counter)
        
#         for point in bg_particles_far:
#             point.rotate_y(angle)
#             point.calculate_lighting(light_pos)
        
#         for point in bg_particles_near:
#             point.rotate_y(angle)
#             point.calculate_lighting(light_pos)
        
#         background.draw(screen)
#         starfield.draw(screen)
        
#         for point in bg_particles_far:
#             pos_2d, size_2d = point.project_to_2d(SCREEN_WIDTH, SCREEN_HEIGHT)
#             if size_2d > 0:
#                 pygame.draw.circle(screen, point.color, pos_2d, max(1, size_2d))
        
#         ground.draw(screen)
        
#         for point in tree_points:
#             pos_2d, size_2d = point.project_to_2d(SCREEN_WIDTH, SCREEN_HEIGHT)
#             if size_2d > 0:
#                 pygame.draw.circle(screen, point.color, pos_2d, max(1, size_2d))
#                 if point.is_decoration and size_2d > 3:
#                     pygame.draw.circle(screen, (255, 255, 255), pos_2d, max(1, size_2d//3))
        
#         heart.draw(screen)
#         floating.draw(screen)
        
#         for point in bg_particles_near:
#             pos_2d, size_2d = point.project_to_2d(SCREEN_WIDTH, SCREEN_HEIGHT)
#             if size_2d > 0:
#                 pygame.draw.circle(screen, point.color, pos_2d, max(1, size_2d))
        
#         light_source.draw_glow(screen)
        
#         pygame.display.flip()
#         clock.tick(FPS)
    
#     pygame.quit()
#     sys.exit()


# if __name__ == "__main__":
#     main()