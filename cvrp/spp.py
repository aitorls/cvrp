import numpy as np

class Label:
    def __init__(self, node, res, weight, time_stamp, previous_label):
        self.node = node
        self.res = res
        self.weight = weight
        self.time_stamp = time_stamp
        self.previous_label = previous_label

    def print_path(self):
        if self.previous_label != None:
            self.previous_label.print_path()
            print (' --> ')
        print(self.node + ' ' + str(self.res) + ' ' + str(self.weight))

    def get_path(self):
        if self.previous_label == None:
            return [self.node]
        else:
            path = self.previous_label.get_path()
            path.append(self.node)
            return path
        
    def get_str_path(self):
        if self.previous_label == None:
            return [str(self.node)]
        else:
            path = self.previous_label.get_str_path()
            path.append(str(self.node))
            return path
        
    def get_timing_path(self):
        if self.previous_label == None:
            return { self.node : self.res[1] } # 1 is timing
        else:
            path = self.previous_label.get_timing_path()
            path = path |  {self.node : self.res[1] }
            return path
    
    def print_label(self):
        return f"node: {self.node}, res: {self.res}, weight: {self.weight}, path: {self.get_str_path()}"


class Heurisitcs_SPPRC:

    def __init__(self, G):
        
        self.G = G
        self.time_stamp = 0
        self.n_res = self.G.graph['n_res']
        self.labels = {n : [] for n in list(self.G.nodes)}
        self.EPS = 0.0001

        self.dominates = self.dominates_best_weight_strict


    def new_label(self, node, previous_label=None):
        
        # FORBID CYCLES
        label = previous_label
        while label != None:
            if label.node == node:
                return None
            label = label.previous_label

        res = []
        weight = 0
        if previous_label == None:
            res = [0 for _ in range(self.n_res)]
        else:
            res = [previous_label.res[r] for r in range(self.n_res)]
            edge = self.G.edges[previous_label.node, node]
            weight = previous_label.weight + edge['weight']

            for r in range(self.n_res):
                res[r] += edge['res_cost'][r]
                if 'res_max' in self.G.nodes[node]:
                    if res[r] > self.G.nodes[node]['res_max'][r]:
                        return None
                if 'res_min' in self.G.nodes[node]:
                    if res[r] < self.G.nodes[node]['res_min'][r]:
                        res[r] = self.G.nodes[node]['res_min'][r]

        return Label(node, res, weight, self.time_stamp, previous_label)


    def dominates_best_weight(self, label1, label2):
        if label1.weight < label2.weight:  #TODO: <=
            return True
        return False
    
    def dominates_best_weight_strict(self, label1, label2):
        if label1.weight < label2.weight:
            return True
        return False
    
    def dominates_resources(self, label1, label2):
        if label1.weight < label2.weight:
            return True
        if label1.weight <= label2.weight and all(label1.res[r] <= label2.res[r] for r in range(self.n_res)):
            return True
        return False

    def dominate_length(self, label1, label2):
        if label1.weight <= label2.weight and label1.res[0] <= label2.res[0]: #LENGTH
            return True
        return False
    
    def dominate_strict(self, label1, label2):
        if self.n_res >= 3:
            if label1.weight <= label2.weight and label1.res[2] <= label2.res[2]: #CAPACITY
                return True
        else:
            if label1.weight <= label2.weight: # VEHICLES DONT HAVE CAPACITY
                return True
        #if label1.weight < label2.weight and all(label1.res[r] < label2.res[r] for r in range(self.n_res)):
        #    return True
        return False

    def solve(self, start, end, warm_start= None):
        self.time_stamp = 0
        self.labels = {n : [] for n in list(self.G.nodes)}
        label = self.new_label(start, None)
        self.labels[start].append(label)
        new_labels = [label]
        labels = new_labels
        
        while len(labels) > 0:
            new_labels = []
            for previous_label in labels:
                #print("Generation label ",previous_label.print_label())
                from_node = previous_label.node
                for to_node, datadict in self.G.adj[from_node].items():
                    
                    new_label = self.new_label(to_node, previous_label)
                    

                    if new_label == None:
                        continue
                    #print(new_label.print_label())
                    

                    dominates = False
                    if len (self.labels[to_node]) == 0 or to_node == end:
                        dominates = True
                    else:
                        for label in self.labels[to_node]:
                            
                            if self.dominates_best_weight(new_label, label):
                                if self.dominates(new_label, label):
                                    # remove label
                                    if label.time_stamp == self.time_stamp and to_node != end:
                                        # also remove from new
                                        new_labels.remove(label)
                                    self.labels[to_node].remove(label)
                                dominates = True
                    if dominates:
                        self.labels[to_node].append(new_label)
                        if to_node!=end:
                            new_labels.append(new_label)
            
            self.time_stamp += 1
            labels = new_labels
            #[ print(l.print_label())  for l in new_labels ]
            #print("HOli")

    def get_solution_paths(self, end, K=None):
        #TODO K bests
        all_paths = [ (l.weight, l.get_path()) for l in self.labels[end] if l.weight <= -self.EPS ]
        if K:
            sorted_K_paths = sorted(all_paths, key=lambda w_path: w_path[0])[:K]
            return [p for _,p in sorted_K_paths]
        
        return [ l.get_path() for l in self.labels[end] if l.weight <= -self.EPS ]
    
    def get_solution_timing_paths(self, end):

        return [ l.get_timing_path() for l in self.labels[end] if l.weight <= -self.EPS ]
    
    def create_path(self, path):
        prev_label = None
        for n in path:
            prev_label = self.new_label(n, prev_label)
        return prev_label
    
 
