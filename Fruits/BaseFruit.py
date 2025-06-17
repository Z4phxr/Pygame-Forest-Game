import pygame
from Images import IMAGES

class BaseFruit(pygame.sprite.Sprite):
    """
       Base class for animated fruit sprites.
    """
    def __init__(self, x, y, frame_keys, anim_interval=200):
        super().__init__()
        self.frames = [IMAGES[k] for k in frame_keys]
        self.frame_index    = 0
        self.anim_dir       = 1
        self.last_anim_time = pygame.time.get_ticks()
        self.anim_interval  = anim_interval
        self.image = self.frames[0]
        self.rect  = self.image.get_rect(topleft=(x, y))

    def animate(self):
        now = pygame.time.get_ticks()
        if now - self.last_anim_time >= self.anim_interval:
            self.last_anim_time = now
            if self.frame_index == len(self.frames) - 1:
                self.anim_dir = -1
            elif self.frame_index == 0:
                self.anim_dir = 1
            self.frame_index += self.anim_dir
            self.image = self.frames[self.frame_index]