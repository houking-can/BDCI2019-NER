import re
from collections import Counter

import codecs

oracle_dict = open('./data/dict/dict_oracle.txt').read().split('\n')
oracle_dict = [each.strip() for each in oracle_dict]
oracle_dict = set([each for each in oracle_dict if each != ''])

remove = set(open('./data/dict/remove.txt').read().split('\n'))
if '' in remove: remove.remove('')

none = set(open('./data/dict/dict_label_none.txt').read().split('\n'))
none = [each.strip() for each in none]
none = set([each for each in none if each != ''])
none = none - oracle_dict

# remove = set(open('./data/dict/remove.txt').read().split('\n'))
# if '' in remove: remove.remove('')
#
# results = open('./res/best.csv').read().split('\n')
# if results[-1] == '':
#     results = results[:-1]
# res = codecs.open('./res/best.csv', 'w')
# res.write('id,unknownEntities\n')
# for line in results[1:]:
#     if ',' in line:
#         id, entities = line.split(',')
#         entities = entities.split(';')
#         tmp = [each for each in entities if each not in remove]
#         res.write('%s,%s\n' % (id, ';'.join(tmp)))
#     else:
#         res.write('%s\n' % line)


# a = open('./res/test_completion.csv', encoding='utf-8').read().split('\n')
# tmp = []
# for i in range(1, len(a)):
#     entities = ''
#     if ',' in a[i]:
#         id, entities = a[i].split(',')
#     else:
#         id = a[i]
#     entities = entities.split(';')
#     tmp.extend(entities)
#
# tmp = list(set(tmp))
# tmp.sort(key=lambda k: (k, len(k)))
# # C = list(Counter(tmp).items())
# # C.sort(key=lambda k: k[1], reverse=True)
# # cnt = 0
# # for each in C:
# #     if each[0] != '':
# #         xx.append(each[0] + ' ' + str(each[1]))
# with open('./res/order.txt', 'w', encoding='utf-8') as f:
#     f.write('\n'.join(tmp))

# try:
#     if each[0][-1].isdigit():
#         print(each[0], each[1])
#         cnt += each[1]
# except:
#     pass

# a = open('./res/best-tf-only.csv', encoding='utf-8').read().split('\n')
# b = open('./res/post_results.csv', encoding='utf-8').read().split('\n')
# with open('./res/combine.csv', 'w', encoding='utf-8') as f:
#     f.write('id,unknownEntities\n')
#     for i in range(1, len(a) - 1):
#         a_entities = ''
#         b_entities = ''
#         if ',' in a[i]:
#             a_id, a_entities = a[i].split(',')
#         else:
#             a_id = a[i]
#         if ',' in b[i]:
#             b_id, b_entities = b[i].split(',')
#         else:
#             b_id = b[i]
#         assert (a_id == b_id)
#         a_entities = a_entities.split(';')
#         b_entities = b_entities.split(';')
#         entities = set(a_entities) | set(b_entities)
#         if '' in entities:
#             entities.remove('')
#         f.write('%s,%s\n' % (a_id, ';'.join(list(entities))))

# def judge_pure_english(keyword):
#     return all(ord(c) < 128 for c in keyword)

# a = open(r'C:\Users\Houking\Desktop\label\best.csv',encoding='utf-8').read().split('\n')
# b = set(open(r'C:\Users\Houking\Desktop\label\remove.txt', encoding='utf-8').read().split('\n'))
# with open(r'C:\Users\Houking\Desktop\label\test.csv','w',encoding='utf-8') as f:
#     f.write('id,unknownEntities\n')
#     for i in range(1,len(a)):
#         a_entities = ''
#         b_entities = ''
#         if ',' in a[i]:
#             a_id,a_entities = a[i].split(',')
#             a_entities = a_entities.split(';')
#             tmp = []
#             for each in  a_entities:
#                 # if judge_pure_english(each):
#                 #     continue
#                 if each in b:
#                     continue
#                 tmp.append(each)
#             f.write('%s,%s\n' % (a_id,';'.join(tmp)))


