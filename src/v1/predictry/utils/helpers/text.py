__author__ = 'guilherme'

import chardet

"""
import urllib2
g_de = urllib2.urlopen('https://www.google.de/').read()
g_com = urllib2.urlopen('https://www.google.com/').read()
g_uk = urllib2.urlopen('https://www.google.co.uk/').read()
g_hk = urllib2.urlopen('https://www.google.com.hk/').read()
g_az = urllib2.urlopen('https://www.google.az/').read()
cnn = urllib2.urlopen('http://edition.cnn.com/').read()

o = {
    "google": {
        "europe": [g_de, g_uk],
        "asia": g_az
    },
    "others": [(cnn, g_hk), g_com]
}

o = encode(o)

print "converting..."

print chardet.detect(o["google"]["europe"][0])
print chardet.detect(o["google"]["europe"][1])
print chardet.detect(o["google"]["asia"])
print chardet.detect(o["others"][0][0])
print chardet.detect(o["others"][0][1])
print chardet.detect(o["others"][1][1])
"""


def encode(e, charset='utf-8'):

    if type(e) is str:
        encoding = chardet.detect(e)["encoding"]
        #print "Found charset %s" % encoding
        if encoding == charset:
            #print encoding + " is equal to " + charset
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

