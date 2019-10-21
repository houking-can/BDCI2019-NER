import codecs
import csv
import re
from tqdm import tqdm
import pandas as pd
import random

oracle_dict = open('./data/dict/dict_oracle.txt').read().split('\n')
oracle_dict = [each.strip() for each in oracle_dict]
oracle_dict = set([each for each in oracle_dict if each != ''])

remove = set(open('./data/dict/remove.txt').read().split('\n'))
if '' in remove: remove.remove('')
remove = remove - oracle_dict
# res = codecs.open('./data/dict/remove.txt', 'w')
# aaa=sorted(list(remove), key=lambda k: (k, len(k)))
# res.write('\n'.join(aaa))
# res.close()
# print(oracle_dict & remove)

none_dict = set(open('./data/dict/dict_none.txt').read().split('\n'))
none_dict = [each.strip() for each in none_dict]
none_dict = set([each for each in none_dict if each != ''])
none_dict = none_dict - oracle_dict
# res = codecs.open('./data/dict/dict_none.txt', 'w')
# aaa=sorted(list(none_dict), key=lambda k: (k, len(k)))
# res.write('\n'.join(aaa))
# res.close()

test_dict = open('./data/dict/test_dict_0.txt').read().split('\n')
test_dict = [each.strip() for each in test_dict]
test_dict = set([each for each in test_dict if each != ''])
test_dict = test_dict - oracle_dict - none_dict - remove

train_dict = open('./data/dict/train_dict_2.txt').read().split('\n')
train_dict = [each.strip() for each in train_dict]
train_dict = set([each for each in train_dict if each != ''])
train_dict = train_dict - none_dict - oracle_dict - test_dict - remove
# res = codecs.open('./data/dict/train_dict_2.txt', 'w')
# aaa = sorted(list(train_dict), key=lambda k: (k, len(k)))
# res.write('\n'.join(aaa))
# res.close()

oracle_bio = list(oracle_dict | none_dict)
oracle_bio.sort(key=lambda e: len(e), reverse=True)

test_bio = list(test_dict)
test_bio.sort(key=lambda e: len(e), reverse=True)
none_bio = list(none_dict)
none_bio.sort(key=lambda e: len(e), reverse=True)


# bio_dict = [(each, 'oracle') for each in oracle_dict if each != '']
# bio_dict = bio_dict + [(each, 'none') for each in none_dict if each != '']
# bio_dict = bio_dict + [(each, 'test') for each in test_dict if each != '']
# bio_dict = bio_dict + [(each, 'train') for each in train_dict if each != '']

# bio_dict.sort(key=lambda e: len(e[0]), reverse=True)


def read_csv():
    train_df = pd.read_csv('./data/Train_Data.csv')
    train_df['text'] = train_df['title'].fillna('') + '。' + train_df['text'].fillna('')

    test_df = pd.read_csv('./data/Test_Data.csv')
    test_df['text'] = test_df['title'].fillna('') + '。' + test_df['text'].fillna('')
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

    return train_df, test_df


def get_sentences(text, max_length=512):
    # if len(text) <= max_length - 2:
    #     return [text]
    tmp = re.split('(。|！|？|；|，|\?|\!)', text)
    sent = ''
    sentences = []
    if tmp[-1] != '':
        tmp.append('。')
    else:
        tmp = tmp[:-1]

    i = 0
    while i < len(tmp) - 1:

        if len(sent + tmp[i] + tmp[i + 1]) > max_length - 2:
            sentences.append(sent)
            sent = ''
        if tmp[i] != '':
            sent += (tmp[i] + tmp[i + 1])
        i += 2
    if sent != '':
        sentences.append(sent)

    return sentences


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
        return None


def label_sent(sent):
    bio_list = ['O' for _ in range(len(sent))]
    for entity in oracle_bio:
        index = find_all(entity, sent)
        if index:
            if judge_pure_english(entity):
                for start in index:
                    if start > 0 and sent[start - 1].isalpha():
                        continue
                    elif start + len(entity) < len(sent) and sent[start + len(entity)].isalpha():
                        continue
                    bio_list[start] = 'B-ORG'
                    for k in range(start + 1, start + len(entity)):
                        bio_list[k] = 'I-ORG'

            else:
                for start in index:
                    bio_list[start] = 'B-ORG'
                    for k in range(start + 1, start + len(entity)):
                        bio_list[k] = 'I-ORG'

    # for entity in test_bio:
    #     index = find_all(entity, sent)
    #     if index:
    #         if judge_pure_english(entity):
    #             for start in index:
    #                 if start > 0 and sent[start - 1].isalpha():
    #                     continue
    #                 elif start + len(entity) < len(sent) and sent[start+len(entity)].isalpha():
    #                     continue
    #                 bio_list[start] = 'B-TEST'
    #                 for k in range(start + 1, start + len(entity)):
    #                     bio_list[k] = 'I-TEST'
    #
    #         else:
    #             for start in index:
    #                 bio_list[start] = 'B-TEST'
    #                 for k in range(start + 1, start + len(entity)):
    #                     bio_list[k] = 'I-TEST'

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

    return bio_list


def gen_bio():
    train_df, test_df = read_csv()

    # gen train
    print("generate train...")
    rows = [each for each in train_df.iloc[:].itertuples()]
    with codecs.open('./data/train.txt', 'w') as up:
        for row in tqdm(rows):
            sentences = get_sentences(row.text)
            up.write('Ж{0}Ж {1}\n'.format(str(row.id), 'O'))
            for i, sent in enumerate(sentences):
                bio_list = label_sent(sentences[i])
                for i, c in enumerate(sentences[i]):
                    up.write('{0} {1}\n'.format(c, bio_list[i]))
                up.write('\n')
    # gen dev
    print("generate dev...")
    with codecs.open('./data/dev.txt', 'w') as up:
        rows = random.sample([each for each in train_df.iloc[:].itertuples()], 100)
        for row in tqdm(rows):
            sentences = get_sentences(row.text)
            up.write('Ж{0}Ж {1}\n'.format(str(row.id), 'O'))
            for i, sent in enumerate(sentences):
                bio_list = label_sent(sentences[i])
                for i, c in enumerate(sentences[i]):
                    up.write('{0} {1}\n'.format(c, bio_list[i]))
                up.write('\n')
    # gen test
    print("generate test...")
    with codecs.open('./data/test.txt', 'w') as up:
        rows = [each for each in test_df.iloc[:].itertuples()]
        for row in tqdm(rows):
            sentences = get_sentences(row.text)
            up.write('Ж{0}Ж {1}\n'.format(str(row.id), 'O'))
            for sent in sentences:
                for c1 in sent:
                    up.write('{0} {1}\n'.format(c1, 'O'))
                up.write('\n')


def pre_process():
    print('process train.csv...')
    with open('./data/old/Train_Data_Hand.csv', 'r', encoding='utf-8') as myFile:
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

    print('process test.csv...')
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
            line[i] = re.sub('\<.*?\>', '', line[i])

    return line


if __name__ == "__main__":
    # pass
    pre_process()
    gen_bio()
