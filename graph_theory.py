import networkx as nx
import matplotlib.pyplot as plt
import time

def addDC(asn, dc_id, cost, cap):
    #Add to list
    if(f"ASN{asn}:DC{dc_id}" not in dc[csp.index(asn)]):
        dc[csp.index(asn)][dc_id-1] = f"{asn}:DC{dc_id}"
    d_cost[csp.index(asn)][dc_id-1]= cost
    d_cap[csp.index(asn)][dc_id-1]= cap

def addEdge(asn1, asn2, cost, cap):
    #New edge
    if((asn1, asn2) not in edge_list):
        edge_cost.append(cost)
        edge_cap.append(cap)
        edge_list.append((asn1,asn2))
    #Update edge
    else:
        edge_cost[edge_list.index((asn1, asn2))] = cost
        edge_cap[edge_list.index((asn1, asn2))] = cap

def getBW(g, path):
    cap= g[path[0]][path[1]]["capacity"]
    for i in range(len(path)-1):
        cap = min(cap,g[path[i]][path[i+1]]["capacity"]) 
    return cap
          
def createGraph():
    #Create network graph
    G=nx.Graph()

    #Add nodes
    for i in range(len(csp)):
        G.add_node(csp[i], demand=len(dc[i]))
        #Add DCs to graph
        for j in range(len(dc[i])):
            if dc[i][j] != '':
                G.add_node(dc[i][j])
                G.add_edge(csp[i], dc[i][j] , weight=d_cost[i][j]/d_cap[i][j], capacity=d_cap[i][j])

    #Add edges
    for i in range(len(edge_list)):
        G.add_edge(edge_list[i][0], edge_list[i][1], weight=edge_cost[i]/edge_cap[i], capacity=edge_cap[i])

    #Calculate shortest path from DCi to every other DC
    shortest=[]
    
    for k in dc[csp.index(f"ASN{local_asn}")]:
            if k!='':
                shortest.append(nx.shortest_path(G,k, weight='weight'))

    #Print Routing Tables
    i=0
    #for list_k in dc:
    for k in dc[csp.index(f"ASN{local_asn}")]:
        if k!='':
            print(f"\n\n--------Routing Table for {k}----------------\nDESTINATION\t$/Mbps\tMbps\tPATH\n")
            for key, value in shortest[i].items():
                if ("DC" in key) and key!=k:
                    cost=0
                    for j in range(len(value)-1):
                        cost+= G[value[j]][value[j+1]]['weight']*G[value[j]][value[j+1]]['capacity']
                    bw= getBW(G,value)
                    print(f"{key}\t{cost:.2f}\t{bw:.2f}\t{value}")
            i+=1

    print("\n\n************************************************************************")
    '''
    #Visual representation of the network
    pos = nx.shell_layout(G)
    nx.draw(G, pos, with_labels=True)
    labels = {e: G.edges[e]['weight'] for e in G.edges}
    nx.draw_networkx_edge_labels(G, pos, edge_labels=labels)
    plt.show()
    '''

RCU_TIMER =30

#Lists to store the attributes of ASNs and DCs
csp= ['' for x in range(10)]

dc = [['' for x in range(10)] for y in range(10)]
d_cost = [[0 for x in range(10)] for y in range(10)]
d_cap = [[0 for x in range(10)] for y in range(10)]

#Lists to store the attributes of the links
edge_cost = []
edge_cap  = []
edge_list = []

#Read from config
f =open("config.txt", "r")
local_rc, local_asn = f.readline().split()
local_rc = int(local_rc)

#Add ASN to list
csp[local_rc]=f"ASN{local_asn}"

#Add details of other ASNs
for i in range(int(f.readline())):
    #Get info on ASN
    rc_id, asn, cp, co = f.readline().split()
    rc_id=int(rc_id)
    
    #Add to list
    csp[rc_id]= f"ASN{asn}"
    addEdge(csp[local_rc],csp[csp.index(f"ASN{asn}")], int(co), int(cp))

#Add the local ASN's DCs
for i in range(int(f.readline())):
    #Get info on the DCs
    dc_id, cp, co = f.readline().split()

    #Add to list
    addDC(f"ASN{local_asn}", int(dc_id), int(co), int(cp))

#Create Routing Tables
createGraph()


############Simulate receiving info
#Receive link info from ASN200
addEdge("ASN200", "ASN300", 10, 1000)
addEdge("ASN200", "ASN400", 10, 1000)
#Receive DC info from ASN200
addDC("ASN200", 1, 5, 1)
addDC("ASN200", 2, 5, 2)
addDC("ASN200", 3, 5, 3)

#Receive link info from ASN300
addEdge("ASN200", "ASN300", 10, 1000) #Duplicate edge, ignored (must be sent with asn1<asn2)
addEdge("ASN300", "ASN400", 10, 1000)
#Receive DC info from ASN300
addDC("ASN300", 1, 5, 4)
addDC("ASN300", 2, 5, 5)

#Receive link info from ASN400
addEdge("ASN200", "ASN400", 1, 1000) #Cost changed
addEdge("ASN300", "ASN400", 10, 1000) #Duplicate edge, ignored (must be sent with asn1<asn2)
#Receive DC info from ASN400
addDC("ASN400", 1, 5, 6)
addDC("ASN400", 2, 5, 7)

#'''
while(True):
    time.sleep(RCU_TIMER)
    #SEND RCU TO ALL OTHER RC

    #Display routing table
    createGraph()
    
