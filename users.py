#!/usr/bin/python

import pandas as pd
import json
import os
import sys
import praw
import numpy as np

reddit = praw.Reddit(
    user_agent="Comment Extraction",
    client_id="T5Bw73pLWfu6AB-XSbgL9w",
    client_secret="FS4nDQl1e0FRLNZGW8MksOixcdlznA"
)

def get_author_name(full_link):
    submission = reddit.submission(url=full_link)
    if submission.author:
        author = submission.author.name
    else:
        author = np.nan
    return author

def main(targets):
    
    subredditList = targets
    chunksize = 100

    os.chdir('..')
    cur_dir = os.getcwd()
    os.chdir(cur_dir + '/data')

    for subreddit in subredditList:
        filename = str(subreddit) + '_users.csv'
        sub_file = os.getcwd() + '/' + str(subreddit) + '_posts.jsonl'
        header = True
        for chunk in pd.read_json(sub_file, lines=True, chunksize=chunksize):
            chunk['author'] = chunk['full_link'].apply(get_author_name)
            chunk.to_csv(path_or_buf=filename, columns=['full_link', 'url', 'author'], header=header, index=False, mode='a')
            header = False

if __name__ == '__main__':
    targets = sys.argv[1:]
    main(targets)