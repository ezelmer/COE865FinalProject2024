class path:
    destIP = 0
    Cost = 0
    Capacity = 0
    specPath = 0

    def __init__(self, destIP, Cost, Capacity, specPath):
        self.destIP = destIP
        self.Cost = Cost
        self.Capacity = Capacity
        self.specPath = specPath
    def updateGivenPath(self, linkcost, linkcapacity, curIP):
        return path(self.destIP, self.Cost + linkcost, min(self.Capacity, linkcapacity), curIP + "," + self.specPath)
    def __str__(self):
        return ("Destination:" + self.destIP + ". Cost: " + str(self.Cost) + ". Capacity: " + str(self.Capacity) + ".\nThe Path:" + self.specPath)


class message:
    destIP = 0
    size = 0
    def __init__(self, destIP, size):
        self.destIP = destIP
        self.size = size



class Router:
    IP = 0
    paths = []
    connections = []
    def __init__(self, IP):
        self.paths = []
        self.connections = []
        self.IP = IP

class connection:
    router = 0
    cost = 0
    capacity = 0


myIP = "10.10.10.0"
myCapacity = 999
rzeropath = path(myIP, 0, myCapacity, myIP)

r1addedpath = rzeropath.updateGivenPath(3, 10, "10.10.10.1")

rzeropaths = []
rzeropaths.append(rzeropath)

r1paths = []
r1paths.append()
print(str(r1addedpath))

