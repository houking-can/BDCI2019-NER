import csv
import json
import re


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
