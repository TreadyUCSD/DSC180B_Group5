#!/usr/bin/python

import pandas as pd
import json
import os
import sys
import numpy as np
import requests
import networkx as nx




def misinfo_finder(post, links):
    url = post['url']
    misinfo = False
    for link in links:
        if link in url:
            misinfo = True
    post_info = post[['author', 'url', 'subreddit']]
    post_info['misinfo'] = misinfo
    post_info['url'] = url
    return post_info

def main(targets):

    misinfo = open('misinfo_sites.txt', 'r', encoding='utf-8')
    links = [i.strip() for i in misinfo]
    subredditList = targets
    chunksize = 5

    os.chdir('..')
    cur_dir = os.getcwd()
    os.chdir(cur_dir + '/data')

    for subreddit in subredditList:
        mis = 0
        sub_file = os.getcwd() + '/' + str(subreddit) + '_posts.jsonl'
        for chunk in pd.read_json(sub_file, lines=True, chunksize=chunksize):
            posts = chunk.apply(misinfo_finder, axis= 1, links = links)
            mis += posts.misinfo.sum()

        
        

            
           

if __name__ == '__main__':
    targets = sys.argv[1:]
    main(targets)
