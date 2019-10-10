import re

oracle = set(open('./data/dict/train_dict.txt', encoding='utf-8').read().split('\n'))
with open('./data/dict/train_dict.txt', 'w', encoding='utf-8') as f:
    oracle = [each.strip() for each in oracle if each != '']
    f.write('\n'.join(sorted(oracle)))

# dict = set(open('./data/dict/dict.txt', encoding='utf-8').read().split('\n'))
# # with open('./data/dict/dict_1.txt', 'w', encoding='utf-8') as f:
# #     oracle = [each.strip() for each in oracle if each != '']
# #     f.write('\n'.join(sorted(oracle)))
#
# with open('./data/dict/dict_ex.txt', 'w', encoding='utf-8') as f:
#     f.write('\n'.join(sorted(dict - oracle)))
