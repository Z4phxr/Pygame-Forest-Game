import pygame, random, math

class Particle(pygame.sprite.Sprite):
    """Represents a fading, falling green particle effect."""

    def __init__(self, pos):
        super().__init__()

        size = random.randint(4, 8)
        green = random.randint(100, 160)
        # Create a transparent surface and fill it with a green color
        self.image = pygame.Surface((size, size), pygame.SRCALPHA)
        self.image.fill((0, green, 0, 255))

        self.rect = self.image.get_rect(center=pos)

        # Generate a random angle and speed for movement
        angle = random.uniform(0, 2 * math.pi)
        speed = random.uniform(1, 4)
        self.velocity = pygame.Vector2(speed, 0).rotate_rad(angle)

        self.life = random.randint(20, 40)
        self.max_life = self.life  # Used to calculate fading alpha

    def update(self):
        # Move the particle by its velocity
        self.rect.x += self.velocity.x
        self.rect.y += self.velocity.y

        # Simulate gravity by increasing downward velocity
        self.velocity.y += 0.2

        # Decrease life each frame
        self.life -= 1
        alpha = max(0, int(255 * (self.life / self.max_life)))
        self.image.set_alpha(alpha)

        if self.life <= 0:
            self.kill()
