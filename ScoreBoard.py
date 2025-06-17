import pygame

class ScoreBoard:
    """
    Displays best completion times per level from 'best_times.txt'.
    If a level is missing, shows 'None'.
    """

    def __init__(self, font_path="Adumu.ttf", file_path="best_times.txt"):
        self.file_path = file_path
        self.font = pygame.font.Font(font_path, 36)
        self.title_font = pygame.font.Font(font_path, 60)
        self.font_color = (50, 100, 48)
        self.total_levels = 12
        self.best_times = self.load_best_times()

    def load_best_times(self):
        times = {}
        try:
            with open(self.file_path, "r") as f:
                for line in f:
                    if "," in line:
                        lvl, sec = line.strip().split(",")
                        if lvl.isdigit() and sec.strip().isdigit():
                            times[int(lvl)] = int(sec.strip())
        except FileNotFoundError:
            pass
        return times

    def draw(self, screen, x=100, y=100):
        title = self.title_font.render("BEST TIMES", True, self.font_color)
        screen.blit(title, (x+115, y-20))

        for i in range(1, self.total_levels + 1):
            seconds = self.best_times.get(i)
            if seconds is not None:
                minutes = seconds // 60
                sec = seconds % 60
                time_str = f"{minutes:02d}:{sec:02d}"
            else:
                time_str = "None"


            col = 0 if i <= 6 else 1
            row = (i - 1) % 6

            dx = x + col * 300
            dy = y + 60 + row * 40

            text = self.font.render(f"Level {i}: {time_str}", True, self.font_color)
            screen.blit(text, (dx, dy))