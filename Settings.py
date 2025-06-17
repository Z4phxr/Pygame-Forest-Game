WIDTH, HEIGHT = 1000, 750
TILE_SIZE = 50
MAP_OFFSET = 25
FPS = 60
import pygame

DIRECTION_VECTORS = {
    'left':  (0, -1),
    'right': (0,  1),
    'up':    (-1, 0),
    'down':  (1,  0),
}

WHITE = (255, 255, 255)
BLUE = (50, 100, 255)
GREEN = (0, 255, 0)
BLACK = (0, 0, 0)

def start_music():
    pygame.mixer.init()
    pygame.mixer.music.load("Sounds/las.mp3")
    pygame.mixer.music.set_volume(1.0)
    pygame.mixer.music.play(-1)

def stop_music():
    pygame.mixer.music.stop()


#------------ BUTTONS ---------------

# MAIN_MEN STATE
start_rect = pygame.Rect(300, 400, 400, 90)
scores_rect = pygame.Rect(350, 528, 300, 70)

# GAME_OVER STATE
next_rect = pygame.Rect(300, 324, 400, 100)
menu_rect = pygame.Rect(300, 480, 400, 100)
restart_rect = pygame.Rect(300, 324, 400, 100)
menu_rect1 = pygame.Rect(300, 480, 400, 100)

# LEVEL STATE
lvl_menu_rect = pygame.Rect(330, 22, 210, 50)

# GAME STATE
game_menu_rect = pygame.Rect(52, 689, 150, 40)
game_restart_rect = pygame.Rect(790, 689, 150, 40)

# SCORES STATE
menu_rect_scores = pygame.Rect(330, 22, 210, 50)



