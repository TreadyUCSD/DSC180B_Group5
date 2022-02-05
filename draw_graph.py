#!/usr/bin/python

import os
import sys
import math
import networkx as nx
from matplotlib import pyplot as plt

sublist = ['neoprogs', 'moderatepolitics', 'politics', 'uspolitics', 'americanpolitics', 'republican',
            'Liberal', 'Conservative', 'Libertarian', 'Anarchism', 'socialism', 
            'progressive', 'liberty', 'alltheleft', 'blackflag', 'GreenParty', 
            'democracy', 'LibertarianSocialism', 'Capitalism', 'anarchist', 
            'republicans', 'democrats', 'communist', 'socialdemocracy', 
            'AnarchoPacifism', 'conservatives', 'republicanism', 'conspiracy']

def main(targets):
    file = targets[0]
    filename = file + '.edgelist'
    size_ratio = 2

    ignore_ones = False
    cutoff = 0
    if len(targets) > 1:
        ignore_ones = True
        cutoff = int(targets[1])

    os.chdir('..')
    cur_dir = os.getcwd()
    os.chdir(cur_dir + '/data') 

    G = nx.read_edgelist(filename, create_using = nx.MultiDiGraph)
    
    post_count = {}
    user_colors = {}
    for e in G.edges(data='weight', keys=True):
        #if e[0] in sublist:
           # G.remove_edge(e[0], e[1], key = e[2])
           # G.add_edge(e[0] + '1', e[1], key = e[2], weight = e[3])
        post_count[e[0]] = post_count.get(e[0], 0) + e[3]
        user_colors[e[0]] = max([user_colors.get(e[0], e[2]), e[2]])
    node_separate = {'subs': [], 'users' : [], 'colors': []}
    remove = []
    for n in G.nodes:
        if n in sublist:
            node_separate['subs'] += [n]
        else:
            if not ignore_ones:
                node_separate['users'] += [n]
                if user_colors[n] == 1:
                    node_separate['colors'] += ['#FF7F24']
                else:
                    node_separate['colors'] += ['#3D59AB']
            else:
                if post_count[n] > cutoff:
                    node_separate['users'] += [n]
                    if user_colors[n] == 1:
                        node_separate['colors'] += ['#FF7F24']
                    else:
                        node_separate['colors'] += ['#3D59AB']
                else:
                    remove += [n]

    if ignore_ones:
        G.remove_nodes_from(remove)
        size_ratio = 10
        

    pos =nx.spring_layout(G, k=0.1)

    node_sizes = [int(math.ceil(post_count[n]/size_ratio)) for n in node_separate['users']]
    node_colors = [0.5714285714285714 for n in node_separate['users']]
    s_node_sizes = [100 for n in node_separate['subs']]
    s_node_colors = [0.25 for n in node_separate['subs']]
    nx.draw_networkx_nodes(G, pos = pos, nodelist = node_separate['users'], node_size = node_sizes, node_color = node_separate['colors'], edgecolors='black', linewidths=0.5)
    nx.draw_networkx_nodes(G, pos = pos, nodelist = node_separate['subs'], node_size = s_node_sizes, node_color = 'maroon')

    edge_colors = {'edges': [], 'colors': []}
    for e in G.edges(keys=True):
        if e[0] in node_separate['users']:
            if e[2] == 0:
                if not G.has_edge(e[0], e[1], key = 1):
                    edge_colors['edges'] += [e]
                    edge_colors['colors'] += ['#3D59AB']
            elif e[2] == 1:
                edge_colors['edges'] += [e]
                edge_colors['colors'] += ['#FF7F24']

    nx.draw_networkx_edges(G, pos=pos, edgelist=edge_colors['edges'], edge_color=edge_colors['colors'], arrows=False, width = 0.5)
    
    sub_labels = {sub:sub for sub in sublist if sub in G.nodes}
    nx.draw_networkx_labels(G, pos = pos, labels = sub_labels, font_color = 'black', font_size = 7)
    plt.savefig('graph.png')




if __name__ == '__main__':
    targets = sys.argv[1:]
    main(targets)