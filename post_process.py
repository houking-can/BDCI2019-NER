import codecs
import csv
import re
import os
from tqdm import tqdm
from collections import Counter

oracle_dict = open('./data/dict/dict_oracle.txt').read().split('\n')
oracle_dict = [each.strip() for each in oracle_dict]
oracle_dict = set([each for each in oracle_dict if each != ''])

remove = set(open('./data/train_dict.txt').read().split('\n'))
if '' in remove: remove.remove('')

extra_words = codecs.open('./data/extra_words.txt').read().split('\n')
extra_words = [each.strip() for each in extra_words if each != '']
extra_words = list(set(extra_words))
extra_words.sort(key=lambda k: len(k), reverse=True)


def filter_word(w):
    add_char = {']', '：', '~', '！', '%', '[', '《', '】', ';', ':', '》', '？', '>', '/', '#', '。', '；', '&', '=', '，',
                '【', '@', '、', '|', '大学', '中学', '小学'}
    if w == '':
        return ''

    if re.findall("\\" + "|\\".join(add_char), w):
        return ''

    if 'CEO' in w:
        w = w.replace('CEO', '')
    w = w.strip('-')

    if judge_pure_english(w) and len(w) == 2:
        return ''

    if w.isnumeric():
        return ''
    if len(w) == 1:
        return ''

    if w.endswith('.'):
        return ''

    if w in remove or w in oracle_dict:
        return ''

    if judge_pure_english(w) and len(w) <= 2:
        return ''

    return w


def gen_csv(filename, save_name='./res/predict_results.csv'):
    predicts = codecs.open(filename).read().split('\n\n')
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
            label = each.split()
            word = label[0]
            tag = label[-1]
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

    return save_name


def judge_pure_english(keyword):
    return all(ord(c) < 128 for c in keyword)


def find_all(sub, s):
    index_list = []
    index = s.find(sub)
    while index != -1:
        index_list.append(index)
        index = s.find(sub, index + 1)

    if len(index_list) > 0:
        return index_list
    else:
        return -1


def check_punctuations(w, context):
    w = w.strip('（')
    w = w.strip('(')
    w = w.strip(')')
    w = w.strip('）')

    w = w.strip('”')
    w = w.strip('’')
    w = w.strip('“')
    w = w.strip('‘')

    if all(p not in w for p in ['(', '（', '\'', '"', '‘', '“', ')', '）', '”', '’']):
        return w

    index = context.find(w)
    if index + len(w) < len(context) and context[index + len(w)] in [')', '）', '"', '”', '\'', '’']:
        w = w + context[index + len(w)]
    if index > 0 and context[index - 1] in ['(', '（', '\'', '"', '‘', '“']:
        w = context[index - 1] + w

    if w[0] in ['(', '（'] and w[-1] in [')', '）']:
        return w[1:-1]
    if w[0] in ['"', '“', '\'', '‘'] and w[-1] in ['"', '”', '’', '\'']:
        return w[1:-1]

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

    if cnt_chinese == 0 and cnt_english == 0 and cnt_double == 0 and cnt_single == 0:
        return w

    return ''


def verify_entity(candidates, contex):
    """
    检查后缀是否明显错误
    :param candidates:
    :param contex:
    :return:
    """
    # 引号的处理
    res = []
    for entity in candidates:
        if re.findall('’|‘|\'|\"|“|”', entity):
            tmp = re.sub('’|‘|\'|\"|“|”', '', entity)
            if tmp in candidates:
                res.append(tmp if contex.count(tmp) >= contex.count(entity) else entity)
                # print(tmp, entity)
                continue
        res.append(entity)

    candidates = res

    # 处理非法后缀[会,]
    res = []
    for entity in candidates:
        if entity.endswith('会'):
            if not entity.endswith('基金会'):
                if contex.count(entity[:-1]) > contex.count(entity) and len(entity) > 3:
                    res.append(entity[:-1])
                    continue
        res.append(entity)

    candidates = res

    # 处理数字后缀
    res = []
    

    return res


