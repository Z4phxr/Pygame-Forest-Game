import pygame
from Images import IMAGES

class Obstacle(pygame.sprite.Sprite):
    def __init__(self, x, y, png, destructable = False):
        super().__init__()
        self.image = IMAGES[png]
        self.rect = self.image.get_rect(topleft=(x, y))
        self.destructable = destructable


class Fruit(pygame.sprite.Sprite):
    def __init__(self, x, y, png):
        super().__init__()
        self.image = IMAGES[png]
        self.rect = self.image.get_rect(topleft=(x, y))




