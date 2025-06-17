from abc import ABC, abstractmethod

class GameState(ABC):
    """
    Abstract base class for game states.
    Defines the interface all concrete states must implement.
    """
    @abstractmethod
    def handle_input(self, event):
        """
        Handle a single pygame event (e.g. mouse click, key press).

        Args:
            event (pygame.event.Event): The event to handle.
        """
        pass

    @abstractmethod
    def update(self, keys):
        """
        Update the logic of the state based on the current input.

        Args:
            keys (pygame.key.ScancodeWrapper): Currently pressed keys.
        """
        pass

    @abstractmethod
    def draw(self, screen):
        """
        Draw the current state onto the screen.

        Args:
            screen (pygame.Surface): The game screen surface.
        """
        pass