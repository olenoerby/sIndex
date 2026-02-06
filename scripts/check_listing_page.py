import requests
from bs4 import BeautifulSoup

url='https://old.reddit.com/r/wowthissubexists/?count=100&after=t3_1kxafjn'
headers={'User-Agent':'backfill-script/0.1'}
print('GET',url)
r=requests.get(url,headers=headers,timeout=20)
print('status',r.status_code)
soup=BeautifulSoup(r.text,'html.parser')
things=soup.find_all('div',class_='thing')
print('thing count',len(things))
search_id='1ktb9i2'
search_found=False
for i,div in enumerate(things,1):
    fullname=div.get('data-fullname') or div.get('data-name') or ''
    a=div.find('a',class_='title')
    title=(a.get_text() if a else '').strip()
    href=(a.get('href') if a else '')
    print(i, 'fullname=',fullname,'id_in_href=', '1ktb9i2' in (href or ''), 'title=',title[:120])
    if search_id in fullname or '1ktb9i2' in (href or '') or 'May 23, 2025' in title:
        search_found=True
        print('MATCH FOUND at item',i)

print('Search found?',search_found)
