#!/usr/bin/python
from tracemalloc import start
import requests
import pandas as pd
from datetime import datetime
import json
import os
import sys



def df_from_response(res, endDate = 1609459199):
    df = pd.DataFrame()

    for post in res.json()['data']:
        if post['url'] != post['full_link'] and post['created_utc'] <= endDate:
            df = df.append({
                'subreddit': post['subreddit'],
                'title': post['title'],
                'selftext': post['selftext'],
                #'upvote_ratio': post['upvote_ratio'],
                'score': post['score'],
                'created_utc': post['created_utc'],
                'id': post['id'],
                'full_link': post['full_link'],
                'url': post['url'],
                #'url_overridden_by_dest': post['url_overridden_by_dest']
            }, ignore_index=True)

    return df

def main(targets):

    startDate = 1577836800
    endDate = 1609459199
    subredditList = targets

    # client_auth = requests.auth.HTTPBasicAuth('personal use token', 'secret token')
    # data = {
    #    'grant_type': 'password',
    #    'username': 'username',
    #    'password': 'password'
    #}

    # headers = {'User-Agent': 'myBot/0.0.1'}
    # res = requests.post('https://www.reddit.com/api/v1/access_token',
    #                    auth=client_auth, data=data, headers=headers)

    # TOKEN = f"bearer {res.json()['access_token']}"
    # headers = {**headers, **{'Authorization': TOKEN}}


    data = pd.DataFrame()
    params = {'size': 500}
    os.chdir('..')
    cur_dir = os.getcwd()
    os.chdir(cur_dir + '/data')


    for sub in subredditList:
        filename = str(sub) + '_posts.jsonl'
        with open(filename, 'w') as f:
            params['subreddit'] = sub
            params['after'] = startDate
            while params['after'] <= endDate:
                res = requests.get('https://api.pushshift.io/reddit/search/submission/', params=params)
                new_df = df_from_response(res)
                if new_df.shape[0] > 0:
                    row = new_df.iloc[len(new_df)-1]
                    params['after'] = int(row['created_utc'])
                    data = data.append(new_df, ignore_index=True)
                    length = data.shape[0]
                    if length >= 100000:
                        data_json = data.to_json(orient="records")
                        parsed = json.loads(data_json)
                        lines = json.dumps(parsed)
                        for line in lines:
                            f.write(line)
                            f.write('\n')
                        f.flush()
                        os.fsync(f.fileno())
                        data = pd.DataFrame()
                else: break
            data_json = data.to_json(orient="records")
            parsed = json.loads(data_json)
            for line in parsed:
                f.write(json.dumps(line))
                f.write('\n')
            f.flush()
            os.fsync(f.fileno())
            data = pd.DataFrame()

if __name__ == '__main__':
    targets = sys.argv[1:]
    main(targets)
                




