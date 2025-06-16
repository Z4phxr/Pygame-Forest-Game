import pygame, random
import numpy as np
from Fruits import FruitFactory, Pineapple
from Images import IMAGES
from Obstacles import Obstacle
from Player import Player
from Settings import *
from Menu_bar import MenuBar
from Movable import Movable
from Enemy import EnemyFactory

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
        self.fruits.draw(surface)
        self.all_sprites.draw(surface)
        self.obstacles.draw(surface)
        self.menu_bar.draw(surface)
        self.player.particles.draw(surface)
        for f in self.fruits:
            if isinstance(f, Pineapple):
                f.draw(surface)


    def load_map(self, level_data):
        if not pygame.mixer.music.get_busy():
            start_music()
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
                    e = EnemyFactory.create(1, x, y, self.grid)
                    self.enemies.add(e)
                    self.all_sprites.add(e)
                    self.grid[row_idx][col_idx] = 2
                elif tile_char == 'b':
                    e = EnemyFactory.create(2, x, y, self.grid)
                    self.enemies.add(e)
                    self.all_sprites.add(e)
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