import codecs
import csv
import re
import os
from tqdm import tqdm
from collections import Counter

oracle_dict = open('./data/dict/dict_oracle.txt').read().split('\n')
oracle_dict = [each.strip() for each in oracle_dict]
oracle_dict = set([each for each in oracle_dict if each != ''])

remove = set(open('./data/dict/remove.txt').read().split('\n'))
if '' in remove: remove.remove('')


def check_brackets(w):
    w = w.rstrip('（')
    w = w.rstrip('(')
    w = w.lstrip(')')
    w = w.lstrip('）')
    cnt_chinese = 0
    cnt_english = 0
    for c in w:
        if c == '（':
            cnt_chinese += 1
        elif c == '）':
            cnt_chinese -= 1
    for c in w:
        if c == '(':
            cnt_english += 1
        elif c == ')':
            cnt_english -= 1

    if cnt_chinese == 0 and cnt_english == 0:
        if w.startswith('（') and w.endswith('）'):
            return w[1:-1]
        if w.startswith('(') and w.endswith(')'):
            return w[1:-1]
        return w

    if cnt_chinese > 0:
        if not w.startswith('（'):
            return w + '）'
        return w[1:]
    if cnt_chinese < 0:
        if not w.endswith('）'):
            return '（' + w
        return w[:-1]
    if cnt_english > 0:
        if not w.startswith('('):
            return w + ')'
        return w[1:]
    if cnt_english < 0:
        if not w.endswith(')'):
            return '(' + w
        return w[:-1]


def check_quotation(w):
    w = w.lstrip('”')
    w = w.lstrip('’')
    w = w.rstrip('“')
    w = w.rstrip('‘')

    cnt_double = 0
    cnt_single = 0
    for c in w:
        if c == '“':
            cnt_double += 1
        elif c == '”':
            cnt_double -= 1
    for c in w:
        if c == '‘':
            cnt_single += 1
        elif c == '’':
            cnt_single -= 1

    if cnt_double == 0 and cnt_single == 0:
        if w.startswith('“') and w.endswith('”'):
            return w[1:-1]
        if w.startswith('‘') and w.endswith('’'):
            return w[1:-1]
        return w

    if cnt_double > 0:
        if not w.startswith('“'):
            return w + '”'
        return w[1:]
    if cnt_double < 0:
        if not w.endswith('”'):
            return '“' + w
        return w[:-1]
    if cnt_single > 0:
        if not w.startswith('‘'):
            return w + '’'
        return w[1:]
    if cnt_single < 0:
        if not w.endswith('’'):
            return '‘' + w
        return w[:-1]


def filter_word(w):
    add_char = {']', '：', '~', '！', '%', '[', '《', '】', ';', ':', '》', '？', '>', '/', '#', '。', '；', '&', '=', '，',
                '【', '@', '、', '|', '大学', '中学', '小学'}
    if w == '':
        return ''

    if re.findall("\\" + "|\\".join(add_char), w):
        return ''

    if 'CEO' in w:
        w = w.replace('CEO', '')

    if judge_pure_english(w) and len(w) == 2:
        return ''

    w = check_brackets(w)
    w = check_quotation(w)
    if w.isnumeric():
        return ''
    if len(w) == 1:
        return ''

    if w.endswith('.'):
        return ''

    if w in remove:
        return ''

    if w in oracle_dict:
        return ''

    if judge_pure_english(w) and len(w) == 2:
        return ''

    return w


def gen_csv():
    predicts = codecs.open('./ner_output/test_predictions.txt').read().split('\n\n')
    save_name = './res/ner_results.csv'
    if os.path.exists(save_name):
        os.remove(save_name)
    res = codecs.open(save_name, 'w')
    res.write('id,unknownEntities\n')
    id = ''
    unknown_entities = set()
    for sent in tqdm(predicts):
        sent = sent.split('\n')
        entity = ''
        for each in sent:
            if each == '':
                continue
            tmp_id = re.findall('Ж(.*?)Ж', each)
            if len(tmp_id) == 1:
                if id != '':
                    # unknown_entities = select_candidates(unknown_entities)
                    res.write('{0},{1}\n'.format(id, ';'.join(list(unknown_entities))))
                id = tmp_id[0]
                unknown_entities = set()
                continue
            word, tag = each.split()
            if tag == 'B-ORG':
                if entity == '':
                    entity = word
                else:
                    entity = filter_word(entity)
                    if entity != '':
                        unknown_entities.add(entity)
                    entity = ''
            elif tag == 'I-ORG':
                if entity != '':
                    entity += word
            else:
                entity = filter_word(entity)
                if entity != '':
                    unknown_entities.add(entity)
                entity = ''
    # unknown_entities = select_candidates(unknown_entities)
    res.write('{0},{1}\n'.format(id, ';'.join(list(unknown_entities))))
    res.close()
    post_process(save_name)


# def select_candidates(unknown_entities):
#     unknown_entities = list(unknown_entities)
#     tmp = sorted(unknown_entities, key=lambda e: len(e))
#     if tmp != []:
#         unknown_entities = []
#         for i in range(len(tmp) - 1):
#             flag = True
#             for j in range(i + 1, len(tmp)):
#                 if tmp[i] in tmp[j]:
#                     flag = False
#                     break
#             if flag:
#                 unknown_entities.append(tmp[i])
#         unknown_entities.append(tmp[-1])
#     return unknown_entities

