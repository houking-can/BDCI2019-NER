import codecs
import csv
import re
from tqdm import tqdm
import pandas as pd
import random
import os
import shutil

dict_oracle_1 = open('./data/dict/dict_oracle_1.txt').read().split('\n')
dict_oracle_1 = [each.strip() for each in dict_oracle_1]
dict_oracle_1 = set([each for each in dict_oracle_1 if each != ''])

dict_oracle_2 = open('./data/dict/dict_oracle_2.txt').read().split('\n')
dict_oracle_2 = [each.strip() for each in dict_oracle_2]
dict_oracle_2 = set([each for each in dict_oracle_2 if each != ''])

dict_oracle = dict_oracle_1 | dict_oracle_2

dict_known = open('./data/dict/dict_known.txt').read().split('\n')
dict_known = [each.strip() for each in dict_known]
dict_known = set([each for each in dict_known if each != ''])

bio_none = set(open('./data/dict/bio_none.txt').read().split('\n'))
bio_none = [each.strip() for each in bio_none]
bio_none = set([each for each in bio_none if each != ''])
bio_none = bio_none - dict_oracle

bio_train_1 = open('./data/dict/bio_train_1.txt').read().split('\n')
bio_train_1 = [each.strip() for each in bio_train_1]
bio_train_1 = set([each for each in bio_train_1 if each != ''])
bio_train_1 = bio_train_1 - dict_oracle

bio_train_2 = open('./data/dict/bio_train_2.txt').read().split('\n')
bio_train_2 = [each.strip() for each in bio_train_2]
bio_train_2 = set([each for each in bio_train_2 if each != ''])
bio_train_2 = bio_train_2 - dict_oracle - bio_train_1

bio_train = bio_train_1 | bio_train_2
bio_remove = open('./data/dict/bio_remove.txt').read().split('\n')
bio_remove = [each.strip() for each in bio_remove]
bio_remove = set([each for each in bio_remove if each != ''])

dict_train = open('./data/dict/dict_train.txt').read().split('\n')
dict_train = [each.strip() for each in dict_train]
dict_train = set([each for each in dict_train if each != ''])

remove_city = open('./data/dict/remove_city.txt').read().split('\n')
remove_city = [each.strip() for each in remove_city]
remove_city = set([each for each in remove_city if each != ''])

label_bio = dict_oracle | bio_none | bio_train | dict_known
label_bio = list(label_bio - bio_remove - remove_city)

label_bio.sort(key=lambda e: len(e), reverse=True)

brat_path = '/home/yhj/software/brat-v1.3_Crunchy_Frog/data/BDCI'
done_path = '/home/yhj/software/brat-v1.3_Crunchy_Frog/data/Done'


def read_csv():
    train_df_1 = pd.read_csv('./data/Round1_Train.csv')
    train_df_1['text'] = train_df_1['title'].fillna('') + '。' + train_df_1['text'].fillna('')

    train_df_2 = pd.read_csv('./data/Round2_Train.csv')
    train_df_2['text'] = train_df_2['title'].fillna('') + '。' + train_df_2['text'].fillna('')

    test_df = pd.read_csv('./data/Round2_Test.csv')
    test_df['text'] = test_df['title'].fillna('') + '。' + test_df['text'].fillna('')
    additional_chars = set()
    for t in list(test_df.text) + list(train_df_1.text) + list(train_df_2.text):
        additional_chars.update(re.findall(u'[^\u4e00-\u9fa5a-zA-Z0-9\*]', t))

    extra_chars = set("!#$%&\()*+,-./:;<=>?@[\\]^_`{|}~！#￥%&？《》{}“”，：‘’。（）·、；【】")
    additional_chars = additional_chars.difference(extra_chars)

    def remove_additional_chars(input):
        for x in additional_chars:
            input = input.replace(x, "")
        return input

    train_df_1["text"] = train_df_1["text"].apply(remove_additional_chars)
    train_df_2["text"] = train_df_2["text"].apply(remove_additional_chars)
    test_df["text"] = test_df["text"].apply(remove_additional_chars)

    return train_df_1, train_df_2, test_df


