#!/usr/bin/python

import os
import sys
import math
import networkx as nx
from matplotlib import pyplot as plt

sublist = ['alltheleft', 'AmericanPolitics', 'Anarchism', 'Anarchist', 'AnarchoPacifism', 
            'blackflag',  'Capitalism', 'Communist', 'Conservative', 'conservatives', 
            'conspiracy', 'democracy','democrats', 'GreenParty', 'Liberal', 'Libertarian',
            'LibertarianSocialism', 'Liberty', 'moderatepolitics', 'neoprogs', 'politics', 
            'progressive','republicanism', 'Republican', 'republicans', 'SocialDemocracy',
            'socialism', 'uspolitics']

def draw(file, cutoff = 0, size_ratio = 2, test = False):
    # add file type to file
    filename = file + '.edgelist'

    # go to correct directory based on test
    if not test: 
        os.chdir('..')
        os.chdir('..')
        cur_dir = os.getcwd()
        os.chdir(cur_dir + '/data') 

    # create graph from edgelist
    G = nx.read_edgelist(filename, create_using = nx.MultiDiGraph)
    
    # create dictionaries to store number of posts per user and color per user 
    post_count = {}
    user_colors = {}
    deleted = {'mis': 0, 'fact': 0}
    for e in G.edges(data='weight', keys=True):
        if e[0] == '[deleted]':
            if e[2] == 1:
                deleted['mis'] += e[3]
            else:
                deleted['fact'] += e[3]
        #if e[0] in sublist:
           # G.remove_edge(e[0], e[1], key = e[2])
           # G.add_edge(e[0] + '1', e[1], key = e[2], weight = e[3])
        # add number of posts stored in weight to each user in dict
        post_count[e[0]] = post_count.get(e[0], 0) + e[3]
        # set value of user to 1 in color dictionary if they have shared misinformation, else 0
        user_colors[e[0]] = max([user_colors.get(e[0], e[2]), e[2]])
    # create dictionary to store sub nodes, user nodes, and colors for user nodes
    node_separate = {'subs': [], 'users' : [], 'colors': []}
    # create list of nodes to remove
    remove = []
    for n in G.nodes:
        # populate subs list with sub nodes
        if n in sublist:
            node_separate['subs'] += [n]
        else:
            if n == '[deleted]':
                remove += [n]
            # add user to users list if it meets the cutoff, otherwise add them to list to remove
            if post_count[n] > cutoff:
                node_separate['users'] += [n]
                # add color of the user to colors list based on if they have shared misinfo
                if user_colors[n] == 1:
                    # orange for users who have shared misinfo
                    node_separate['colors'] += ['#FF7F24']
                else:
                    # blue for users who have not
                    node_separate['colors'] += ['#3D59AB']
            else:
                remove += [n]
    
    print(deleted)

    #remove nodes from graph
    if len(remove) > 0:
        G.remove_nodes_from(remove)
        
    # set positions for nodes 
    pos =nx.spring_layout(G, k=0.3)

    # set the size of each node using the size ratio in params so each node is proportional to total posts by user, with sub sizes constant
    node_sizes = [int(math.ceil(post_count[n]/size_ratio)) for n in node_separate['users']]
    s_node_sizes = [100 for n in node_separate['subs']]
    # draw user and sub nodes with predetermined sizes and colors
    nx.draw_networkx_nodes(G, pos = pos, nodelist = node_separate['users'], node_size = node_sizes, node_color = node_separate['colors'], edgecolors='black', linewidths=0.5)
    nx.draw_networkx_nodes(G, pos = pos, nodelist = node_separate['subs'], node_size = s_node_sizes, node_color = 'maroon')

    # determine color of edges using same metric as users
    edge_colors = {'edges': [], 'colors': []}
    for e in G.edges(keys=True):
        # only save edges for users that are drawn
        if e[0] in node_separate['users']:
            if e[2] == 0:
                # only store one copy of each edge, if there is a misinformation edge do not store non-misinformation edge for user, sub edge
                if not G.has_edge(e[0], e[1], key = 1):
                    edge_colors['edges'] += [e]
                    edge_colors['colors'] += ['#3D59AB']
            elif e[2] == 1:
                edge_colors['edges'] += [e]
                edge_colors['colors'] += ['#FF7F24']

    # draw only the required edges with the predetermined colors
    nx.draw_networkx_edges(G, pos=pos, edgelist=edge_colors['edges'], edge_color=edge_colors['colors'], arrows=False, width = 0.5)
    
    #label sub nodes
    sub_labels = {sub:sub for sub in sublist if sub in G.nodes}
    nx.draw_networkx_labels(G, pos = pos, labels = sub_labels, font_color = 'black', font_size = 7)
    if test:
        plt.savefig('test_graph.svg', format = 'svg', dpi = 300)
    else:
        plt.savefig('graph.svg', format = 'svg', dpi = 300)

def main(targets):
    file = targets[0]
    cutoff = 0
    size_ratio = 2
    if len(targets) > 1:
        cutoff = int(targets[1])
    if len(targets) > 2:
        size_ratio = int(targets[2])
    draw(file, cutoff=cutoff, size_ratio=size_ratio)


if __name__ == '__main__':
    targets = sys.argv[1:]
    main(targets)