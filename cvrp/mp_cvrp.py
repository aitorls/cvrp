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

class MP_CVRP():

    def __init__(self, name, customers, n_vehicles):

        self.name = name
        self.customers = customers
        self.n_vehicles = n_vehicles
        self.omega = []

        self.M = 10000
        self.time = 0

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

    def set_verbose(self, verbose):
        self.model.Params.LogToConsole = int(verbose)
    
    def set_time_limit(self,timeLimit):
        self.model.setParam('TimeLimit', timeLimit)

    def set_gap(self, gap):
        self.model.setParam('MIPGap', gap)

    def get_gap(self):
        return self.model.MIPGap
    
    def get_obj_val(self):
        return self.model.ObjVal #.getAttr("ObjVal")
    
    def get_time(self):
        return self.model.getAttr("Runtime") 
    
    def get_status(self):
        return MSGDICT[self.model.getAttr("Status")]
    
    def there_is_solution(self):
        return self.model.SolCount > 0

    def generate_vars(self): # Dummy Vars
        
        self.dummy_customers_vars = self.model.addVars(self.customers, vtype = gp.GRB.CONTINUOUS, name="dummy_customers")    # TODO: Remove vehicles
        self.dummy_vehicle_var = self.model.addVar( lb=0.0, ub=1.0, vtype = gp.GRB.CONTINUOUS, name="dummy_vehicle") 
    
    def generate_obj(self):

        self.model.update()
        cost_route = gp.quicksum( self.M*var for var in self.model.getVars() )
        self.model.setObjective(cost_route, gp.GRB.MINIMIZE)

    def generate_cons(self):
        
        # Visit each node once
        self.cts_veh_visits = self.model.addConstrs(
                                (self.dummy_customers_vars[i]
                                >=
                                1
                                for i in self.customers), 
                                name="visit_all")
        
        self.cts_veh = self.model.addConstr(
                        (self.dummy_vehicle_var
                        <= 
                        self.n_vehicles),
                        name="K-vehicles")    

    def get_duals(self):
        dual_customers = { i : self.cts_veh_visits[i].Pi for i in self.customers} 
        dual_vehicle = self.cts_veh.Pi
        return dual_customers, dual_vehicle
    
    def get_reduced_cost(self):
        pass    
    
    """
    def get_solution(self):
        if self.there_is_solution():
            return self._get_solution()
        else:
            #logger.warning("No solution found")
            return None
    
    def _get_solution(self):
        solution = {}
        solution["name"] = self.name
        solution["status"] = self.get_status()
        solution["cost"] = self.get_obj_val()
        solution["routes"] = self._get_routes()
        solution["gap"] = self.get_gap()
        solution["runtime"] = self.get_time()
        return solution
    
    def _get_routes(self):
        
        routes = []
        
        solution_arcs = [(i,j) for i,j in self.arcs if self.arc_vars[i,j].x > 0.5]
        init_routes = [(self.depot,j) for i,j in solution_arcs if i == self.depot] 

        for r in init_routes:
            routes.append(self._get_route(r, solution_arcs))
        return routes
    
    def _get_route(self, init_arc, solution_arcs ):

        def find(node, route):
            for n1, n2 in route:
                if n1 == node:
                    return (n1,n2)

        depot, j  = init_arc
        route = [depot]
        while j != self.depot:
            i,j = find(j, solution_arcs)
            route.append( i )

        route.append(self.depot)
        return route
    
        


    """