def get_sentences(text, max_length=512):
    # if len(text) <= max_length - 2:
    #     return [text]
    tmp = re.split('(。|！|？|；|，|\?|\!)', text)
    sentences = []
    if tmp[-1] != '':
        tmp.append('。')
    else:
        tmp = tmp[:-1]
    xx = []
    for each in tmp:
        if len(each) > max_length - 2:
            xx.extend(re.findall(r'.{%d}' % (max_length - 2), each))
            tail = len(each) % (max_length - 2)
            if len(each[-tail:]) > 0:
                xx.append(each[-tail:])
        else:
            xx.append(each)
    tmp = xx
    i = 0
    sent = ''
    while i < len(tmp):
        if len(tmp[i]) == max_length - 2:
            if sent != '':
                sentences.append(sent)
                sent = ''
            sentences.append(tmp[i])
            i += 1
            continue
        if len(sent + tmp[i]) > max_length - 2:
            sentences.append(sent)
            sent = tmp[i]
            i += 1
            continue
        sent += tmp[i]
        i += 1

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
    if (unicode_id <= 122 and unicode_id >= 97) or (unicode_id <= 90 and unicode_id >= 65):
        return True
    return False


def label_sent(sent, label_bio):
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

    return bio_list


def gen_bio(shuffle=True):
    train_df_1, train_df_2, test_df = read_csv()

    # gen train
    print("generate train...")
    train_rows_1 = [each for each in train_df_1.iloc[:].itertuples()]
    train_rows_2 = [each for each in train_df_2.iloc[:].itertuples()]
    train_rows = train_rows_1 + train_rows_2
    dev_rows = train_rows[::50]
    index = [i for i in range(len(train_rows))]
    dev_index = set(index[::50])
    train_rows = [train_rows[i] for i in range(len(train_rows)) if i not in dev_index]

    if shuffle:
        random.shuffle(train_rows)
    with codecs.open('./data/train.txt', 'w') as up:
        for row in tqdm(train_rows):
            sentences = get_sentences(row.text)
            up.write('Ж{0}Ж {1}\n'.format(str(row.id), 'O'))
            for i, sent in enumerate(sentences):
                bio_list = label_sent(sentences[i], label_bio)
                for i, c in enumerate(sentences[i]):
                    up.write('{0} {1}\n'.format(c, bio_list[i]))
                up.write('\n')

    # gen dev

    # print("generate dev...")
    # with codecs.open('./data/dev.txt', 'w') as up:
    #     # rows = random.sample([each for each in train_df.iloc[:].itertuples()], 100)
    #     for row in tqdm(dev_rows):
    #         sentences = get_sentences(row.text)
    #         up.write('Ж{0}Ж {1}\n'.format(str(row.id), 'O'))
    #         for i, sent in enumerate(sentences):
    #             bio_list = label_sent(sentences[i], label_bio)
    #             for i, c in enumerate(sentences[i]):
    #                 up.write('{0} {1}\n'.format(c, bio_list[i]))
    #             up.write('\n')

    # gen test
    # print("generate test...")
    # with codecs.open('./data/test.txt', 'w') as up:
    #     rows = [each for each in test_df.iloc[:].itertuples()]
    #     for row in tqdm(rows):
    #         sentences = get_sentences(row.text)
    #         up.write('Ж{0}Ж {1}\n'.format(str(row.id), 'O'))
    #         for sent in sentences:
    #             for c1 in sent:
    #                 up.write('{0} {1}\n'.format(c1, 'O'))
    #             up.write('\n')
    # print("generate test...")
    # with codecs.open('./data/test_1.txt', 'w') as up:
    #     rows = [each for each in train_df_1.iloc[:].itertuples()]
    #     for row in tqdm(rows):
    #         sentences = get_sentences(row.text)
    #         up.write('Ж{0}Ж {1}\n'.format(str(row.id), 'O'))
    #         for sent in sentences:
    #             for c1 in sent:
    #                 up.write('{0} {1}\n'.format(c1, 'O'))
    #             up.write('\n')
    # print("generate test...")
    # with codecs.open('./data/test_2.txt', 'w') as up:
    #     rows = [each for each in train_df_2.iloc[:].itertuples()]
    #     for row in tqdm(rows):
    #         sentences = get_sentences(row.text)
    #         up.write('Ж{0}Ж {1}\n'.format(str(row.id), 'O'))
    #         for sent in sentences:
    #             for c1 in sent:
    #                 up.write('{0} {1}\n'.format(c1, 'O'))
    #             up.write('\n')


