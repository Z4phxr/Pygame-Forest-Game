from Enemies.Enemy1 import Enemy1
from Enemies.Enemy2 import Enemy2

class EnemyFactory:
    """
    Factory to create enemy instances by type.
    """
    @staticmethod
    def create(enemy_type: int, x, y, grid=None):
        if enemy_type == 1:
            return Enemy1(x, y, grid)
        elif enemy_type == 2:
            return Enemy2(x, y, grid)
        else:
            raise ValueError(f"Unknown enemy type: {enemy_type}")