import csv
import json
import pandas as pd
import codecs
import re


def stop_words(x):
    try:
        x = x.strip()
    except:
        return ''
    x = re.sub('\?\?+', '', x)
    x = re.sub('\{IMG:.?.?.?\}', '', x)
    return x


def read_test():
    test_df = pd.read_csv('./data/Test_Data.csv')
    test_df['text'] = test_df['title'].fillna('') + '。' + test_df['text'].fillna('')
    return test_df


def read_train():
    train_df = pd.read_csv('./data/Train_Data.csv')
    train_df['text'] = train_df['title'].fillna('') + '。' + train_df['text'].fillna('')
    train_df = train_df[~train_df['unknownEntities'].isnull()]
    return train_df


def get_sentences(text):
    sentences = []
    tmp = re.split('。|！|\!|\.|？|\?', text)
    for sent in tmp:
        if len(sent) > 126:
            sentences.extend(re.split(',|，', sent))
        else:
            sentences.append(sent)
    return sentences


def gen_dataset():
    train_df = read_train()
    test_df = read_test()
    with codecs.open('./data/train.txt', 'w') as up:
        for row in train_df.iloc[:-300].itertuples():
            for sent in get_sentences(row.text):
                if len(sent) < 2:
                    continue
                entities = str(row.unknownEntities).split(';')
                # if '香港鑫泓' in entities:
                #     a = 1
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
        for row in train_df.iloc[-300:].itertuples():
            for sent in get_sentences(row.text):
                if len(sent) < 2:
                    continue
                entities = str(row.unknownEntities).split(';')
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

    with codecs.open('./data/test.txt', 'w') as up:
        for row in test_df.iloc[:].itertuples():
            for sent in get_sentences(row.text):
                for c1 in sent:
                    up.write('{0} {1}\n'.format(c1, 'O'))
                up.write('\n')


def filter_word(w):
    for bad_word in ['？', '《', '🔺', '️?', '!', '#', '%', '%', '，', 'Ⅲ', '》', '丨', '、', '）', '（', '​',
                     '👍', '。', '😎', '/', '】', '-', '⚠️', '：', '✅', '㊙️', '“', '”', ')', '(', '！', '🔥', ',']:
        if bad_word in w:
            return ''
    return w


def gen_csv():
    test_pred = codecs.open('./output/result_dir/label_test.txt').readlines()
    test_df = read_test()
    pred_tag = []
    pred_word = []

    pred_line_tag = ''
    pred_line_word = ''

    for line in test_pred:
        line = line.strip()

        if len(line) == 0 or line == '':
            pred_tag.append(pred_line_tag)
            pred_word.append(pred_line_word)
            pred_line_tag = ''
            pred_line_word = ''
            continue

        c, _, tag = line.split(' ')

        if tag != 'O':
            tag = tag[1:]
            pred_line_word += c
        else:
            pred_line_word += ';'

        pred_line_tag += tag

    with codecs.open('baseline2.csv', 'w') as up:
        up.write('id,unknownEntities\n')
        for word, id in zip(pred_word, test_df['id'].values):
            word = set([filter_word(x) for x in word.split(';') if x not in ['', ';'] and len(x) > 1])
            word = [x for x in word if x != '']

            if len(word) == 0:
                word = ['我们']

            word = ';'.join(list(word))
            up.write('{0},{1}\n'.format(id, word))


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

        print(len(none), len(data), len(lines) - 1)
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

    return line


if __name__ == "__main__":
    # process_train()
    # process_test()
    gen_dataset()
