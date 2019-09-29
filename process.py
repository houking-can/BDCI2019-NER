import csv
import json
import pandas as pd
import codecs
import re
from collections import Counter

dictionary = set(json.load(open('./data/dict.json'))['dict'])


def read_test():
    test_df = pd.read_csv('./data/Test_Data.csv')
    test_df['text'] = test_df['title'].fillna('') + '。' + test_df['text'].fillna('')
    return test_df


def read_train():
    train_df = pd.read_csv('./data/Train_Data.csv')
    train_df['text'] = train_df['title'].fillna('') + '。' + train_df['text'].fillna('')
    train_df = train_df[~train_df['unknownEntities'].isnull()]
    return train_df


def get_sentences(text, max_length=300):
    if len(text) < max_length - 2:
        return [text]
    tmp = re.split('。|！|？|；', text)
    sent = ''
    sentences = []
    for each in tmp:
        if len(sent + each) > max_length - 2:
            sentences.append(sent)
            sent = ''
        else:
            sent += each
    if sent != '':
        sentences.append(sent)

    return sentences


def gen_train():
    train_df = read_train()
    with codecs.open('./data/train.txt', 'w') as up:
        for row in train_df.iloc[:-200].itertuples():
            sentences = get_sentences(row.text)
            for sent in sentences:
                entities = str(row.unknownEntities).split(';')
                # 按长度进行排序
                entities = sorted(entities, key=lambda i: len(i))
                for entity in entities:
                    mark_sent = sent.replace(entity, 'Ё' + (len(entity) - 1) * 'Ж')
                for c1, c2 in zip(sent, mark_sent):
                    if c2 == 'Ё':
                        up.write('{0} {1}\n'.format(c1, 'B-ORG'))
                    elif c2 == 'Ж':
                        up.write('{0} {1}\n'.format(c1, 'I-ORG'))
                    else:
                        up.write('{0} {1}\n'.format(c1, 'O'))

                up.write('\n')

    with codecs.open('./data/dev.txt', 'w') as up:
        for row in train_df.iloc[-200:].itertuples():
            for sent in get_sentences(row.text):
                if len(sent) < 2:
                    continue
                entities = str(row.unknownEntities).split(';')
                entities = sorted(entities, key=lambda i: len(i))
                for entity in entities:
                    mark_sent = sent.replace(entity, 'Ё' + (len(entity) - 1) * 'Ж')
                for c1, c2 in zip(sent, mark_sent):
                    if c2 == 'Ё':
                        up.write('{0} {1}\n'.format(c1, 'B-ORG'))
                    elif c2 == 'Ж':
                        up.write('{0} {1}\n'.format(c1, 'I-ORG'))
                    else:
                        up.write('{0} {1}\n'.format(c1, 'O'))
                up.write('\n')


def gen_test():
    test_df = read_test()
    with codecs.open('./data/test.txt', 'w') as up:
        for row in test_df.iloc[:].itertuples():
            sentences = get_sentences(row.text)
            up.write('ЖЖ{0}ЖЖ {1}\n'.format(str(row.id), 'O'))
            for sent in sentences:
                for c1 in sent:
                    up.write('{0} {1}\n'.format(c1, 'O'))
                up.write('\n')


def filter_word(w, filter_known=False):
    w = w.replace('…', '')
    if len(w) == 1:
        return ''
    for bad_word in ['？', '《', '🔺', '️?', '!', '#', '%', '%', '，', 'Ⅲ', '》', '丨', '、', '）', '（', '​',
                     '👍', '。', '😎', '/', '】', '-', '⚠️', '：', '✅', '㊙️', '“', '”', ')', '(', '！', '🔥', ',']:
        if bad_word in w:
            return ''

    if filter_known and w in dictionary:
        print(w)
        return ''

    return w


