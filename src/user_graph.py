import os
import sys
import math
import networkx as nx
import json


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
    for sub in subs_users:
        for u1 in subs_users[sub]:
            for u2 in subs_users[sub]:
                if u1 == u2:
                    continue
                if user_graph.has_edge(u1, u2):
                    break
                for sub2 in subs_users:
                    if sub == sub2:
                        continue
                    if u1 in subs_users[sub2] and u2 in subs_users[sub2]:
                        user_graph.add_edge(u1,u2)
                        break
    
    G_k = nx.algorithms.core.k_core(user_graph)
    main_core = max(nx.algorithms.core.core_number(G_k).values())
    print(main_core)
                    


if __name__ == '__main__':
    targets = sys.argv[1:]
    main(targets)