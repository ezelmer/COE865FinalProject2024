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
        return ("Destination:" + self.destIP + ". Cost: " + str(self.Cost) + ". Capacity: " + str(self.Capacity) + ".\nThe Path:" + self.specPath + "\n\n")
    def __repr__(self):
        return str(self)
    
    def __eq__(self, other):
        return self.destIP == other.destIP and self.Cost == other.Cost and self.Capacity == other.Capacity and self.specPath == other.specPath


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
        selfpath = path(self.IP, 0, 999, self.IP)
        self.paths.append(selfpath)
    #advertised paths, connection used, and who we're receiving hello from.
    def Hello(self, advpaths, theconnection, fromIP):
        for path in advpaths:
            if(self.IP not in path.specPath):
                addpath = path.updateGivenPath(theconnection.cost, theconnection.capacity, self.IP)
                alreadyHaveIt = False
                for path2 in self.paths:
                    if(path2 == addpath):
                        alreadyHaveIt = True
                if(alreadyHaveIt == False):
                    self.paths.append(addpath)



    def SayHello(self):
        for cxn in self.connections:
            cxn.router.Hello(self.paths, cxn, self.IP)


class connection:
    router = 0
    cost = 0
    capacity = 0
    def __init__(self, router, cost, capacity):
        self.router = router
        self.cost = cost
        self.capacity = capacity

r1 = Router("10.10.10.1")
r2 = Router("10.10.10.2")
r3 = Router("10.10.10.3")
print(str(r2.paths))
print("\n\n\n")
r1.connections.append(connection(r2, 3, 3))
r2.connections.append(connection(r1, 3, 3))
r3.connections.append(connection(r1, 5, 2))

r3.connections.append(connection(r2, 1, 10))
r2.connections.append(connection(r3, 1, 10))
r1.connections.append(connection(r3, 5, 2))

r1.SayHello()
r2.SayHello()
r3.SayHello()
r1.SayHello()
r2.SayHello()
r3.SayHello()
r1.SayHello()
r2.SayHello()
r3.SayHello()
r1.SayHello()
r2.SayHello()
r3.SayHello()
r1.SayHello()
r2.SayHello()
r3.SayHello()

print(str(r2.paths))

#myIP = "10.10.10.0"
#myCapacity = 999
#rzeropath = path(myIP, 0, myCapacity, myIP)

#r1addedpath = rzeropath.updateGivenPath(3, 10, "10.10.10.1")

#rzeropaths = []
#rzeropaths.append(rzeropath)

#r1paths = []
#r1paths.append()
#print(str(r1addedpath))

