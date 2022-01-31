#!/usr/bin/python
from tracemalloc import start
import requests
import pandas as pd
from datetime import datetime
import time
import json
import os
import sys



def df_from_response(res, endDate = 1640995199):
    df = pd.DataFrame()

    for post in res.json()['data']:
        if post['url'] != post['full_link'] and post['created_utc'] <= endDate:
            df = df.append({
                'subreddit': post['subreddit'],
                'title': post['title'],
                'selftext': post['selftext'],
                'score': post['score'],
                'created_utc': post['created_utc'],
                'id': post['id'],
                'full_link': post['full_link'],
                'url': post['url'],
                'upvote_ratio': 'NA',
                'url_overridden_by_dest': 'NA'
            }, ignore_index=True)
            if 'upvote_ratio' in post.keys():
                df.iat[len(df)-1, 8] = post['upvote_ratio']
            if 'url_overridden_by_dest' in post.keys():
                df.iat[len(df)-1, 9] = post['url_overridden_by_dest']

    return df

def main(targets):

    startDate = 1577836800
    endDate = 1640995199
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
            timeout = 0
            while params['after'] <= endDate:
                try:
                    res = requests.get('https://api.pushshift.io/reddit/search/submission/', params=params)
                    if res.status_code != 200:
                        tries = 0
                        while res.status_code != 200:
                            time.sleep(5)
                            res = requests.get('https://api.pushshift.io/reddit/search/submission/', params=params)
                            tries += 1
                            if tries >= 5:
                                raise Exception('Cannot resolve url: ' + res.url)
                    new_df = df_from_response(res)
                    if new_df.shape[0] > 0:
                        row = new_df.iloc[len(new_df)-1]
                        params['after'] = int(row['created_utc'])
                        data = data.append(new_df, ignore_index=True)
                        length = data.shape[0]
                        if length >= 15000:
                            data_json = data.to_json(orient="records")
                            parsed = json.loads(data_json)
                            for line in parsed:
                                f.write(json.dumps(line))
                                f.write('\n')
                            f.flush()
                            os.fsync(f.fileno())
                            data = pd.DataFrame()
                    else: break
                except:
                    timeout += 1
                    if timeout <= 5:
                        if data.shape[0] > 0:
                            row = data.iloc[len(data)-1]
                            params['after'] = int(row['created_utc'])
                        data_json = data.to_json(orient="records")
                        parsed = json.loads(data_json)
                        for line in parsed:
                            f.write(json.dumps(line))
                            f.write('\n')
                        f.flush()
                        os.fsync(f.fileno())
                        data = pd.DataFrame()
                        time.sleep(25)
                    else: 
                        raise Exception('Cannot resolve url: ' + res.url)
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
                




