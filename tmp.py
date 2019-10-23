def check_brackets(w):
    w = w.rstrip('（')
    w = w.rstrip('(')
    w = w.lstrip(')')
    w = w.lstrip('）')
    cnt_chinese = 0
    cnt_english = 0
    for c in w:
        if c == '（':
            cnt_chinese += 1
        elif c == '）':
            cnt_chinese -= 1
    for c in w:
        if c == '(':
            cnt_english += 1
        elif c == ')':
            cnt_english -= 1

    if cnt_chinese == 0 and cnt_english == 0:
        if w.startswith('（') and w.endswith('）'):
            return w[1:-1]
        if w.startswith('(') and w.endswith(')'):
            return w[1:-1]
        return w

    if cnt_chinese > 0:
        if not w.startswith('（'):
            return w + '）'
        return w[1:]
    if cnt_chinese < 0:
        if not w.endswith('）'):
            return '（' + w
        return w[:-1]
    if cnt_english > 0:
        if not w.startswith('('):
            return w + ')'
        return w[1:]
    if cnt_english < 0:
        if not w.endswith(')'):
            return '(' + w
        return w[:-1]


def check_quotation(w):
    w = w.lstrip('”')
    w = w.lstrip('’')
    w = w.rstrip('“')
    w = w.rstrip('‘')

    cnt_double = 0
    cnt_single = 0
    for c in w:
        if c == '“':
            cnt_double += 1
        elif c == '”':
            cnt_double -= 1
    for c in w:
        if c == '‘':
            cnt_single += 1
        elif c == '’':
            cnt_single -= 1

    if cnt_double == 0 and cnt_single == 0:
        if w.startswith('“') and w.endswith('”'):
            return w[1:-1]
        if w.startswith('‘') and w.endswith('’'):
            return w[1:-1]
        return w

    if cnt_double > 0:
        if not w.startswith('“'):
            return w + '”'
        return w[1:]
    if cnt_double < 0:
        if not w.endswith('”'):
            return '“' + w
        return w[:-1]
    if cnt_single > 0:
        if not w.startswith('‘'):
            return w + '’'
        return w[1:]
    if cnt_single < 0:
        if not w.endswith('’'):
            return '‘' + w
        return w[:-1]

def check_punctuations(w, context):
    w = w.rstrip('（')
    w = w.rstrip('(')
    w = w.lstrip(')')
    w = w.lstrip('）')

    w = w.lstrip('”')
    w = w.lstrip('’')
    w = w.rstrip('“')
    w = w.rstrip('‘')

    index = context.find(w)
    if index + len(w) < len(context) and context[index + len(w)] in [')', '）', '"', '”', '\'', '’']:
        w = w + context[index + len(w)]
    if index > 0 and context[index - 1] in ['(', '（', '\'', '"', '‘', '“']:
        w = context[index - 1] + w
    if w[0] in ['(', '（'] and w[-1] in [')', '）']:
        return w[1:-1]
    if w[0] in ['"', '“', '\'', '‘'] and w[-1] in ['"', '”', '’', '\'']:
        return w[1:-1]

    return w

print(check_punctuations('aa(aaa','sdfdsfaa(aaa)sdf'))