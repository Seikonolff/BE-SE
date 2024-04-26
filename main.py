from types import *
import math
from datetime import datetime
import pint
import icontract


ureg = pint.UnitRegistry()

currency_reg="""
USD = [currency]
EUR = 1.114 USD
"""
creg = pint.UnitRegistry(currency_reg.split('\n'))

class StateService :
    @icontract.require(lambda name : name != None)
    def __init__(self, name: str):
        self.name = name
        self.orders = [] #Orders object's adress

    @icontract.require(lambda pillRequest : pillRequest != None)
    def createOrder(self, pillRequest, IODelivery):
        #pillRequest = {townHall : quantity}
        Order(pillRequest, self, IODelivery)

class Zone :
    @icontract.require(lambda livingSouls : livingSouls > 0)
    def __init__(self, name: str, livingSouls: int):
        self.name = name
        self.livingSouls = livingSouls

class TownHall :
    @icontract.require(lambda name, lat, lon : name != None and lat != None and lon != None)
    def __init__(self, name: str, stateService: StateService, lat : float, lon : float):
        self.name = name
        self.stateService = stateService
        self.zones = [] #Zones object's adress
        self.lat = lat
        self.lon = lon
    
    def addZone(self, zone: Zone):
        self.zones.append(zone)
    
    def getZones(self):
        #sorted_zones = sorted(self.zones, key=lambda zone: zone.livingSouls, reverse=True)
        return self.zones
    
    def receive(self, zone: Zone):
        pass

class Order :
    @icontract.require(lambda IODelivery: isinstance(IODelivery, IODeliv))
    def __init__(self, pillRequest: dict[TownHall, int], stateService : StateService, IODelivery):
        print("[IODELIV LOG] Order received...")
        self.totalPrice = 0
        self.OrderRows = [] #OrderRows object's adress
        self.stateService = stateService
        self.IoDelivery = IODelivery
        self.state = 0 #0 = en attente, 1 = en cours, 2 = terminée

        #print(f"[IODELIV LOG] Order received : {pillRequest}")
        for townHall  in pillRequest:
            self.OrderRows.append(OrderRow(self, townHall, pillRequest[townHall]))
            #print(f"OrderRow added for {townHall.name} with {pillRequest[townHall]} pills in main order")
        for orderRow in self.OrderRows:
            orderRow.assign(self.IoDelivery)
            print(f"[IODELIV LOG] OrderRow assigned to operator {orderRow.operator.name}")
            self.totalPrice += orderRow.price
        print("[IODELIV LOG] Order created !")
        print(f"[IODELIV LOG] Order total price : {self.totalPrice}")
    
    def check(self):
        #print("Checking if order is finished...")
        #print(f"Order state : {self.state}")
        #print(f"orderRows : {self.OrderRows}")
        for orderRow in self.OrderRows:
            #print(f"Checking orderRow {orderRow.townHall.name} state : {orderRow.state}")
            if orderRow.state !=2 and orderRow.state != 3:
                return
        
        self.state = 2
        print(f"[IODELIV LOG] Order for {self.stateService.name} is finished !")

class OrderRow :
    @icontract.require(lambda order, townHall, quantity : order != None and townHall != None and quantity > 0)
    def __init__(self, order: Order, townHall : TownHall, quantity: int):
        self.order = order
        self.quantity = quantity
        self.price = quantity*10*creg.USD
        self.payload = quantity*0.01*ureg.kg
        self.townHall = townHall
        self.operator = None
        self.state = 0 #0 = en attente, 1 = en cours, 2 = terminée, 3 = annulée
    
    def assign(self, IODelivery):
        operator = IODelivery.getMatchingOperators(self.townHall)
        if operator:
            self.operator = operator
            operator.setNewOrderRow(self)
        else :
            print("[IODELIV LOG] No operator available for this row, cancelling...")
            self.state = 3

    @icontract.require(lambda state : state >= 0 and state <= 3)
    def setState(self, state: int):
        self.state = state
        if self.state == 0:
            print(f"[IODELIV LOG] OrderRow for {self.townHall.name} has been received by IoDelivery")
        elif self.state == 1:
            print(f"[IODELIV LOG] OrderRow for {self.townHall.name} is out for delivery")
        elif self.state == 2:
            print(f"[IODELIV LOG] OrderRow for {self.townHall.name} is delivered")
        elif self.state == 3:
            print(f"[IODELIV LOG] OrderRow for {self.townHall.name} has been cancelled")
        else:
            print("[IODELIV LOG] Invalid OrderRow state")
        self.order.check()

            
