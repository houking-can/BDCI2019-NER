import codecs
import csv
import re
from tqdm import tqdm
import pandas as pd
import random

dict_oracle = open('./data/dict/dict_oracle.txt').read().split('\n')
dict_oracle = [each.strip() for each in dict_oracle]
dict_oracle = set([each for each in dict_oracle if each != ''])

dict_known = open('./data/dict/dict_known.txt').read().split('\n')
dict_known = [each.strip() for each in dict_known]
dict_known = set([each for each in dict_known if each != ''])

bio_none = set(open('./data/dict/bio_none.txt').read().split('\n'))
bio_none = [each.strip() for each in bio_none]
bio_none = set([each for each in bio_none if each != ''])
bio_none = bio_none - dict_oracle

bio_train = open('./data/dict/bio_train.txt').read().split('\n')
bio_train = [each.strip() for each in bio_train]
bio_train = set([each for each in bio_train if each != ''])
bio_train = bio_train - dict_oracle

label_bio = list(dict_oracle | bio_none | bio_train | dict_known)
label_bio.sort(key=lambda e: len(e), reverse=True)


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

def judge_alpha(c):
    unicode_id = ord(c)
    if (unicode_id<=122 and unicode_id>=97) or (unicode_id<=90 and unicode_id>=65):
        return True
    return False

def label_sent(sent):
    bio_list = ['O' for _ in range(len(sent))]
    for entity in label_bio:
        index = find_all(entity, sent)
        if index:
            if judge_pure_english(entity):
                for start in index:
                    if all(ch == 'O' for ch in bio_list[start:start + len(entity)]):
                        if start > 0 and judge_alpha(sent[start - 1]):
                            continue
                        elif start + len(entity) < len(sent) and judge_alpha(sent[start + len(entity)]):
                            continue
                        bio_list[start] = 'B-ORG'
                        for k in range(start + 1, start + len(entity)):
                            bio_list[k] = 'I-ORG'

            else:
                for start in index:
                    if all(ch == 'O' for ch in bio_list[start:start + len(entity)]):
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
    train_rows = rows[:-100]
    random.shuffle(train_rows)
    with codecs.open('./data/train.txt', 'w') as up:
        for row in tqdm(train_rows):
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
        # rows = random.sample([each for each in train_df.iloc[:].itertuples()], 100)
        test_rows = rows[-100:]
        for row in tqdm(test_rows):
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
    with open('./data/oracle/Train_Data_Hand.csv', 'r', encoding='utf-8') as myFile:
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
    with open('./data/oracle/Test_Data.csv', 'r', encoding='utf-8') as myFile:
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


def judge_code(s):
    cnt = 0
    for each in s:
        if ord(each) < 128:
            cnt += 1
    if cnt / len(s) > 0.9:
        return True

    return False


def clean(line):
    http_pattern = 'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'
    www_pattern = 'www\.(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'
    for i in range(1, 3):
        if line[i] != '':
            line[i] = line[i].replace('▋', '，')
            line[i] = line[i].replace("\xa0", "")
            line[i] = line[i].replace("\b", "")
            line[i] = line[i].replace('"', "")
            line[i] = re.sub("\t|\n|\x0b|\x1c|\x1d|\x1e", "", line[i])
            line[i] = line[i].strip()
            line[i] = re.sub('\?\?+', '', line[i])
            line[i] = re.sub('\{IMG:.?.?.?\}', '', line[i])
            line[i] = re.sub('\<.*?\>', '', line[i])
            line[i] = re.sub('\u3000+', '，', line[i])
            line[i] = re.sub(http_pattern, '，', line[i])
            line[i] = re.sub(www_pattern, '，', line[i])
            line[i] = re.sub('https://', '', line[i])
            line[i] = re.sub('http://', '', line[i])
            line[i] = re.sub('window.public=.*\(window,document\);', '，', line[i])
            line[i] = re.sub('varcontentConEle=.*AD_SURVEY_Add_AdPos\(.*\);', '，', line[i])
            line[i] = re.sub('function\(\).*\(\);', '，', line[i])
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

    return line


if __name__ == "__main__":
    pre_process()
    gen_bio()
