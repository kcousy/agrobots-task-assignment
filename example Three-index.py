from docplex.mp.model import Model
import numpy as np

size =   [2]

#Parameters
num_instances = 1

alpha = 0.1
beta = 0.85
gamma = 0.05

solving_times_dic = {}


#loop over different sizes of matrix
for s in size:
    
    num_tasks = s
    num_vehicles = s
    num_implements = s
    
    #Lists that will store the results 
    solving_times = []
    optimal_values = []
    
    #loop over as many instances as we want
    for n in range(num_instances):
        print(f"Solving instance {n+1}/{num_instances}")
    
        #Generate random instance
        C = [[[5, 10], [6, 8]], [[3, 7], [4, 4]]]
        M = [500, 1000]
        T_max = [35, 50]
        c_prime = [[8, 5],[7, 6] ]
        T = [25, 30]
        I = range(num_implements)
        K = range(num_tasks)
        V = range(num_vehicles)
        

        
        
        
        
        #Model definition
        model = Model()
        model.context.cplex_parameters.threads = 1
        model.context.cplex_parameters.workmem = 8192.0
        model.set_time_limit(3600)
        
        #Decision variables
        x = {}
        for i in I:
            for k in K:
                for v in V:
                    x[(i, k, v)] = model.binary_var(name=f'x_{i}_{k}_{v}')
        
        y = {}
        for v in V:
            y[v] = model.binary_var(name=f'y_{v}')
        

        Mmax = sum(M[k] for k in K)
        Tmax = sum((T_max[v] - T[v]) for v in V)
        Cmax = 14
        
        #Objective function
        obj = model.sum((alpha/(Cmax)) * C[i][k][v] * x[(i, k, v)] for i in I for k in K for v in V) \
              + model.sum((beta/(Mmax)) * M[k] * (1 - model.sum(x[(i, k, v)] for i in I for v in V)) for k in K) \
              + model.sum((gamma/(Tmax)) * (T_max[v] - T[v]) * (1 - y[v]) for v in V)
        model.minimize(obj)

        
        #Constraints
        for i in I:
            model.add_constraint(model.sum(x[(i, k, v)] for k in K for v in V) <= 1)
        for k in K:
            model.add_constraint(model.sum(x[(i, k, v)] for i in I for v in V) <= 1)
        for v in V:
            model.add_constraint(y[v] + model.sum(x[(i, k, v)] for i in I for k in K) == 1)
            model.add_constraint(model.sum((C[i][k][v] + c_prime[v][k]) * x[(i, k, v)] for i in I for k in K) <= T[v])
            
        #Solving
        solution = model.solve()#log_output=True)
        
        #Recording values
        solve_time = solution.solve_details.time
        obj_value = solution.get_objective_value()
        
        solving_times.append(solve_time)
        optimal_values.append(obj_value)
        solving_times_dic[s] = np.mean(solving_times)
    
    print(f'The average solving time for instances of size {s} is: {np.mean(solving_times)}')