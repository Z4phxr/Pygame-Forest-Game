from Settings import *

class BaseEnemy(pygame.sprite.Sprite):
    """
    Base class for enemy movement and animation.
    Handles grid-based positioning, movement flags, and directional animation logic.
    """

    def __init__(self, x, y, grid, speed=1, anim_interval=200):
        """
        Initialize base enemy data.

        Args:
            x (int): Initial X position in pixels.
            y (int): Initial Y position in pixels.
            grid (2D array): Grid representation of the level for collision/reservation.
            speed (int): Pixels per frame.
            anim_interval (int): Milliseconds between animation frames.
        """
        super().__init__()
        self.grid = grid
        self.speed = speed
        self.anim_interval = anim_interval
        self.frame_index = 0
        self.anim_dir = 1
        self.last_anim_time = pygame.time.get_ticks()

        # Grid position from pixel coordinates
        row = (y - MAP_OFFSET) // TILE_SIZE
        col = (x - MAP_OFFSET) // TILE_SIZE
        self.grid_pos = [row, col]

        self.target_pos = None  # Will be set when movement starts
        self.moving = False     # True while moving to a target tile

    def animate(self):
        """
        Updates the enemy animation frame based on time and current direction.
        Uses a ping-pong animation style.
        """
        now = pygame.time.get_ticks()
        if now - self.last_anim_time >= self.anim_interval:
            self.last_anim_time = now
            # Changing direction of the animation (ping-pong)
            if self.frame_index == len(self.frames[self.direction]) - 1:
                self.anim_dir = -1
            elif self.frame_index == 0:
                self.anim_dir = 1
            # Changing animation frame
            self.frame_index += self.anim_dir
            self.image = self.frames[self.direction][self.frame_index]