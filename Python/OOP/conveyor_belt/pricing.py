from enum import Enum, auto
from abc import ABC, abstractmethod

class PlateColor(Enum):
    RED = auto()
    GOLD = auto()
    BLACK = auto()

class PricingStrategy(ABC):
    def __init__(self, tiers) -> None:
        self._tiers = tiers

    @abstractmethod
    def price_for(self, color):
        pass

class DefaultPricingStrategy(PricingStrategy):
    def price_for(self, color):
        return self._tiers[color]

class DiscountPricingStrategy(PricingStrategy):
    def __init__(self, tiers, discount=1.0):
        ...

    def price_for(self, color):
        ...

default_price_tiers = DefaultPricingStrategy({PlateColor.RED: 5, PlateColor.GOLD: 8, PlateColor.BLACK: 12})