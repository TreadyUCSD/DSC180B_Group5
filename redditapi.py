import requests
import pandas as pd
from datetime import datetime

def df_from_response(res):
    df = pd.DataFrame()

    for post in res.json()['data']['children']:
        df = df.append({
            'subreddit': post['data']['subreddit'],
            'title': post['data']['title'],
            'selftext': post['data']['selftext'],
            'upvote_ratio': post['data']['upvote_ratio'],
            'ups': post['data']['ups'],
            'downs': post['data']['downs'],
            'score': post['data']['score'],
            'link_flair_css_class': post['data']['link_flair_css_class'],
            'created_utc': datetime.fromtimestamp(post['data']['created_utc']).strftime('%Y-%m-%dT%H:%M:%SZ'),
            'id': post['data']['id'],
            'kind': post['kind']
        }, ignore_index=True)

    return df

client_auth = requests.auth.HTTPBasicAuth('personal use token', 'secret token')
data = {
    'grant_type': 'password',
    'username': 'username',
    'password': 'password'
}

headers = {'User-Agent': 'myBot/0.0.1'}
res = requests.post('https://www.reddit.com/api/v1/access_token',
                    auth=client_auth, data=data, headers=headers)

TOKEN = f"bearer {res.json()['access_token']}"
headers = {**headers, **{'Authorization': TOKEN}}


data = pd.DataFrame()
params = {'limit': 100}

for i in range(3):
    res = requests.get("https://oauth.reddit.com/r/demsocialist/new",
                       headers=headers,
                       params=params)


    new_df = df_from_response(res)
    row = new_df.iloc[len(new_df)-1]
    fullname = row['kind'] + '_' + row['id']
    params['after'] = fullname
    
    data = data.append(new_df, ignore_index=True)