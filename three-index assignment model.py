from docplex.mp.model import Model
import random

#Cardinality of each set
num_tasks = 10
num_vehicles = 7
num_implements = 5

#Define the sets
K = range(num_tasks)
V = range(num_vehicles)
I = range(num_implements)

#Randomized parameters for the model:

#Cost for vehicle v to do task k
c_kv = {(k, v): random.randint(1, 10) for k in K for v in V}
#Cost for using implement i to do task k
c_ki = {(k, i): random.randint(1, 5) for k in K for i in I}
#Compatibility task-implement
p = {(k, i): random.randint(0, 1) for k in K for i in I}
#Compatibility task-vehicle
q = {(k, v): random.randint(0, 1) for k in K for v in V}
#Resource capacity of implement i
b_i = {i: random.randint(1, 100) for i in I}
#Resource requirement of task k
r_k = {k: random.randint(1, 75) for k in K}
#Maximum autonomy of vehicle v
T_v_max = {v: random.randint(50, 200) for v in V}
#Current autonomy of vehicle v
T_v = {v: random.randint(1, T_v_max[v]) for v in V}
#Autonomy required for vehicle v to go from depot to task k
t_v0k = {(v, k): random.randint(1, 30) for v in V for k in K}
#Autonomy required for vehicle v to go from task k to depot
t_vk0 = {(v, k): random.randint(1, 30) for v in V for k in K}
#Sets of implements not compatible with a task k
I_bar = {k: set(random.sample(I, random.randint(0, num_implements))) for k in K}
#Penalty for not doing a task
M = {k: random.randint(100, 5000) for k in K}

#Initialize the model
mdl = Model('Vehicle-Task Assignment')



#Decision variables
x = mdl.binary_var_matrix(K, V, name='x')  # vehicle-task assignment
z = mdl.binary_var_matrix(K, I, name='z')  # implement-task assignment
y = mdl.binary_var_dict(V, name='y')  # vehicle-depot assignment

#Objective function
obj = mdl.sum(c_kv[k, v] * x[k, v] + c_ki[k, i] * z[k, i] for k in K for v in V for i in I) \
      + mdl.sum(M[k] * (1 - mdl.sum(x[k, v] for v in V)) for k in K) \
      - mdl.sum((T_v_max[v] - T_v[v]) * y[v] for v in V)
mdl.minimize(obj)

#Constraints:

#Each task must be assigned to exactly one vehicle
for k in K:
    mdl.add_constraint(mdl.sum(q[k, v]*x[k, v] for v in V) == 1)

#Each vehicle can only be assigned to at most one task
for v in V:
    mdl.add_constraint(mdl.sum(q[k, v]*x[k, v] for k in K) <= 1)

#Each task must use exactly one implement
for k in K:
    mdl.add_constraint(mdl.sum(p[k, i]*z[k, i] for i in I) == 1)

#The total amount of resources required for each task cannot exceed the transport capacity of the implement
for i in I:
    mdl.add_constraint(mdl.sum(r_k[k] * z[k, i] for k in K) <= b_i[i])
    
#A vehicle can only be assigned to a task if it is compatible with the task
for v in V:
    for k in K:
        mdl.add_constraint(x[k, v] <= 1 - mdl.sum(z[k, i] for i in I_bar[k]))
        
#The sum of the autonomy needed for a vehicle to go from the depot to a task, do it, and then come back to the depot cannot exceed its current autonomy
for v in V:
    mdl.add_constraint(mdl.sum(x[k, v]*(t_v0k[v, k] + t_vk0[v, k]) for k in K) <= T_v[v])

#If a vehicle is ordered to go back to the depot, then its autonomy usage to go to the depot cannot exceed its current autonomy
for v in V:
    mdl.add_constraint(mdl.sum(t_vk0[v, k] for k in K) * y[v] <= T_v[v])

#A vehicle is either ordered to go back to the depot, or (exclusive) ordered to do a task
for v in V:
    mdl.add_constraint(y[v] + mdl.sum(x[k, v] for k in K) == 1)

#If a vehicle is assigned to a task, there can be at most one implement assigned to that task.
for v in V:
    for k in K:
        mdl.add_constraint(x[k, v] + mdl.sum(z[k, i] for i in I) <= 2)
        
mdl.print_information()

solution = mdl.solve()


if solution:
    print(f"Solution status: {solution.solve_status}")
    #Solution details
    details = {}
    
    #Store the objective value
    details['objective_value'] = solution.objective_value
    
    #Store the decision variable values
    details['x'] = {(k, v): x[k, v].solution_value for k in K for v in V}
    details['z'] = {(k, i): z[k, i].solution_value for k in K for i in I}
    details['y'] = {v: y[v].solution_value for v in V}
    print(details)
else:
    print("The model could not be solved.")
