from Settings import *
import random
from Images import IMAGES
from Enemies.BaseEnemy import BaseEnemy

class Enemy1(BaseEnemy):
    """
    Enemy1: moves in a fixed direction until hitting an obstacle,
    then turns randomly to try a new direction.
    """

    DIRECTIONS = ['up', 'right', 'down', 'left']

    def __init__(self, x, y, grid, speed=1, anim_interval=200):
        super().__init__(x, y, grid, speed, anim_interval)

        # Load directional animation frames
        self.frames = {
            'up':    [IMAGES['E1_UP_1'], IMAGES['E1_UP_2'], IMAGES['E1_UP_3']],
            'right': [IMAGES['E1_RIGHT_1'], IMAGES['E1_RIGHT_2'], IMAGES['E1_RIGHT_3']],
            'down':  [IMAGES['E1_DOWN_1'], IMAGES['E1_DOWN_2'], IMAGES['E1_DOWN_3']],
            'left':  [IMAGES['E1_LEFT_1'], IMAGES['E1_LEFT_2'], IMAGES['E1_LEFT_3']],
        }

        self.direction = 'up'
        self.image = self.frames[self.direction][0]
        self.rect = self.image.get_rect(topleft=(x, y))
        self.grid[self.grid_pos[0]][self.grid_pos[1]] = 2

    @staticmethod
    def pixel_from_grid(grid_pos):
        """Convert grid (row, col) to pixel coordinates."""
        r, c = grid_pos
        return [c * TILE_SIZE + MAP_OFFSET, r * TILE_SIZE + MAP_OFFSET]

    def update(self, *args):
        """Main movement logic called each frame."""
        # Decide direction if not moving
        if not self.moving:
            drow, dcol = DIRECTION_VECTORS[self.direction]
            new_r = self.grid_pos[0] + drow
            new_c = self.grid_pos[1] + dcol

            if (0 <= new_r < self.grid.shape[0] and
                    0 <= new_c < self.grid.shape[1] and
                    self.grid[new_r][new_c] != 1 and
                    self.grid[new_r][new_c] != 2):
                # Free old tile and reserve new one
                old_r, old_c = self.grid_pos
                self.grid[old_r][old_c] = 0
                self.grid[new_r][new_c] = 2
                self.grid_pos = [new_r, new_c]
                self.target_pos = self.pixel_from_grid(self.grid_pos)
                self.moving = True
            else:
                # Obstacle: pick a new random direction
                self.direction = random.choice(self.DIRECTIONS)
                self.frame_index = 0

        # Move toward target
        if self.moving:
            dx = self.target_pos[0] - self.rect.x
            dy = self.target_pos[1] - self.rect.y
            step_x = max(-self.speed, min(self.speed, dx))
            step_y = max(-self.speed, min(self.speed, dy))
            self.rect.x += step_x
            self.rect.y += step_y

            if abs(dx) <= self.speed and abs(dy) <= self.speed:
                self.rect.topleft = self.target_pos
                self.moving = False

        # Animate - from BaseEnemy class
        self.animate()