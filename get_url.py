import requests
import re
from bs4 import BeautifulSoup

index = 0

g = set()

while True:
    u = f'https://guxiang.app/filter-home/?query-10-page={index}'
    x = requests.get(u)
    s = set()
    index += 1
    if x.status_code != 200:
        raise f'error code : {x.status_code} {u}'
    print(x.text)
    for i in re.findall('city-list\/([\d|-]+)', x.text):
        print(i)
        s.add(i)

    g |= s
    if len(s) == 0:
        break


with open('urls.txt', 'a') as the_file:
    for i in g:
        the_file.write(f'{i}\n')