class Base :
    @icontract.require(lambda name, lat, lon, townHall : name != None and lat != None and lon != None and townHall != None)
    def __init__(self, name : str, lat : float, lon : float, townHall : TownHall):
        self.name = name
        self.lat = lat
        self.lon = lon
        self.townHall = townHall
        self.droneList = [] #Drones object's adress
    
    @icontract.require(lambda payload, range : payload > 0 and range > 0)
    def BuyDrone(self, name: str, payload : int, range : int):
        drone = Drone(name, self, payload, range)
        self.droneList.append(drone)
    
    def getDrones(self):
        droneReady = [] #Drones object's adress
        for drone in self.droneList:
            if drone.state == 0:
                #drone is not on mission
                droneReady.append(drone)
        return droneReady

class Operator :
    @icontract.require(lambda name,base : name != None and base != None)
    def __init__(self, name: str, base : Base):
        self.name = name
        self.base = base
        self.missions = [] #Missions object's adress
        self.listOrderRows = [] #OrderRows object's adress

    @icontract.require(lambda IO : type(IO) is IODeliv)
    def signIn(self, IO):
        IO.register(self)
    
    def setNewOrderRow(self, orderRow : OrderRow):
        self.listOrderRows.append(orderRow)

    def createMissions(self):
        print(f"[IODELIV LOG] Operator {self.name} is launching missions")
        readyDrones = self.base.getDrones()
        print(f"[IODELIV LOG] Operator {self.name} has {len(readyDrones)} drones ready")
        print(f"[IODELIV LOG] Operator {self.name} has {len(self.listOrderRows)} orderRows to deliver")
        
        for orderRow in self.listOrderRows:
            print(f"[IODELIV LOG] OrderRow {orderRow.townHall.name} has {orderRow.payload} payload")

        for drone in readyDrones:
            currentMissionPayload = 0
            missionOrderRows = []

            if not self.listOrderRows:
                print("[IODELIV LOG] No orderRow to deliver")
                break
            
            #print(f"{self.listOrderRows}")
            for orderRow in self.listOrderRows:
                #print(f"Checking orderRow {orderRow.townHall.name}")
                #print(f"OrderRow payload : {orderRow.payload}")
                #print(f"Current payload : {currentMissionPayload}")
                #print(f"Drone payload : {drone.payload}")
                if orderRow.payload >= drone.payload:
                    print(f"[IODELIV LOG] {orderRow.townHall.name} payload exceeded, cancelling the orderRow...")
                    #NTS : Maybe we should check if a drone has more payload than the current one
                    orderRow.setState(3)
                    self.listOrderRows.remove(orderRow)
                else :
                    #print(f"[IODELIV LOG] Adding orderRow {orderRow.townHall.name} to the mission")
                    currentMissionPayload = orderRow.payload
                    #print(f"[IODELIV LOG] Current payload : {currentMissionPayload} after adding orderRow {orderRow.townHall.name}")
                    missionOrderRows.append(orderRow)
                    #orderRow.setState(1)
                    self.listOrderRows.remove(orderRow)
                        
                    currentMission = Mission()
                    currentMission.setDrone(drone)
                    currentMission.setMissionPayload(currentMissionPayload)
                    currentMission.createOFP(missionOrderRows, orderRow.townHall)
                    #print(f"[IODELIV LOG] OFP created for {orderRow.townHall.name} with {len(missionOrderRows)} orderRows")

                    self.missions.append(currentMission)
                    currentMission.saveLog("Mission Created")
                    print(f"[IODELIV LOG] Mission created with {len(missionOrderRows)} orderRows")
                    print(f"[IODELIV LOG] Mission payload of {currentMissionPayload}")

        if len(self.listOrderRows) > 0:
            print(f"[IODELIV LOG] {self.name} No drone available for the remaining orderRows")

    def launchMission(self):
        print(f"[IODELIV LOG] Operator {self.name} is launching missions")
        print(f"[IODELIV LOG] Operator {self.name} has {len(self.missions)} missions to launch")

        for mission in self.missions:
            print(f"mission orderRows : {mission.missionRows}")
            mission.startMission()
        
