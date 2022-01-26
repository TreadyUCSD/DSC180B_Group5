#!/usr/bin/python

from tracemalloc import start
import requests
import pandas as pd
from datetime import datetime
import json
import os
import sys
import praw
import numpy as np

# reddit api authorization

reddit = praw.Reddit(
    user_agent="Comment Extraction",
    client_id="T5Bw73pLWfu6AB-XSbgL9w",
    client_secret="FS4nDQl1e0FRLNZGW8MksOixcdlznA"
)

def main(targets):

    subredditList = targets

    os.chdir('..')
    cur_dir = os.getcwd()
    os.chdir(cur_dir + '/data')

    for sub in subredditList:
        filename = str(sub) + '_comments.csv'
        subreddit = os.getcwd() + '/' + str(sub) + '_posts.jsonl'
        df = pd.read_json(subreddit, lines=True)
        comments = pd.DataFrame(columns = ['full_link', 'comment'])
        for full_link in df['full_link']:
            submission = reddit.submission(url=full_link)
            submission.comments.replace_more()
            for comment in submission.comments.list():
                comments = comments.append({'full_link': full_link, 'comment': comment.body}, ignore_index=True)
        comments.to_csv(filename)
    
if __name__ == '__main__':
    targets = sys.argv[1:]
    main(targets)