import pygame
from Images import IMAGES

class Orange(pygame.sprite.Sprite):
    """
    Static fruit, not animated.
    """
    def __init__(self, x, y, png = "ORANGE"):
        super().__init__()
        self.image = IMAGES[png]
        self.rect = self.image.get_rect(topleft=(x, y))
        self.collectable = True