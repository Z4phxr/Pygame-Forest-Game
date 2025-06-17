import random

from Fruits.GridMovableMixin import GridMovableMixin
from Fruits.BaseFruit import BaseFruit

class Strawberry(GridMovableMixin, BaseFruit):
    def __init__(self, x, y):
        frame_keys = ['STRAWBERRY_1', 'STRAWBERRY_2', 'STRAWBERRY_3', 'STRAWBERRY_4', 'STRAWBERRY_5', 'STRAWBERRY_6']
        BaseFruit.__init__(self, x, y, frame_keys, anim_interval=180)
        GridMovableMixin.__init__(self, move_speed=1)
        self.collectable = True

    def update(self, obstacles):
        direction = random.choice(['left', 'right', 'up', 'down'])
        self.move(direction)
        super().update(obstacles)
