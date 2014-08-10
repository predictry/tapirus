__author__ = 'guilherme'

import urllib2
import json


def is_db_running(url):

    req = urllib2.Request(url)

    try:
        resp = urllib2.urlopen(req)
    except urllib2.URLError, e:
        #print e
        return False

    else:
        # 200
        body = resp.read()

        try:
            js = json.loads(body)

            if "node" in js:
                if js["node"] is not None:
                    return True

        except ValueError:
            return False

    return False