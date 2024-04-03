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
    links = []
    def __init__(self, IP):
        self.paths = []
        self.links = []
        self.IP = IP
        selfpath = path(self.IP, 0, 999, self.IP)
        self.paths.append(selfpath)
    #advertised paths, link used, and who we're receiving hello from.
    def Hello(self, advpaths, thelink, fromIP):
        for path in advpaths:
            if(self.IP not in path.specPath):
                addpath = path.updateGivenPath(thelink.cost, thelink.capacity, self.IP)
                alreadyHaveIt = False
                for path2 in self.paths:
                    if(path2 == addpath):
                        alreadyHaveIt = True
                if(alreadyHaveIt == False):
                    self.paths.append(addpath)



    def SayHello(self):
        for cxn in self.links:
            cxn.router.Hello(self.paths, cxn, self.IP)

class link:
    router = 0
    cost = 0
    capacity = 0
    def __init__(self, router, cost, capacity):
        self.router = router
        self.cost = cost
        self.capacity = capacity

r1 = Router("ASN100")
r2 = Router("ASN200")
r3 = Router("ASN300")
r4 = Router("ASN400")
r5 = Router("ASN400:DC1")

print(str(r5.paths))
print("--------------------")
r1.links.append(link(r2, 1, 1))
r1.links.append(link(r3, 1, 1))
r1.links.append(link(r4, 10, 1))

r2.links.append(link(r1, 1, 1))
r2.links.append(link(r3, 10, 1))
r2.links.append(link(r4, 1, 1))

r3.links.append(link(r1, 1, 1))
r3.links.append(link(r2, 10, 1))
r3.links.append(link(r4, 1, 1))

r4.links.append(link(r1, 10, 1))
r4.links.append(link(r2, 1, 1))
r4.links.append(link(r3, 1, 1))
r4.links.append(link(r5, 0, 1))

r5.links.append(link(r4, 0, 1))

for i in range(5):
    r1.SayHello()
    r2.SayHello()
    r3.SayHello()
    r4.SayHello()
    r5.SayHello()


#Find optimal path
for i in range (1,5):
    weight=999
    preferred= None
    for p in r5.paths:
        if (p.destIP == f'ASN{i}00' and (p.Cost/p.Capacity)<weight):
            preferred = p
            weight =p.Cost/p.Capacity
    
    print(preferred)
