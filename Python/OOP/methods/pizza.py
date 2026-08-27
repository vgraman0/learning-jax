from __future__ import annotations
import math
from tokenize import Double

class Pizza:
    DEFAULT_RADIUS = 1

    def __init__(self, radius: int, ingredients: list[str]):
        self.radius = radius
        self.ingredients = list(ingredients)

    def __repr__(self) -> str:
        return f"Pizza({self.radius}, {self.ingredients})"

    def add_ingredient(self, ingredient: str) -> None:
        self.ingredients.append(ingredient)
    
    def remove_ingredient(self, ingredient: str) -> None:
        if ingredient in self.ingredients:
            self.ingredients.remove(ingredient)

    @classmethod
    def margherita(cls) -> Pizza:
        return cls(Pizza.DEFAULT_RADIUS, ["mozzerella", "tomatoes"])
    
    @classmethod
    def prosciutto(cls) -> Pizza:
        return cls(Pizza.DEFAULT_RADIUS, ["mozzerella", "tomatoes", "ham"])

    def area(self) -> float:
        return self.circle_area(self.radius)

    @staticmethod
    def circle_area(r: int) -> float:
        return r ** 2 * math.pi