import os, pygame
pygame.init()
WIDTH, HEIGHT = 1000, 700
TILE_SIZE = 50
screen = pygame.display.set_mode((WIDTH, HEIGHT))


path = os.path.join(os.getcwd(), 'images')  # folder z obrazkami
IMAGES = {}
for file_name in os.listdir(path):
    if file_name.endswith('.png'):  # lub .jpg itp.
        name = file_name[:-4].upper()  # nazwa np. "OBSTACLE"
        IMAGES[name] = pygame.image.load(os.path.join(path, file_name)).convert_alpha()

