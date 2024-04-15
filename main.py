class StateService :
    def __init__(self, name: str):
        self.name = False

    def order(self, pillRequest: dict[str, int]):
        for townHalls, pillBoxs in pillRequest :
            print(f"Mairie {townHalls} : {pillBoxs} boîtes de pilules")
        pass

#Un héritage avec StateService est-il vraiment nécessaire ici ?
class TownHall :
    def __init__(self, name: str, stateService: StateService, lat : float, lon : float):
        self.name = name
        self.stateService = stateService
        self.lat = lat
        self.lon = lon
    
    def receive(self):
        pass

class Zone :
    def __init__(self, name: str, town_hall: TownHall):
        self.name = name
        self.town_hall = town_hall

class Order :
    def __init__(self, name: str, price: int):
        self.name = name
        self.price = price
        self.state = 0 #0 = en attente, 1 = en cours, 2 = terminée
    
    def init(self):
        pass

class OrderRow :
    def __init__(self, order: Order, townHall : TownHall, quantity: int):
        self.order = order
        self.quantity = quantity
        self.townHall = townHall
        self.state = 0 #0 = en attente, 1 = en cours, 2 = terminée
    
    def assign(self):
        pass

class Base :
    def __init__(self, lat : float, lon : float):
        self.lat = lat
        self.lon = lon

class Operator :
    def __init__(self, name: str, base : Base):
        self.name = name
        self.base = base
    
    def signIn(self):
        pass

    def launchMission(self):
        pass

class Drone :
    def __init__(self, base: Base, payload : int, range : int):
        self.base = base
        self.payload = payload
        self.range = range
    
    #Ce ne sont que des propositions
    def takeOff(self):
        pass

    def land(self):
        pass

    def delivery(self):
        pass

    def charge(self):
        pass

class Mission :
    def __init__(self):
        self.state = 0 #0 = en attente, 1 = en cours, 2 = terminée

class LogMission :
    def __init__(self, mission: Mission, drone: Drone):
        self.mission = mission
        self.drone = drone

if __name__ == '__main__' :
    #actions ici
    pass