def judge_pure_english(keyword):
    return all(ord(c) < 128 for c in keyword)


def post_process(filename):
    print('Post process...')
    results = open(filename).read().split('\n')
    # results = open('./res/best.csv').read().split('\n')
    if results[-1] == '':
        results = results[:-1]
    save_path = './res/post_results.csv'
    res = codecs.open(save_path, 'w')
    # res = codecs.open('./res/best.csv', 'w')

    res.write('id,unknownEntities\n')

    with open('./data/Test_Data.csv', 'r', encoding='utf-8') as myFile:
        lines = list(csv.reader(myFile))
        if lines[-1] == '':
            lines = lines[:-1]
        for i in range(1, len(lines)):
            id, candidates = results[i].split(',')
            candidates = candidates.split(';')
            entity = completion(candidates, lines[i])
            res.write('{0},{1}\n'.format(id, ';'.join(entity)))
    res.close()
    remove_entity('./res/post_results.csv')


def completion(candidates, context):
    remove_char = {']', '：', '~', '！', '%', '[', '《', '】', ';', ':', '》', '？', '>', '/', '#', '。', '；', '&', '=',
                   '，',
                   '【', '@', '、', '|', ',', '”', '?'}

    context = context[1] + '。' + context[2]
    tmp = []
    for each in candidates:
        index = context.find(each)
        ex = 1
        if context.count(each) > 1:
            for i in range(1, len(context) - index - len(each)):
                if context.count(each) != context.count(context[index:index + i + len(each)]):
                    ex = i
                    break

            new = context[index:index + ex - 1 + len(each)]
            flag = True
            if len(new) < 22 and len(re.findall("\\" + "|\\".join(remove_char), new)) == 0:
                try:
                    xx = re.findall('(%s.*?)(理财|集团|控股|平台|银行|公司|资本|投资|生态|策略|控股集团)' % each, new)
                    if xx:
                        flag = False
                        new = xx[0][0] + xx[0][1]
                        if context.count(each) == context.count(new):
                            tmp.append(new)
                        else:
                            tmp.append(each)
                            tmp.append(new)
                    # else:
                    #     if ex > 1:
                    #         if len(each) <= 3 and len(new) == 4:
                    #             tmp.append(new)
                    #             # print(each, new)
                    #
                    #         flag = False
                except:
                    pass

            if flag:
                tmp.append(each)
        else:
            tmp.append(each)

    tmp = list(set(tmp))

    xx = []
    for w in tmp:
        if w in remove:
            continue
        cnt = context.count(w)
        # if judge_pure_english(w) and cnt == 1:
        #     continue
        xx.append((cnt, len(context) - context.find(w), w))
    xx.sort(key=lambda k: (k[0], k[1]), reverse=True)

    res = []
    for i in range(len(xx) - 1):
        if xx[i + 1][0] == xx[i][0] and xx[i + 1][2].startswith(xx[i][2]):
            continue
        res.append(xx[i])
    if len(xx) > 0:
        res.append(xx[-1])

    res = [each[2] for each in res]
    # if len(res) <= 2:
    #     return [each[2] for each in res]
    # else:
    #     tmp = [each[2] for each in res[:2]]
    #     for i in range(2, len(res)):
    #         if res[i][0] >= 2 and (len(context) - res[i][1]) < len(context) // 2:
    #             tmp.append(res[i][2])
    #     return tmp
    return res


def remove_entity(filename):
    print('Removing entities...')
    results = open(filename).read().split('\n')
    if results[-1] == '':
        results = results[:-1]
    res = codecs.open(filename, 'w')
    res.write('id,unknownEntities\n')
    for line in results[1:]:
        if ',' in line:
            id, entities = line.split(',')
            entities = entities.split(';')
            tmp = []
            for each in entities:
                if each in remove:
                    continue
                if judge_pure_english(each) and len(each) == 2:
                    print(each)
                    continue
                tmp.append(each)
            res.write('%s,%s\n' % (id, ';'.join(tmp)))
        else:
            res.write('%s\n' % line)

    lines = open(filename, encoding='utf-8').read().split('\n')
    tmp = []
    for i in range(1, len(lines)):
        entities = ''
        if ',' in lines[i]:
            id, entities = lines[i].split(',')
        else:
            id = lines[i]
        entities = entities.split(';')
        tmp.extend(entities)

    # tmp = list(set(tmp))
    tmp.sort(key=lambda k: (k, len(k)))
    C = list(Counter(tmp).items())
    C.sort(key=lambda k: (k[1], k, len(k)), reverse=True)
    xx = []
    for each in C:
        if each[0] != '':
            # xx.append(each[0] + ' ' + str(each[1]))
            xx.append(each[0])

    with open('./res/entities.txt', 'w', encoding='utf-8') as f:
        f.write('\n'.join(xx))


if __name__ == "__main__":
    # gen_csv()
    # post_process('./res/extra.csv')
    remove_entity('./res/combine.csv')
