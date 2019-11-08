import re
from collections import Counter

import codecs

dict_oracle_1 = open('./data/dict/dict_oracle_1.txt').read().split('\n')
dict_oracle_1 = [each.strip() for each in dict_oracle_1]
dict_oracle_1 = set([each for each in dict_oracle_1 if each != ''])

dict_oracle_2 = open('./data/dict/dict_oracle_2.txt').read().split('\n')
dict_oracle_2 = [each.strip() for each in dict_oracle_2]
dict_oracle_2 = set([each for each in dict_oracle_2 if each != ''])

dict_oracle = dict_oracle_1 | dict_oracle_2

remove_city = open('./data/dict/remove_city.txt').read().split('\n')
remove_city = [each.strip() for each in remove_city]
remove_city = set([each for each in remove_city if each != ''])

remove_train = open('./data/dict/remove_train.txt').read().split('\n')
remove_train = [each.strip() for each in remove_train]
remove_train = set([each for each in remove_train if each != ''])

computer = open('./data/dict/computer.txt').read().split('\n')
computer = [each.strip() for each in computer]
computer = set([each for each in computer if each != ''])
computer = set()

dict_known = open('./data/dict/dict_known.txt').read().split('\n')
dict_known = [each.strip() for each in dict_known]
dict_known = set([each for each in dict_known if each != ''])
dict_known = dict_known - computer

bio_train = open('./data/dict/bio_train_1.txt').read().split('\n')
bio_train = [each.strip() for each in bio_train]
bio_train = set([each for each in bio_train if each != ''])

bio_none = set(open('./data/dict/bio_none.txt').read().split('\n'))
bio_none = [each.strip() for each in bio_none]
bio_none = set([each for each in bio_none if each != ''])
bio_none = bio_none - dict_oracle




# tmp = []
# print(len(remove_train))
# print(len(extra))
# for each in extra:
#     # if each in train_text:
#     print(each)


# tmp=list(a-dict_oracle)
# print(len(tmp))
# tmp.sort(key=lambda k:(k,len(k)))
# for each in tmp:
#     print(each)
# print(len(tmp))


# remove = set(open('./data/dict/remove_select.txt').read().split('\n'))
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

"""extra"""
# a = open('./res/results.csv', encoding='utf-8').read().split('\n')
# b = open('./res/best.csv', encoding='utf-8').read().split('\n')
# with open('./res/extra.csv', 'w', encoding='utf-8') as f:
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
#         entities = set(a_entities) - set(b_entities)
#         if len(entities) == 0:
#             continue
#         f.write('%s,%s\n' % (a_id, ';'.join(list(entities))))

# def judge_pure_english(keyword):
#     return all(ord(c) < 128 for c in keyword)

# a = open(r'C:\Users\Houking\Desktop\label\best.csv',encoding='utf-8').read().split('\n')
# b = set(open(r'C:\Users\Houking\Desktop\label\remove_select.txt', encoding='utf-8').read().split('\n'))
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

# with open(r'C:\Users\Houking\Desktop\label\bio_train_1.txt', 'w', encoding='utf-8') as f:
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

# lines = open('/home/yhj/competitions/BDCI/data/oracle/Train_Data.csv', encoding='utf-8').read().split('\n')
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


"""pre_process.py"""
# start = 0
# cnt = 0
# j = 0
# tmp = line[i]
#
# while j < len(line[i]):
#     if line[i][j] == '{':
#         if cnt == 0:
#             start = j
#         cnt += 1
#         j += 1
#         continue
#     elif line[i][j] == '}':
#         cnt -= 1
#         if cnt == 0:
#             end = j
#             if judge_code(line[i][start:j]):
#                 k = start
#                 while k >= 0:
#                     if ord(line[i][k]) < 128:
#                         start -= 1
#                     else:
#                         break
#                     k -= 1
#                 k = j
#                 while k < len(line[i]):
#                     if ord(line[i][k]) < 128 and line[i][k] != '{':
#                         end += 1
#                     else:
#                         break
#                     k += 1
#                 tmp = tmp.replace(line[i][start + 1:end], '，')
#                 print(line[0])
#                 print(line[i][start + 1:end])
#                 print('\n')
#             j = end + 1
#             continue
#
#     j += 1
# line[i] = tmp


# for entity in none_bio:
#     index = find_all(entity, sent)
#     if index:
#         if judge_pure_english(entity):
#             for start in index:
#                 if start > 0 and sent[start - 1].isalpha():
#                     continue
#                 elif start + len(entity) < len(sent) and sent[start+len(entity)].isalpha():
#                     continue
#                 bio_list[start] = 'B-NONE'
#                 for k in range(start + 1, start + len(entity)):
#                     bio_list[k] = 'I-NONE'
#
#         else:
#             for start in index:
#                 bio_list[start] = 'B-NONE'
#                 for k in range(start + 1, start + len(entity)):
#                     bio_list[k] = 'I-NONE'
