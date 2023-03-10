from docplex.mp.model import Model
import numpy as np

size =   [3,5,10,20,30,40,50,75,100,150]

#Parameters
num_instances = 20

alpha = 1.0
beta = 1.0
gamma = 1.0

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
        C = np.random.randint(1, 100, size=(num_implements, num_tasks, num_vehicles))
        M = np.random.randint(100, 5000, size=num_tasks)
        T_max = np.random.randint(400, 500, size=num_vehicles)
        c_prime = np.random.randint(1, 50, size=num_vehicles)
        T = [np.random.randint(c_prime[t], T_max[t]) for t in range(num_vehicles)]
        I = range(num_implements)
        K = range(num_tasks)
        V = range(num_vehicles)
        
        Mmax = sum(M[k] for k in K)
        Tmax = sum((T_max[v] - T[v]) for v in V)
        
        #Caculate Cmax solving a similar maximization problem
        model = Model()
        
        #Decision variables
        x = {}
        for i in I:
            for k in K:
                for v in V:
                    x[(i, k, v)] = model.binary_var(name=f'x_{i}_{k}_{v}')
        
        obj = model.sum(C[i][k][v] * x[(i, k, v)] for i in I for k in K for v in V)
        model.maximize(obj)
        
        #Constraints
        for i in I:
            model.add_constraint(model.sum(x[(i, k, v)] for k in K for v in V) <= 1)
        for k in K:
            model.add_constraint(model.sum(x[(i, k, v)] for i in I for v in V) <= 1)
        for v in V:
            model.add_constraint(model.sum(x[(i, k, v)] for i in I for k in K) <= 1)
        
        #Solving
        solution = model.solve()
        Cmax = solution.get_objective_value()
        
        
        
        
        #Model definition
        model = Model()
        
        #Decision variables
        x = {}
        for i in I:
            for k in K:
                for v in V:
                    x[(i, k, v)] = model.binary_var(name=f'x_{i}_{k}_{v}')
        
        y = {}
        for v in V:
            y[v] = model.binary_var(name=f'y_{v}')
        
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
            model.add_constraint(model.sum(x[(i, k, v)] for i in I for k in K) <= 1)
            model.add_constraint(y[v] + model.sum(x[(i, k, v)] for i in I for k in K) == 1)
            model.add_constraint(model.sum((C[i][k][v] + c_prime[v]) * x[(i, k, v)] for i in I for k in K) <= T[v])
            model.add_constraint(c_prime[v] * y[v] <= T[v])
            
        #Solving
        solution = model.solve()
        
        #Recording values
        solve_time = solution.solve_details.time
        obj_value = solution.get_objective_value()
        
        solving_times.append(solve_time)
        optimal_values.append(obj_value)
        solving_times_dic[s] = np.mean(solving_times)
    
    print(f'The average solving time for instances of size {s} is: {np.mean(solving_times)}')
    
    
