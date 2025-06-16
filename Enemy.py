from collections import deque
import os
import pygame
from Images import IMAGES, TILE_SIZE
import numpy as np
from Maps import DIRECTION_VECTORS

TILE_SIZE = 50
MAP_OFFSET = 25


class Enemy(pygame.sprite.Sprite):
    def __init__(self, x, y, player):
        super().__init__()
        self.images = {
            'up': IMAGES['O_UP'],
            'down': IMAGES['O_DOWN'],
            'left': IMAGES['O_LEFT'],
            'right': IMAGES['O_RIGHT']
        }
        self.direction = 'down'
        self.image = self.images[self.direction]
        self.rect = self.image.get_rect(topleft=(x, y))
        self.speed = 1
        self.player = player


    def move(self, obstacles, direction):
        x, y = self.rect.x, self.rect.y
        moved = False

        if direction == "left":
            self.rect.x -= self.speed
            self.direction = 'left'

            moved = True
        if direction == 'right':
            self.rect.x += self.speed
            self.direction = 'right'
            moved = True
        if direction == 'up':
            self.rect.y -= self.speed
            self.direction = 'up'
            moved = True
        if direction == 'down':
            self.rect.y += self.speed
            self.direction = 'down'
            moved = True

        if pygame.sprite.spritecollideany(self, obstacles):
            self.rect.x = x
            self.rect.y = y

        # Aktualizuj obrazek tylko jeśli rusza się
        if moved:
            self.image = self.images[self.direction]


