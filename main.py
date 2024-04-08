import pika, sys, time
import networkx as nx

def on_message_received(ch, method, properties, body):
    #Split RCU into its components 
    s_asn, d_asn, co, cp, dc_att =body.decode().split(';')
    dc_att= eval(dc_att)

    #Do not consume RCU sent from this RC
    if s_asn != csp[local_rc]: 

        #Update/Add link to graph of the network
        addEdge(s_asn, d_asn, int(co), int(cp))

        #Update/Add data center to graph of the network
        for i in range(len(dc_att)):
            if (dc_att[i] != (0,0)):
                addDC(s_asn, i+1, dc_att[i][0], dc_att[i][1])
    
    #Send ACK
    ch.basic_ack(delivery_tag=method.delivery_tag)

def sendRCU(message):
    channel.basic_publish(exchange='RCU', routing_key='', body=message)

def addDC(asn, dc_id, cost, cap):
    #Add to list if data center is not in list
    if(f"ASN{asn}:DC{dc_id}" not in dc[csp.index(asn)]):
        dc[csp.index(asn)][dc_id-1] = f"{asn}:DC{dc_id}"

    #Update cost and capacity for data center    
    dc_attr[csp.index(asn)][dc_id-1] = (cost,cap)

def addEdge(asn1, asn2, cost, cap):
    #Update edge
    if((asn1, asn2) in edge_list):
        edge_cost[edge_list.index((asn1, asn2))] = cost
        edge_cap[edge_list.index((asn1, asn2))] = cap
    elif((asn2, asn1) in edge_list):
        edge_cost[edge_list.index((asn2, asn1))] = cost
        edge_cap[edge_list.index((asn2, asn1))] = cap  

    #New edge
    else:
        edge_cost.append(cost)
        edge_cap.append(cap)
        edge_list.append((asn1,asn2))
    
def getBW(g, path):
    #Start with capacity of link between DC and local ASN
    cap= g[path[0]][path[1]]["capacity"]

    #Update capacity if smaller capacity found
    for i in range(len(path)-1):
        cap = min(cap,g[path[i]][path[i+1]]["capacity"]) 
    
    return cap
          
def createGraph():
    #Create network graph
    G=nx.Graph()

    #Add nodes
    for i in range(len(csp)):
        #Add each ASN to the graph
        G.add_node(csp[i])

        #Add this ASN's DCs to the graph
        for j in range(len(dc[i])):
            if dc[i][j] != '':
                G.add_node(dc[i][j])

                #Create link between ASN and DC
                G.add_edge(csp[i], dc[i][j] , weight=dc_attr[i][j][0]/dc_attr[i][j][1], capacity=dc_attr[i][j][1])

    #Add edges
    for i in range(len(edge_list)):
        #Link between two ASNs
        G.add_edge(edge_list[i][0], edge_list[i][1], weight=edge_cost[i]/edge_cap[i], capacity=edge_cap[i])

    #Calculate shortest path from DCi to every other DC in the network
    shortest=[]
    for k in dc[csp.index(f"ASN{local_asn}")]:
            if k!='':
                #Use Bellman-Ford Algorithm
                shortest.append(nx.shortest_path(G,k, weight='weight', method='bellman-ford'))


    #Calculate number of DCs in network
    num_dc=0
    for k in dc:
        for v in k:
            if v!='':
                num_dc += 1

    #Print Routing Tables for each DC connected to local ASN
    i=0
    for k in dc[csp.index(f"ASN{local_asn}")]:
        #Ignore empty elements in list
        if k!='':
            print(f"\n\n--------Routing Table for {k}----------------\nDESTINATION\t$/Mbps\tMbps\t\tPATH\n")
            for key, value in shortest[i].items():

                #Only show paths from DC to DC
                if ("DC" in key) and key!=k:

                    cost=0
                    for j in range(len(value)-1):
                        #Calculate cost
                        cost+= G[value[j]][value[j+1]]['weight']*G[value[j]][value[j+1]]['capacity']

                    #Calculate bandwidth and share equally between all DCs   
                    bw= getBW(G,value)/num_dc

                    #Print routing table for DC
                    print(f"{key}\t{cost:.2f}\t{bw:.2f}\t\t{value}")
            i+=1

    print("\n\n************************************************************************")

RCU_TIMER =30

#Get RC number from user
num=int(sys.argv[1])

#Lists to store the attributes of ASNs and DCs
csp= ['' for x in range(10)]
dc = [['' for x in range(10)] for y in range(10)]
dc_attr = [[(0,0) for x in range(10)] for y in range(10)]

#Lists to store the attributes of the links
edge_cost = []
edge_cap  = []
edge_list = []

#Read from config
f =open(f"config_{num}.txt", "r")
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

#Create initial routing tables
createGraph()

#Connect to RabbitMQ channel
connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
channel = connection.channel()

#Declare the exchange
channel.exchange_declare(exchange='RCU',exchange_type='fanout')

#Declare the queue this RC will consume from
channel.queue_declare(queue=f'ASN{num}00')
queue_state = channel.queue_declare(queue=f'ASN{num}00', durable=True, passive=True)
queue_empty = queue_state.method.message_count == 0

#Bind the queue to the exchange
channel.queue_bind(exchange='RCU', queue=f'ASN{num}00')


#Send initial RCU on startup
for e in edge_list:
    #For every link connected to this RC
    if e[0] == csp[local_rc]:
        i = edge_list.index(e)

        # LOCAL_ASN; DEST_ASN; COST; CAPACITY; LIST OF DC (COST, CAPACITY) 
        sendRCU(f"{e[0]};{e[1]};{edge_cost[i]};{edge_cap[i]};{dc_attr[local_rc]}")

#Start RCU_TIMER
t= time.time()

while(True):
    #Check for messages in the queue
    queue_state = channel.queue_declare(queue=f'ASN{num}00', durable=True, passive=True)
    queue_empty = queue_state.method.message_count == 0

    #Consume messages in the queue
    if queue_state.method.message_count != 0:
        method, properties, body = channel.basic_get(queue=f'ASN{num}00')
        on_message_received(channel, method, properties, body)

    #Check if RCU_TIMER has expired
    if(time.time()-t > RCU_TIMER):
        t=time.time()

        #Send RCUs
        for e in edge_list:
            if e[0] == csp[local_rc]:
                i = edge_list.index(e)
                sendRCU(f"{e[0]};{e[1]};{edge_cost[i]};{edge_cap[i]};{dc_attr[local_rc]}")
        
        #Print routing table
        createGraph()
