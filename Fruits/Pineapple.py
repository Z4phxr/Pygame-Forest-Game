import random
from Images import IMAGES
from Settings import *

class Pineapple(pygame.sprite.Sprite):
    """
    A special fruit that can walk, fly over obstacles, and land.
    It animates differently depending on the current movement state.
    """

    def __init__(self, x, y, grid):
        super().__init__()
        self.collectable = True

        # Animation frames for different states
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

        # Animation intervals (ms)
        self.walk_interval = 100
        self.departure_interval = 350
        self.fly_interval = 75
        self.landing_interval = 350

        # Starting image and position
        self.image = self.walk_frames[0]
        self.rect = self.image.get_rect(topleft=(x, y))
        self.grid = grid
        self.grid_pos = [(y - MAP_OFFSET) // TILE_SIZE, (x - MAP_OFFSET) // TILE_SIZE]
        self.target_pos = [x, y]
        self.direction = random.choice(list(DIRECTION_VECTORS.keys()))
        self.speed = 2
        self.fly_speed = 1

        # Movement states
        self.moving = False
        self.flying = False
        self.departing = False
        self.landing = False

        self.fly_target = None
        self.frame_index = 0
        self.anim_time = pygame.time.get_ticks()
        self.anim_dir = 1


    def update(self, obstacles):
        now = pygame.time.get_ticks()

        # DEPARTURE phase: plays departure animation before flying
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

        # FLYING phase: moves in air to the new tile
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

        # LANDING phase: plays landing animation
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

        # regular tile-to-tile movement
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

        # CHOOSE NEXT STEP
        dr, dc = DIRECTION_VECTORS[self.direction]
        r, c = self.grid_pos
        nr, nc = r + dr, c + dc

        if not (0 <= nr < self.grid.shape[0] and 0 <= nc < self.grid.shape[1]):
            self._change_direction()
            return

        # If wall ahead, check if it can fly over
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

        # Normal walk if next tile is free
        self.grid_pos = [nr, nc]
        self.target_pos = [nc * TILE_SIZE + MAP_OFFSET, nr * TILE_SIZE + MAP_OFFSET]
        self.moving = True
        self.frame_index = 0
        self.anim_time = now
        self.image = self.walk_frames[0]

    def _change_direction(self):
        self.direction = random.choice(list(DIRECTION_VECTORS.keys()))

    def draw(self, surface):
        surface.blit(self.image, self.rect)
