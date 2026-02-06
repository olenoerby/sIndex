import requests, datetime
url='https://old.reddit.com/r/wowthissubexists/comments/1ktb9i2/.json'
headers={'User-Agent':'backfill-script/0.1'}
r=requests.get(url,headers=headers,timeout=20)
print('GET',url,'status',r.status_code)
if r.status_code==200:
    payload=r.json()
    try:
        post=payload[0]['data']['children'][0]['data']
        ts=post.get('created_utc')
        print('id',post.get('id'),'title',post.get('title'))
        print('created_utc',ts,datetime.datetime.utcfromtimestamp(ts))
    except Exception as e:
        print('parse error',e)
