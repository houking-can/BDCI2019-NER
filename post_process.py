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
                '【', '@', '、', '|', '大学', '中学', '小学', '?'}
    if w == '':
        return ''

    if re.findall("\\" + "|\\".join(add_char), w):
        return ''

    if 'CEO' in w:
        w = w.replace('CEO', '')
    w = w.strip('-')

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

    # 处理非法后缀[会,公众号,有限公,]
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
        elif entity.endswith('有限公') and entity + '司' not in context:
            continue
        elif entity.startswith('与'):
            entity = entity[1:]
        elif entity.endswith('其') and context.count(entity[:-1]) >= context.count(entity):
            entity = entity[1:]
        elif entity.endswith('神话'):
            continue
        elif entity.startswith('辣鸡'):
            continue
        elif entity.startswith('山寨'):
            continue
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

    return res


def judge_ends(entity):
    for word in completion_words:
        if entity.endswith(word):
            return True
    if entity.endswith('平台'):
        return True
    return False


def judge_alpha(c):
    unicode_id = ord(c)
    if (unicode_id <= 122 and unicode_id >= 97) or (unicode_id <= 90 and unicode_id >= 65):
        return True
    return False


def complement_candidates(candidates, context):
    new_candidates = []
    for entity in candidates:
        new_entity = complement_entity(entity, context)
        if new_entity != []:
            new_candidates.extend(new_entity)
    return new_candidates


def complement_entity(entity, context):
    """
    根据文本内容补全
    :param entity:
    :param context:
    :return:
    """
    # 如果实体结尾为公司，国际，控股等直接返回
    if judge_ends(entity):
        return [entity]

    # 补全实体前后的英文
    index = context.find(entity)
    if index < 0: return []
    if judge_alpha(entity[0]):
        for i in range(index - 1, -1, -1):
            if judge_alpha(context[i]):
                continue
            entity = context[i + 1:index] + entity
            break

    if judge_alpha(entity[-1]):
        for i in range(index + len(entity), len(context)):
            if judge_alpha(context[i]):
                continue
            tmp = entity + context[index + len(entity):i]
            if tmp.lower().endswith('app'):

                if context.count(tmp) == context.count(tmp[:-3]):
                    # print(1, entity, tmp)
                    return [tmp]
                # print(2, entity, tmp[:-3])
                return [tmp[:-3]]
            break

    # 补全中文后面的英文
    start = index + len(entity)
    if start < len(context) and judge_alpha(context[start]):
        for i in range(start, len(context)):
            if judge_alpha(context[i]):
                continue
            tmp = entity + context[index + len(entity):i]
            if len(tmp) - len(entity) <= 1:
                break

            if tmp.lower().endswith('qq'):
                break
            if context.count(entity) == context.count(tmp):
                # print(3, entity, tmp)
                return [tmp]
            elif tmp.lower().endswith('app'):
                # print(4, entity, tmp[:-3])
                return [tmp[:-3]]

            break

    # 补全中文前面的英文
    start = index - 1
    if start >= 0 and judge_alpha(context[start]):
        for i in range(start, -1, -1):
            if judge_alpha(context[i]):
                continue

            tmp = context[i + 1:index] + entity
            if len(tmp) - len(entity) <= 1:
                break

            if context[i + 1:index].lower() in ['app', 'cn', 'ceo', 'com']:
                break

            if context.count(entity) == context.count(tmp):
                # print(3, entity, tmp)
                return [tmp]
            break

    cnt = context.count(entity)

    for word in completion_words:
        new_entity = entity + word
        new_cnt = context.count(new_entity)
        if new_cnt > 0:
            if new_cnt == cnt:
                return [new_entity]
            if new_cnt >= 3:
                return [entity, new_entity]
                # print(new_entity)
            return [entity]

    for word in completion_words + ['平台', '挖矿']:
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

                return [new_entity]

    return [entity]


def post_process(results_path, complete_path):
    """
    后处理部分
    :param filename:
    :return:
    """
    print('Post process...')
    results = open(results_path).read().split('\n')
    # results = open('./res/best.csv').read().split('\n')
    if results[-1] == '':
        results = results[:-1]
    res = codecs.open(complete_path, 'w')
    # res = codecs.open('./res/best.csv', 'w')

    res.write('id,unknownEntities\n')

    with open('./data/Test_Data.csv', 'r', encoding='utf-8') as myFile:
        lines = list(csv.reader(myFile))
        if lines[-1] == '':
            lines = lines[:-1]
        # for i in tqdm(range(1, len(lines))):
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


