import pygame
from Settings import *

class MenuBar:
    def __init__(self, level):
        self.rect = pygame.Rect(200, HEIGHT - 60, 600, 60)
        self.color = (50, 100, 50)
        self.level = level

    def draw(self, screen):
        #TEKST
        font = pygame.font.Font(None, 40)
        font_color = (255, 255, 255)
        score_text = f"LEVEL {self.level}"
        score_surf = font.render(score_text, True, font_color)
        score_rect = score_surf.get_rect(topleft=(200, HEIGHT-50))
        screen.blit(score_surf, score_rect)