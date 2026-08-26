# A Program Stores Data and Does Stuff With Data
import datetime
from token import AT

class Plate:
    # to be reviewed
    RESTAURANT_NAME = "Real Sushi"
    PRICE_TIERS = {"red": 5, "gold": 8, "black": 12}

    def __init__(self, item_name, color, max_belt_time=0, created=None):
        print("Calling Plate.__init__")
        self.item_name = item_name
        self.color = color
        self.created = created or datetime.datetime.now()
        self.max_belt_time = max_belt_time

    #instance method
    def get_price(self):
        return self.PRICE_TIERS[self.color]

    def get_age(self):
        return datetime.datetime.now() - self.created

    def is_too_old(self):
        return self.get_age().total_seconds() > self.max_belt_time

    @classmethod
    def from_ticket(cls, ticket):
        return cls(ticket.item, ticket.color)

    @staticmethod
    def price_for(color):
        return Plate.PRICE_TIERS.get(color)

    def __str__(self):
        return f"item_name: {self.item_name}, color: {self.color}"

    # we should add this to EVERY class
    def __repr__(self):
        return f"Plate('{self.item_name}', '{self.color}', {self.max_belt_time}, {self.created})"

class Ticket:
    # non-public attribute
    _next_id = 1 

    # the first method that Python calls when creating a class.
    # def __new__(cls, *args, **kwargs):
    #     pass

    def __init__(self, item, color, chef_id):
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
    def __init__(self, plates=None):
        self.plates = plates or []

    def add_plate(self, plate):
        # validation
        self.plates.append(plate)

    def __len__(self):
        return len(self.plates)

    def get(self, index):
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