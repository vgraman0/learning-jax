from abc import ABC, abstractmethod

# Abstract Base Class
class Chef(ABC):
    _next_id = 1
    
    def __init__(self, name, station=None):
        self.id = self._next_id
        type(self)._next_id += 1
        self.name = name
        self.station = station

    @abstractmethod
    def show_title(self):
        ...

class HeadChef(Chef):
    def __init__(self, name, station=None):
        super().__init__(name, station)
        self.team = []

    def assign_station(self, chef, station):
        chef.station = station
    
    def approve_plate(self): 
        ...

    def show_title(self):
        return "Head Chef"

    
class ApprenticeChef(Chef):
    def __init__(self, name, station=None):
        super().__init__(name, station)
        self.approvals = []

    def place_plate_on_approvals(self):
        ...

    def show_title(self):
        return "Apprentice Chef"

class StandardChef(Chef):
    def show_title(self):
        return "Standard Chef"

mary = HeadChef("Mary Jones", "head")
