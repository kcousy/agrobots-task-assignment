import networkx as nx

#Nodes represent the points of interest of the field. Tasks can appear at a node at any time, but strictly among those nodes, meaning no new node can appear.
#Nodes can also simply be an intersection of roads, and it is not necessary that a task appears at a node.
#Node 0 is the depot
nodes = [n for n in range(6)]

#Edges represent the roads between two nodes. Those are the paths which vehicles can take in order to navigate in the field.
#Edges are characterized by a couple (node1, node2): the two nodes that are linked.
edges = [(0,1), (0,2), (0,5), (1,2), (1,4), (2,3), (4,5)]

#Distances represent the travel cost for one vehicle to travel an edge from one node to the other.
distances = {(0, 1): 10, (0, 2): 6, (0, 5): 5, (1, 2): 14, (1, 4): 4, (2, 3): 8, (4, 5): 12}

#The graph formed is undirected.

class Vehicle:
    
    implement = None
    task = None
    
    node = -1 #-1 means the vehicle is along an edge and not a node
    edge = (-1, -1) #(-1, -1) means the vehicle is on a node and not along an edge
    percent = 0.0 #percentage of the edge travelled, when applicable, from -1.0 if coming at node1 of the edge, to 1.0 if coming at node2 of the edge
    
    #By default, a vehicle is at the depot, with no implement and not assigned to a task.
    def __init__(self, autonomy, max_autonomy, position = 0, implement = None, task = None):
        
        #If position is an integer, it means the vehicle is currently at a node.
        if type(position) == int:
            self.node = position
        #If position is a tuple, it means the vehicle is currently along an edge
        if type(position) == tuple:
            self.edge = (position[0],position[1])
            self.percent = position[2]
        self.autonomy = autonomy
        self.max_autonomy = max_autonomy
        self.implement = implement
        self.task = task
        
    def assign_implement(i):
        implement = i
    
    def assign_task(k):
        task = k
        
class Implement:
    
    vehicle = None
    task = None
    
    max_raws = {'water': 10, 'pesticide': 3} #raw material max capacity in liters
    raws = {'water': 5, 'pesticide': 2} #raw material currently held by the implement
    
    node = -1 #-1 means the implement is along an edge and not a node
    edge = (-1, -1) #(-1, -1) means the implement is on a node and not along an edge
    percent = 0.0 #percentage of the edge travelled, when applicable, from -1.0 if coming at node1 of the edge, to 1.0 if coming at node2 of the edge
    
    #By default, an implement is at the depot, not on any vehicle and not assigned to a task.
    def __init__(self, raws = None, max_raws = None, position = 0, vehicle = None, task = None):
        
        #If position is an integer, it means the implement is currently at a node.
        if type(position) == int:
            self.node = position
        #If position is a tuple, it means the implement is currently along an edge
        if type(position) == tuple:
            self.edge = (position[0],position[1])
            self.percent = position[2]
        self.raws = raws
        self.max_raws = max_raws
        self.vehicle = vehicle
        self.task = task
        
    def assign_vehicle(v):
        vehicle = v
    
    def assign_task(k):
        task = k
    
class Task:
    
    vehicle = None
    implement = None
    
    node = -1
    required_raws = {'water': 5} #raw material required to finish the task, in liters
    
    def __init__(self, node, required_raws = None, vehicle = None, implement = None):
        
        self.node = node
        self.required_raws = required_raws
        self.vehicle = vehicle
        self.implement = implement
        
    def assign_vehicle(v):
        vehicle = v
    
    def assign_implement(i):
        implement = i

