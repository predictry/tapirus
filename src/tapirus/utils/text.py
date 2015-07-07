def minify(payload):

    if type(payload) is list:
        newlist = []
        for i in range(0, len(payload)):
            if payload[i] is not None:
                newlist.append(minify(payload[i]))
        return newlist

    if type(payload) is tuple:
        l = list(payload)
        payload = tuple(minify(l))

    if type(payload) is set:
        l = list(payload)
        payload = set(minify(l))

    if type(payload) is dict:
        newdict = {}
        for key in payload:
            if payload[key] is not None:
                newdict[key] = minify(payload[key])

        return newdict

    return payload


def boolean(word):

    value = str(word).lower()

    if value in ['false', '0']:
        return False
    elif value in ['true', '1']:
        return True
    else:
        return None


