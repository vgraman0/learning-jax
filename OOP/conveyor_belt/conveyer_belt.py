from __future__ import annotations
from collections.abc import Sequence

from conveyor_belt.plate import Plate

class ConveyerBelt(Sequence):
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

    def __getitem__(self, index: int) -> Plate:
        return self.plates[index]

    def __setitem__(self, index: int, plate: Plate) -> None:
        self.plates[index] = plate

    def __delitem__(self, index: int) -> None:
        del self.plates[index]

    def insert(self, index: int, plate: Plate) -> None:
        self.plates.insert(index, plate)

    def __iter__(self):
        return iter(self.plates)

    def __add__(self, other: ConveyerBelt) -> ConveyerBelt:
        return ConveyerBelt(self.plates + other.plates)

    def __iadd__(self, other: ConveyerBelt):
        self.plates.extend(other.plates)

    def __repr__(self) -> str:
        return repr(self.plates)