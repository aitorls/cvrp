import gurobipy as gp


MSGDICT = {gp.GRB.LOADED : 'LOADED', 
           gp.GRB.OPTIMAL : 'OPTIMAL',
           gp.GRB.INFEASIBLE : 'INFEASIBLE',
           gp.GRB.INF_OR_UNBD : 'INF_OR_UNBD',
           gp.GRB.UNBOUNDED : 'UNBOUNDED',
           gp.GRB.ITERATION_LIMIT : 'ITERATION_LIMIT',
           gp.GRB.NODE_LIMIT : 'NODE_LIMIT',
           gp.GRB.TIME_LIMIT : 'TIME_LIMIT',
           gp.GRB.SOLUTION_LIMIT : 'SOLUTION_LIMIT', 
           gp.GRB.INTERRUPTED : 'INTERRUPTED',
           gp.GRB.NUMERIC : 'NUMERIC',
           gp.GRB.SUBOPTIMAL : 'SUBOPTIMAL',
           gp.GRB.INPROGRESS : 'INPROGRESS',
           gp.GRB.USER_OBJ_LIMIT : 'USER_OBJ_LIMIT',
           gp.GRB.WORK_LIMIT : 'WORK_LIMIT'}

class CVRP():

    def __init__(self, instance):

        # Read data from instance
        self.name = instance["name"]
        
        self.n_vehicles = instance["vehicles"]
        self.vehicles_capacity = instance["capacity"]

        self.node_coord = instance["node_coord"]
        self.demand = instance["demand"]
        self.time_window = instance["time_window"]
        self.service_time = instance["service_time"]
        self.edge_weight = instance["edge_weight"]

        # Compute the graph
        self.n_nodes = len(self.node_coord)

        self.nodes = list(range(self.n_nodes))
        self.customers = self.nodes[1:]
        self.depot = self.nodes[0]

        self.arcs = [(i,j) for i in self.nodes for j in self.nodes if i!= j]
        self.vehicles = list(range(self.n_vehicles))

        # Create the model
        self.model = gp.Model(self.name)
        self.set_verbose(False)
        self.build_model()

    def build_model(self):
        self.generate_vars()
        self.generate_cons()
        self.generate_obj()
        self.update()

    def update(self):
        self.model.update()

    def solve(self, timeLimit = None, gap = 0.0001):
        self.set_time_limit(timeLimit)
        self.set_gap(gap)
        self.model.optimize()

    def generate_vars(self):
        
        self.arc_vars = self.model.addVars(self.arcs, self.vehicles, vtype = gp.GRB.BINARY, name="x")    # TODO: Remove vehicles
        self.capacity_vars = self.model.addVars(self.nodes,   lb=0.0, ub=self.vehicles_capacity, vtype = gp.GRB.CONTINUOUS, name="z") 
    
    def generate_obj(self):
        cost_route = gp.quicksum(self.arc_vars[i,j,v]*self.edge_weight[i,j] for i,j in self.arcs for v in self.vehicles)
        self.model.setObjective(cost_route, gp.GRB.MINIMIZE)


    def set_verbose(self, verbose):
        self.model.Params.LogToConsole = int(verbose)

    def generate_cons(self):
        
        # Visit each node once
        self.model.addConstrs(
            (gp.quicksum(self.arc_vars[i, j, v] for v in self.vehicles for i in self.nodes if (i,j)  in self.arcs) 
            == 
            1
            for j in self.customers),
            name="visit_customers")

        # Flow conservation
        self.model.addConstrs(
            (gp.quicksum(self.arc_vars[i, j, v]  for i in self.nodes if (i,j)  in self.arcs) 
            ==
            gp.quicksum(self.arc_vars[j, i, v] for i in self.nodes if (j,i)  in self.arcs) 
            for j in self.customers for v in self.vehicles),
            name="flow_conservation")
        
        # Leave the depot
        self.model.addConstrs(
            (gp.quicksum(self.arc_vars[self.depot, j, v] for j in self.customers if (self.depot,j)  in self.arcs) 
            <=
            1
            for v in self.vehicles),
            name="leave_depot")
        
        # Capacity constraint
        self.model.addConstrs(
            (self.capacity_vars[j] 
            >=
            self.capacity_vars[i] + self.demand[j] - self.vehicles_capacity*(1 - gp.quicksum(self.arc_vars[i, j, v] for v in self.vehicles))
            for i in self.nodes for j in self.customers if (i,j)  in self.arcs),
            name="capacity_constraint")

    def set_time_limit(self,timeLimit):
        self.model.setParam('TimeLimit', timeLimit)

    def set_gap(self, gap):
        self.model.setParam('MIPGap', gap)

    def get_solution(self):
        if self.model.status == gp.GRB.OPTIMAL:
            return self._get_solution()
        else:
            return None
    
    def _get_solution(self):
        solution = {}
        solution["name"] = self.name
        solution["status"] = MSGDICT[self.model.status]
        solution["cost"] = self.model.objVal
        solution["routes"] = self._get_routes()
        return solution
    
    def _get_routes(self):
        routes = []
        for v in self.vehicles:
            routes.append(self._get_route(v))
        return routes
    
    def _get_route(self, v):
        route = []
        for i,j in self.arcs:
            if self.arc_vars[i,j,v].x > 0.5:
                route.append((i,j))
        return self.sort_route(route)
    
    def sort_route(self, route):

        def find(node, route):
            for n1, n2 in route:
                if n1 == node:
                    return (n1,n2)
            
        if route:
            first = self.depot
            i,j = find(first,route)
            sol = [i]
            while j != self.depot:
                i,j = find(j,route)
                sol.append( i )
            sol.append(self.depot)
            return sol
        else:
            return []
        
    def get_status(self):
        return MSGDICT[self.model.getAttr("Status")]
    
    def there_is_solution(self):
        return self.model.SolCount > 0