#Getting the cost of an assignment in terms of the shortest possible distance to do the trip.
def get_cost(v, i, k):
    #Create a graph for the current vehicle
    G = nx.Graph()
    
    #Create another graph for the implement
    G2 = nx.Graph()
    
    num_nodes = len(nodes)
    edges_2 = edges.copy()
    distances_2 = distances.copy()
    
    edges_3 = edges_2.copy()
    distances_3 = distances_2.copy()

    
    #starting node
    v_node = v.node
    #first step node
    i_node = i.node
    #finish node
    k_node = k.node
    
    #In the case where vehicle and implement are along the same edge
    if v.node == -1 and i.node == -1 and v.edge == i.edge:
        d = distances[i.edge]
        
        #If v is closer to the first node than i
        if v.percent < i.percent:
            edges_2.remove((v.edge))
            distances_2.pop((v.edge))
            
            v_node = num_nodes+1
            i_node = num_nodes+2
            num_nodes += 2
            
            #Add a node in the location of the vehicle and the implement along the same initial edge.
            edges_2.append((v.edge[0],v_node))
            edges_2.append((v_node,i_node))
            edges_2.append((i_node,v.edge[1]))
            
            #Add the distances
            distances_2[(v.edge[0],v_node)] = d*v.percent
            distances_2[(v_node,i_node)] = d*(i.percent-v.percent)
            distances_2[(i_node,v.edge[1])] = d*(1-i.percent)
            
            #In the previous case, we must also make some change for the next graph from implement to task, and doing it here earns us some time
            edges_3 = edges_2.copy()
            distances_3 = distances_2.copy()
            
            edges_3.remove((v.edge[0], v_node))
            edges_3.remove((v_node, i_node))
            edges_3.append(v.edge[0], i_node)
            
            distances_3.pop((v.edge[0], v_node))
            distances_3.pop((v_node, i_node))
            distances_3[(v.edge[0], i_node)] = d*i.percent
        
        #If i is closer to the first node than v
        elif v.percent > i.percent:
            edges_2.remove((v.edge))
            distances_2.pop((v.edge))
            
            i_node = num_nodes+1
            v_node = num_nodes+2
            num_nodes += 2
            
            #Add a node in the location of the vehicle and the implement along the same initial edge.
            edges_2.append((v.edge[0],i_node))
            edges_2.append((i_node,v_node))
            edges_2.append((v_node,v.edge[1]))
            
            #Add the distances
            distances_2[(v.edge[0],i_node)] = d*i.percent
            distances_2[(i_node,v_node)] = d*(v.percent-i.percent)
            distances_2[(v_node,v.edge[1])] = d*(1-v.percent)
        
            #In the previous case, we must also make some change for the next graph from implement to task, and doing it here earns us some time
            edges_3 = edges_2.copy()
            distances_3 = distances_2.copy()
            
            edges_3.remove((v_node, v.edge[1]))
            edges_3.remove((i_node, v_node))
            edges_3.append((i_node, v.edge[1]))
            
            distances_3.pop((v_node, v.edge[1]))
            distances_3.pop((i_node, v_node))
            distances_3[(i_node, v.edge[1])] = d*(1-i.percent)
            
            
            
    else:  
        if i.node == -1: #If the implement is not on a node
            d = distances[i.edge]
            
            edges_2.remove((i.edge))
            distances_2.pop((i.edge))
            
            i_node = num_nodes+1
            num_nodes += 1
        
            #Add a node in the location of the implement
            edges_2.append((i.edge[0],i_node))
            edges_2.append((i_node,i.edge[1]))
            
            #Add the distances
            distances_2[(i.edge[0],i_node)] = d*i.percent
            distances_2[(i_node,i.edge[1])] = d*(1.0-i.percent)
            
            edges_3 = edges_2.copy()
            distances_3 = distances_2.copy()
            
        if v.node == -1: #If the vehicle is not on a node
            d = distances[v.edge]
            
            edges_2.remove((v.edge))
            distances_2.pop((v.edge))
            
            v_node = num_nodes+1
            num_nodes += 1
            
            #Add a node in the location of the vehicle
            edges_2.append((v.edge[0],v_node))
            edges_2.append((v_node,v.edge[1]))
            
            print(distances_2)
            
            #Add the distances
            distances_2[(v.edge[0],v_node)] = d*v.percent
            distances_2[(v_node,v.edge[1])] = d*(1.0-v.percent)
    
    #Add the edges and distances to the graph
    for edge in edges_2:
        node1, node2 = edge
        d = distances_2[edge] # get the distance for the current edge
        G.add_edge(node1, node2, distance=d)
        
    #Use Dijkstra's algorithm to find shortest path from vehicle to implement
    s1, distance_vi = shortest_path_vehicle_to_implement(G, v_node, i_node)
    
    #Now from the implement's location, we want to go to task k in the fastest way possible.
    #Add the edges and distances to the graph
    for edge in edges_3:
        node1, node2 = edge
        d = distances_3[edge] # get the distance for the current edge
        G2.add_edge(node1, node2, distance=d)
        
    #Use Dijkstra's algorithm to find shortest path from implement to task location
    s2, distance_ik = shortest_path_vehicle_to_implement(G2, i_node, k_node)
    
    return [s1, s2, distance_vi + distance_ik] #returns path from v to i, from i to k, and the total distance



def shortest_path_vehicle_to_implement(G, vehicle_node, implement_node):
    """
    Returns the shortest path from a vehicle node to an implement node.
    
    Args:
    - G: a NetworkX graph object
    - vehicle_node: the node where the vehicle is located
    - implement_node: the node where the implement is located
    
    Returns:
    - a list of nodes representing the shortest path
    """
    #Compute the shortest path from the vehicle node to the implement node using Dijkstra's algorithm
    path = nx.shortest_path(G, source=vehicle_node, target=implement_node, weight='distance')
    total_distance = nx.shortest_path_length(G, source=vehicle_node, target=implement_node, weight='distance')
    return path, total_distance
        

"""Test code:
v1 = Vehicle(50,100,4)
v2 = Vehicle(50,100,(0,1,0.7))
i1 = Implement(position = 2)
i2 = Implement(position = (0,2,0.6))
i3 = Implement(position = (0,1,0.3))
k1 = Task(5)
get_cost(v1, i1, k1)
get_cost(v1, i2, k1)
get_cost(v2, i1, k1)
get_cost(v2, i3, k1)
"""