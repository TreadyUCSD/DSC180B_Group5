import os
import sys
import math
import networkx as nx
import json
import time


def main(targets):
    os.chdir('..')
    os.chdir('..')
    cur_dir = os.getcwd()
    os.chdir(cur_dir + '/data')

    subs_graph = nx.read_edgelist('misinformation_graph.edgelist', create_using = nx.MultiDiGraph) 
    subs_users = {}
    for e in subs_graph.edges:
        if e[1] not in subs_users:
            subs_users[e[1]] = set()
        subs_users[e[1]].add(e[0])

    user_graph = nx.Graph()
    sub_pairs = []
    #for n in subs_graph.nodes:
    #    if n not in subs_users:
    #        users += [n]
    #print('users list')
    subs = list(subs_users.keys())
    interactions = 0
    start = time.time()
    for s1 in subs:
        for s2 in subs:
            ints = subs_users[s1].intersection(subs_users[s2])
            interactions += len(ints)
            sub_pairs += [ints]
        print(str(time.time() - start) + '      ' + str(interactions))



            

    
    #G_k = nx.algorithms.core.k_core(user_graph)
    #main_core = max(nx.algorithms.core.core_number(G_k).values())
    #print(main_core)
                    


if __name__ == '__main__':
    targets = sys.argv[1:]
    main(targets)