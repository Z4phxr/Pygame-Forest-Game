from collections import deque
import os
import pygame
from Images import IMAGES, TILE_SIZE
import numpy as np

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
# test

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
    """Enemy with BFS pathfinding and collision avoidance."""
    REPATH_INTERVAL = 10  # frames between path recalculations

    def __init__(self, x: int, y: int, player: pygame.sprite.Sprite, grid: np.ndarray):
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

        self.player = player
        self.grid = grid

        # Grid-based position
        self.grid_pos = [
            (y - MAP_OFFSET + TILE_SIZE // 2) // TILE_SIZE,
            (x - MAP_OFFSET + TILE_SIZE // 2) // TILE_SIZE
        ]
        self.pixel_pos = self.pixel_pos_from_grid(self.grid_pos)
        self.rect.center = self.pixel_pos

        self.path = []
        self.move_speed = 1
        self.moving = False
        self.next_grid_pos = None
        self.target_pos = self.pixel_pos.copy()
        self.clock = 0

    def pixel_pos_from_grid(self, grid_pos: tuple) -> list:
        row, col = grid_pos
        px = col * TILE_SIZE + MAP_OFFSET + TILE_SIZE // 2
        py = row * TILE_SIZE + MAP_OFFSET + TILE_SIZE // 2
        return [px, py]

    def bfs(self, start: tuple, goal: tuple) -> list:
        rows, cols = self.grid.shape
        queue = deque([start])
        came_from = {start: None}
        visited = set([start])

        while queue:
            current = queue.popleft()
            if current == goal:
                path = []
                while current:
                    path.append(current)
                    current = came_from[current]
                return path[::-1]

            for dy, dx in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                neighbor = (current[0] + dy, current[1] + dx)
                if (0 <= neighbor[0] < rows and 0 <= neighbor[1] < cols and
                        (self.grid[neighbor] == 0 or neighbor == goal) and
                        neighbor not in visited):
                    queue.append(neighbor)
                    visited.add(neighbor)
                    came_from[neighbor] = current
        return []

    def update(self, obstacles: pygame.sprite.Group):
        # Smooth movement towards target
        if self.moving:
            dx = self.target_pos[0] - self.rect.centerx
            dy = self.target_pos[1] - self.rect.centery
            move_x = max(-self.move_speed, min(self.move_speed, dx))
            move_y = max(-self.move_speed, min(self.move_speed, dy))
            self.rect.centerx += move_x
            self.rect.centery += move_y

            if abs(dx) <= self.move_speed and abs(dy) <= self.move_speed:
                # Arrived at target
                self.rect.center = self.target_pos
                self.moving = False
                # Update grid_pos now that we've arrived
                self.grid_pos = self.next_grid_pos
            return

        # Recalculate path periodically or if no path
        self.clock += 1
        if self.clock % self.REPATH_INTERVAL == 0 or not self.path:
            start = tuple(self.grid_pos)
            goal = (
                (self.player.rect.centery - MAP_OFFSET) // TILE_SIZE,
                (self.player.rect.centerx - MAP_OFFSET) // TILE_SIZE
            )
            self.path = self.bfs(start, goal)

        # Follow path if available
        if len(self.path) > 1:
            next_tile = self.path[1]
            # Safety: ensure cell is free or is player's tile
            player_tile = (
                (self.player.rect.centery - MAP_OFFSET) // TILE_SIZE,
                (self.player.rect.centerx - MAP_OFFSET) // TILE_SIZE
            )
            if self.grid[next_tile] != 0 and next_tile != player_tile:
                return

            # Reserve next tile to prevent overlapping with other enemies
            self.grid[self.grid_pos[0]][self.grid_pos[1]] = 0
            self.next_grid_pos = [next_tile[0], next_tile[1]]
            self.grid[self.next_grid_pos[0]][self.next_grid_pos[1]] = 2

            # Set movement target
            self.target_pos = self.pixel_pos_from_grid(self.next_grid_pos)

            # Update sprite direction
            dy = next_tile[0] - self.grid_pos[0]
            dx = next_tile[1] - self.grid_pos[1]
            if dx == -1:
                self.direction = 'left'
            elif dx == 1:
                self.direction = 'right'
            elif dy == -1:
                self.direction = 'up'
            elif dy == 1:
                self.direction = 'down'
            self.image = self.images[self.direction]

            # Begin movement
            self.moving = True