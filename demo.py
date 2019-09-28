from   collections import Counter

a= open('./data/train.txt').read().split('\n\n')
b=[]
for each in a:
    b.append(len(each.split('\n')))
c= Counter(b)
d = []
for key,value in c.items():
    print(key)
    d.append((key,value))
d.sort()
a=1