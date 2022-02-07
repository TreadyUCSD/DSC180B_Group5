#!/usr/bin/python

import pandas as pd
import os
import sys
import networkx as nx




def misinfo_finder(post, links):
    url = post['url']
    over_url = post['url_overridden_by_dest']
    misinfo = False
    for link in links:
        if link in over_url:
            misinfo = True
            url = over_url
            break
        if link in url:
            misinfo = True
            break
    post_info = post[['author', 'url', 'subreddit']]
    post_info['misinfo'] = misinfo
    post_info['url'] = url
    return post_info

def updateGraph(post, graph):
    # determine if post is misinformation
    key = 0
    if post['misinfo']:
        key = 1
    # if edge exists, increment weight by one
    if graph.has_edge(post['author'], post['subreddit'], key = key):
        graph.edges[post['author'], post['subreddit'], key]['weight'] += 1
    # Add an edge from user to subreddit if it does not exist. with weight 0 and appropriate key (1 for misinfo, otherwise 0)
    else:
        graph.add_edge(post['author'], post['subreddit'], key, weight = 1)
    return post

def main(targets):

    misinfo = open('misinfo_sites.txt', 'r', encoding='utf-8')
    links = [i.strip() for i in misinfo]
    misinfo.close()
    subredditList = targets
    chunksize = 200

    G = nx.MultiDiGraph()

    os.chdir('..')
    cur_dir = os.getcwd()
    os.chdir(cur_dir + '/data')

    with open('subreddit_misinformation.csv', 'w') as f:
        f.write('Subreddit,Num_Posts,Num_Misinfo_Links\n')
        for subreddit in subredditList:
            G.add_node(subreddit)
            mis = 0
            num_posts = 0
            sub_file = os.getcwd() + '/' + str(subreddit) + '_posts.jsonl'
            for chunk in pd.read_json(sub_file, lines=True, chunksize=chunksize):
                posts = chunk.apply(misinfo_finder, axis= 1, links = links)
                mis += posts.misinfo.sum()
                num_posts += chunk.shape[0]
                posts.apply(updateGraph, axis=1, graph = G)
            f.write(subreddit + ',' + str(num_posts) + ',' + str(mis) + '\n')
    nx.write_edgelist(G, 'misinformation_graph.edgelist')

        

if __name__ == '__main__':
    targets = sys.argv[1:]
    main(targets)
