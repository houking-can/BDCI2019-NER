import codecs
import csv
import re

import pandas as pd

dictionary = set(open('./data/dict.txt').read().split('\n'))


def read_csv():
    train_df = pd.read_csv('./data/Train_Data.csv')
    train_df['text'] = train_df['title'].fillna('') + '。' + train_df['text'].fillna('')
    train_df = train_df[~train_df['unknownEntities'].isnull()]

    test_df = pd.read_csv('./data/Test_Data.csv')
    test_df['text'] = test_df['title'].fillna('') + '。' + test_df['text'].fillna('')
    return train_df, test_df


def get_sentences(text, max_length=300):
    if len(text) <= max_length - 2:
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


def gen_bio():
    train_df, test_df = read_csv()
    additional_chars = set()
    for t in list(test_df.text) + list(train_df.text):
        additional_chars.update(re.findall(u'[^\u4e00-\u9fa5a-zA-Z0-9\*]', t))

    extra_chars = set("!#$%&\()*+,-./:;<=>?@[\\]^_`{|}~！#￥%&？《》{}“”，：‘’。（）·、；【】")
    additional_chars = additional_chars.difference(extra_chars)

    def remove_additional_chars(input):
        for x in additional_chars:
            input = input.replace(x, "")
        return input

    train_df["text"] = train_df["text"].apply(remove_additional_chars)
    test_df["text"] = test_df["text"].apply(remove_additional_chars)

    # gen train
    print("generate train...")
    with codecs.open('./data/train.txt', 'w') as up:
        for row in train_df.iloc[:-300].itertuples():
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

    # gen dev
    print("generate dev...")
    with codecs.open('./data/dev.txt', 'w') as up:
        for row in train_df.iloc[-300:].itertuples():
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
    # gen test
    print("generate test...")
    with codecs.open('./data/test.txt', 'w') as up:
        for row in test_df.iloc[:].itertuples():
            sentences = get_sentences(row.text)
            up.write('ЖЖ{0}ЖЖ {1}\n'.format(str(row.id), 'O'))
            for sent in sentences:
                for c1 in sent:
                    up.write('{0} {1}\n'.format(c1, 'O'))
                up.write('\n')


def filter_word(w):
    add_char = {']', '：', '~', '！', '%', '[', '《', '】', ';', '”', ':', '》', '？', '>', '/', '#', '。', '；', '&', '=', '，',
                '“', '【'}
    if len(w) == 1:
        return ''
    if re.findall("\\" + "|\\".join(add_char), w):
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
                entity = filter_word(entity)
                if entity != '':
                    unknown_entities.add(entity)
                if tag == 'B-ORG':
                    entity = word
                else:
                    entity = ''

    res.write('{0},{1}\n'.format(id, ';'.join(list(unknown_entities))))
    res.close()


def process_data():
    with open('./data/old/Train_Data.csv', 'r', encoding='utf-8') as myFile:
        lines = list(csv.reader(myFile))
        data = []
        for line in lines[1:]:
            line = clean(line)
            data.append(line)

        headers = ['id', 'title', 'text', 'unknownEntities']
        with open('./data/Train_Data.csv', 'w', encoding='utf-8') as f:
            f_csv = csv.writer(f)
            f_csv.writerow(headers)
            f_csv.writerows(data)

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
    # remove title is the same as text
    if len(line[1]) > 40 and line[2].startswith(line[1][:-9]):
        line[1] = ''
    for i in range(1, 3):
        if line[i] != '':
            line[i] = line[i].replace(",", "，")
            line[i] = line[i].replace("\xa0", "")
            line[i] = line[i].replace("\b", "")
            line[i] = line[i].replace('"', "")
            line[i] = re.sub("\t|\n|\x0b|\x1c|\x1d|\x1e", "", line[i])
            line[i] = line[i].strip()
            line[i] = re.sub('\?\?+', '', line[i])
            line[i] = re.sub('\{IMG:.?.?.?\}', '', line[i])
            line[i] = re.sub('\t|\n', '', line[i])
    return line


if __name__ == "__main__":
    process_data()
    gen_bio()
    # gen_csv()
