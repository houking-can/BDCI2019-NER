import re
from collections import Counter

import codecs

a = open('./data/dict/bio_train.txt').read().split('\n')
a = [each.strip() for each in a]
a = set([each for each in a if each != ''])

dict_oracle = open('./data/dict/dict_oracle.txt').read().split('\n')
dict_oracle = [each.strip() for each in dict_oracle]
dict_oracle = set([each for each in dict_oracle if each != ''])

# remove_city = open('./data/dict/remove_city.txt').read().split('\n')
# remove_city = [each.strip() for each in remove_city]
# remove_city = set([each for each in remove_city if each != ''])
#
# b = open('./data/dict/none_reserved.txt').read().split('\n')
# b = [each.strip() for each in b]
# b = set([each for each in b if each != ''])
#
# a=list(a-dict_oracle-remove_city-b)
# a.sort(key=lambda k:(k,len(k)))
# train_text = codecs.open('./data/Train_Data.csv').read()
# tmp=[]
# print(len(dict_oracle))
# for each in dict_oracle:
#     if each in train_text:
#         tmp.append(each)
    # else:
    #     print(each)
# print('\n')
# print(len(a))
#
# tmp=list(a-dict_oracle)
# print(len(tmp))
# tmp.sort(key=lambda k:(k,len(k)))
# for each in tmp:
#     print(each)
# print(len(tmp))
# def get_sentences(text, max_length=512):
#     # if len(text) <= max_length - 2:
#     #     return [text]
#     tmp = re.split('(。|！|？|；|，|\?|\!)', text)
#     sent = ''
#     sentences = []
#     if tmp[-1] != '':
#         tmp.append('。')
#     else:
#         tmp = tmp[:-1]
#
#     i = 0
#     while i < len(tmp) - 1:
#         if len(tmp[i] + tmp[i + 1]) > max_length - 2:
#             if sent != '':
#                 sentences.append(sent)
#             x = tmp[i] + tmp[i + 1]
#             pieces = [x[i:i + max_length - 2] for i in range(0, len(x), max_length - 2)]
#             sentences.extend(pieces)
#             i += 2
#             sent = ''
#             continue
#         if len(sent + tmp[i] + tmp[i + 1]) > max_length - 2:
#             sentences.append(sent)
#             sent = ''
#             i += 2
#             continue
#         sent += (tmp[i] + tmp[i + 1])
#         i += 2
#
#     if sent != '':
#         sentences.append(sent)
#
#     return sentences
#
#
# a='【】点击上方蓝色字体免费关注（别私存，快给朋友们看看，多一个人看到少一个人受害！）警惕：163家消费全返（返利）传销骗局名单曝光，已有人倾家荡产！提醒亲朋好友千万别碰点点啦聚赢宝云集品云联惠心未来得来惠零零购利客购7号网信优惠美芝妮洄游客匀加速微客谷喇叭客聚富网云吃货商城天添薪益杞来大星白云零购未来梦壹购物极之道跨界通我来买乐赚惠一指淘e多购白贝购万商惠哪划算爱利购优卡特全返通多可丽金粉团唯宝汇乐宜购淘丰乐德信美兑乐购商城乐采商城胖胖生活利人商城万金商城万聚商盟人人快购未来商城乐享无忧聚商一百云圈商城福泽天下瑞丰集团货通天下黎民商城德通天下全返时代大白军团浩沅云商乐享无忧全惠商城MT电商聚商一百乐福全返互联宝宝嘀的商城返本商城一淘云购吧娜科技云惠天下车房时代优返商城亿联数贸春媛商城智道百业帝峰商城云龙易购云梦生活E道商城无界生活万商昭和江苏皇缘人人公益易迅惠民大唐天下中佳易购城邦商城宝微商城壹号商圈宝微商城趣购商城众和乐购乐活无界沃佳商城博邦商城无上商城千度网购我的未来网爱尚购物网购实惠云商同城优速购珍优福商城鑫易鑫商贸白拿白送网中天国际城时尚365辰旭商务网随9快易购百姓创富汇美乐购商城创客920万品换购网V8同城汇趣购购物商城51天天乐购珠峰购物商城百姓乐购商城山东通购购物深圳无界珠宝贪猫值换平台恩威道源商城聪慧健康产业知启消费全返道吉生态平台三古汇云生活乐活积分平台vce一卡通超越未来超市融城全返商城缪迪得一容易德信返利超市高新惠好超市优狐消费服务网腾云消费服务网江苏圣迪雅集团合赢消费创富网翱圣搭伙O2O利利购全返购物九丰消费服务网玉聚缘全返商城河北众智云平台丙丙卷支付全返云消费全返大系统旭日东升全返商城生活百需消费全返天地物联消费全返创客优品汇免费购物商城礼部尚品商家联盟一卡通青云百货消费全返平台易返云商消费全返平台提醒大家⊙以后一定要擦亮眼睛！千万别相信购物全额报销！天上不会掉馅饼！！！贪心害死人！传出去，别再让你的家人、朋友被骗了!'
# b = get_sentences(a)
# c = 1

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

# a = open('./res/post_results.csv', encoding='utf-8').read().split('\n')
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

# with open(r'C:\Users\Houking\Desktop\label\bio_train.txt', 'w', encoding='utf-8') as f:
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