def gen_csv():
    predict = codecs.open('./output/label_test.txt').read().split('\n\n')
    res = codecs.open('./res_with_filter.csv', 'w')
    res.write('id,unknownEntities\n')
    id = ''
    unknown_entities = set()
    for sent in predict:
        sent = sent.split('\n')
        entity = ''
        for each in sent:
            if each == '':
                continue
            tmp_id = re.findall('ЖЖ(.*?)ЖЖ', each)
            if len(tmp_id) == 1:
                if id != '':
                    res.write('{0},{1}\n'.format(id, ';'.join(list(unknown_entities))))
                id = tmp_id[0]
                unknown_entities = set()
                continue
            word, _, tag = each.split()
            if tag == 'B-ORG':
                entity = word
            elif tag == 'I-ORG':
                entity += word
            else:
                entity = filter_word(entity, filter_known=True)
                # entity = filter_word(entity, filter_known=False)
                if entity != '':
                    unknown_entities.add(entity)
                if tag == 'B-ORG':
                    entity = word
                else:
                    entity = ''

    res.write('{0},{1}\n'.format(id, ';'.join(list(unknown_entities))))
    res.close()


def process_train(build_dict=True):
    dictionary = set()
    with open('./data/old/Train_Data.csv', 'r', encoding='utf-8') as myFile:
        lines = list(csv.reader(myFile))
        none = []
        data = []
        for line in lines[1:]:
            line = clean(line)
            if len(line[3]) == 0:
                none.append(line)
            else:
                tmp = line[3].split(';')
                flag = True
                for each in tmp:
                    if len(each) > 30:  # 统计的先验
                        flag = False
                        break

                if flag:
                    if build_dict:
                        for each in tmp:
                            dictionary.add(each)
                    data.append(line)
                else:
                    line[3] = ''
                    none.append(line)

        if build_dict:
            json.dump({"dict": list(dictionary)}, open('./data/dict.json', 'w', encoding='utf-8'), ensure_ascii=False,
                      indent=4)

        headers = ['id', 'title', 'text', 'unknownEntities']
        with open('./data/Train_Data.csv', 'w', encoding='utf-8') as f:
            f_csv = csv.writer(f)
            f_csv.writerow(headers)
            f_csv.writerows(data)

        with open('./data/Train_Data_None.csv', 'w', encoding='utf-8') as f:
            f_csv = csv.writer(f)
            f_csv.writerow(headers)
            f_csv.writerows(none)


def process_test():
    with open('./data/old/Test_Data.csv', 'r', encoding='utf-8') as myFile:
        lines = list(csv.reader(myFile))
    data = []
    for line in lines[1:]:
        line = clean(line)
        data.append(line)
    headers = ['id', 'title', 'text']
    with open('./data/Test_Data.csv', 'w', encoding='utf-8') as f:
        f_csv = csv.writer(f)
        f_csv.writerow(headers)
        f_csv.writerows(data)


def clean(line):
    for i in range(1, len(line)):
        line[i] = re.sub('\s', '', line[i])
        line[i] = re.sub('\{IMG.*?\}', '', line[i])
        line[i] = re.sub('<.*?>', '', line[i])

        tmp = ''
        for each in line[i]:
            if each in ['，', '。', '？', '！', '：', ',', '.', '?', '!', ':']:
                if tmp != '' and tmp[-1] == each:
                    continue
            tmp += each
        line[i] = tmp
    # remove title is the same as text
    if len(line[1]) > 40 and line[2].startswith(line[1][:-9]):
        line[1] = ''
    return line


if __name__ == "__main__":
    process_train()
    process_test()
    gen_train()
    gen_test()
    # gen_csv()

    # train = read_train()
    # a = []
    # for row in train.iloc[:].itertuples():
    #     a.append(len(row.text))
    # b = Counter(a)
    # c = 0
    # d = 0
    # for key, value in b.items():
    #     if key < 300:
    #         c += value
    #     else:
    #         d += value
    # print(c, d)