#po prostu porusza się w kierunku player
class Enemy1(pygame.sprite.Sprite):
    """
    Enemy with BFS pathfinding and collision avoidance via grid reservation:
    - Rezerwuje swoją komórkę w grid (wartość 2)
    - Co REPATH_INTERVAL klatek przelicza ścieżkę do gracza przekazanego w update()
    - Porusza się płynnie kafelek po kafelku
    - Animuje 3-klatkową sekwencję dla każdego kierunku
    """
    REPATH_INTERVAL = 10

    def __init__(self, x: int, y: int, grid: np.ndarray, speed: int = 1, anim_interval: int = 200):
        super().__init__()
        # 1) Wczytanie klatek animacji dla każdego kierunku
        self.frames = {
            'up':    [IMAGES['O_UP_1'],    IMAGES['O_UP_2'],    IMAGES['O_UP_3']],
            'right': [IMAGES['O_RIGHT_1'], IMAGES['O_RIGHT_2'], IMAGES['O_RIGHT_3']],
            'down':  [IMAGES['O_DOWN_1'],  IMAGES['O_DOWN_2'],  IMAGES['O_DOWN_3']],
            'left':  [IMAGES['O_LEFT_1'],  IMAGES['O_LEFT_2'],  IMAGES['O_LEFT_3']],
        }
        # 2) Stan animacji
        self.direction      = 'down'
        self.frame_index    = 0
        self.anim_dir       = 1
        self.last_anim_time = pygame.time.get_ticks()
        self.anim_interval  = anim_interval

        # 3) Obraz i prostokąt
        self.image = self.frames[self.direction][0]
        self.rect  = self.image.get_rect(topleft=(x, y))

        # 4) Logika ruchu i pathfinding
        self.grid      = grid
        self.speed     = speed
        # Wyliczenie pozycji w gridzie
        row = (y - MAP_OFFSET + TILE_SIZE//2) // TILE_SIZE
        col = (x - MAP_OFFSET + TILE_SIZE//2) // TILE_SIZE
        self.grid_pos = [row, col]
        # Rezerwacja kafelka
        self.grid[row][col] = 2

        # 5) Przygotowanie do płynnego ruchu
        self.target_pos = [self.rect.x, self.rect.y]
        self.moving     = False

        # 6) BFS
        self.path  = []
        self.clock = 0

    def pixel_pos_from_grid(self, grid_pos: tuple) -> list:
        """Przelicza współrzędne grid -> piksele"""
        r, c = grid_pos
        px = c * TILE_SIZE + MAP_OFFSET + TILE_SIZE//2
        py = r * TILE_SIZE + MAP_OFFSET + TILE_SIZE//2
        return [px, py]

    def bfs(self, start: tuple, goal: tuple) -> list:
        """Oblicza ścieżkę z start do goal w tablicy grid"""
        rows, cols = self.grid.shape
        q = deque([start])
        came_from = {start: None}
        visited = {start}
        while q:
            cur = q.popleft()
            if cur == goal:
                path = []
                while cur is not None:
                    path.append(cur)
                    cur = came_from[cur]
                return path[::-1]
            for dr, dc in [(-1,0),(1,0),(0,-1),(0,1)]:
                nb = (cur[0]+dr, cur[1]+dc)
                if (0 <= nb[0] < rows and 0 <= nb[1] < cols
                   and (self.grid[nb] == 0 or nb == goal)
                   and nb not in visited):
                    visited.add(nb)
                    came_from[nb] = cur
                    q.append(nb)
        return []

    def update(self, obstacles: pygame.sprite.Group, player: pygame.sprite.Sprite):
        """
        obstacles jest ignorowane (kolizje przez grid),
        player musi być dostarczony każdorazowo przy wywołaniu
        """
        if player is None:
            return

        # 1) Kontynuacja płynnego ruchu
        if self.moving:
            dx = self.target_pos[0] - self.rect.x
            dy = self.target_pos[1] - self.rect.y
            sx = max(-self.speed, min(self.speed, dx))
            sy = max(-self.speed, min(self.speed, dy))
            self.rect.x += sx
            self.rect.y += sy
            if abs(dx) <= self.speed and abs(dy) <= self.speed:
                self.rect.topleft = (self.target_pos[0], self.target_pos[1])
                self.moving = False
            # animacja podczas ruchu
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

        # 2) Co REPATH_INTERVAL klatek przeliczamy ścieżkę
        self.clock += 1
        if self.clock % self.REPATH_INTERVAL == 0 or not self.path:
            start = tuple(self.grid_pos)
            goal = ((player.rect.centery - MAP_OFFSET)//TILE_SIZE,
                    (player.rect.centerx  - MAP_OFFSET)//TILE_SIZE)
            self.path = self.bfs(start, goal)

        # 3) Realizacja kolejnego kroku z path
        if len(self.path) > 1:
            nxt = self.path[1]
            player_tile = ((player.rect.centery - MAP_OFFSET)//TILE_SIZE,
                           (player.rect.centerx  - MAP_OFFSET)//TILE_SIZE)
            if self.grid[nxt] != 0 and nxt != player_tile:
                return
            # zwalniamy starą i rezerwujemy nową komórkę
            self.grid[self.grid_pos[0]][self.grid_pos[1]] = 0
            self.grid[nxt[0]][nxt[1]] = 2
            self.grid_pos = [nxt[0], nxt[1]]
            # ustawiamy pikselowy cel
            self.target_pos = self.pixel_pos_from_grid(self.grid_pos)
            # ustawiamy kierunek i obrazek
            dr = nxt[0] - self.grid_pos[0]
            dc = nxt[1] - self.grid_pos[1]
            if dc == -1: self.direction = 'left'
            elif dc == 1: self.direction = 'right'
            elif dr == -1: self.direction = 'up'
            elif dr == 1: self.direction = 'down'
            self.frame_index = 0
            self.image = self.frames[self.direction][0]
            # rozpoczynamy ruch
            self.moving = True




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
            'up':    [IMAGES['E_UP_1'],    IMAGES['E_UP_2'],    IMAGES['E_UP_3']],
            'right': [IMAGES['E_RIGHT_1'], IMAGES['E_RIGHT_2'], IMAGES['E_RIGHT_3']],
            'down':  [IMAGES['E_DOWN_1'],  IMAGES['E_DOWN_2'],  IMAGES['E_DOWN_3']],
            'left':  [IMAGES['E_LEFT_1'],  IMAGES['E_LEFT_2'],  IMAGES['E_LEFT_3']],
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