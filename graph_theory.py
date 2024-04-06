import pika, sys, time
import networkx as nx

def on_message_received(ch, method, properties, body):

    s_asn, d_asn, co, cp, dc_att =body.decode().split(';')
    dc_att= eval(dc_att)

    if s_asn != csp[local_rc]: 
        addEdge(s_asn, d_asn, int(co), int(cp))
        for i in range(len(dc_att)):
            if (dc_att[i] != (0,0)):
                addDC(s_asn, i+1, dc_att[i][0], dc_att[i][1])
    
        #print(f"RCU Link Update: {s_asn}-{d_asn}")
    ch.basic_ack(delivery_tag=method.delivery_tag)

def sendRCU(message):
    channel.basic_publish(exchange='RCU', routing_key='', body=message)
    print(f" [x] Sent {message}")

def addDC(asn, dc_id, cost, cap):
    #Add to list
    if(f"ASN{asn}:DC{dc_id}" not in dc[csp.index(asn)]):
        dc[csp.index(asn)][dc_id-1] = f"{asn}:DC{dc_id}"
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
                G.add_edge(csp[i], dc[i][j] , weight=dc_attr[i][j][0]/dc_attr[i][j][1], capacity=dc_attr[i][j][1])

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

#Create Routing Tables
createGraph()

#Connect to RabbitMQ channel
connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
channel = connection.channel()

channel.exchange_declare(exchange='RCU',exchange_type='fanout')

channel.queue_declare(queue=f'ASN{num}00')
queue_state = channel.queue_declare(queue=f'ASN{num}00', durable=True, passive=True)
queue_empty = queue_state.method.message_count == 0

channel.queue_bind(exchange='RCU', queue=f'ASN{num}00')


#Send initial RCU on bootup
for e in edge_list:
    if e[0] == csp[local_rc]:
        i = edge_list.index(e)
        sendRCU(f"{e[0]};{e[1]};{edge_cost[i]};{edge_cap[i]};{dc_attr[local_rc]}")


t= time.time()

while(True):
    #Check for messages in the queue
    queue_state = channel.queue_declare(queue=f'ASN{num}00', durable=True, passive=True)
    queue_empty = queue_state.method.message_count == 0

    #Consume messages in the queue
    if queue_state.method.message_count != 0:
        method, properties, body = channel.basic_get(queue=f'ASN{num}00')
        on_message_received(channel, method, properties, body)

    if(time.time()-t > RCU_TIMER):
        t=time.time()

        for e in edge_list:
            if e[0] == csp[local_rc]:
                i = edge_list.index(e)
                sendRCU(f"{e[0]};{e[1]};{edge_cost[i]};{edge_cap[i]};{dc_attr[local_rc]}")
        
        createGraph()