def pre_process():
    print('process Round1 train.csv...')
    # with open('./data/oracle/Train_Data_Hand.csv', 'r', encoding='utf-8') as myFile:
    with open('./data/oracle/Train_Data_Hand.csv', 'r', encoding='utf-8') as myFile:
        lines = list(csv.reader(myFile))
        data = []
        for line in lines[1:]:
            line = clean(line)
            data.append(line)

        headers = ['id', 'title', 'text', 'unknownEntities']
        with open('./data/Round1_Train.csv', 'w', encoding='utf-8') as f:
            f_csv = csv.writer(f)
            f_csv.writerow(headers)
            f_csv.writerows(data)

    print('process Round2 train.csv...')
    # with open('./data/oracle/Train_Data_Hand.csv', 'r', encoding='utf-8') as myFile:
    with open('./data/oracle/Round2_train.csv', 'r', encoding='utf-8') as myFile:
        lines = list(csv.reader(myFile))
        data = []
        for line in lines[1:]:
            line = clean(line)
            data.append(line)

        headers = ['id', 'title', 'text', 'unknownEntities']
        with open('./data/Round2_Train.csv', 'w', encoding='utf-8') as f:
            f_csv = csv.writer(f)
            f_csv.writerow(headers)
            f_csv.writerows(data)

    print('process Round2 test.csv...')
    # with open('./data/oracle/Test_Data.csv', 'r', encoding='utf-8') as myFile:
    with open('./data/oracle/Round2_Test.csv', 'r', encoding='utf-8') as myFile:
        lines = list(csv.reader(myFile))
        data = []
        for line in lines[1:]:
            line = clean(line)
            data.append(line)
        headers = ['id', 'title', 'text']
        with open('./data/Round2_Test.csv', 'w', encoding='utf-8') as f:
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
            line[i] = re.sub('\?\?+', '？', line[i])
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
            line[i] = line[i].replace(',', '，')

    return line


