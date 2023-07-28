import requests
import re
import time
import json
from bs4 import BeautifulSoup
g = set()

with open('urls.txt', 'r') as the_file:
    for line in the_file:
        g.add(line.rstrip())

result = []

all_size = len(g)
index = 0

for i in g: 
    u = f'https://guxiang.app/city-list/{i}'
    r = requests.get(u)
    s = BeautifulSoup(r.text, 'html.parser')
    a = s.find("div", {"class": "entry-content"})
    print(a.decode_contents())
    result.append({"key": i, "value": a.decode_contents()})
    time.sleep(1)

    index += 1
    print(f'all size {all_size} current index {index}')

v = json.dumps(result)
with open('result.txt', 'w', encoding='utf-8') as the_file:
    the_file.writelines(v)