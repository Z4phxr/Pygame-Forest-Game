import random
from collections import deque
import os
import pygame
from Images import IMAGES, TILE_SIZE
import numpy as np
from Maps import DIRECTION_VECTORS

TILE_SIZE = 50
MAP_OFFSET = 25


class Enemy1(pygame.sprite.Sprite):
    """
    Enemy1: porusza się kafelek po kafelku za graczem, używając BFS,
    z płynną interpolacją ruchu i animacją 3-klatkową dla każdego kierunku.
    Dodatkowo animacja "frustracji" gdy brak ścieżki.
    Rezerwuje swój kafelek w gridzie (wartość 2), by unikać kolizji.
    """
    REPATH_INTERVAL = 10

    def __init__(self, x: int, y: int, grid: np.ndarray, speed: int = 1, anim_interval: int = 200, frustr_interval: int = 600):
        super().__init__()
        # animacyjne klatki dla czterech kierunków
        self.frames = {
            'up': [IMAGES['E2_UP_1'], IMAGES['E2_UP_2'], IMAGES['E2_UP_3']],
            'right': [IMAGES['E2_RIGHT_1'], IMAGES['E2_RIGHT_2'], IMAGES['E2_RIGHT_3']],
            'down': [IMAGES['E2_DOWN_1'], IMAGES['E2_DOWN_2'], IMAGES['E2_DOWN_3']],
            'left': [IMAGES['E2_LEFT_1'], IMAGES['E2_LEFT_2'], IMAGES['E2_LEFT_3']],
        }
        # nowe klatki frustracji (E2)
        self.frustration_frames = [
            IMAGES['E2_IDLE_1'],
            IMAGES['E2_IDLE_2'],
            IMAGES['E2_IDLE_3'],
            IMAGES['E2_IDLE_4']
        ]
        # stan animacji
        self.direction      = 'down'
        self.frame_index    = random.randint(0, 3)
        self.anim_dir       = 1
        self.last_anim_time = pygame.time.get_ticks()
        self.anim_interval      = anim_interval
        self.frustr_interval    = frustr_interval  # wolniejsza animacja frustracji
        # obraz i prostokąt
        self.image = self.frames[self.direction][0]
        self.rect  = self.image.get_rect(topleft=(x, y))

        # logika ruchu
        self.grid  = grid
        self.speed = speed
        # wyznacz pozycję w gridzie i rezerwuj
        row = (y - MAP_OFFSET + TILE_SIZE//2) // TILE_SIZE
        col = (x - MAP_OFFSET + TILE_SIZE//2) // TILE_SIZE
        self.grid_pos = [row, col]
        self.grid[row][col] = 2

        self.target_pos = [self.rect.x, self.rect.y]
        self.moving     = False
        self.path       = []
        self.clock      = 0

    def pixel_pos_from_grid(self, grid_pos):
        r, c = grid_pos
        px = c * TILE_SIZE + MAP_OFFSET
        py = r * TILE_SIZE + MAP_OFFSET
        return [px, py]

    def bfs(self, start: tuple, goal: tuple) -> list:
        rows, cols = self.grid.shape
        queue = deque([start])
        came_from = {start: None}
        visited = {start}
        while queue:
            cur = queue.popleft()
            if cur == goal:
                path = []
                while cur is not None:
                    path.append(cur)
                    cur = came_from[cur]
                return path[::-1]
            for dr, dc in [(-1,0),(1,0),(0,-1),(0,1)]:
                nb = (cur[0]+dr, cur[1]+dc)
                if (0 <= nb[0] < rows and 0 <= nb[1] < cols
                   and (self.grid[nb] != 1 or nb == goal)
                   and nb not in visited):
                    visited.add(nb)
                    came_from[nb] = cur
                    queue.append(nb)
        return []

    def animate_frustration(self):
        now = pygame.time.get_ticks()
        if now - self.last_anim_time >= self.frustr_interval:
            self.last_anim_time = now
            max_idx = len(self.frustration_frames) - 1
            if self.frame_index == max_idx:
                self.anim_dir = -1
            elif self.frame_index == 0:
                self.anim_dir = 1
            self.frame_index += self.anim_dir
            # obraz frustracji (bez zmiany kierunku)
            self.image = self.frustration_frames[self.frame_index]

    def update(self, obstacles: pygame.sprite.Group, player: pygame.sprite.Sprite):
        # 1) Dokończ interpolację ruchu jak wcześniej...
        if self.moving:
            dx = self.target_pos[0] - self.rect.x
            dy = self.target_pos[1] - self.rect.y
            step_x = max(-self.speed, min(self.speed, dx))
            step_y = max(-self.speed, min(self.speed, dy))
            self.rect.x += step_x
            self.rect.y += step_y
            if abs(dx) <= self.speed and abs(dy) <= self.speed:
                self.rect.topleft = (self.target_pos[0], self.target_pos[1])
                self.moving = False
                self.frame_index = 0
                self.image = self.frames[self.direction][0]
                self.path = []
            else:
                now = pygame.time.get_ticks()
                if now - self.last_anim_time >= self.anim_interval:
                    self.last_anim_time = now
                    max_i = len(self.frames[self.direction]) - 1
                    if self.frame_index == max_i:
                        self.anim_dir = -1
                    elif self.frame_index == 0:
                        self.anim_dir = 1
                    self.frame_index += self.anim_dir
                    self.image = self.frames[self.direction][self.frame_index]
            return

        # 2) Wyznacz trasę
        start = tuple(self.grid_pos)
        goal = ((player.rect.centery - MAP_OFFSET)//TILE_SIZE,
                (player.rect.centerx  - MAP_OFFSET)//TILE_SIZE)
        self.path = self.bfs(start, goal)

        # 3) Jeżeli są kroki to chodź
        if len(self.path) > 1:
            nxt = self.path[1]
            old_r, old_c = self.grid_pos
            dr = nxt[0] - old_r
            dc = nxt[1] - old_c
            self.grid[old_r][old_c] = 0
            self.grid[nxt[0]][nxt[1]] = 2
            self.grid_pos = [nxt[0], nxt[1]]
            self.target_pos = self.pixel_pos_from_grid(self.grid_pos)
            # ustaw kierunek
            if dc < 0:
                self.direction = 'left'
            elif dc > 0:
                self.direction = 'right'
            elif dr < 0:
                self.direction = 'up'
            elif dr > 0:
                self.direction = 'down'
            self.frame_index = 0
            self.image = self.frames[self.direction][0]
            self.moving = True
        else:
            # brak ścieżki: animacja frustracji
            self.animate_frustration()




class Enemy2(pygame.sprite.Sprite):
    """
    Enemy2 moves continuously in its current direction;
    when the next grid cell is occupied, it steps back,
    turns right (clockwise), and tries again.
    It reserves its position in the provided grid so that
    create_obs() sees it as blocked.
    Includes smooth tile-by-tile movement and 3-frame animation per direction.
    """
    DIRECTIONS = ['up', 'right', 'down', 'left']

    def __init__(self, x, y, grid, speed=1, anim_interval=200):
        super().__init__()
        # 1) Load animation frames (3 per direction)
        self.frames = {
            'up':    [IMAGES['E1_UP_1'],    IMAGES['E1_UP_2'],    IMAGES['E1_UP_3']],
            'right': [IMAGES['E1_RIGHT_1'], IMAGES['E1_RIGHT_2'], IMAGES['E1_RIGHT_3']],
            'down':  [IMAGES['E1_DOWN_1'],  IMAGES['E1_DOWN_2'],  IMAGES['E1_DOWN_3']],
            'left':  [IMAGES['E1_LEFT_1'],  IMAGES['E1_LEFT_2'],  IMAGES['E1_LEFT_3']],
        }

        # Animation state
        self.direction      = 'up'
        self.frame_index    = 0
        self.anim_dir       = 1
        self.last_anim_time = pygame.time.get_ticks()
        self.anim_interval  = anim_interval
        # Initial image and rect
        self.image = self.frames[self.direction][0]
        self.rect  = self.image.get_rect(topleft=(x, y))

        # Movement state
        self.speed   = speed
        self.grid    = grid
        # Compute initial grid position
        row = (y - MAP_OFFSET) // TILE_SIZE
        col = (x - MAP_OFFSET) // TILE_SIZE
        self.grid_pos   = [row, col]
        # Reserve this cell
        self.grid[row][col] = 2
        # Pixel target for smooth movement
        self.target_pos = [self.rect.x, self.rect.y]
        self.moving     = False

    def animate(self):
        now = pygame.time.get_ticks()
        if now - self.last_anim_time >= self.anim_interval:
            self.last_anim_time = now
            max_i = len(self.frames[self.direction]) - 1
            if self.frame_index == max_i:
                self.anim_dir = -1
            elif self.frame_index == 0:
                self.anim_dir = 1
            self.frame_index += self.anim_dir
            self.image = self.frames[self.direction][self.frame_index]

    def pixel_from_grid(self, grid_pos):
        r, c = grid_pos
        px = c * TILE_SIZE + MAP_OFFSET
        py = r * TILE_SIZE + MAP_OFFSET
        return [px, py]

    def update(self, *args):
        # 1) If not moving, attempt to step into next grid cell
        if not self.moving:
            drow, dcol = DIRECTION_VECTORS[self.direction]
            new_r = self.grid_pos[0] + drow
            new_c = self.grid_pos[1] + dcol
            # Check within bounds and empty
            if (0 <= new_r < self.grid.shape[0]
                and 0 <= new_c < self.grid.shape[1]
                and self.grid[new_r][new_c] != 1):
                # Free old, reserve new
                old_r, old_c = self.grid_pos
                self.grid[old_r][old_c] = 0
                self.grid[new_r][new_c] = 2
                self.grid_pos = [new_r, new_c]
                # Set pixel target
                self.target_pos = self.pixel_from_grid(self.grid_pos)
                self.moving = True
            else:
                # Blocked: turn right
                idx = self.DIRECTIONS.index(self.direction)
                self.direction = self.DIRECTIONS[(idx + 1) % len(self.DIRECTIONS)]
                self.frame_index = 0

        # 2) Smooth movement if in progress
        if self.moving:
            dx = self.target_pos[0] - self.rect.x
            dy = self.target_pos[1] - self.rect.y
            step_x = max(-self.speed, min(self.speed, dx))
            step_y = max(-self.speed, min(self.speed, dy))
            self.rect.x += step_x
            self.rect.y += step_y
            # Arrived?
            if abs(dx) <= self.speed and abs(dy) <= self.speed:
                self.rect.topleft = (self.target_pos[0], self.target_pos[1])
                self.moving = False

        # 3) Animate each frame
        self.animate()