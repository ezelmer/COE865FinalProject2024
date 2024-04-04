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
   
def addDC(rc, asn_dc, cost, capacity):
    #Create the router object for the DC
    dc[f"{rc}:{asn_dc[-1]}"]= Router(asn_dc)

    #Add the link between the RC and the DC
    csp[rc].links.append(link(dc[f"{rc}:{asn_dc[-1]}"], int(cost), int(capacity)))
    dc[f"{rc}:{asn_dc[-1]}"].links.append(link(csp[rc], int(cost), int(capacity)))


f =open("config.txt", "r")

local_rc, local_asn = f.readline().split()

#Dicts to store ASNs
csp = {}
dc = {}

#Key= RC_id Value= ASN
csp[local_rc]= Router(f"ASN{local_asn}")

for i in range(int(f.readline())):
    #Get info on CSP
    rc_id, asn, cap, co = f.readline().split()

    #Create the router object for the RC
    csp[rc_id]= Router(f"ASN{asn}")

    #Add the link between the local RC and this RC
    csp[local_rc].links.append(link(csp[rc_id], int(co), int(cap)))
    csp[rc_id].links.append(link(csp[local_rc], int(co), int(cap)))
        
for i in range(int(f.readline())):
    #Get info on the DCs
    dc_id, cap, co = f.readline().split()

    #Create the router object for the DC
    #Key= RC_id:DC_id  Value=ASN:DC
    dc[f"{local_rc}:{dc_id}"]= Router(f"ASN{local_asn}:DC{dc_id}")

    #Add the link between the local RC and the DC
    csp[local_rc].links.append(link(dc[f"{local_rc}:{dc_id}"], int(co), int(cap)))
    dc[f"{local_rc}:{dc_id}"].links.append(link(csp[local_rc], int(co), int(cap)))

#Add links between the other RCs
for k in csp.keys():
        for m in csp.keys():
            if (k!= local_rc and m!= local_rc):
                csp[k].links.append(link(csp[m], 999, 1))


#Add info on DC obtained from RCU
addDC("2", "ASN200:DC1", 1, 10)

for i in range(5):
    for k in  csp.keys():
        csp[k].SayHello()
    for k in dc.keys():
        dc[k].SayHello()




#Find optimal path
for i in range (1,5):
    weight=999
    preferred= None
    for p in dc["1:1"].paths:
        if (p.destIP == f'ASN{i}00' and (p.Cost/p.Capacity)<weight):
            preferred = p
            weight =p.Cost/p.Capacity
    
    print(preferred)
            
            