#         else:
#             a_id = a[i]
#             f.write('%s,\n' % a_id)

# import re

# a = set(open(r'C:\Users\Houking\Desktop\label\a.csv', encoding='utf-8').read().split('\n'))


# with open(r'C:\Users\Houking\Desktop\label\b.txt', 'w', encoding='utf-8') as f:
#     oracle = [each.strip() for each in oracle if each != '']
#     f.write('\n'.join(sorted(oracle,key=lambda x:(len(x),x))))

# dict_1 = set(open(r'C:\Users\Houking\Desktop\label\train_clean_1.txt', encoding='utf-8').read().split('\n'))
# dict_2 = set(open(r'C:\Users\Houking\Desktop\label\train_clean_2.txt', encoding='utf-8').read().split('\n'))
# print(len(dict_1))
# print(len(dict_2))
# a = dict_1 & dict_2
# a = [each.strip() for each in a]
# a = [each for each in a if each!='']
# a = sorted(a,key=lambda k: (len(k),k))
# print(len(a))

# with open(r'C:\Users\Houking\Desktop\label\train_dict.txt', 'w', encoding='utf-8') as f:
#     for each in a:
#         f.write(each+'\n')

# oracle = [each.strip() for each in dict if each != '']
# f.write('\n'.join(sorted(oracle)))
#
# with open('./data/dict/dict_ex.txt', 'w', encoding='utf-8') as f:
#     f.write('\n'.join(sorted(dict - oracle)))


# oracle = set(open('./data/dict/train_dict_1.txt', encoding='utf-8').read().split('\n'))
# a = set(open('./data/dict/train_dict_2.txt', encoding='utf-8').read().split('\n'))
# oracle = oracle & a
# with open('./data/dict/train_dict_1.txt', 'w', encoding='utf-8') as f:
#     oracle = [each.strip() for each in oracle if each != '']
#     f.write('\n'.join(sorted(oracle, key=lambda x: (len(x), x))))

# dict = set(open('./data/dict/dict.txt', encoding='utf-8').read().split('\n'))
# # with open('./data/dict/dict_1.txt', 'w', encoding='utf-8') as f:
# #     oracle = [each.strip() for each in oracle if each != '']
# #     f.write('\n'.join(sorted(oracle)))
#
# with open('./data/dict/dict_ex.txt', 'w', encoding='utf-8') as f:
#     f.write('\n'.join(sorted(dict - oracle)))

# lines = open('/home/yhj/competitions/BDCI/data/old/Train_Data.csv', encoding='utf-8').read().split('\n')
# lines = lines[1:]
# for line in lines:
#     line = line.split(',')
#     if line[-1]=='':
#         print(line[0])

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


# b = codecs.open('./data/Train_Data.csv').read()
# a = codecs.open('/home/yhj/competitions/BDCI/res/entities.txt').read().split('\n')
# # a=a.split(' ')
# # a = [each.strip('\n') for each in a]
# # print(len(a))
# cnt = 0
# tmp = []
# for each in a:
#     # if each+'资' in b:
#     if each in b:
#         tmp.append(each)
#         # print(each)
#         cnt += 1
# print(cnt)
# c = codecs.open('test_dict_0.txt','w')
# c.write('\n'.join(tmp))
# c.close()

import csv
import codecs

with open('./data/old/Train_Data_Hand.csv', 'r', encoding='utf-8') as myFile:
    lines = list(csv.reader(myFile))
    res = codecs.open('none.csv', 'w')
    res1 = codecs.open('nice.csv','w')
    for line in lines[1:]:
        if line[3] == '':
            res.write(','.join(line) + '\n')
            continue
        else:
            res1.write(','.join(line) + '\n')
    res.close()
    res1.close()
