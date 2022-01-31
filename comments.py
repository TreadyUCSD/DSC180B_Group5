#!/usr/bin/python

import pandas as pd
import json
import os
import sys
import praw
import numpy as np
import itertools

# reddit api authorization

reddit = praw.Reddit(
    user_agent="Comment Extraction",
    client_id="T5Bw73pLWfu6AB-XSbgL9w",
    client_secret="FS4nDQl1e0FRLNZGW8MksOixcdlznA"
)

# get top level comments from link 

def get_comments(full_link):
    submission = reddit.submission(url=full_link)
    submission.comments.replace_more()
    bodies = [comment.body for comment in submission.comments]
    return bodies

def main(targets):

    subredditList = targets
    chunksize = 500

    os.chdir('..')
    cur_dir = os.getcwd()
    os.chdir(cur_dir + '/data')

    for subreddit in subredditList:
        filename = str(subreddit) + '_comments.csv'
        sub_file = os.getcwd() + '/' + str(subreddit) + '_posts.jsonl'
        header = True
        for chunk in pd.read_json(sub_file, lines=True, chunksize=chunksize):
            temp = chunk['full_link'].apply(get_comments)
            lens = temp.map(len)
            idx = np.repeat(lens.index, lens.values)
            comments_exp = list(itertools.chain.from_iterable(temp.values))
            s = pd.Series(comments_exp, index=idx)
            s.name = 'comment'
            comments = chunk.join(s, how='inner')[['full_link', 'comment']].reset_index(drop=True)
            comments.to_csv(filename, header=header, index=False, mode='a')
            header = False
    
if __name__ == '__main__':
    targets = sys.argv[1:]
    main(targets)