def gen_brat():
    train_df_1, train_df_2, _ = read_csv()

    # gen train

    train_rows_1 = [each for each in train_df_1.iloc[:].itertuples()]
    train_rows_2 = [each for each in train_df_2.iloc[:].itertuples()]
    train_rows = train_rows_1 + train_rows_2
    # dev_rows = train_rows[::50]
    index = [i for i in range(len(train_rows))]
    dev_index = set(index[::50])
    train_rows = [train_rows[i] for i in range(len(train_rows)) if i not in dev_index]

    print("generate train brat...")
    i = 0
    for row in tqdm(train_rows):
        if i % 2500 == 0:
            save_path = os.path.join(brat_path, 'train_%d' % (i // 2500))
            if not os.path.exists(save_path):
                os.makedirs(save_path)
            shutil.copy(os.path.join(brat_path, 'annotation.conf'), save_path)
        id = (4 - len(str(i))) * '0' + str(i)
        sentences = get_sentences(row.text, max_length=50)
        text = '\n'.join(sentences)
        with open(os.path.join(save_path, '%s_%s.txt' % (id, row.id)), 'w', encoding='utf-8') as f:
            f.write(text)
        with open(os.path.join(save_path, '%s_%s.ann' % (id, row.id)), 'w', encoding='utf-8') as f:
            bio_list = label_sent(text, label_bio)
            cnt = 1
            k = 0
            while k < len(bio_list):
                if bio_list[k] == 'B-ORG':
                    start = k
                    k += 1
                    while k < len(bio_list) and bio_list[k] == 'I-ORG':
                        k += 1
                    entity = text[start:k]
                    if entity in dict_oracle:
                        f.write('T%d\tOracle %d %d\t%s\n' % (cnt, start, k, entity))
                    else:
                        f.write('T%d\tAddition %d %d\t%s\n' % (cnt, start, k, entity))
                    cnt += 1
                else:
                    k += 1

        i += 1

    # print("generate dev brat...")
    # start = 164
    # i = start
    # save_path = os.path.join(brat_path, 'dev')
    # if not os.path.exists(save_path):
    #     os.makedirs(save_path)
    # shutil.copy(os.path.join(brat_path, 'annotation.conf'), save_path)
    # for row in tqdm(dev_rows[start:]):
    #     id = (4 - len(str(i))) * '0' + str(i)
    #     sentences = get_sentences(row.text, max_length=50)
    #     text = '\n'.join(sentences)
    #     with open(os.path.join(save_path, '%s_%s.txt' % (id, row.id)), 'w', encoding='utf-8') as f:
    #         f.write(text)
    #     with open(os.path.join(save_path, '%s_%s.ann' % (id, row.id)), 'w', encoding='utf-8') as f:
    #         bio_list = label_sent(text, label_bio)
    #         cnt = 1
    #         k = 0
    #         while k < len(bio_list):
    #             if bio_list[k] == 'B-ORG':
    #                 start = k
    #                 k += 1
    #                 while k < len(bio_list) and bio_list[k] == 'I-ORG':
    #                     k += 1
    #                 entity = text[start:k]
    #                 if entity in dict_oracle:
    #                     f.write('T%d\tOracle %d %d\t%s\n' % (cnt, start, k, entity))
    #                 else:
    #                     f.write('T%d\tAddition %d %d\t%s\n' % (cnt, start, k, entity))
    #                 cnt += 1
    #             else:
    #                 k += 1
    #
    #     i += 1


def iter_files(path):
    """Walk through all files located under a root path."""
    if os.path.isfile(path):
        yield path
    elif os.path.isdir(path):
        for dir_path, _, file_names in os.walk(path):
            for f in file_names:
                yield os.path.join(dir_path, f)
    else:
        raise RuntimeError('Path %s is invalid' % path)


# def move_done(end):
#     files = os.listdir(brat_path_1)
#     if 'annotation.conf' in files:
#         files.remove('annotation.conf')
#     if '.stats_cache' in files:
#         files.remove('.stats_cache')
#     files.sort()
#     for each in files[:2 * end]:
#         shutil.copy(os.path.join(brat_path_1, each), done_path)

def gen_bio_hand(shuffle=True):
    _, _, test_df = read_csv()

    # gen train

    # print("generate train...")
    # dirs = os.listdir(brat_path)
    # train_dirs = [os.path.join(brat_path, each) for each in dirs if 'train' in each]
    # train_dirs.sort()
    # train_files = []
    # for dir in train_dirs:
    #     train_files.extend(list(iter_files(dir)))
    # train_files = [each for each in train_files if each.endswith('ann') or each.endswith('txt')]
    # train_files.sort()
    # train_files = [(train_files[i], train_files[i + 1]) for i in range(0, len(train_files) - 1, 2)]
    #

    # if shuffle:
    #     random.shuffle(train_files)

    # with codecs.open('./data/train.txt', 'w') as up:
    #     for ann, txt in tqdm(train_files):
    #         text = codecs.open(txt).read()
    #         text = text.replace('\n', '')
    #
    #         id = ann[:-4].split('_')[-1]
    #         up.write('Ж{0}Ж {1}\n'.format(id, 'O'))
    #         labels = set()
    #         lines = codecs.open(ann).read().split('\n')
    #         for line in lines:
    #             if len(line) > 0:
    #                 line = line.split()
    #                 labels.add(line[-1])
    #         labels = list(labels)
    #         labels.sort(key=lambda k: len(k), reverse=True)
    #
    #         sentences = get_sentences(text)
    #         for i, sent in enumerate(sentences):
    #             bio_list = label_sent(sent, labels)
    #             for k, c in enumerate(sentences[i]):
    #                 up.write('{0} {1}\n'.format(c, bio_list[k]))
    #             up.write('\n')

    # gen dev
    print("generate dev...")
    dev_dir = os.path.join(brat_path, 'dev')
    dev_files = iter_files(dev_dir)
    dev_files = [each for each in dev_files if each.endswith('ann') or each.endswith('txt')]
    dev_files.sort()
    dev_files = [(dev_files[i], dev_files[i + 1]) for i in range(0, len(dev_files) - 1, 2)]

    with codecs.open('./data/dev.txt', 'w') as up:
        # for ann, txt in tqdm(dev_files):

        for ann, txt in dev_files:
            text = codecs.open(txt).read()
            text = text.replace('\n', '')

            id = ann[:-4].split('_')[-1]
            up.write('Ж{0}Ж {1}\n'.format(id, 'O'))
            labels = set()
            lines = codecs.open(ann).read().split('\n')
            for line in lines:
                if len(line) > 0:
                    line = line.split('\t')
                    label = line[-1].replace(' ', '')
                    labels.add(label)
            labels = list(labels)
            labels.sort(key=lambda k: len(k), reverse=True)

            sentences = get_sentences(text)
            for i, sent in enumerate(sentences):
                bio_list = label_sent(sent, labels)
                for k, c in enumerate(sentences[i]):
                    up.write('{0} {1}\n'.format(c, bio_list[k]))
                up.write('\n')
    # gen test
    # print("generate test...")
    # with codecs.open('./data/test.txt', 'w') as up:
    #     rows = [each for each in test_df.iloc[:].itertuples()]
    #     for row in tqdm(rows):
    #         sentences = get_sentences(row.text)
    #         up.write('Ж{0}Ж {1}\n'.format(str(row.id), 'O'))
    #         for sent in sentences:
    #             for c1 in sent:
    #                 up.write('{0} {1}\n'.format(c1, 'O'))
    #             up.write('\n')


if __name__ == "__main__":
    # pre_process()
    # gen_bio()
    # gen_bio_hand()
    # gen_bio(shuffle=False, split=False)

    gen_brat()
    # move_done(end=135)
