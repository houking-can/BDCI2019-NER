import codecs
import csv
import re
import os
from tqdm import tqdm
from collections import Counter

dict_oracle = open('./data/dict/dict_oracle.txt').read().split('\n')
dict_oracle = [each.strip() for each in dict_oracle]
dict_oracle = set([each for each in dict_oracle if each != ''])

remove_city = open('./data/dict/remove_city.txt').read().split('\n')
remove_city = [each.strip() for each in remove_city]
remove_city = set([each for each in remove_city if each != ''])

remove_train = open('./data/dict/remove_train.txt').read().split('\n')
remove_train = [each.strip() for each in remove_train]
remove_train = set([each for each in remove_train if each != ''])

dict_known = open('./data/dict/dict_known.txt').read().split('\n')
dict_known = [each.strip() for each in dict_known]
dict_known = set([each for each in dict_known if each != ''])

bio_train = open('./data/dict/bio_train.txt').read().split('\n')
bio_train = [each.strip() for each in bio_train]
bio_train = set([each for each in bio_train if each != ''])

remove_select = set(open('./data/dict/remove_select.txt').read().split('\n'))
if '' in remove_select: remove_select.remove('')

completion_words = codecs.open('./data/dict/completion_words.txt').read().split('\n')
completion_words = [each.strip() for each in completion_words if each != '']
completion_words = list(set(completion_words))
completion_words.sort(key=lambda k: len(k), reverse=True)


def filter_word(w):
    add_char = {']', '：', '~', '！', '%', '[', '《', '】', ';', ':', '》', '？', '>', '/', '#', '。', '；', '&', '=', '，',
                '【', '@', '、', '|', '大学', '中学', '小学','?'}
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

    # if w in remove or w in dict_oracle:
    #     return ''

    # if judge_pure_english(w) and len(w) <= 2:
    #     return ''

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


def verify_entity(candidates, context):
    """
    检查后缀是否明显错误
    :param candidates:
    :param context:
    :return:
    """
    # 引号的处理
    res = []
    for entity in candidates:
        if re.findall('’|‘|\'|\"|“|”|（|）|\(|\)', entity):
            tmp = re.sub('’|‘|\'|\"|“|”|（|）|\(|\)', '', entity)
            if tmp in candidates:
                res.append(tmp if context.count(tmp) > 0 else entity)
                # print(tmp, entity)
                continue
        res.append(entity)

    candidates = res

    # 处理非法后缀[会,公众号]
    res = []
    for entity in candidates:
        if entity.endswith('会'):
            if not entity.endswith('基金会'):
                if context.count(entity[:-1]) > context.count(entity) and len(entity) > 3:
                    res.append(entity[:-1])
                    continue
        elif '公众号' in entity:
            index = entity.find('公众号')
            entity = entity[:index]
            # print(1, entity, entity[:index])
        res.append(entity)

    candidates = [e for e in res if e != '']

    # 处理数字后缀
    res = []
    for entity in candidates:
        if entity[-1].isdigit() and not entity[-2].isdigit():
            if context.count(entity[:-1]) > context.count(entity):
                # print(2, entity, entity[:-1])
                entity = entity[:-1]
        res.append(entity)

    # 处理大小写

    return res


def complement_entity(entity, context):
    """
    根据文本内容补全
    :param entity:
    :param context:
    :return:
    """

    def judge_ends(entity):
        for word in completion_words:
            if entity.endswith(word):
                return True
        return False

    if judge_ends(entity):
        return [entity]
    if entity.endswith('有限公'):
        if entity+'司' in context:
            return [entity+'司']
        return []

    cnt = context.count(entity)
    if cnt == 0: return []

    for word in completion_words:
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

    for word in completion_words:
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
                candidates = [e for e in candidates.split(';') if e != '']
                if candidates != []:
                    entity = complement_verify(candidates, lines[i])
                else:
                    entity = []
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
        rank_candidates.append((cnt, context.find(entity), entity))
    rank_candidates.sort(key=lambda k: (k[1]))

    rank_candidates = [each[2] for each in rank_candidates]

    return rank_candidates


def gen_oracle_add_dict():
    oracle_add_dict = set()
    for entity in dict_oracle:
        for word in completion_words:
            oracle_add_dict.add(entity + word)
    return oracle_add_dict


def remove_entity(filename):
    print('Removing entities...')
    results = open(filename).read().split('\n')
    if results[-1] == '':
        results = results[:-1]
    res = codecs.open(filename, 'w')
    res.write('id,unknownEntities\n')
    # train_text = codecs.open('./data/Train_Data.csv').read()

    tmp = set()
    # cnt = 0
    remove_set = dict_oracle  | remove_city | remove_select | remove_train
    for line in tqdm(results[1:]):
        if ',' in line:
            id, entities = line.split(',')
            entities = entities.split(';')
            candidates = []
            for entity in entities:
                # if entity in remove or entity in dict_oracle:
                if entity in remove_set:
                    continue

                if entity in dict_known:
                    # print(entity)
                    continue
                # if entity in bio_train:
                #     tmp.add(entity)
                #     continue

                if judge_pure_english(entity) and len(entity) <= 2:
                    continue
                candidates.append(entity)
            res.write('%s,%s\n' % (id, ';'.join(candidates)))
        else:
            res.write('%s\n' % line)
    tmp = list(tmp)
    tmp.sort(key=lambda k: (k, len(k)))
    for each in tmp:
        print(each)

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
    # cnt=0
    for each in C:
        if each[0] != '':
            # if each[0] != '' and each[0] in train_text and len(each[0]) < 3 and each[1] >=3:
            xx.append(each[0] + ' ' + str(each[1]))
            # cnt+=each[1]
            # xx.append(each[0])
    # print(cnt)
    with open('./res/entities.txt', 'w', encoding='utf-8') as f:
        f.write('\n'.join(xx))


if __name__ == "__main__":
    results_path = './res/predict_results.csv'
    # results_path = './res/best.csv'
    # gen_csv('./output/label_test.txt', results_path)
    post_path = post_process(results_path)
    remove_entity(post_path)
