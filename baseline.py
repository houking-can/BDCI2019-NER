import pandas as pd
import codecs
import re
from preprocess import process_test, process_train


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


def gen_dataset():
    train_df = read_train()
    test_df = read_test()
    with codecs.open('./data/train.txt', 'w') as up:
        for row in train_df.iloc[:-300].itertuples():
            sentences = re.split('。|！|\!|\.|？|\?', row.text)
            for sent in sentences:
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
            for sent in re.split('。|！|\!|\.|？|\?', row.text):
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
            for sent in re.split('。|！|\!|\.|？|\?', row.text):
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


if __name__ == "__main__":
    # process_train()
    # process_test()
    gen_dataset()
