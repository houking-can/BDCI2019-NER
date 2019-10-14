import csv
import codecs
import re

city = set(open('./data/dict/city.txt').read().split('\n'))

add_char = {']', '：', '~', '！', '%', '[', '《', '】', ';', ':', '》', '？', '>', '/', '#', '。', '；', '&', '=',
            '，',
            '【', '@', '、', '|', ',', '”', '?'}


def completion(candidates, context):
    context = context[1] + '。' + context[2]
    tmp = []
    for each in candidates:

        index = context.find(each)
        ex = 1
        if context.count(each) > 1:
            for i in range(1, len(context) - index - len(each)):
                if context.count(each) != context.count(context[index:index + i + len(each)]):
                    ex = i
                    break

            new = context[index:index + ex - 1 + len(each)]
            flag = True
            if len(new) < 22 and len(re.findall("\\" + "|\\".join(add_char), new)) == 0:
                xx = re.findall('(%s.*?)(理财|集团|控股|平台|银行|公司|资本|投资|生态|策略|控股集团)' % each, new)
                if xx:
                    flag = False
                    new = xx[0][0] + xx[0][1]
                    if context.count(each) == context.count(new):
                        tmp.append(new)
                    else:
                        tmp.append(each)
                        tmp.append(new)
            if flag:
                tmp.append(each)
        else:
            # xx = re.findall('(%s.*?)(理财|集团|控股|平台|银行|公司|资本|投资|生态|策略|控股集团)' % each, context)
            # if xx:
            #     new = xx[0][0] + xx[0][1]
            #     if len(new) < 22 and len(re.findall("\\" + "|\\".join(add_char), new)) == 0:
            #         print(each, new)
            #     each = new
            tmp.append(each)

    tmp = list(set(tmp))
    tmp = [(context.count(each), each) for each in tmp]
    tmp.sort(key=lambda k: (k[0], len(k[1])), reverse=True)

    res = []
    for i in range(len(tmp) - 1):
        if tmp[i + 1][0] == tmp[i][0] and tmp[i + 1][1].startswith(tmp[i][1]):
            continue
        res.append(tmp[i])
    return tmp


def get_most(candidates, context):
    # if len(candidates) <= 3:
    #     return candidates

    res_1 = []
    res_2 = []
    candidates = [each for each in candidates if each not in city]
    candidates = completion(candidates, context)

    for each in candidates:
        if each[1] in context[1]:
            res_1.append(each[1])
        else:
            res_2.append(each[1])

    # tmp = []
    # if len(res_1) < 3:
    #     tmp = [each[1] for each in res_2[:3 - len(res_1)]]

    res = res_1 + res_2

    return res


if __name__ == '__main__':
    results = open('./res/best.csv').read().split('\n')
    if results[-1] == '':
        results = results[:-1]
    res = codecs.open('test.csv', 'w')
    res.write('id,unknownEntities\n')

    with open('./data/old/Test_Data.csv', 'r', encoding='utf-8') as myFile:
        lines = list(csv.reader(myFile))
        if lines[-1] == '':
            lines = lines[:-1]
        data = []
        for i in range(1, len(lines)):
            id, candidates = results[i].split(',')
            candidates = candidates.split(';')
            entity = get_most(candidates, lines[i])
            data.append('')
            res.write('{0},{1}\n'.format(id, ';'.join(entity)))

    res.close()
