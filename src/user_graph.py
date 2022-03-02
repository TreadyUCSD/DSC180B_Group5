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
    users = []
    for n in subs_graph.nodes:
        if n not in subs_users:
            users += [n]
    print('users list')
    for i in range(len(users)):
        for j in range(i+1, len(users)):
            count = 0
            for sub in subs_users:
                if users[i] in subs_users[sub] and users[j] in subs_users[sub]:
                    count += 1
                if count >= 2:
                    user_graph.add_edge(users[i], users[j])
                    break
        if i % 1000 == 0:
            print(str(i) + '/' + str(len(users)))

            

    
    G_k = nx.algorithms.core.k_core(user_graph)
    main_core = max(nx.algorithms.core.core_number(G_k).values())
    print(main_core)
                    


if __name__ == '__main__':
    targets = sys.argv[1:]
    main(targets)