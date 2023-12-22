import os

dir_actual = os.getcwd()
dir_home, _ = os.path.split(dir_actual)

dir_data = os.path.join(dir_home, 'data')
dir_code = os.path.join(dir_home, 'cvrp')

dir_instances = os.path.join(dir_data, 'instances')
dir_solutions = os.path.join(dir_data, 'solutions')
dir_my_solutions = os.path.join(dir_data, 'my_solutions')

import sys
sys.path.append(dir_home)
from vrptw.gurobi_vrptw import VRPTW 
from utils.utils import save_solution

import vrplib
#import cvrp

# Main
if __name__ == '__main__':
    
    # Read instance
    instance_name = "R101.txt"    
    instance = vrplib.read_instance(f"{dir_instances}/{instance_name}", instance_format="solomon")

    # Solve
    prob = VRPTW(instance)
    prob.solve( timeLimit = 60*60 )
    my_solution = prob.get_solution()
    save_solution(dir_my_solutions, my_solution)