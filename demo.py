import re

# oracle = set(open('./data/dict/train_dict.txt', encoding='utf-8').read().split('\n'))
# with open('./data/dict/train_dict.txt', 'w', encoding='utf-8') as f:
#     oracle = [each.strip() for each in oracle if each != '']
#     f.write('\n'.join(sorted(oracle,key=lambda x:(len(x),x))))

# dict = set(open('./data/dict/dict.txt', encoding='utf-8').read().split('\n'))
# # with open('./data/dict/dict_1.txt', 'w', encoding='utf-8') as f:
# #     oracle = [each.strip() for each in oracle if each != '']
# #     f.write('\n'.join(sorted(oracle)))
#
# with open('./data/dict/dict_ex.txt', 'w', encoding='utf-8') as f:
#     f.write('\n'.join(sorted(dict - oracle)))

lines = open('/home/yhj/competitions/BDCI/data/old/Train_Data.csv', encoding='utf-8').read().split('\n')
lines = lines[1:]
for line in lines:
    line = line.split(',')
    if line[-1]=='':
        print(line[0])
    # print(line[-1])
    # try:
    #     line = line.split(',')
    #
    #     entity = line[-1].split(';')
    #     for e in entity:
    #         if len(e)>20:
    #             print(id)
    #             break
    # except:
    #     print(line.split(',')[0])