class Mission :
    def __init__(self):
        self.state = 0 #0 = created, 1 = in progress, 2 = fisnished, 3 = cancelled
        self.drone = None
        self.missionRows = None
        self.missionPayload = None
        self.logMissions = []
        self.OFP = None
    
    @icontract.ensure(lambda drone : type(drone) is Drone)
    def setDrone(self, drone):
        self.drone = drone

    def setMissionPayload(self, missionPayload : int):
        self.missionPayload = missionPayload

    def createOFP(self, missionRows : list[OrderRow], townHallToDeliver : TownHall):
        self.missionRows = missionRows
        self.OFP = townHallToDeliver.getZones()

    @icontract.require(lambda state : state >= 0 and state <= 3)
    def setState(self, state : int):
        self.state = state
        if self.state == 2 :
            #Order rows are delivered, updating their state
            for missionRow in self.missionRows :
                missionRow.setState(2)
                self.saveLog("Delivered")
    
    def startMission(self):
        self.setState(1)
        for missionRow in self.missionRows :
            missionRow.setState(1)
        self.saveLog("Out for delivery")
        self.drone.uploadOFP(self, self.OFP, self.missionPayload)
    
    def saveLog(self, msg: str):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_msg = f"[{timestamp}] {msg}"
        self.logMissions.append(LogMission(log_msg))
        print(log_msg)

class Drone :
    @icontract.require(lambda payload, range : payload > 0 and range > 0)
    def __init__(self, name : str, base: Base, payload : int, range : int):
        self.name = name
        self.base = base
        self.payload = payload*ureg.kg
        self.range = range*ureg.km #range is not used in this version
        self.state = 0 #0 = idle, 1 = in mission
        self.OFP = None
        self.currentMission = None
        self.currentPayload = 0*ureg.kg

    @icontract.ensure(lambda self, missionPayload : missionPayload <= self.payload and missionPayload > 0*ureg.kg)
    def uploadOFP(self, mission : Mission, OFP, missionPayload : int):
        self.currentMission = mission
        self.OFP = OFP
        self.currentPayload = missionPayload
        print(f"[IODELIV LOG] OFP received, {self.name} ready to take off !")
        #print(f"[IODELIV LOG] OFP :")
       #for zone in OFP:
            #print(f"{zone.name}")
        #print(f"[IODELIV LOG] Payload : {missionPayload}")
        self.doMission()
    
    def doMission(self):
        self.takeOff(None) #take off from base
        for zone in self.OFP:
            self.land(zone)
            if self.delivery(zone):
                self.currentMission.saveLog(f"Delivery to {zone.name} successful")
            else :
                self.currentMission.saveLog(f"Delivery to {zone.name} failed")
                self.returnToBase()
                return
            self.takeOff(zone)
        self.returnToBase()

    def takeOff(self, zone : Zone):
        if zone :
            self.currentMission.saveLog(f"{self.name} taking off from {zone.name}")
        else :
            self.currentMission.saveLog(f"{self.name} taking off from {self.base.name}")

    def land(self, zone : Zone):
        if zone :
            self.currentMission.saveLog(f"{self.name} landing on {zone.name}")
        else :
            self.currentMission.saveLog(f"{self.name} landing on its base")

    def returnToBase(self):
        self.currentMission.saveLog(f"{self.name} returning to {self.base.name}")
        self.land(None) #land on base
        self.finishMission() #mission is finished, payload is reset to 0
        pass

    def delivery(self, zone : Zone):
        if(self.currentPayload >= zone.livingSouls*0.01*ureg.kg):
            self.currentPayload -= zone.livingSouls*0.01*ureg.kg
            return True
        else :
            self.currentMission.saveLog(f"{self.name} has not enough pills !")
            return False

    def finishMission(self):
        print(f"[IODELIV LOG] {self.name} finished mission")
        self.currentPayload = 0
        self.currentMission.setState(2) #mission is finished
        self.state = 0
        self.mission = None
        self.OFP = None

