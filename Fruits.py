import random

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
        frame_keys = ['STRAWBERRY_1', 'STRAWBERRY_2', 'STRAWBERRY_3', 'STRAWBERRY_4', 'STRAWBERRY_5', 'STRAWBERRY_6']
        AnimatedFruit.__init__(self, x, y, frame_keys, anim_interval=180)
        GridMovableMixin.__init__(self, move_speed=1)
        self.collectable = True

class Orange(pygame.sprite.Sprite):
    def __init__(self, x, y, png = "ORANGE"):
        super().__init__()
        self.image = IMAGES[png]
        self.rect = self.image.get_rect(topleft=(x, y))
        self.collectable = True

class FruitFactory:
    """
    Factory to create fruit instances by type.
    """
    @staticmethod
    def create(fruit_type, x, y, grid=None):
        ft = fruit_type.lower()
        if ft == 'strawberry':
            return Strawberry(x, y)
        elif ft == 'orange':
            # Orange class must be defined/imported
            return Orange(x, y)
        elif ft == 'pineapple':
            return Pineapple(x, y, grid)
        else:
            raise ValueError(f"Unknown fruit type: {fruit_type}")

class Pineapple(pygame.sprite.Sprite):
    def __init__(self, x, y, grid):
        super().__init__()
        self.collectable = True

        # Animacje
        self.walk_frames = [
            IMAGES['PINEAPPLE_R_1'],
            IMAGES['PINEAPPLE_R_2'],
            IMAGES['PINEAPPLE_R_3']
        ]
        self.departure_frames = [
            IMAGES['PINEAPPLE_DEPART_0'],
            IMAGES['PINEAPPLE_DEPART_1'],
            IMAGES['PINEAPPLE_DEPART_2']
        ]
        self.fly_frames = [
            IMAGES['PINEAPPLE_FLY_1'],
            IMAGES['PINEAPPLE_FLY_2']
        ]
        self.landing_frames = [
            IMAGES['PINEAPPLE_LAND_1'],
            IMAGES['PINEAPPLE_LAND_2'],
            IMAGES['PINEAPPLE_LAND_3']
        ]

        # Interwały animacji
        self.walk_interval = 100
        self.departure_interval = 350
        self.fly_interval = 75
        self.landing_interval = 350

        self.image = self.walk_frames[0]
        self.rect = self.image.get_rect(topleft=(x, y))

        # Pozycje i grid
        self.grid = grid
        self.grid_pos = [(y - MAP_OFFSET) // TILE_SIZE, (x - MAP_OFFSET) // TILE_SIZE]
        self.target_pos = [x, y]
        self.direction = random.choice(list(direction_vectors.keys()))
        self.speed = 2
        self.fly_speed = 1

        # Stan ruchu
        self.moving = False
        self.flying = False
        self.departing = False
        self.landing = False

        self.fly_target = None
        self.frame_index = 0
        self.anim_time = pygame.time.get_ticks()
        self.anim_dir = 1  # do ping-ponga

    def update(self, obstacles):
        now = pygame.time.get_ticks()

        # DEPARTURE
        if self.departing:
            self.collectable = False
            if now - self.anim_time >= self.departure_interval:
                self.anim_time = now
                self.frame_index += 1
                if self.frame_index < len(self.departure_frames):
                    self.image = self.departure_frames[self.frame_index]
                else:
                    self.departing = False
                    self.flying = True
                    self.frame_index = 0
                    self.image = self.fly_frames[0]
            return

        # FLYING
        if self.flying:
            dx = self.fly_target[0] - self.rect.x
            dy = self.fly_target[1] - self.rect.y
            self.rect.x += max(-self.fly_speed, min(self.fly_speed, dx))
            self.rect.y += max(-self.fly_speed, min(self.fly_speed, dy))

            if now - self.anim_time >= self.fly_interval:
                self.anim_time = now
                self.frame_index = (self.frame_index + 1) % len(self.fly_frames)
                self.image = self.fly_frames[self.frame_index]

            if abs(dx) <= self.fly_speed and abs(dy) <= self.fly_speed:
                self.rect.topleft = self.fly_target
                self.flying = False
                self.landing = True
                self.frame_index = 0
                self.anim_time = now
                self.image = self.landing_frames[0]
            return

        # LANDING
        if self.landing:
            self.collectable = True
            if now - self.anim_time >= self.landing_interval:
                self.anim_time = now
                self.frame_index += 1
                if self.frame_index < len(self.landing_frames):
                    self.image = self.landing_frames[self.frame_index]
                else:
                    self.landing = False
                    self.frame_index = 0
                    self.image = self.walk_frames[0]
            return

        # WALKING
        if self.moving:
            dx = self.target_pos[0] - self.rect.x
            dy = self.target_pos[1] - self.rect.y
            self.rect.x += max(-self.speed, min(self.speed, dx))
            self.rect.y += max(-self.speed, min(self.speed, dy))

            if now - self.anim_time >= self.walk_interval:
                self.anim_time = now
                if self.frame_index == len(self.walk_frames) - 1:
                    self.anim_dir = -1
                elif self.frame_index == 0:
                    self.anim_dir = 1
                self.frame_index += self.anim_dir
                self.image = self.walk_frames[self.frame_index]

            if abs(dx) <= self.speed and abs(dy) <= self.speed:
                self.rect.topleft = self.target_pos
                self.moving = False
                self.frame_index = 0
                self.image = self.walk_frames[0]
            return

        # WYBÓR NOWEGO KROKU
        dr, dc = direction_vectors[self.direction]
        r, c = self.grid_pos
        nr, nc = r + dr, c + dc

        if not (0 <= nr < self.grid.shape[0] and 0 <= nc < self.grid.shape[1]):
            self._change_direction()
            return

        if self.grid[nr][nc] == 1:
            fr, fc = nr + dr, nc + dc
            if 0 <= fr < self.grid.shape[0] and 0 <= fc < self.grid.shape[1] and self.grid[fr][fc] == 0:
                self.departing = True
                self.fly_target = [fc * TILE_SIZE + MAP_OFFSET, fr * TILE_SIZE + MAP_OFFSET]
                self.grid_pos = [fr, fc]
                self.frame_index = 0
                self.anim_time = now
                self.image = self.departure_frames[0]
                return
            else:
                self._change_direction()
                return

        # Normalny krok
        self.grid_pos = [nr, nc]
        self.target_pos = [nc * TILE_SIZE + MAP_OFFSET, nr * TILE_SIZE + MAP_OFFSET]
        self.moving = True
        self.frame_index = 0
        self.anim_time = now
        self.image = self.walk_frames[0]

    def _change_direction(self):
        self.direction = random.choice(list(direction_vectors.keys()))

    def draw(self, surface):
        surface.blit(self.image, self.rect)


