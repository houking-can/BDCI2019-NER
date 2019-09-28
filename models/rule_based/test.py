lines = open('./res_without_filter.csv',encoding='utf-8').read().split()
tmp = []
tmp.append(lines[0])
for line in lines[1:]:
    line = line.strip(';')
    try:
        id,entity = line.split(',')
        entity = entity.split(';')
    except:
        continue
    a=[]
    for each in entity:
        each = each.replace(' ','')
        try:
            int(each)
        except:
            a.append(each)
    x = id+','+';'.join(a)
    tmp.append(x)
    with open('a.csv','w',encoding='utf-8') as f:
        f.write('\n'.join(tmp))