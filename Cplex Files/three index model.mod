int num_implements=...;
int num_tasks=...;
int num_vehicles=...;

range I = 1..num_implements;
range K = 1..num_tasks;
range V = 1..num_vehicles;

int z = 0;


int M[k in K]= 100 + rand(5000);
int T_max[v in V] = 400 + rand(100);
int C_prime[v in V] = 1 + rand(49);
int T[v in V] = C_prime[v] + rand(T_max[v] - C_prime[v]);
int C[i in I][k in K][v in V] = 1 + rand(99);

float alpha = ...;
float beta = ...;
float gamma = ...;

int Cmax = 1;
int Mmax = 1;
int Tmax = 1;

dvar boolean x[I][K][V];
dvar boolean y[V];

minimize sum(i in I, k in K, v in V) (alpha/Cmax) * C[i][k][v] * x[i][k][v]
         + sum(k in K) (beta/Mmax) * M[k] * (1 - sum(i in I, v in V) x[i][k][v])
         + sum(v in V) (gamma/Tmax) * (T_max[v] - T[v]) * (1 - y[v]);

subject to {
    forall(i in I) {
        sum(k in K, v in V) x[i][k][v] <= 1;
    }
    forall(k in K) {
        sum(i in I, v in V) x[i][k][v] <= 1;
    }
    forall(v in V) {
        sum(i in I, k in K) x[i][k][v] <= 1;
        y[v] + sum(i in I, k in K) x[i][k][v] == 1;
        sum(i in I, k in K) (C[i][k][v] + C_prime[v]) * x[i][k][v] <= T[v];
        C_prime[v] * y[v] <= T[v];
    }
}

execute {
    cplex.tilim = 3600;
}
