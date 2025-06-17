from collections import deque
from Images import IMAGES
import numpy as np
from Settings import *
from Enemies.BaseEnemy import BaseEnemy

class Enemy2(BaseEnemy):
    """
    Enemy2: follows the player using BFS pathfinding with tile-by-tile movement,
    direction-based animation, and frustration animation when stuck.
    """

    def __init__(self, x: int, y: int, grid: np.ndarray, speed: int = 1, anim_interval: int = 200, frustr_interval: int = 600):
        super().__init__(x, y, grid, speed, anim_interval)

        self.frames = {
            'up':    [IMAGES['E2_UP_1'], IMAGES['E2_UP_2'], IMAGES['E2_UP_3']],
            'right': [IMAGES['E2_RIGHT_1'], IMAGES['E2_RIGHT_2'], IMAGES['E2_RIGHT_3']],
            'down':  [IMAGES['E2_DOWN_1'], IMAGES['E2_DOWN_2'], IMAGES['E2_DOWN_3']],
            'left':  [IMAGES['E2_LEFT_1'], IMAGES['E2_LEFT_2'], IMAGES['E2_LEFT_3']],
        }

        self.direction = 'down'
        self.image = self.frames[self.direction][0]
        self.rect = self.image.get_rect(topleft=(x, y))

        self.frustration_frames = [
            IMAGES['E2_IDLE_1'],
            IMAGES['E2_IDLE_2'],
            IMAGES['E2_IDLE_3'],
            IMAGES['E2_IDLE_4']
        ]
        self.frustr_interval = frustr_interval
        self.path = []
        self.grid[self.grid_pos[0]][self.grid_pos[1]] = 2

    @staticmethod
    def pixel_pos_from_grid(grid_pos):
        r, c = grid_pos
        return [c * TILE_SIZE + MAP_OFFSET, r * TILE_SIZE + MAP_OFFSET]

    def bfs(self, start: tuple, goal: tuple):
        """
         Compute the shortest path from start to goal using BFS.
         """
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
            # For every neighbour
            for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                nb = (cur[0] + dr, cur[1] + dc)
                # If the neighbour is available and not in visited, it's added to the queue
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
            self.image = self.frustration_frames[self.frame_index]

    def update(self, obstacles: pygame.sprite.Group, player: pygame.sprite.Sprite):
        """
        Update enemy state: follow path toward player or animate frustration.
        """
        if self.moving:
            dx = self.target_pos[0] - self.rect.x
            dy = self.target_pos[1] - self.rect.y
            self.rect.x += max(-self.speed, min(self.speed, dx))
            self.rect.y += max(-self.speed, min(self.speed, dy))

            if abs(dx) <= self.speed and abs(dy) <= self.speed:
                self.rect.topleft = self.target_pos
                self.moving = False
                self.frame_index = 0
                self.image = self.frames[self.direction][0]
                self.path = []
            else:
                self.animate()
            return

        start = tuple(self.grid_pos)
        goal = ((player.rect.centery - MAP_OFFSET) // TILE_SIZE,
                (player.rect.centerx - MAP_OFFSET) // TILE_SIZE)
        self.path = self.bfs(start, goal)

        if len(self.path) > 1:
            nxt = self.path[1]
            old_r, old_c = self.grid_pos

            # Jeśli pole docelowe jest zajęte przez innego enemy – czekaj
            if self.grid[nxt[0]][nxt[1]] == 2:
                self.animate_frustration()
                return

            dr, dc = nxt[0] - old_r, nxt[1] - old_c

            self.grid[old_r][old_c] = 0
            self.grid[nxt[0]][nxt[1]] = 2
            self.grid_pos = [nxt[0], nxt[1]]
            self.target_pos = self.pixel_pos_from_grid(self.grid_pos)


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
            self.animate_frustration()