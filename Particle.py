import pygame, random

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