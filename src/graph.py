#!/usr/bin/python

import pandas as pd
import os
import sys
import networkx as nx



# determines if each link contains misinformation and outputs a new dataframe
def misinfo_finder(post, links):
    # checks url and url_overridden_by_dest against links to see if any urls 
    # are in the list of untrustworthy domains
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
    # returns a dataframe with author, url, subreddit, and whether the url contains misinfo
    post_info = post[['author', 'url', 'subreddit']]
    post_info['misinfo'] = misinfo
    post_info['url'] = url
    return post_info

# populates a graph with edges based on whether each post contains misinformation
def updateGraph(post, graph):
    # add (user) to end of author name if it is the same as the subreddit name
    auth = post['author']
    sub = post['subreddit']
    if auth == sub:
        auth = auth + '(user)'
    # determine if post is misinformation
    key = 0
    if post['misinfo']:
        key = 1
    # if edge exists, increment weight by one
    if graph.has_edge(auth, sub, key = key):
        graph.edges[auth, sub, key]['weight'] += 1
    # Add an edge from user to subreddit if it does not exist. with weight 0 and appropriate key (1 for misinfo, otherwise 0)
    else:
        graph.add_edge(auth, sub, key, weight = 1)
    return post

# generates a csv and graph containing information on misinformation in posts
def generate_graphs(subs, test = False):

    # load list of untrustworthy domains into links 
    cur_dir = os.getcwd()
    os.chdir(cur_dir + '/src')
    misinfo = open('misinfo_sites.txt', 'r', encoding='utf-8')
    links = [i.strip() for i in misinfo]
    misinfo.close()
    subredditList = subs
    chunksize = 200

    # initialize the graph
    G = nx.MultiDiGraph()
    if test:
        # change directory to test directory if test
        os.chdir('..')
        cur_dir = os.getcwd()
        os.chdir(cur_dir + '/test/testdata')
        # open test csv to write based off of test data
        with open('test_misinformation.csv', 'w') as f:
            f.write('Subreddit,Num_Posts,Num_Misinfo_Links\n')
            # open test file as a dataframe
            test_file = os.getcwd() + '/test.jsonl'
            for chunk in pd.read_json(test_file, lines=True, chunksize=chunksize):
                # gather misinfo data on each post and populate the graph
                posts = chunk.apply(misinfo_finder, axis= 1, links = links)
                posts.apply(updateGraph, axis=1, graph = G)
                sub_info = {}
                # fill a dictionary with total misinformation and total posts for each subreddit based off the graph
                for e in G.edges(data='weight', keys=True):
                    if e[1] not in list(sub_info.keys()):
                        sub_info[e[1]] = [0,0]
                    sub_info[e[1]][0] += e[3]
                    if e[2] == 1:
                        sub_info[e[1]][1] += e[3]
                #write data for each subreddit to csv
                for subreddit in list(sub_info.keys()):
                    f.write(subreddit + ',' + str(sub_info[subreddit][0]) + ',' + str(sub_info[subreddit][1]) + '\n')
        print('Generated test CSV')
        nx.write_edgelist(G, 'test_graph.edgelist')
        print('Generated test graph edgelist')


    else:
        #if not test, open data directory 
        os.chdir('..')
        os.chdir('..')
        cur_dir = os.getcwd()
        os.chdir(cur_dir + '/data')

        #write to csv
        with open('subreddit_misinformation.csv', 'w') as f:
            f.write('Subreddit,Num_Posts,Num_Misinfo_Links\n')
            #iterate over subreddits
            for subreddit in subredditList:
                #add a node for the subreddit in the graph 
                G.add_node(subreddit)
                mis = 0
                num_posts = 0
                # open the file for the subreddit in chunks as a dataframe
                sub_file = os.getcwd() + '/' + str(subreddit) + '_posts.jsonl'
                for chunk in pd.read_json(sub_file, lines=True, chunksize=chunksize):
                    # gather misinfo data on each post and add total posts and total misinfo
                    posts = chunk.apply(misinfo_finder, axis= 1, links = links)
                    mis += posts.misinfo.sum()
                    num_posts += chunk.shape[0]
                    #populate graph
                    posts.apply(updateGraph, axis=1, graph = G)
                # write misinformation data to csv for the subreddit
                f.write(subreddit + ',' + str(num_posts) + ',' + str(mis) + '\n')
        # if there is only a misinformation edge for a user, add a fact edge with a weight of 0
        for e in G.edges(keys=True):
            if e[2] == 1:
                if not G.has_edge(e[0], e[1], key = 0):
                    G.add_edge(e[0], e[1], 0, weight = 0)

        nx.write_edgelist(G, 'misinformation_graph.edgelist')

        
def main(targets):
    generate_graphs(targets)

if __name__ == '__main__':
    targets = sys.argv[1:]
    main(targets)