def judge_illegal(entity, context):
    one_word = [w for w in completion_words if len(w) == 1]
    one_word += ['贷', '盘', '购', '狗']
    if context.count(entity) == 1:
        if not entity[-1].isdigit() and entity[-1] not in ['）', ')', '”', '’'] and not judge_alpha(entity[-1]):
            if entity[-1] not in one_word and all(judge_alpha(c) for c in entity[:-1]):
                return True
    return False


def delete_words(candidates, context):
    new_candidates = []
    for entity in candidates:
        if judge_illegal(entity, context):
            entity = entity[:-1]
        new_candidates.append(entity)

    return new_candidates


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

    candidates = complement_candidates(candidates, context)

    candidates = list(set(candidates))
    candidates = [check_punctuations(w, context) for w in candidates]
    candidates = list(set(candidates))

    candidates = verify_entity(candidates, context)
    candidates = [e for e in candidates if len(e) >= 2]

    candidates = [(each, context.count(each)) for each in candidates if each != '']
    candidates.sort(key=lambda k: (k[0], len(k[0])))

    de_duplicate = []
    for i in range(len(candidates) - 1):
        if candidates[i + 1][0].startswith(candidates[i][0]) \
                and (candidates[i][1] - candidates[i + 1][1]) < candidates[i + 1][1]:
            # print(cnt_candidates[i][0],cnt_candidates[i + 1][0])
            continue
        de_duplicate.append((candidates[i]))
    if len(candidates) > 0:
        de_duplicate.append(candidates[-1])

    # sort candidates
    rank_candidates = []
    for entity, cnt in de_duplicate:
        rank_candidates.append((cnt, context.find(entity), entity))
    # 排序规则，频率优先，位置靠前优先
    rank_candidates.sort(key=lambda k: (1000 - k[0], k[1]))

    # 删除出现一次靠后的长度为2的实体，比如：币圈
    res = [each[2] for each in rank_candidates[:3]]
    if len(rank_candidates) > 3:
        for cnt, _, entity in rank_candidates[3:]:
            if len(entity) == 2 and cnt == 1:
                continue
            res.append(entity)

    candidates = delete_words(res, context)

    return candidates


def is_known(entity):
    # 带有金融牌照的银行，证券，保险等机构
    if entity in dict_known:
        return True
    # 机构简称开头的实体可认为也是已知实体，需要去除
    for word in dict_known:
        if len(word) == 2:
            if entity.startswith(word):
                return True
        elif word in entity:
            return True

    return False


def should_remove(entity, candidates):
    if judge_pure_english(entity) and len(entity) <= 2:
        return True

    return False


def remove_entity(post_path, res_path):
    print('Removing entities...')
    results = open(post_path).read().split('\n')
    if results[-1] == '':
        results = results[:-1]
    res = codecs.open(res_path, 'w')
    res.write('id,unknownEntities\n')
    # train_text = codecs.open('./data/Train_Data.csv').read()

    tmp = set()
    cnt = 0

    remove_set = dict_oracle | remove_city | remove_train
    for line in tqdm(results[1:]):
        if ',' in line:
            id, entities = line.split(',')
            entities = entities.split(';')
            candidates = []
            for entity in entities:
                if entity in remove_set:
                    continue
                if is_known(entity):
                    continue

                if should_remove(entity, entities):
                    continue
                if entity in remove_select:
                    tmp.add(entity)
                    cnt += 1
                    continue

                # if entity in train_text:
                #     tmp.add(entity)
                #     cnt += 1
                candidates.append(entity)

            res.write('%s,%s\n' % (id, ';'.join(candidates)))
        else:
            res.write('%s\n' % line)

    tmp = list(tmp)
    tmp.sort(key=lambda k: (k, len(k)))
    for each in tmp:
        print(each)
    print(cnt)


def count_entity(filename):
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
    post_path = './res/post_results.csv'
    res_path = './res/results.csv'
    # gen_csv('./output/label_test.txt', results_path)

    # post_process(results_path, post_path)
    remove_entity(post_path, res_path)
    count_entity(res_path)