# TODO
class Label_ESPPRC:
    def __init__(self, node, res, weight, time_stamp, previous_nodes, previous_label):
        self.node = node
        self.res = res
        self.weight = weight
        self.time_stamp = time_stamp
        self.previous_nodes = previous_nodes
        self.previous_label = previous_label

    def print_path(self):
        if self.previous_label != None:
            self.previous_label.print_path()
            print (' --> ')
        print(self.node + ' ' + str(self.res) + ' ' + str(self.weight))

    def get_path(self):
        if self.previous_label == None:
            return [self.node]
        else:
            path = self.previous_label.get_path()
            path.append(self.node)
            return path
        
    def get_prev_nodes(self):
        return self.previous_nodes
    
    def get_timing_path(self):
        if self.previous_label == None:
            return { self.node : self.res[1] } # 1 is timing
        else:
            path = self.previous_label.get_timing_path()
            path = path |  {self.node : self.res[1] }
            return path


class ESPPRC:
    def __init__(self, G):
        self.G = G
        self.time_stamp = 0
        self.n_res = self.G.graph['n_res']
        self.labels = {n : [] for n in list(self.G.nodes)}
        self.EPS = 0.001

    def new_label(self, node, previous_label=None):
        # FORBID CYCLES
        if previous_label and node in previous_label.previous_nodes:
            return None
            
        res = []
        weight = 0
        if previous_label == None:
            res = [0 for r in range(self.n_res)]
            set_nodes = set()
            set_nodes.add(node)
        else:
            res = [previous_label.res[r] for r in range(self.n_res)]
            edge = self.G.edges[previous_label.node, node]
            set_nodes = set(previous_label.previous_nodes)
            set_nodes.add(node)
            #weight = previous_label.weight + edge['weight']
            weight = previous_label.weight + edge['weight']
            
            for r in range(self.n_res):
                res[r] += edge['res_cost'][r]
                if 'res_max' in self.G.nodes[node]:
                    if res[r] > self.G.nodes[node]['res_max'][r]:
                        return None
                if 'res_min' in self.G.nodes[node]:
                    if res[r] < self.G.nodes[node]['res_min'][r]:
                        res[r] = self.G.nodes[node]['res_min'][r]

        return Label_ESPPRC(node, res, weight, self.time_stamp, set_nodes, previous_label)
    
    def is_dominated(self, label1, label2):
        if  label2.previous_nodes <= label1.previous_nodes:
            if all(label2.res[r] <= label1.res[r] for r in range(self.n_res)) and label2.weight <= label1.weight:
                return True
        return False
    
    def warm_label(self, node, warm_start):

        weight = 0
        res = warm_start[1:]
        
        return Label_ESPPRC(node, res, weight, 0, {node}, None)

        
    def solve(self, start, end, warm_start= None):
        self.time_stamp = 0
        self.labels = {n : [] for n in list(self.G.nodes)}
        if not warm_start:
            label = self.new_label(start, None)
        else:
            label = self.warm_label(start, warm_start)
        self.labels[start].append(label)
        new_labels = [label]
        labels = new_labels
        while len(labels) > 0:
            new_labels = []
            for previous_label in labels:
                from_node = previous_label.node
                for to_node, datadict in self.G.adj[from_node].items():
                    new_label = self.new_label(to_node, previous_label)
                    if new_label == None:
                        continue

                    dominates = False
                    if len (self.labels[to_node]) == 0:
                        dominates = True
                    else:
                        for label in self.labels[to_node]:
                            if self.is_dominated(new_label, label):
                                dominates = False
                            elif self.is_dominated(label, new_label):
                                # remove label
                                if label.time_stamp == self.time_stamp and to_node != end:
                                    # also remove from new
                                    new_labels.remove(label)
                                self.labels[to_node].remove(label)
                                dominates = True
                            else:
                                dominates = True
                    if dominates:
                        self.labels[to_node].append(new_label)
                        if to_node!=end:
                            new_labels.append(new_label)

            self.time_stamp += 1
            labels = new_labels
            #print (f'Iteration {self.time_stamp} found {len(labels)} new labels')
            #for n in self.labels:
            #    print("NODE {} number of labels {}".format(n, len(self.labels[n])))
            #    for i,l in enumerate(self.labels[n]):
            #        print("Label {}".format(i))
            #        l.print_path()
            #if self.time_stamp == 2:
            #    break
    def get_solution_paths(self, end, K):

        return [ l.get_path() for l in self.labels[end] if l.weight <= -self.EPS ]       

    def create_path(self, path):
        prev_label = None
        for n in path:
            prev_label = self.new_label(n, prev_label)
        return prev_label
    


