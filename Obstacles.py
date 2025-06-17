from Images import IMAGES
from Settings import *

class Obstacle(pygame.sprite.Sprite):
    """
    Represents an obstacle on the map.
    """

    def __init__(self, x, y, png, destructable=False, growing=False):
        super().__init__()
        self.base_image = IMAGES[png]
        self.destructable = destructable
        self.growing = growing # Only obstacles created by player have growing animation

        if png.upper().startswith('BOX') and self.growing:
            # Initialize growing animation frames by scaling the image step-by-step
            self.frames = []
            steps = 10
            for i in range(1, steps + 1):
                scale = i / steps
                size = (int(TILE_SIZE * scale), int(TILE_SIZE * scale))
                scaled_img = pygame.transform.scale(self.base_image, size)
                self.frames.append(scaled_img)
            self.frame_index = 0
            self.image = self.frames[0]

            # Center the growing animation around the middle of the tile
            cx, cy = x + TILE_SIZE // 2, y + TILE_SIZE // 2
            self.rect = self.image.get_rect(center=(cx, cy))
            self.growth_delay = 50
            self.last_time = pygame.time.get_ticks()

        else:
            self.image = self.base_image
            self.rect = self.image.get_rect(topleft=(x, y))

    def update(self, *args):
        """
        Updates the obstacle's animation if it's a growing object.
        """
        if hasattr(self, 'frames'):
            now = pygame.time.get_ticks()
            if now - self.last_time >= self.growth_delay:
                self.last_time = now
                self.frame_index += 1

                if self.frame_index < len(self.frames):
                    old_center = self.rect.center
                    self.image = self.frames[self.frame_index]
                    self.rect = self.image.get_rect(center=old_center)
                else:
                    # Animation finished, switch to final image and stop updating
                    old_center = self.rect.center
                    self.image = self.base_image
                    self.rect = self.image.get_rect(center=old_center)
                    del self.frames