def complement_entity(entity, context):
    """
    根据文本内容补全
    :param entity:
    :param context:
    :return:
    """
    cnt = context.count(entity)
    if cnt == 0: return []

    for word in extra_words:
        new_entity = entity + word
        new_cnt = context.count(new_entity)
        if new_cnt > 0:
            if new_cnt == cnt:
                # print(1, entity, entity + word)
                return [new_entity]
            if new_entity.lower().endswith('app'):
                # print(2, new_entity[:-3])
                return [new_entity[:-3]]
            # print(2, entity, entity + word)
            return [entity]

    for word in extra_words:
        for i in range(1, len(word)):
            new_cnt = context.count(entity + word[i:])
            if entity.endswith(word[:i]) and new_cnt > 0:
                new_entity = entity + word[i:]
                if context.index(entity) == context.index(new_entity):
                    if len(new_entity) == 3 and len(entity) == 2:
                        return []

                if new_cnt != cnt and new_entity.lower().endswith('app'):
                    print(2, entity, new_entity[:-3], new_entity)
                    return [new_entity[:-3]]

                # print(3, entity, new_entity)
                return [new_entity]

    return [entity]


def post_process(filename):
    """
    后处理部分
    :param filename:
    :return:
    """
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
            if candidates == '':
                entity = []
            else:
                candidates = candidates.split(';')
                entity = complement_verify(candidates, lines[i])
            res.write('{0},{1}\n'.format(id, ';'.join(entity)))
    res.close()
    return save_path


def complement_verify(candidates, context):
    """
    对候选实体集合补全，删除非法后缀
    :param candidates:
    :param context:
    :return:
    """
    if len(context[1]) > 40 and context[2].startswith(context[1][:-9]):
        context = context[2]
    else:
        context = context[1] + '。' + context[2]

    new_candidates = []
    for entity in candidates:
        new_entity = complement_entity(entity, context)
        if new_entity != []:
            new_candidates.extend(new_entity)

    new_candidates = list(set(new_candidates))
    new_candidates = [check_punctuations(w, context) for w in new_candidates]
    new_candidates = list(set(new_candidates))

    verify_candidates = verify_entity(new_candidates, context)

    cnt_candidates = [(each, context.count(each)) for each in verify_candidates if each != '']
    cnt_candidates.sort(key=lambda k: (k[0], len(k[0])))

    de_duplicate = []
    for i in range(len(cnt_candidates) - 1):
        if cnt_candidates[i + 1][0].startswith(cnt_candidates[i][0]) \
                and (cnt_candidates[i][1] - cnt_candidates[i + 1][1]) < cnt_candidates[i + 1][1]:
            # print(cnt_candidates[i][0],cnt_candidates[i + 1][0])
            continue
        de_duplicate.append((cnt_candidates[i]))
    if len(cnt_candidates) > 0:
        de_duplicate.append(cnt_candidates[-1])

    # sort candidates
    rank_candidates = []
    for entity, cnt in de_duplicate:
        rank_candidates.append((cnt, len(context) - context.find(entity), entity))
    rank_candidates.sort(key=lambda k: (k[0], k[1]), reverse=True)

    rank_candidates = [each[2] for each in rank_candidates]

    return rank_candidates


def remove_entity(filename):
    print('Removing entities...')
    results = open(filename).read().split('\n')
    if results[-1] == '':
        results = results[:-1]
    res = codecs.open(filename, 'w')
    res.write('id,unknownEntities\n')
    for line in tqdm(results[1:]):
        if ',' in line:
            id, entities = line.split(',')
            entities = entities.split(';')
            candidates = []
            for entity in entities:
                if entity in remove or entity in oracle_dict:
                    continue
                if judge_pure_english(entity) and len(entity) <= 2:
                    continue
                candidates.append(entity)
            res.write('%s,%s\n' % (id, ';'.join(candidates)))
        else:
            res.write('%s\n' % line)

    lines = open(filename, encoding='utf-8').read().split('\n')
    tmp = []
    for i in range(1, len(lines)):
        entities = ''
        if ',' in lines[i]:
            _, entities = lines[i].split(',')
        else:
            _ = lines[i]
        entities = entities.split(';')
        tmp.extend(entities)

    # tmp = list(set(tmp))
    tmp.sort(key=lambda k: (k, len(k)))
    C = list(Counter(tmp).items())
    C.sort(key=lambda k: (k[1], k, len(k)), reverse=True)
    xx = []
    for each in C:
        if each[0] != '':
            xx.append(each[0] + ' ' + str(each[1]))
            # xx.append(each[0])

    with open('./res/entities.txt', 'w', encoding='utf-8') as f:
        f.write('\n'.join(xx))


if __name__ == "__main__":
    results_path = './res/predict_results.csv'
    # gen_csv('./label_test.txt', results_path)
    # gen_csv('./output/test_predictions.txt',results_path)
    post_path = post_process(results_path)
    remove_entity(post_path)
