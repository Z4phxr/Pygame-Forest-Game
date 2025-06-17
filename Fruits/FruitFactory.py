from Fruits.Strawberry import Strawberry
from Fruits.Orange import Orange
from Fruits.Pineapple import Pineapple


class FruitFactory:
    """
    Factory to create fruit instances by type.
    """
    @staticmethod
    def create(fruit_type, x, y, grid=None):
        ft = fruit_type.lower()
        if ft == 'strawberry':
            return Strawberry(x, y)
        elif ft == 'orange':
            # Orange class must be defined/imported
            return Orange(x, y)
        elif ft == 'pineapple':
            return Pineapple(x, y, grid)
        else:
            raise ValueError(f"Unknown fruit type: {fruit_type}")