import os
import sys
import math
import networkx as nx
import json


def main(targets):

    G = nx.read_edgelist('misinformation_graph.edgelist', create_using = nx.MultiDiGraph) 
    post_count = {}
    for e in G.edges(data='weight', keys=True):
        post_count[e[0]] = post_count.get(e[0], 0) + e[3]
    remove = []
    for u in post_count:
        if post_count[u] < 10:
            remove += [u]
    G.remove_nodes_from(remove)
    remove = []
    sub_count = {}
    for e in G.edges:
        if e[0] not in sub_count:
            sub_count[e[0]] = []
        if e[1] not in sub_count[e[0]]:
            sub_count[e[0]] += [e[1]]
    for u in sub_count:
        if len(sub_count[u]) < 2:
            remove += [u]
    G.remove_nodes_from(remove)
    subs_users = {}
    for e in G.edges:
        if e[1] not in subs_users:
            subs_users[e[1]] = set()
        subs_users[e[1]].add(e[0])

    user_graph = nx.Graph()
    users = []
    for n in G.nodes:
        if n not in subs_users:
            users += [n]
    print('users')
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
    nx.write_edgelist(G_k, 'k-core.edgelist')
                    


if __name__ == '__main__':
    targets = sys.argv[1:]
    main(targets)