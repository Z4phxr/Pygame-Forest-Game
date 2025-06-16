import random
import pygame
import numpy as np
import sys
import Maps
from Enemy import Enemy1, Enemy2
from Fruits import FruitFactory, Pineapple
from Images import IMAGES
from Obstacles import Obstacle
from typing import Protocol, runtime_checkable, Any

@runtime_checkable
class Movable(Protocol):
    """
    Protocol for objects that support a .move(...) method.
    Use isinstance(obj, Movable) to check at runtime.
    """
    def move(self, *args: Any, **kwargs: Any) -> None:
        pass

pygame.init()

pygame.mixer.init()
pygame.mixer.music.load("las.mp3")
pygame.mixer.music.set_volume(1.0)
pygame.mixer.music.play(-1)

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

# --- Particle class for burst effect ---
class Particle(pygame.sprite.Sprite):
    def __init__(self, pos):
        super().__init__()
        size = random.randint(4, 8)
        self.image = pygame.Surface((size, size), pygame.SRCALPHA)
        col = random.randint(100, 160)
        # zielony odcień dla cząsteczek
        green = col
        self.image.fill((0, green, 0, 255))
        self.rect = self.image.get_rect(center=pos)
        angle = random.uniform(0, 2 * 3.1415)
        speed = random.uniform(1, 4)
        vec = pygame.math.Vector2(1, 0).rotate_rad(angle) * speed
        self.velocity = [vec.x, vec.y]
        self.life = random.randint(20, 40)

    def update(self):
        self.rect.x += self.velocity[0]
        self.rect.y += self.velocity[1]
        self.velocity[1] += 0.2
        self.life -= 1
        alpha = max(0, int(255 * (self.life / 40)))
        self.image.set_alpha(alpha)
        if self.life <= 0:
            self.kill()


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


