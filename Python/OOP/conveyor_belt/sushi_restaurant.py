# A Program Stores Data and Does Stuff With Data
import datetime

class Plate:
    # to be reviewed
    RESTAURANT_NAME = "Real Sushi"
    PRICE_TIERS = {"red": 5, "gold": 8, "black": 12}

    def __init__(self, item_name, color, max_belt_time, created=None):
        print("Calling Plate.__init__")
        self.item_name = item_name
        self.color = color
        self.created = created or datetime.datetime.now()
        self.max_belt_time = max_belt_time

    def get_price(self):
        # there are pros and cons of using self.PRICE_TIERS vs Plate.PRICE_TIERS
        return self.PRICE_TIERS[self.color]

plate_1 = Plate("tuna_nigiri", "red", 100, 0)
plate_2 = Plate("california_gold", "gold", 100, 0)

# shared memory location
print(plate_1.RESTAURANT_NAME is plate_2.RESTAURANT_NAME)

print(plate_1.get_price())
print(Plate.get_price(plate_1)) # using Plate as a namespace