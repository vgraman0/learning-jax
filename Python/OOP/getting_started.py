# A Program Stores Data and Does Stuff With Data
restaurant_name = "Real Sushi"

PRICE_TIERS = {"red": 5, "gold": 8, "black": 12}

def make_plate(item, color):
    return {"item": item, "color": color}

# Problem 1. We are making an assumption that all the items are the same type. There is no "plate" datatype.
customer_plates = [
    make_plate("salmon nigiri", "red"),
    make_plate("tuna nigiri", "gold"),
]

# Problem 2. This is a free function. There is no link because the function and the data it acts on.
def get_plate_price(plate):
    # Avoid globals (why?)
    # square brackets throws a KeyError for a missing key. `.get` lets you pick a default (or defaults to None)
    return PRICE_TIERS[plate.get("color", "red")]

def calculate_total(plates):
    return sum(get_plate_price(plate) for plate in plates)

