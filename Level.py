import random
import numpy as np
from Fruits.FruitFactory import FruitFactory
from Fruits.Pineapple import Pineapple
from Images import IMAGES
from Obstacles import Obstacle
from Player import Player
from Settings import *
from Menu_bar import MenuBar
from Enemies.EnemyFactory import EnemyFactory

class Level:
    """
    Level class manages the game state for a single level: including loading the map,
    updating all game objects, handling win/loss conditions, and drawing everything.
    """

    def __init__(self, level_data, lvl_idx):
        # Sprite groups
        self.obstacles = pygame.sprite.Group()
        self.fruits = pygame.sprite.Group()
        self.all_sprites = pygame.sprite.Group()
        self.enemies = pygame.sprite.Group()

        self.fruits_to_collect = 0
        self.grid = np.zeros((13, 19), dtype=int)  # 2D grid to represent tile states
        self.player = None
        self.lvl_idx = lvl_idx

        #Loading the map
        self.load_map(level_data)

        self.all_sprites.add(self.player)
        self.menu_bar = MenuBar(self.lvl_idx)
        self.create_borders()
        self.running = True
        self.won = False

        #Timer
        self.start_time = pygame.time.get_ticks()
        self.time_limit = 60_000

    def update(self, keys):
        """
        Update all game objects for this frame.
        """
        self.player.update(keys, self.obstacles, self.grid)
        self.player.particles.update()
        self.obstacles.update(keys)
        self.enemies.update(self.obstacles, self.player)
        self.fruits.update(self.obstacles)

        # Check for collisions with enemies or win condition
        if pygame.sprite.spritecollideany(self.player, self.enemies) or self.fruits_to_collect == 0:
            self.running = False
            if self.fruits_to_collect == 0:
                self.won = True
                elapsed = pygame.time.get_ticks() - self.start_time
                self.save_best_time(elapsed)

        # Check if the time is up
        elapsed = pygame.time.get_ticks() - self.start_time
        if elapsed >= self.time_limit:
            self.running = False
            self.won = False

        # Update timer
        remaining_time = max(0, self.time_limit - (pygame.time.get_ticks() - self.start_time)) // 1000
        self.menu_bar.update_timer(remaining_time)

        # Check for fruit collection
        collected = pygame.sprite.spritecollide(self.player, self.fruits, dokill=False)
        for fruit in collected:
            if fruit.collectable: # When pineapple is flying it is temporary not collectable
                self.fruits_to_collect -= 1
                fruit.kill()

    def draw(self, surface):
        """
        Draw the level and all visible elements.
        """
        surface.blit(IMAGES["GRASS"], (0, 0))
        self.fruits.draw(surface)
        self.all_sprites.draw(surface)
        self.obstacles.draw(surface)
        self.menu_bar.draw(surface)
        self.player.particles.draw(surface)

        for f in self.fruits: # Above obstacles, when flying
            if isinstance(f, Pineapple):
                f.draw(surface)

    def load_map(self, level_data):
        """
        Load the level layout and populate the grid and sprite groups.
        """
        if not pygame.mixer.music.get_busy(): # Start music
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
        """
        Adds decorative screen border elements.
        """
        self.obstacles.add(Obstacle(0, 0, "BORDER_P"))
        self.obstacles.add(Obstacle(WIDTH-25, 0, "BORDER_P"))
        self.obstacles.add(Obstacle(25, 0, "BORDER_D"))
        self.obstacles.add(Obstacle(25, HEIGHT-75, "BORDER_DL"))

    def save_best_time(self, elapsed_ms):
        """
        Save the best completion time (in seconds) for the current level if it's better.
        """
        elapsed_sec = elapsed_ms // 1000
        filename = "Assets/best_times.txt"
        best_times = {}

        # Load existing best times from file
        try:
            with open(filename, "r") as f:
                for line in f:
                    lvl, sec = line.strip().split(",")
                    best_times[int(lvl)] = int(sec)
        except FileNotFoundError:
            pass  # No file yet

        # Save only if this is a better (lower) time
        best = best_times.get(self.lvl_idx, float('inf'))
        if elapsed_sec < best:
            best_times[self.lvl_idx] = elapsed_sec
            with open(filename, "w") as f:
                for lvl, sec in best_times.items():
                    f.write(f"{lvl},{sec}\n")

