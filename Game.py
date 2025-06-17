import sys, Images
from Settings import *
from States import MainMenuState

class Game:
    """
    Main Game class responsible for initializing the game,
    managing the current state, and running the main loop.
    """
    def __init__(self):
        pygame.init()
        pygame.display.set_caption("Forest")
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        Images.load_images()
        self.clock = pygame.time.Clock()
        self.current_state = MainMenuState(self)
        self.current_lvl = None
        self.level = None

    def change_state(self, new_state):
        """
        Change the current active game state.

        Args:
            new_state: An instance of a class that inherits from GameState.
        """
        self.current_state = new_state

    def run(self):
        """
        Run the main game loop: handle input, update state, and draw each frame.
        """
        running = True
        while running:
            keys = pygame.key.get_pressed()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                self.current_state.handle_input(event)

            self.current_state.update(keys)
            self.current_state.draw(self.screen)
            pygame.display.flip()
            self.clock.tick(FPS)
        pygame.quit()
        sys.exit()