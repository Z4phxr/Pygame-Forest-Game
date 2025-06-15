import pygame
import numpy as np
import sys
import Maps
from Enemy import Enemy1
from Images import IMAGES
from Obstacles import Obstacle, Fruit

pygame.init()

WIDTH, HEIGHT = 1000, 750
TILE_SIZE = 50
MAP_OFFSET = 25
FPS = 60
screen = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()
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

class MenuBar:
    def __init__(self):
        self.rect = pygame.Rect(200, HEIGHT - 60, 600, 60)
        self.color = (50, 100, 50)

    def draw(self, screen):
        pygame.draw.rect(screen, self.color, self.rect)


class Player(pygame.sprite.Sprite):
    def __init__(self, x, y):
        # 1) Konstruktora Sprite wywołujemy BEZ argumentów!
        super().__init__()

        # 2) Ramki animacji ping-pong dla każdego kierunku
        self.frames = {
            'up':    [IMAGES['PLAYER_UP_1'],    IMAGES['PLAYER_UP_2'],    IMAGES['PLAYER_UP_3']],
            'down':  [IMAGES['PLAYER_DOWN_1'],  IMAGES['PLAYER_DOWN_2'],  IMAGES['PLAYER_DOWN_3']],
            'left':  [IMAGES['PLAYER_LEFT_1'],  IMAGES['PLAYER_LEFT_2'],  IMAGES['PLAYER_LEFT_3']],
            'right': [IMAGES['PLAYER_RIGHT_1'], IMAGES['PLAYER_RIGHT_2'], IMAGES['PLAYER_RIGHT_3']],
        }
        self.direction      = 'down'
        self.frame_index    = 0
        self.anim_dir       = 1                # +1 lub -1
        self.last_anim_time = pygame.time.get_ticks()
        self.anim_interval  = 200            # ms między klatkami

        # 3) Ustawiamy początkowy obraz i pozycję (topleft, nie center)
        self.image     = self.frames[self.direction][self.frame_index]
        self.rect      = self.image.get_rect(topleft=(x, y))

        # 4) Pozycja w siatce i pixelach:
        self.grid_pos  = [(y - MAP_OFFSET)//TILE_SIZE, (x - MAP_OFFSET)//TILE_SIZE]
        self.target_pos = [x, y]               # pixelowa pozycja celu

        # 5) Ruch i obsługa przeszkód:
        self.moving          = False
        self.move_speed      = 3
        self.pending_create  = []
        self.pending_destroy = []
        self.next_change_time = 0
        self.change_interval  = 100
        self.space_pressed_last_frame = False

    def create_obs(self, obstacles, grid):
        # _wyczyść kolejkę destroy_ na starcie
        self.pending_destroy.clear()

        y, x = self.grid_pos
        dy, dx = DIRECTION_VECTORS[self.direction]
        ny, nx = y + dy, x + dx

        self.pending_create.clear()
        while 0 <= ny < grid.shape[0] and 0 <= nx < grid.shape[1] and grid[ny][nx] == 0:
            self.pending_create.append((ny, nx))
            ny += dy
            nx += dx

        self.next_change_time = pygame.time.get_ticks() + self.change_interval

    def destroy_obs(self, obstacles, grid):
        # budujemy listę pól do odkopania
        y, x = self.grid_pos
        dy, dx = DIRECTION_VECTORS[self.direction]
        ny, nx = y + dy, x + dx

        self.pending_destroy.clear()
        # aż natrafimy na coś innego niż skrzynka (==1)
        while 0 <= ny < grid.shape[0] and 0 <= nx < grid.shape[1] and grid[ny][nx] == 1:
            self.pending_destroy.append((ny, nx))
            ny += dy
            nx += dx

    def change_obs(self, obstacles, grid):
        y, x = self.grid_pos
        dy, dx = DIRECTION_VECTORS.get(self.direction, (0, 0))
        ny, nx = y + dy, x + dx

        if grid[ny][nx] == 1:
            self.destroy_obs(obstacles, grid)
        elif grid[ny][nx] == 0:
            self.create_obs(obstacles, grid)

    def pixel_pos_from_grid(self, grid_pos):
        row, col = grid_pos
        px = col * TILE_SIZE + MAP_OFFSET + TILE_SIZE // 2
        py = row * TILE_SIZE + MAP_OFFSET + TILE_SIZE // 2
        return [px, py]

    def update(self, keys, obstacles, grid):
        now = pygame.time.get_ticks()

        # — handle pending create/destroy one step at a time —
        if (self.pending_destroy or self.pending_create) and now >= self.next_change_time:
            if self.pending_destroy:
                ry, rx = self.pending_destroy.pop(0)
                for obs in list(obstacles):
                    oy = (obs.rect.top - MAP_OFFSET) // TILE_SIZE
                    ox = (obs.rect.left - MAP_OFFSET) // TILE_SIZE
                    if (oy, ox) == (ry, rx):
                        obstacles.remove(obs)
                        obs.kill()
                        grid[ry][rx] = 0
                        break
            elif self.pending_create:
                ry, rx = self.pending_create.pop(0)
                px = rx * TILE_SIZE + MAP_OFFSET
                py = ry * TILE_SIZE + MAP_OFFSET
                tile = Obstacle(px, py, "BOX", True)
                obstacles.add(tile)
                grid[ry][rx] = 1

            self.next_change_time = now + self.change_interval

        # — smooth movement towards target tile —
        if self.moving:
            dx = self.target_pos[0] - self.rect.centerx
            dy = self.target_pos[1] - self.rect.centery
            mvx = max(-self.move_speed, min(self.move_speed, dx))
            mvy = max(-self.move_speed, min(self.move_speed, dy))
            self.rect.centerx += mvx
            self.rect.centery += mvy
            if abs(dx) <= self.move_speed and abs(dy) <= self.move_speed:
                self.rect.center = self.target_pos
                self.moving = False
            # animate while moving
            if now - self.last_anim_time >= self.anim_interval:
                self.last_anim_time = now
                self.frame_index = (self.frame_index + 1) % len(self.frames[self.direction])
                self.image = self.frames[self.direction][self.frame_index]
            return

        # — input: space toggles obs, arrows move grid_pos —
        move = None
        if keys[pygame.K_SPACE]:
            if not self.space_pressed_last_frame:
                self.change_obs(obstacles, grid)
                self.space_pressed_last_frame = True
        else:
            self.space_pressed_last_frame = False

        if keys[pygame.K_LEFT]:
            move = (0, -1);
            self.direction = 'left'
        elif keys[pygame.K_RIGHT]:
            move = (0, 1);
            self.direction = 'right'
        elif keys[pygame.K_UP]:
            move = (-1, 0);
            self.direction = 'up'
        elif keys[pygame.K_DOWN]:
            move = (1, 0);
            self.direction = 'down'

        if move:
            new_r = self.grid_pos[0] + move[0]
            new_c = self.grid_pos[1] + move[1]
            new_px = new_c * TILE_SIZE + MAP_OFFSET
            new_py = new_r * TILE_SIZE + MAP_OFFSET
            test_rect = self.frames[self.direction][0].get_rect(topleft=(new_px, new_py))
            if not any(test_rect.colliderect(o.rect) for o in obstacles):
                grid[self.grid_pos[0]][self.grid_pos[1]] = 0
                self.grid_pos = [new_r, new_c]
                self.target_pos = self.pixel_pos_from_grid(self.grid_pos)
                self.moving = True
            grid[self.grid_pos[0]][self.grid_pos[1]] = 3

        # — reset to standing frame if not moving —
        if not self.moving:
            if self.frame_index != 0:
                self.frame_index = 0
                self.image = self.frames[self.direction][0]


# Klasa Level - zarządza grą
class Level:
    nazwa = "aaa"
    def __init__(self, level_data):
        self.obstacles = pygame.sprite.Group()
        self.fruits = pygame.sprite.Group()
        self.all_sprites = pygame.sprite.Group()
        self.enemies = pygame.sprite.Group()
        self.grid = np.zeros((13, 19), dtype=int)
        self.player = None
        self.load_map(level_data)
        self.all_sprites.add(self.player)
        self.menu_bar = MenuBar()
        self.create_borders()
        self.running = True



    def update(self, keys):
        self.player.update(keys, self.obstacles, self.grid)
        self.obstacles.update(keys)
        self.enemies.update(self.obstacles)
        if pygame.sprite.spritecollideany(self.player, self.enemies):
            self.running = False
        collected = pygame.sprite.spritecollide(self.player, self.fruits, dokill=True)
        for fruit in collected:
            print("a")

    def draw(self, surface):
        surface.blit(IMAGES["GRASS"], (0, 0))
        self.fruits.draw(screen)
        self.all_sprites.draw(surface)
        self.obstacles.draw(surface)
        self.menu_bar.draw(screen)


    def load_map(self, level_data):
        for row_idx, row in enumerate(level_data):
            for col_idx, tile_char in enumerate(row):
                x = col_idx * TILE_SIZE + MAP_OFFSET
                y = row_idx * TILE_SIZE + MAP_OFFSET
                if tile_char == '#':
                    tile = Obstacle(x, y, "BOX", True)
                    self.obstacles.add(tile)
                    self.all_sprites.add(tile)
                    self.grid[row_idx][col_idx] = 1
                elif tile_char == 'P':
                    self.player = Player(x, y)
                    self.grid[row_idx][col_idx] = 3
                elif tile_char == 'O':
                    tile = Enemy1(x, y, self.player, self.grid)
                    self.enemies.add(tile)
                    self.all_sprites.add(tile)
                    self.grid[row_idx][col_idx] = 2
                elif tile_char == 'A':
                    tile = Fruit(x, y, "F1")
                    self.fruits.add(tile)
                else:
                    self.grid[row_idx][col_idx] = 0

    def create_borders(self):
        self.obstacles.add(Obstacle(0, 0, "BORDER_P"))
        self.obstacles.add(Obstacle(WIDTH-25, 0, "BORDER_P"))
        self.obstacles.add(Obstacle(25, 0, "BORDER_D"))
        self.obstacles.add(Obstacle(25, HEIGHT-75, "BORDER_DL"))



# Prosty system menu i głównej pętli
def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    clock  = pygame.time.Clock()

    # przygotuj overlay raz
    overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 160))

    # czcionki i przyciski
    title_font = pygame.font.SysFont(None, 80)
    btn_font   = pygame.font.SysFont(None, 50)

    # MAIN_MENU
    start_rect = pygame.Rect(300, 400, 400, 90)

    LEVELS = {
        "LEVEL_1": (pygame.Rect(315, 195, 80, 80), Maps.LEVEL_1),
        "LEVEL_2": (pygame.Rect(440, 128, 80, 80), Maps.LEVEL_2),
        "LEVEL_3": (pygame.Rect(570, 195, 80, 80), Maps.LEVEL_3),
        "LEVEL_4": (pygame.Rect(710, 255, 80, 80), Maps.LEVEL_4),
        "LEVEL_5": (pygame.Rect(315, 332, 80, 80), Maps.LEVEL_5),
        "LEVEL_6": (pygame.Rect(440, 260, 80, 80), Maps.LEVEL_6),
        "LEVEL_7": (pygame.Rect(575, 328, 80, 80), Maps.LEVEL_7),
        "LEVEL_8": (pygame.Rect(720, 395, 80, 80), Maps.LEVEL_8),
        "LEVEL_9": (pygame.Rect(312, 470, 80, 80), Maps.LEVEL_9),
        "LEVEL_10": (pygame.Rect(440, 395, 80, 80), Maps.LEVEL_10),
        "LEVEL_11": (pygame.Rect(580, 474, 80, 80), Maps.LEVEL_11),
        "LEVEL_12": (pygame.Rect(450, 532, 80, 80), Maps.LEVEL_12),
    }

    # GAME_OVER
    go_txt       = title_font.render("GAME OVER", True, BLACK)
    go_rect      = go_txt.get_rect(center=(WIDTH//2, HEIGHT//3))
    restart_txt  = btn_font.render("RESTART", True, BLACK)
    restart_rect = restart_txt.get_rect(center=(WIDTH//2, HEIGHT//2 - 30))
    menu_txt     = btn_font.render("MENU", True, BLACK)
    menu_rect    = menu_txt.get_rect(center=(WIDTH//2, HEIGHT//2 + 30))

    state = "MAIN_MENU"
    level = None
    selected_lvl = 0

    running = True
    while running:
        keys = pygame.key.get_pressed()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if event.type == pygame.MOUSEBUTTONDOWN:
                mx, my = event.pos
                if state == "MAIN_MENU":
                    if start_rect.collidepoint(mx, my):
                        state = "LEVEL_SELECT"
                elif state == "LEVEL_SELECT":
                    for lvl_name, (rect, mapa) in LEVELS.items():
                        if rect.collidepoint(mx, my):
                            selected_lvl = lvl_name
                            level = Level(mapa)  # przekazujemy listę znaków, nie współrzędną
                            state = "PLAY"
                            break

                elif state == "GAME_OVER":
                    if restart_rect.collidepoint(mx, my):
                        level = Level(LEVELS[selected_lvl][1])
                        state = "PLAY"
                    elif menu_rect.collidepoint(mx, my):
                        state = "MAIN_MENU"

        screen.fill(WHITE)

        if state == "MAIN_MENU":
            screen.blit(IMAGES["FOREST"], (0, 0))
            #pygame.draw.rect(screen, GREEN, start_rect.inflate(20,20))

        elif state == "LEVEL_SELECT":
            screen.blit(IMAGES["LEVELS"], (0, 0))

        elif state == "PLAY":
            level.draw(screen)
            # Game Over + przyciski
            level.update(keys)
            level.draw(screen)
            if not level.running:
                state = "GAME_OVER"

        elif state == "GAME_OVER":
            # rysuj zamrożony poziom
            screen.blit(go_txt, go_rect)
            pygame.draw.rect(screen, BLUE, restart_rect.inflate(20,10))
            screen.blit(restart_txt, restart_rect)
            screen.blit(overlay, (0,0))
            pygame.draw.rect(screen, BLUE, menu_rect.inflate(20,10))
            screen.blit(menu_txt, menu_rect)

        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
