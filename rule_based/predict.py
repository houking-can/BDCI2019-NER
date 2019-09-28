import csv
import json
from tqdm import tqdm
from preprocess import process_test

punctuation = open('./data/punctuation.txt', encoding='utf-8').read().split()


def find_entity(example):
    id = example[0]
    title = example[1]
    text = example[2]

    entity = set()
    res = []

    content = title + ' ' + text
    max_span = min(20, len(content) // 2)
    if max_span == 0:
        return []
    for span in range(max_span, 1, -1):
        if span >= len(content):
            continue
        for i in range(0, len(content) - span):
            sub_str = content[i:i + span]
            flag = True
            for p in punctuation:
                if p in sub_str:
                    flag = False
                    break
            if flag:
                cnt = 1
                for j in range(i + span + 1, len(content) - span):
                    if sub_str == content[j:j + span]:
                        cnt += 1
                if cnt >= 3 and (sub_str not in entity):
                    entity.add(sub_str)
                    res.append((cnt, sub_str))

    res.sort(reverse=True)
    return res


def match(label, predict):
    label = set(label)
    predict = set(predict)
    return len(label & predict), len(predict), len(label)


if __name__ == "__main__":
    mode = "Test"
    dictionary = set(json.load(open('./data/dict.json', encoding='utf-8'))['dict'])
    process_test()
    print("preprocess done!")
    test = json.load(open('./data/%s_Data.json' % mode, encoding='utf-8'))['examples']
    all_correct = 0
    all_predict = 0
    all_label = 0

    headers = ['id', 'unknownEntities']
    rows = []
    for example in tqdm(test):
        entity = find_entity(example)[:3]
        x = [e[1] for e in entity]
        tmp = [e[1] for e in entity]
        for m in range(len(x)):
            for n in range(len(x)):
                if m == n:
                    continue
                if x[n] in x[m]:
                    try:
                        tmp.remove(x[n])
                    except:
                        pass
        row = [e for e in tmp if e not in dictionary]
        rows.append([example[0],';'.join(row)])
    with open('res.csv','w',encoding='utf-8') as f:
        f_csv = csv.writer(f)
        f_csv.writerow(headers)
        f_csv.writerows(rows)