class LogMission :
    def __init__(self, msg : str):
        self.msg = msg

class IODeliv :
    def __init__(self) :
        self.orders = [] #Orders object's adress
        self.operators = [] #Operators object's adress
    
    def register(self, newOperator : Operator):
        newBase = newOperator.base
        for operator in self.operators :
            if newBase.townHall == operator.base.townHall:
                print("[IODELIV LOG] Register impossible IODeliv has already an operator in this zone")
                return
        self.operators.append(newOperator)
        print("[IODELIV LOG] Operator registered")
    
    def getMatchingOperators(self, townHall : TownHall) -> Operator:
        for operator in self.operators:
            if operator.base.townHall == townHall:
                return operator
        print("[IODELIV LOG] No operator available in this zone")
        print("[IODELIV LOG] Searching for the nearest operator")
        shortestDistance = 1000000*ureg.km
        for operator in self.operators:
            distance = math.sqrt((operator.base.lat-townHall.lat)**2 + (operator.base.lon-townHall.lon)**2)*ureg.km
            if distance < shortestDistance:
                shortestDistance = distance
                nearestOperator = operator
        
        if shortestDistance <= 10*ureg.km:
            return nearestOperator
        else :
            print("[IODELIV LOG] No operator available in a 10km radius")
            return None

if __name__ == '__main__' :
    IODelivery = IODeliv()

    provenceAlpesCotesDazur = StateService("Provence-Alpes-Côtes d'Azur")

    Antibes = TownHall("Antibes", provenceAlpesCotesDazur, 43.5804, 7.1232)
    Nice = TownHall("Nice", provenceAlpesCotesDazur, 43.7102, 7.2620)
    Biot = TownHall("Biot", provenceAlpesCotesDazur, 43.6187, 7.0696)

    Antibes.addZone(Zone("Antibes Zone1", 100))
    Antibes.addZone(Zone("Antibes Zone2", 200))
    Antibes.addZone(Zone("Antibes Zone3", 150))

    Nice.addZone(Zone("Nice Zone1", 300))
    Nice.addZone(Zone("Nice Zone2", 250))
    Nice.addZone(Zone("Nice Zone3", 350))

    Biot.addZone(Zone("Biot Zone1", 50))
    Biot.addZone(Zone("Biot Zone2", 100))
    Biot.addZone(Zone("Biot Zone3", 75))

    Base1 = Base("Base d'Antibes", 43.5804, 7.1232, Antibes)
    Base1.BuyDrone("Drone1", 10, 100)
    Base1.BuyDrone("Drone2", 10, 100)
    Base1.BuyDrone("Drone3", 10, 100)

    Base2 = Base("Base de Nice", 43.7102, 7.2620, Nice)
    Base2.BuyDrone("Drone1", 10, 100)
    Base2.BuyDrone("Drone2", 10, 100)
    Base2.BuyDrone("Drone3", 10, 100)

    Operator1 = Operator("Operator1", Base1)
    Operator2 = Operator("Operator2", Base2)

    Operator1.signIn(IODelivery)
    Operator2.signIn(IODelivery)

    order = {
        Antibes : 450,
        Nice : 900,
        Biot : 500
    }

    provenceAlpesCotesDazur.createOrder(order, IODelivery)
    Operator1.createMissions()
    Operator1.launchMission()

    Operator2.createMissions()
    Operator2.launchMission()
