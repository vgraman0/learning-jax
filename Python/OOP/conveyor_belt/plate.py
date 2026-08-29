# A Program Stores Data and Does Stuff With Data
from __future__ import annotations

import datetime

from conveyor_belt.pricing import DefaultPricingStrategy, PlateColor, default_price_tiers
from conveyor_belt.ticket import Ticket


class Plate:
    def __init__(
        self,
        item_name: str,
        color,
        max_belt_time: int = 0,
        created: int | None = None,
        pricing=default_price_tiers,
    ) -> None:
        print("Calling Plate.__init__")
        self.item_name = item_name
        self.color = color
        self.created = created if created is not None else int(datetime.datetime.now().timestamp())
        self.max_belt_time = max_belt_time
        self.pricing = pricing
        self._is_approved = False

    @property
    def is_approved(self):
        return self._is_approved

    @is_approved.setter
    def is_approved(self, status):
        if isinstance(status, bool):
            self._is_approved = status
        else:
            raise TypeError("Value must be a bool")
        

    @property
    def price(self):
        return self.pricing.price_for(self.color)

    @property
    def age(self) -> int:
        return int(datetime.datetime.now().timestamp()) - self.created

    def is_too_old(self) -> bool:
        return self.age > self.max_belt_time

    @classmethod
    def from_ticket(cls, ticket: Ticket) -> Plate:
        return cls(ticket.item, ticket.color)

    def __str__(self) -> str:
        return f"item_name: {self.item_name}, color: {self.color}"

    # we should add this to EVERY class
    def __repr__(self) -> str:
        return f"Plate({self.item_name!r}, {self.color!r}, {self.max_belt_time}, {self.created})"