class Player(pygame.sprite.Sprite):
    def __init__(self, x, y):
        self.sound_destroy = pygame.mixer.Sound("niszczenie.mp3")
        self.sound_destroy.set_volume(0.7)
        super().__init__()
        # walking frames
        self.frames = {
            'up':    [IMAGES['PLAYER_UP_1'], IMAGES['PLAYER_UP_2'], IMAGES['PLAYER_UP_3']],
            'down':  [IMAGES['PLAYER_DOWN_1'], IMAGES['PLAYER_DOWN_2'], IMAGES['PLAYER_DOWN_3']],
            'left':  [IMAGES['PLAYER_LEFT_1'], IMAGES['PLAYER_LEFT_2'], IMAGES['PLAYER_LEFT_3']],
            'right': [IMAGES['PLAYER_RIGHT_1'], IMAGES['PLAYER_RIGHT_2'], IMAGES['PLAYER_RIGHT_3']],
        }
        # action frames (same for create/destroy)
        self.action_frames = {
            d: [IMAGES[f'PLAYER_ACTION_{d.upper()}_1'], IMAGES[f'PLAYER_ACTION_{d.upper()}_2'], IMAGES[f'PLAYER_ACTION_{d.upper()}_3']]
            for d in ['up','down','left','right']
        }
        self.direction = 'down'
        self.frame_index = 0
        self.action_frame_index = 0
        self.state = 'idle'
        self.last_anim_time = pygame.time.get_ticks()
        self.anim_interval = 200
        # initial image & rect
        self.image = self.frames[self.direction][0]
        self.rect = self.image.get_rect(topleft=(x, y))
        # grid position
        self.grid_pos = [(y - MAP_OFFSET)//TILE_SIZE, (x - MAP_OFFSET)//TILE_SIZE]
        self.target_pos = [x, y]
        # movement & build/destroy queues
        self.moving = False
        self.move_speed = 3
        self.pending_create = []
        self.pending_destroy = []
        self.next_change_time = 0
        self.change_interval = 100
        self.space_pressed_last_frame = False
        # particles group
        self.particles = pygame.sprite.Group()

    def create_obs(self, obstacles, grid):
        self.pending_destroy.clear()
        y, x = self.grid_pos
        dy, dx = DIRECTION_VECTORS[self.direction]
        ny, nx = y + dy, x + dx
        self.pending_create.clear()
        while 0 <= ny < grid.shape[0] and 0 <= nx < grid.shape[1] and grid[ny][nx] == 0:
            self.pending_create.append((ny, nx)); ny += dy; nx += dx
        self.next_change_time = pygame.time.get_ticks() + self.change_interval

    def destroy_obs(self, obstacles, grid):self.pending_create.clear()
    y, x = self.grid_pos
    dx, dy = DIRECTION_VECTORS[self.direction]
    ny, nx = y + dy, x + dx
    self.pending_destroy.clear()

    while 0 <= ny < grid.shape[0] and 0 <= nx < grid.shape[1] and grid[ny][nx] == 1:
        self.pending_destroy.append((ny, nx))
        self.sound_destroy.play()  # odtwórz dźwięk niszczenia
        ny += dy
        nx += dx

    # Ustaw zniszczone przeszkody jako 0, żeby nie niszczyć ich ponownie
    for ny, nx in self.pending_destroy:
        grid[ny][nx] = 0

    self.next_change_time = pygame.time.get_ticks() + self.change_interval


    def change_obs(self, obstacles, grid):
        y, x = self.grid_pos
        dy, dx = DIRECTION_VECTORS[self.direction]
        ny, nx = y + dy, x + dx
        if grid[ny][nx] == 1:
            self.destroy_obs(obstacles, grid)
        elif grid[ny][nx] == 0:
            self.create_obs(obstacles, grid)
        self.state = 'action'
        self.action_frame_index = 0
        self.last_anim_time = pygame.time.get_ticks()

    def pixel_pos_from_grid(self, grid_pos):
        r, c = grid_pos
        return [c*TILE_SIZE + MAP_OFFSET + TILE_SIZE//2,
                r*TILE_SIZE + MAP_OFFSET + TILE_SIZE//2]

    def update(self, keys, obstacles, grid):
        now = pygame.time.get_ticks()
        # 1) action animation
        if self.state == 'action':
            if now - self.last_anim_time >= self.anim_interval:
                self.last_anim_time = now
                self.action_frame_index += 1
                frames = self.action_frames[self.direction]
                if self.action_frame_index < len(frames):
                    self.image = frames[self.action_frame_index]
                else:
                    self.state = 'idle'
                    self.image = self.frames[self.direction][0]
            return
        # 2) pending create/destroy
        if (self.pending_destroy or self.pending_create) and now >= self.next_change_time:
            if self.pending_destroy:
                ry, rx = self.pending_destroy.pop(0)
                for obs in list(obstacles):
                    oy = (obs.rect.top - MAP_OFFSET)//TILE_SIZE
                    ox = (obs.rect.left - MAP_OFFSET)//TILE_SIZE
                    if (oy, ox) == (ry, rx):
                        obstacles.remove(obs); obs.kill(); grid[ry][rx]=0
                        # spawn particles
                        for _ in range(20): self.particles.add(Particle(obs.rect.center))
                        break
            elif self.pending_create:
                ry, rx = self.pending_create.pop(0)
                px = rx * TILE_SIZE + MAP_OFFSET
                py = ry * TILE_SIZE + MAP_OFFSET
                obstacles.add(Obstacle(px, py, f"BOX{random.randint(0,2)}", True, growing=True))
                grid[ry][rx] = 1
            self.next_change_time = now + self.change_interval
            return
        # 3) smooth movement
        if self.moving:
            dx = self.target_pos[0] - self.rect.centerx
            dy = self.target_pos[1] - self.rect.centery
            mvx = max(-self.move_speed, min(self.move_speed, dx))
            mvy = max(-self.move_speed, min(self.move_speed, dy))
            self.rect.centerx += mvx; self.rect.centery += mvy
            if abs(dx) <= self.move_speed and abs(dy) <= self.move_speed:
                self.rect.center = self.target_pos; self.moving=False
            if now - self.last_anim_time >= self.anim_interval:
                self.last_anim_time = now
                self.frame_index = (self.frame_index+1) % len(self.frames[self.direction])
                self.image = self.frames[self.direction][self.frame_index]
            return
        # 4) input: space
        if keys[pygame.K_SPACE] and not self.space_pressed_last_frame:
            self.change_obs(obstacles, grid); self.space_pressed_last_frame=True
        elif not keys[pygame.K_SPACE]:
            self.space_pressed_last_frame=False
        # 5) movement input
        pressed, move = None, None
        if keys[pygame.K_LEFT]: pressed='left'
        elif keys[pygame.K_RIGHT]: pressed='right'
        elif keys[pygame.K_UP]: pressed='up'
        elif keys[pygame.K_DOWN]: pressed='down'
        if pressed:
            if self.direction == pressed: move = DIRECTION_VECTORS[pressed]
            else: self.direction = pressed
        if move:
            nr, nc = self.grid_pos[0]+move[0], self.grid_pos[1]+move[1]
            px = nc*TILE_SIZE + MAP_OFFSET; py = nr*TILE_SIZE + MAP_OFFSET
            test_rect = self.frames[self.direction][0].get_rect(topleft=(px, py))
            if not any(test_rect.colliderect(o.rect) for o in obstacles):
                grid[self.grid_pos[0]][self.grid_pos[1]] = 0
                self.grid_pos = [nr, nc]
                self.target_pos = self.pixel_pos_from_grid(self.grid_pos)
                self.moving = True
            grid[self.grid_pos[0]][self.grid_pos[1]] = 3
        if not self.moving:
            self.frame_index = 0
        self.image = self.frames[self.direction][self.frame_index]

# Klasa Level - zarządza grą
class Level:
    def __init__(self, level_data, lvl_idx):
        self.obstacles = pygame.sprite.Group()
        self.fruits = pygame.sprite.Group()
        self.all_sprites = pygame.sprite.Group()
        self.enemies = pygame.sprite.Group()
        self.fruits_to_collect = 0
        self.grid = np.zeros((13, 19), dtype=int)
        self.player = None
        self.lvl_idx = lvl_idx
        self.load_map(level_data)
        self.all_sprites.add(self.player)
        self.menu_bar = MenuBar(self.lvl_idx)
        self.create_borders()
        self.running = True
        self.won = False



    def update(self, keys):
        # update player and its particles
        self.player.update(keys, self.obstacles, self.grid)
        self.player.particles.update()
        # update other sprites
        self.obstacles.update(keys)
        self.enemies.update(self.obstacles, self.player)
        for fruit in self.fruits:
            direction = random.choice(['left','right','up','down'])
            if isinstance(fruit, Movable):
                fruit.move(direction)

        # 3) update wszystkich owoców (kolizje i animacja)
        self.fruits.update(self.obstacles)

        if pygame.sprite.spritecollideany(self.player, self.enemies) or self.fruits_to_collect == 0:
            self.running = False
            if self.fruits_to_collect == 0:
                self.won = True

        # SPRAWDZAMY, CZY GRACZ DOTYKA OWOCÓW — ale nie zabijamy automatycznie
        collected = pygame.sprite.spritecollide(self.player, self.fruits, dokill=False)

        for fruit in collected:
            if hasattr(fruit, 'collectable') and fruit.collectable:
                self.fruits_to_collect -= 1
                fruit.kill()

        self.player.particles.update()

    def draw(self, surface):
        surface.blit(IMAGES["GRASS"], (0, 0))
        self.fruits.draw(screen)
        self.all_sprites.draw(surface)
        self.obstacles.draw(surface)
        self.menu_bar.draw(screen)
        self.player.particles.draw(surface)
        for f in self.fruits:
            if isinstance(f, Pineapple):
                f.draw(surface)


    def load_map(self, level_data):
        for row_idx, row in enumerate(level_data):
            for col_idx, tile_char in enumerate(row):
                x = col_idx * TILE_SIZE + MAP_OFFSET
                y = row_idx * TILE_SIZE + MAP_OFFSET
                if tile_char == '#':
                    ob = f"BOX{random.randint(0, 2)}"
                    tile = Obstacle(x, y, ob, True)
                    self.obstacles.add(tile)
                    self.all_sprites.add(tile)
                    self.grid[row_idx][col_idx] = 1
                elif tile_char == 'P':
                    self.player = Player(x, y)
                    self.grid[row_idx][col_idx] = 3
                elif tile_char == 'a':
                    e1 = Enemy1(x, y, self.grid)
                    self.enemies.add(e1)
                    self.all_sprites.add(e1)
                elif tile_char == 'b':
                    tile = Enemy2(x, y, self.grid)
                    self.enemies.add(tile)
                    self.all_sprites.add(tile)
                    self.grid[row_idx][col_idx] = 2
                elif tile_char == 'A':
                    tile = FruitFactory.create('orange', x, y)
                    self.fruits.add(tile)
                    self.fruits_to_collect += 1
                elif tile_char == 'B':
                    tile = FruitFactory.create('strawberry', x, y)
                    self.fruits.add(tile)
                    self.fruits_to_collect += 1
                elif tile_char == 'C':
                    tile = FruitFactory.create('pineapple', x, y, grid=self.grid)
                    self.fruits.add(tile)
                    self.fruits_to_collect += 1
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
    current_lvl = None

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
    next_rect = pygame.Rect(300, 324, 400, 100)
    menu_rect = pygame.Rect(300, 480, 400, 100)
    restart_rect = pygame.Rect(300, 324, 400, 100)
    menu_rect1 = pygame.Rect(300, 480, 400, 100)
    lvl_menu_rect = pygame.Rect(330, 22, 210, 50)
    game_menu_rect = pygame.Rect(52, 689, 150, 40)
    game_restart_rect = pygame.Rect(790, 689, 150, 40)

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
                            current_lvl = int(lvl_name.split('_')[1])
                            level = Level(mapa, current_lvl)  # przekazujemy listę znaków, nie współrzędną
                            state = "PLAY"
                            break
                    if lvl_menu_rect.collidepoint(mx, my):
                        state = "MAIN_MENU"

                elif state == "GAME_OVER_WON":
                    if restart_rect.collidepoint(mx, my):
                        current_lvl = int(current_lvl) + 1
                        next_lvl_key = f"LEVEL_{current_lvl}"
                        selected_lvl = next_lvl_key  # <--- TO DODAJ
                        if next_lvl_key in LEVELS:
                            level = Level(LEVELS[next_lvl_key][1], current_lvl)
                            state = "PLAY"
                        else:
                            # jeśli poziomu nie ma, wróć do menu lub zakończ
                            state = "MAIN_MENU"

                elif state == "GAME_OVER_LOST":
                    if next_rect.collidepoint(mx, my):
                        level = Level(LEVELS[selected_lvl][1], current_lvl)
                        state = "PLAY"
                    elif menu_rect1.collidepoint(mx, my):
                        state = "MAIN_MENU"
                elif state == "PLAY":
                    if game_menu_rect.collidepoint(mx, my):
                        state = "MAIN_MENU"
                    elif game_restart_rect.collidepoint(mx, my):
                        state = "PLAY"
                        level = Level(LEVELS[f"LEVEL_{current_lvl}"][1], current_lvl)


        screen.fill(WHITE)

        if state == "MAIN_MENU":
            screen.blit(IMAGES["FOREST"], (0, 0))

        elif state == "LEVEL_SELECT":
            screen.blit(IMAGES["LEVELS"], (0, 0))

        elif state == "PLAY":
            level.update(keys)
            level.draw(screen)
            if not level.running:
                state = "GAME_OVER_LOST"
                if level.won:
                    state = 'GAME_OVER_WON'

        elif state == "GAME_OVER_WON":
            screen.blit(IMAGES["OVERLAY"], (0, 0))
            screen.blit(IMAGES["YOU_WON"], (0,0))
        elif state == "GAME_OVER_LOST":
            screen.blit(IMAGES["OVERLAY"], (0, 0))
            screen.blit(IMAGES["GAME_OVER"], (0,0))

        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