class ESPPRC_2:
    def __init__(self, G):
        self.G = G
        self.time_stamp = 0
        self.n_res = self.G.graph['n_res']
        self.labels = {n : [] for n in list(self.G.nodes)}
        self.EPS = 0.0001
        #self.F = {e : [] for e in list(self.G.edges)}
        
    def succ(self, from_node):
        return self.G.adj[from_node].items()
    
    def extend(self, node, previous_label=None):

        res = [previous_label.res[r] for r in range(self.n_res)]
        edge = self.G.edges[previous_label.node, node]

        set_nodes = previous_label.previous_nodes.copy()
        
        set_nodes.add(node)
        weight = previous_label.weight + edge['weight']
        
        for r in range(self.n_res):
            res[r] += edge['res_cost'][r]
            if 'res_max' in self.G.nodes[node]:
                if res[r] > self.G.nodes[node]['res_max'][r]:
                    return None
            if 'res_min' in self.G.nodes[node]:
                if res[r] < self.G.nodes[node]['res_min'][r]:
                    res[r] = self.G.nodes[node]['res_min'][r]

        if node != "Sink":
            #Explore unreachable nodes
            prev_set_nodes = set_nodes.copy()
            for unreachablenode in set(self.G.nodes) - prev_set_nodes:
            
                if (node, unreachablenode) in self.G.edges:
                    edge = self.G.edges[node, unreachablenode]
                    for r in range(self.n_res):
                        if 'res_max' in self.G.nodes[unreachablenode]:
                            if res[r] + edge['res_cost'][r] > self.G.nodes[unreachablenode]['res_max'][r]:
                                set_nodes.add(unreachablenode)


        return Label_ESPPRC(node, res, weight, self.time_stamp, set_nodes, previous_label)
    
    def eff(self, labels):
        nondominated_labels = []
        for l1 in labels:
            nondominated = True
            for l2 in labels:
                if l1 != l2:
                    if self.dominates(l2,l1): #If l2 no domina a l1
                        nondominated = False
                        break
            if nondominated:
                nondominated_labels.append(l1)
                    
        return nondominated_labels

        
    def dominates(self, label1, label2):
        if label1.previous_nodes <= label2.previous_nodes:
            #if all(label1.res[r] <= label2.res[r] for r in range(self.n_res)) and label1.weight <= label2.weight and label1.time_stamp <= label2.time_stamp:
            if all(label1.res[r] <= label2.res[r] for r in range(self.n_res)) and label1.weight <= label2.weight:
                if label1.time_stamp <= label2.time_stamp:
                    return True
                elif any(label1.res[r] < label2.res[r] for r in range(self.n_res)) or label1.weight < label2.weight:
                    return True
        return False
    

    def warm_label(self, node, warm_start):

        weight = 0
        res = warm_start[1:]
        
        return Label_ESPPRC(node, res, weight, self.time_stamp, set([node]), None)
                
    
    def solve(self, start, end,  warm_start= None):
        self.time_stamp = 0
        self.labels = {n : [] for n in list(self.G.nodes)}

        if not warm_start:
            start_label = Label_ESPPRC(start, [0 for r in range(self.n_res)], 0, self.time_stamp, set([start]), None)
        else:
            start_label = self.warm_label(start, warm_start)
        
        self.labels[start].append(start_label)
        len_prev_n_labels = sum([len(self.labels[k]) for k in list(self.G.nodes)])
        E = set([start])
        while len(E) > 0:
            
            v_i = E.pop()
            #print(v_i)
            #print(E)
            for v_j, data in self.succ(v_i):
                Fij = []
                for label in self.labels[v_i]:
                    if v_j not in label.previous_nodes:
                        new_Fij_label = self.extend(v_j, label)
                        if new_Fij_label:
                            Fij.append(new_Fij_label)


                previous_labels_j = len(self.labels[v_j])
                #print("labels {}".format(v_j))
                #[ l.print_path() for l in self.labels[v_j] if l.weight <= -self.EPS ]    
                #print("Fij {}".format(v_j))
                #[ l.print_path() for l in Fij if l.weight <= -self.EPS ] 
                
                self.labels[v_j] = self.eff(Fij+self.labels[v_j])

                #print("Fusion labels {}".format(v_j))
                #[ l.print_path() for l in self.labels[v_j] if l.weight <= -self.EPS ]

                if len(self.labels[v_j]) != previous_labels_j:
                    #print(len(self.labels[v_j]) - previous_labels_j)
                    E.add(v_j)
                    
            #E.discard(v_i)
            self.time_stamp += 1
            #len_n_labels = sum([len(self.labels[k]) for k in list(self.G.nodes)])
            #print (f'Iteration {self.time_stamp} found {len_n_labels-len_prev_n_labels} new labels')

        
    def get_solution_paths(self, end, K):
        return [ l.get_path() for l in self.labels[end] if l.weight <= -self.EPS ]   
    
    def create_path(self, path):
        prev_label = None
        for n in path:
            prev_label = self.new_label(n, prev_label)
        return prev_label