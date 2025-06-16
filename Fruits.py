import pygame
from Images import IMAGES
import numpy as np

# Constants (match Main.py)
TILE_SIZE = 50
MAP_OFFSET = 25

# wektor kierunków
direction_vectors = {
    'left':  (0, -1),
    'right': (0,  1),
    'up':    (-1, 0),
    'down':  (1,  0),
}

class AnimatedFruit(pygame.sprite.Sprite):
    def __init__(self, x, y, frame_keys, anim_interval=200):
        super().__init__()
        self.frames = [IMAGES[k] for k in frame_keys]
        self.frame_index    = 0
        self.anim_dir       = 1  # ping-pong
        self.last_anim_time = pygame.time.get_ticks()
        self.anim_interval  = anim_interval

        self.image = self.frames[0]
        self.rect  = self.image.get_rect(topleft=(x, y))

    def animate(self):
        now = pygame.time.get_ticks()
        if now - self.last_anim_time >= self.anim_interval:
            self.last_anim_time = now
            if self.frame_index == len(self.frames) - 1:
                self.anim_dir = -1
            elif self.frame_index == 0:
                self.anim_dir = 1
            self.frame_index += self.anim_dir
            self.image = self.frames[self.frame_index]

class GridMovableMixin:
    def __init__(self, move_speed=2):  # zmniejsz prędkość z 3 na 2 dla wolniejszego ruchu:
        # Assumes AnimatedFruit.__init__ was called first
        self.move_speed = move_speed
        row = (self.rect.top - MAP_OFFSET) // TILE_SIZE
        col = (self.rect.left - MAP_OFFSET) // TILE_SIZE
        self.grid_pos = [row, col]
        self.target_pos = [self.rect.x, self.rect.y]
        self.moving = False
        self.next_direction = None

    def move(self, direction):
        if not self.moving and direction in direction_vectors:
            self.next_direction = direction

    def update(self, obstacles):
        # enqueue movement
        if not self.moving and self.next_direction:
            drow, dcol = direction_vectors[self.next_direction]
            new_r = self.grid_pos[0] + drow
            new_c = self.grid_pos[1] + dcol
            test_rect = self.rect.move(dcol * TILE_SIZE, drow * TILE_SIZE)
            if not any(test_rect.colliderect(o.rect) for o in obstacles):
                px = new_c * TILE_SIZE + MAP_OFFSET
                py = new_r * TILE_SIZE + MAP_OFFSET
                self.target_pos = [px, py]
                self.grid_pos = [new_r, new_c]
                self.moving = True
            self.next_direction = None

        # smooth movement towards target
        if self.moving:
            dx = self.target_pos[0] - self.rect.x
            dy = self.target_pos[1] - self.rect.y
            step_x = max(-self.move_speed, min(self.move_speed, dx))
            step_y = max(-self.move_speed, min(self.move_speed, dy))
            self.rect.x += step_x
            self.rect.y += step_y
            if abs(dx) <= self.move_speed and abs(dy) <= self.move_speed:
                self.rect.topleft = (self.target_pos[0], self.target_pos[1])
                self.moving = False
            self.animate()
        else:
            self.frame_index = 0
            self.image = self.frames[0]

class Strawberry(GridMovableMixin, AnimatedFruit):
    def __init__(self, x, y):
        frame_keys = ['APPLE_1', 'APPLE_2', 'APPLE_3']
        AnimatedFruit.__init__(self, x, y, frame_keys, anim_interval=180)
        GridMovableMixin.__init__(self, move_speed=1)

class Orange(pygame.sprite.Sprite):
    def __init__(self, x, y, png = "F1"):
        super().__init__()
        self.image = IMAGES[png]
        self.rect = self.image.get_rect(topleft=(x, y))

class FruitFactory:
    """
    Factory to create fruit instances by type.
    """
    @staticmethod
    def create(fruit_type, x, y):
        ft = fruit_type.lower()
        if ft == 'strawberry':
            return Strawberry(x, y)
        elif ft == 'orange':
            # Orange class must be defined/imported
            return Orange(x, y)
        # add more types here
        else:
            raise ValueError(f"Unknown fruit type: {fruit_type}")





