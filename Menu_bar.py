from Settings import *

class MenuBar:
    def __init__(self, level):
        self.level = level
        self.time_left = 60  # seconds

    def update_timer(self, time_left):
        """Update the time left to be displayed."""
        self.time_left = time_left

    def draw(self, screen):
        font = pygame.font.Font("Assets/Adumu.ttf", 40)
        font_color = (29, 78, 28)

        # LEVEL info
        level_text = f"LEVEL {self.level}"
        level_surf = font.render(level_text, True, font_color)
        screen.blit(level_surf, (320, HEIGHT - 50))

        # TIME info
        minutes = self.time_left // 60
        seconds = self.time_left % 60
        time_str = f"{minutes:02}:{seconds:02}"
        time_surf = font.render(time_str, True, font_color)
        screen.blit(time_surf, (560, HEIGHT - 50))

