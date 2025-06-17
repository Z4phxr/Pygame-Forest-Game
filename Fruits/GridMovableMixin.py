from Settings import *

class GridMovableMixin:
    """
    A mixin class that adds smooth grid-based movement logic to a sprite.
    Requires the host class to define `rect`, `frames`, `frame_index`, `image`, and `animate()`.
    """
    def __init__(self, move_speed=2):
        # AnimatedFruit.__init__ was called first
        self.move_speed = move_speed
        row = (self.rect.top - MAP_OFFSET) // TILE_SIZE
        col = (self.rect.left - MAP_OFFSET) // TILE_SIZE
        self.grid_pos = [row, col]
        self.target_pos = [self.rect.x, self.rect.y]
        self.moving = False
        self.next_direction = None

    def move(self, direction):
        if not self.moving and direction in DIRECTION_VECTORS:
            self.next_direction = direction

    def update(self, obstacles):
        # enqueue movement
        if not self.moving and self.next_direction:
            drow, dcol = DIRECTION_VECTORS[self.next_direction]
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

        # movement towards target
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
