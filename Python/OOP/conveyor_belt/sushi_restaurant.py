# A Program Stores Data and Does Stuff With Data
from __future__ import annotations

import datetime
from token import AT

class Plate:
    # to be reviewed
    RESTAURANT_NAME: str = "Real Sushi"
    PRICE_TIERS: dict[str, int] = {"red": 5, "gold": 8, "black": 12}

    def __init__(
        self,
        item_name: str,
        color: str,
        max_belt_time: int = 0,
        created: int | None = None,
    ) -> None:
        print("Calling Plate.__init__")
        self.item_name = item_name
        self.color = color
        self.created = created if created is not None else int(datetime.datetime.now().timestamp())
        self.max_belt_time = max_belt_time

    #instance method
    def get_price(self) -> int:
        return self.PRICE_TIERS[self.color]

    def get_age(self) -> int:
        return int(datetime.datetime.now().timestamp()) - self.created

    def is_too_old(self) -> bool:
        return self.get_age() > self.max_belt_time

    @classmethod
    def from_ticket(cls, ticket: Ticket) -> Plate:
        return cls(ticket.item, ticket.color)

    @staticmethod
    def price_for(color: str) -> int | None:
        return Plate.PRICE_TIERS.get(color)

    def __str__(self) -> str:
        return f"item_name: {self.item_name}, color: {self.color}"

    # we should add this to EVERY class
    def __repr__(self) -> str:
        return f"Plate('{self.item_name}', '{self.color}', {self.max_belt_time}, {self.created})"

class Ticket:
    # non-public attribute
    _next_id: int = 1

    # the first method that Python calls when creating a class.
    # def __new__(cls, *args, **kwargs):
    #     pass

    def __init__(self, item: str, color: str, chef_id: int) -> None:
        self.item = item
        self.color = color
        self.chef_id = chef_id
        self.ticket_id = Ticket._next_id
        Ticket._next_id += 1

class ConveyerBelt:

    # We should NEVER use mutable types as default values
    # Python constructs the default arguments when defining the method
    # So the same object will be shared by all instances of the class
    # e.g. def __init(self, plates=[])
    def __init__(self, plates: list[Plate] | None = None) -> None:
        self.plates = plates or []

    def add_plate(self, plate: Plate) -> None:
        # validation
        self.plates.append(plate)

    def __len__(self) -> int:
        return len(self.plates)

    def get(self, index: int | slice) -> Plate | list[Plate]:
        return self.plates[index]


# plate testing 

plate_1 = Plate("tuna_nigiri", "red", 100, 0)
plate_2 = Plate("california_gold", "gold", 100, 0)

# shared memory location
print(plate_1.RESTAURANT_NAME is plate_2.RESTAURANT_NAME)

print(plate_1.get_price())
print(Plate.get_price(plate_1)) # using Plate as a namespace

# ticket testing
a_ticket = Ticket("salmon roll", "gold", 3)
print(a_ticket.ticket_id)

another_ticket = Ticket("salmon roll", "gold", 3) 
print(another_ticket.ticket_id)

my_plate = Plate.from_ticket(a_ticket)
print(my_plate.item_name, my_plate.color)

# conveyor belt testing

main_conveyor_belt = ConveyerBelt()
main_conveyor_belt.add_plate(plate_1)
main_conveyor_belt.add_plate(plate_2)
print(len(main_conveyor_belt))
print(main_conveyor_belt.get(slice(0, 2)))
print(plate_1)