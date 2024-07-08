class Passenger:
    instances = []

    def __init__(self, name, passenger_id):
        self.name = name
        self.passenger_id = passenger_id
        Passenger.instances.append(self)

    def __repr__(self):
        return f'Passenger {self.name}'



