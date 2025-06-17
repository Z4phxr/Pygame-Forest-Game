from ABC_Game_State import GameState
from Settings import *
from Images import IMAGES
from Level import Level
from Maps import LEVELS
from ScoreBoard import ScoreBoard


class MainMenuState(GameState):
    """
    Represents the main menu screen where the player starts the game.
    """
    def __init__(self, game):
        self.game = game
        self.start_rect = start_rect
        self.scores_rect = scores_rect

    def enter(self):
        pass
    def exit(self):
        pass

    def handle_input(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.start_rect.collidepoint(event.pos):
                self.game.change_state(LevelSelectState(self.game))
            elif self.scores_rect.collidepoint(event.pos):
                self.game.change_state(Scores_State(self.game))

    def update(self, keys):
        pass

    def draw(self, screen):
        screen.blit(IMAGES["FOREST"], (0, 0))


class LevelSelectState(GameState):
    """
    Allows the player to select a level from the available options.
    """
    def __init__(self, game):
        self.game = game
        self.menu_rect = lvl_menu_rect

    def handle_input(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.menu_rect.collidepoint(event.pos):
                self.game.change_state(MainMenuState(self.game))
            mx, my = event.pos
            for lvl_name, (rect, mapa) in LEVELS.items():
                if rect.collidepoint(mx, my):
                    lvl_num = int(lvl_name.split('_')[1])
                    self.game.current_lvl = lvl_num
                    self.game.level = Level(mapa, lvl_num)
                    self.game.change_state(PlayState(self.game))
                    break

    def update(self, keys):
        pass

    def draw(self, screen):
        screen.blit(IMAGES["LEVELS"], (0, 0))


class PlayState(GameState):
    """
    Active gameplay state where the player moves and interacts with the game.
    """
    def __init__(self, game):
        self.game = game
        self.restart_rect = game_restart_rect
        self.menu_rect = game_menu_rect

    def handle_input(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.restart_rect.collidepoint(event.pos):
                key = f"LEVEL_{self.game.current_lvl}"
                mapa = LEVELS[key][1]
                self.game.level = Level(mapa, self.game.current_lvl)
                self.game.change_state(PlayState(self.game))
            elif self.menu_rect.collidepoint(event.pos):
                stop_music()
                self.game.change_state(MainMenuState(self.game))

    def update(self, keys):
        self.game.level.update(keys)
        if not self.game.level.running:
            if self.game.level.won:
                self.game.change_state(GameOverWinState(self.game))
            else:
                self.game.change_state(GameOverLostState(self.game))

    def draw(self, screen):
        self.game.level.draw(screen)


class GameOverWinState(GameState):
    """
    State shown when the player completes a level successfully.
    """
    def __init__(self, game):
        self.game = game
        self.next_level_rect = next_rect
        self.menu_rect = menu_rect

    def handle_input(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.next_level_rect.collidepoint(event.pos):
                nxt = self.game.current_lvl + 1
                key = f"LEVEL_{nxt}"
                if key in LEVELS:
                    mapa = LEVELS[key][1]
                    self.game.current_lvl = nxt
                    self.game.level = Level(mapa, nxt)
                    self.game.change_state(PlayState(self.game))
                else:
                    stop_music()
                    self.game.change_state(MainMenuState(self.game))
            elif self.menu_rect.collidepoint(event.pos):
                stop_music()
                self.game.change_state(MainMenuState(self.game))


    def update(self, keys):
        pass

    def draw(self, screen):
        screen.blit(IMAGES["OVERLAY"], (0, 0))
        screen.blit(IMAGES["YOU_WON"], (0, 0))


class GameOverLostState(GameState):
    """
    State shown when the player fails a level.
    """
    def __init__(self, game):
        self.game = game
        self.restart_rect = restart_rect
        self.menu_rect = menu_rect1


    def handle_input(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.restart_rect.collidepoint(event.pos):
                key = f"LEVEL_{self.game.current_lvl}"
                mapa = LEVELS[key][1]
                self.game.level = Level(mapa, self.game.current_lvl)
                self.game.change_state(PlayState(self.game))
            elif self.menu_rect.collidepoint(event.pos):
                stop_music()
                self.game.change_state(MainMenuState(self.game))

    def update(self, keys):
        pass

    def draw(self, screen):
        screen.blit(IMAGES["OVERLAY"], (0, 0))
        screen.blit(IMAGES["GAME_OVER"], (0, 0))


class Scores_State(GameState):
    def __init__(self, game):
        self.game = game
        self.menu_rect = menu_rect_scores
        self.scoreboard = ScoreBoard()  # 2. Stwórz instancję ScoreBoard

    def handle_input(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.menu_rect.collidepoint(event.pos):
                self.game.change_state(MainMenuState(self.game))

    def update(self, keys):
        pass

    def draw(self, screen):
        screen.blit(IMAGES["SCORES"], (0, 0))
        self.scoreboard.draw(screen, 225, 200)