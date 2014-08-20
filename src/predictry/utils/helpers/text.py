__author__ = 'guilherme'

import chardet

def encode(e, charset='utf-8'):

    if type(e) is str and e:
        encoding = chardet.detect(e)["encoding"]
        if encoding == charset:
            pass
        else:
            e = e.decode(encoding).encode(charset)
    elif type(e) is list:
        for i in range(0, len(e)):
            e[i] = encode(e[i])
    elif type(e) is tuple:
        l = list(e)
        e = tuple(encode(l))
    elif type(e) is set:
        l = list(e)
        e = set(encode(l))
    elif type(e) is dict:
        for k in e:
            e[k] = encode(e[k])

    return e

