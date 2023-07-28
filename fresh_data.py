import re
import codecs
import json

t = ''
with codecs.open('result.txt', 'r') as the_file:
    for l in the_file:
        t += l


r = json.loads(t)
for i in r:
    print(i['value'])