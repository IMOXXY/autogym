import re
f = open('/home/imoxxy/all git/git practice/GymAutoBook/gym_auto_book.py', 'r', encoding='utf-8')
c = f.read()
f.close()
m = re.search(r'football.*', c)
print(repr(m.group()))
