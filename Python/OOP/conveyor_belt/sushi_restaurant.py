from conveyor_belt.conveyer_belt import ConveyerBelt
from conveyor_belt.plate import Plate
from conveyor_belt.pricing import PlateColor
from conveyor_belt.ticket import Ticket

RESTAURANT_NAME: str = "Real Sushi"

def main() -> None:
    # plate testing
    plate_1 = Plate("tuna_nigiri", PlateColor.RED, 100, 0)
    plate_2 = Plate("california_gold", PlateColor.GOLD, 100, 0)

    print(plate_1.price)

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
    print(main_conveyor_belt[1])
    print(plate_2)


if __name__ == "__main__":
    main()
