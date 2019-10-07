import re
def filter_word(w):
    add_char = {']', '：', '~', '！', '%', '[', '《', '】', ';', '”', ':', '》', '？', '>', '/', '#', '。', '；', '&', '=', '，',
                '“', '【'}
    if len(w) == 1:
        return ''
    a="\\" + "|\\".join(add_char)
    a=1

print(filter_word('《第三方》'))