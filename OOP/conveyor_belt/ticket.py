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
