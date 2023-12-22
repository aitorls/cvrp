from cvrp.centr_cvrp import CVRP
import vrplib

import os

dir_home = os.getcwd()
dir_data = os.path.join(dir_home, 'data')


class TestCVRP():
    
    def test_prueba(self):

        assert 0 == 0

    def test_cvrp(self):
        instance = vrplib.read_instance(f"{dir_data}/solomon_instances/R101.txt", instance_format="solomon")
        prob = CVRP(instance)
        assert prob != None