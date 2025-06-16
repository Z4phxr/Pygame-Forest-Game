import pygame
from Images import IMAGES
TILE_SIZE = 50
MAP_OFFSET = 25

class Obstacle(pygame.sprite.Sprite):
    def __init__(self, x, y, png, destructable=False, growing=False):
        super().__init__()
        self.base_image = IMAGES[png]
        self.destructable = destructable
        self.growing = growing

        if png.upper().startswith('BOX') and self.growing:
            # przygotowanie animacji wzrostu
            self.frames = []
            steps = 10
            for i in range(1, steps+1):
                s = i/steps
                size = (int(TILE_SIZE*s), int(TILE_SIZE*s))
                img = pygame.transform.scale(self.base_image, size)
                self.frames.append(img)
            self.frame_index = 0
            self.image = self.frames[0]
            cx, cy = x + TILE_SIZE//2, y + TILE_SIZE//2
            self.rect = self.image.get_rect(center=(cx, cy))
            self.growth_delay = 50
            self.last_time = pygame.time.get_ticks()
        else:
            # zwykły blok
            self.image = self.base_image
            self.rect = self.image.get_rect(topleft=(x, y))

    def update(self, *args):
        # tylko dla drzew
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
                    # zakończ animację
                    old_center = self.rect.center
                    self.image = self.base_image
                    self.rect = self.image.get_rect(center=old_center)
                    del self.frames  # już nie aktualizujemy