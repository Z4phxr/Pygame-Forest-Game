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

class Orange(pygame.sprite.Sprite):
    def __init__(self, x, y, png = "ORANGE"):
        super().__init__()
        self.image = IMAGES[png]
        self.rect = self.image.get_rect(topleft=(x, y))

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
    """
    Pineapple porusza się po siatce:
     - podczas normalnego ruchu animuje się klatkami walk_frames (ping-pong)
     - gdy natrafi na przeszkodę i przeskoczy, animuje klatkami fly_frames
    """
    def __init__(self, x: int, y: int, grid):
        super().__init__()
        # — klatki chodzenia —
        walk_keys = ['PINEAPPLE_FLY_1','PINEAPPLE_FLY_2','PINEAPPLE_FLY_3','PINEAPPLE_FLY_4']
        self.walk_frames   = [IMAGES[k] for k in walk_keys]
        self.walk_interval = 200  # ms między klatkami chodzenia

        # — klatki lotu —
        fly_keys = ['PINEAPPLE_FLY_1','PINEAPPLE_FLY_2','PINEAPPLE_FLY_3','PINEAPPLE_FLY_4']
        self.fly_frames   = [IMAGES[k] for k in fly_keys]
        self.fly_interval = 200   # ms między klatkami lotu

        # ustaw początkowy obraz i rect
        self.frame_index = 0
        self.anim_dir    = 1
        self.last_anim   = pygame.time.get_ticks()
        self.image       = self.walk_frames[0]
        self.rect        = self.image.get_rect(topleft=(x, y))

        # dane do ruchu po gridzie
        self.grid       = grid
        self.direction  = random.choice(list(direction_vectors.keys()))
        self.grid_pos   = [
            (y - MAP_OFFSET) // TILE_SIZE,
            (x - MAP_OFFSET) // TILE_SIZE
        ]
        self.target_pos = [x, y]
        self.moving     = False
        self.speed      = 2    # piksele na klatkę ruchu

        # dane do lotu nad przeszkodą
        self.flying     = False
        self.fly_target = None
        self.fly_speed  = 1    # piksele na klatkę lotu

    def update(self, obstacles: pygame.sprite.Group):
        now = pygame.time.get_ticks()

        # --- tryb lotu ---
        if self.flying:
            # smooth lot
            dx = self.fly_target[0] - self.rect.x
            dy = self.fly_target[1] - self.rect.y
            step_x = max(-self.fly_speed, min(self.fly_speed, dx))
            step_y = max(-self.fly_speed, min(self.fly_speed, dy))
            self.rect.x += step_x
            self.rect.y += step_y
            # animacja lotu
            if now - self.last_anim >= self.fly_interval:
                self.last_anim = now
                max_i = len(self.fly_frames) - 1
                if self.frame_index == max_i:
                    self.anim_dir = -1
                elif self.frame_index == 0:
                    self.anim_dir = 1
                self.frame_index += self.anim_dir
                self.image = self.fly_frames[self.frame_index]
            # sprawdź koniec lotu
            if abs(dx) <= self.fly_speed and abs(dy) <= self.fly_speed:
                self.rect.topleft = self.fly_target
                self.flying       = False
                self.fly_target   = None
                # zresetuj animację do początku chodzenia
                self.frame_index = 0
                self.image = self.walk_frames[0]
            return

        # --- tryb chodzenia (interpolacja) ---
        if self.moving:
            dx = self.target_pos[0] - self.rect.x
            dy = self.target_pos[1] - self.rect.y
            step_x = max(-self.speed, min(self.speed, dx))
            step_y = max(-self.speed, min(self.speed, dy))
            self.rect.x += step_x
            self.rect.y += step_y

            # animacja chodzenia podczas ruchu
            if now - self.last_anim >= self.walk_interval:
                self.last_anim = now
                max_i = len(self.walk_frames) - 1
                if self.frame_index == max_i:
                    self.anim_dir = -1
                elif self.frame_index == 0:
                    self.anim_dir = 1
                self.frame_index += self.anim_dir
                self.image = self.walk_frames[self.frame_index]

            # zakończ ruch, gdy osiągnięto cel
            if abs(dx) <= self.speed and abs(dy) <= self.speed:
                self.rect.topleft = self.target_pos
                self.moving = False
                # po ruchu ustaw stałą pierwszą klatkę chodzenia
                self.frame_index = 0
                self.image = self.walk_frames[0]
            return

        # --- wybór kolejnego kroku ---
        dr, dc = direction_vectors[self.direction]
        r, c   = self.grid_pos
        nr, nc = r + dr, c + dc

        # poza planszą → zmień kierunek
        if not (0 <= nr < self.grid.shape[0] and 0 <= nc < self.grid.shape[1]):
            self._change_direction()
            return

        # natrafiono na przeszkodę → sprawdź możliwość lotu
        if self.grid[nr][nc] == 1:
            fr, fc = nr + dr, nc + dc
            if (0 <= fr < self.grid.shape[0]
                and 0 <= fc < self.grid.shape[1]
                and self.grid[fr][fc] == 0):
                # rozpocznij lot
                self.flying     = True
                self.fly_target = [
                    fc * TILE_SIZE + MAP_OFFSET,
                    fr * TILE_SIZE + MAP_OFFSET
                ]
                # od razu zarezerwuj nowe pole
                self.grid_pos = [fr, fc]
                self.frame_index = 0
                return
            else:
                self._change_direction()
                return

        # normalny krok po gridzie
        self.grid_pos   = [nr, nc]
        self.target_pos = [
            nc * TILE_SIZE + MAP_OFFSET,
            nr * TILE_SIZE + MAP_OFFSET
        ]
        self.moving     = True

    def _change_direction(self):
        self.direction = random.choice(list(direction_vectors.keys()))

    def draw(self, surface: pygame.Surface):
        surface.blit(self.image, self.rect)