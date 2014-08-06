__author__ = 'guilherme'

#NOTE: THIS FILE IS NOT IN USE. IT IS W.I.P.
#TODO reduce loops, c

class NodeQueryGenerator():

    def __init__(self):
        pass

    def create(self, labels, properties, merge=False, name="x"):

        qbuild = []
        params = {}

        strlabels = ""
        strproperties = ""

        c = 0
        sep = lambda: ", " if c > 0 else " "

        if properties and type(properties) is dict:
            for p in properties:
                strproperties += "%s %s : {%s} " % (sep(), p, p)
                params[p] = properties[p]
                c += 1

        if labels and type(labels) is list:
            for l in labels:
                if type(l) is str:
                    strlabels += " :%s " % l.upper()

        if merge:
            qbuild.append("MERGE (%s %s { %s })\n" % (name, strlabels, strproperties))
        else:
            qbuild.append("CREATE (%s %s { %s })\n" % (name, strlabels, strproperties))

        if properties and type(properties) is dict:
            c = 0
            qbuild.append("RETURN ")
            for p in properties:
                qbuild.append("%s %s.%s AS %s" % (sep(), name, p, p))
                c += 1
        else:
            qbuild.append("RETURN %s", name)

        qbuild.append("\n")

        query = ''.join(qbuild)

        #print 'query: ', query
        #print 'params: ', params

        return query, params

    #TODO: match(exactly equal {var,value}), searchpattern(string{var,pattern},"case-sensitivity"), higher/lower(numerical), within range ({var, range})
    def read(self, labels, properties, limit=10, skip=0, merge=False, name="x"):

        qbuild = []
        params = {}

        strlabels = ""
        strproperties = ""

        c = 0
        sep = lambda: ", " if c > 0 else " "

        if properties and type(properties) is dict:
            for p in properties:
                strproperties += "%s %s : {%s} " % (sep(), p, p)
                params[p] = properties[p]
                c += 1

        if labels and type(labels) is list:
            for l in labels:
                if type(l) is str:
                    strlabels += " :%s " % l.upper()

        if merge:
            qbuild.append("MERGE (%s %s { %s })\n" % (name, strlabels, strproperties))
        else:
            qbuild.append("MATCH (%s %s { %s })\n" % (name, strlabels, strproperties))

        #TODO: [URGENT] FIX THIS
        if newlabels and type(newlabels) is list:
            for l in newlabels:
                if type(l) is str:
                    qbuild.append("SET %s :%s\n" % (name, l.upper()))

        if newproperties and type(newproperties) is dict:
            for p in newproperties:
                qbuild.append("SET %s.%s = {%s}\n" % (name, p, p))
                params[p] = newproperties[p]

        pr = True
        if properties and type(properties) is dict:
            pr = False
            qbuild.append("RETURN ")
            for p in properties:
                qbuild.append("%s i.%s AS %s" % (sep(), p, p))
                c += 1

        if newproperties and type(newproperties) is dict:
            if pr:
                qbuild.append("RETURN ")
                c = 0
            pr = False
            for p in newproperties:
                qbuild.append("%s i.%s AS %s" % (sep(), p, p))
                c += 1
        if pr:
            qbuild.append("RETURN x")

        qbuild.append("\n")

        query = ''.join(qbuild)

        #print 'query: ', query
        #print 'params: ', params

        return query, params

    def update(self, labels, properties, newlabels=None, newproperties=None, merge=False, name="x"):

        qbuild = []
        params = {}

        strlabels = ""
        strproperties = ""

        c = 0
        sep = lambda: ", " if c > 0 else " "

        if properties and type(properties) is dict:
            for p in properties:
                strproperties += "%s %s : {%s} " % (sep(), p, p)
                params[p] = properties[p]
                c += 1

        if labels and type(labels) is list:
            for l in labels:
                if type(l) is str:
                    strlabels += " :%s " % l.upper()

        if merge:
            qbuild.append("MERGE (%s %s { %s })\n" % (name, strlabels, strproperties))
        else:
            qbuild.append("MATCH (%s %s { %s })\n" % (name, strlabels, strproperties))

        if newlabels and type(newlabels) is list:
            for l in newlabels:
                if type(l) is str:
                    qbuild.append("SET %s :%s\n" % (name, l.upper()))

        if newproperties and type(newproperties) is dict:
            for p in newproperties:
                qbuild.append("SET %s.%s = {%s}\n" % (name, p, p))
                params[p] = newproperties[p]

        pr = True
        if properties and type(properties) is dict:
            pr = False
            qbuild.append("RETURN ")
            for p in properties:
                qbuild.append("%s i.%s AS %s" % (sep(), p, p))
                c += 1

        if newproperties and type(newproperties) is dict:
            if pr:
                qbuild.append("RETURN ")
                c = 0
            pr = False
            for p in newproperties:
                qbuild.append("%s i.%s AS %s" % (sep(), p, p))
                c += 1
        if pr:
            qbuild.append("RETURN x")

        qbuild.append("\n")

        query = ''.join(qbuild)

        #print 'query: ', query
        #print 'params: ', params

        return query, params

    def delete(self, labels, properties, name="x"):

        #query.append("WITH i, i.id AS id\n")
        #query.append("OPTIONAL MATCH (i)-[r]-()\n")
        #query.append("DELETE r,i\n")
        #query.append("RETURN id\n")

        qbuild = []
        params = {}

        strlabels = ""
        strproperties = ""

        c = 0
        sep = lambda: ", " if c > 0 else " "

        if properties and type(properties) is dict:
            c = 0
            for p in properties:
                strproperties += "%s %s : {%s} " % (sep(), p, p)
                params[p] = properties[p]
                c += 1

        if labels and type(labels) is list:
            for l in labels:
                if type(l) is str:
                    strlabels += " :%s " % l.upper()

        qbuild.append("MATCH (%s %s { %s })\n" % (name, strlabels, strproperties))

        if properties and type(properties) is dict:
            qbuild.append("WITH %s" % name)
            c = 1
            for p in properties:
                qbuild.append("%s %s.%s AS %s " % (sep(), name, p, p))
                c += 1
            qbuild.append("\n")

        qbuild.append("OPTIONAL MATCH (%s)-[r]-()\n" % name)
        qbuild.append("DELETE %s,r\n" % name)

        if properties and type(properties) is dict:
            qbuild.append("RETURN")
            c = 0
            for p in properties:
                qbuild.append("%s %s" % (sep(), p))
                c += 1
        else:
            qbuild.append("RETURN %s" % name)

        qbuild.append("\n")

        query = ''.join(qbuild)

        #print 'query: ', query
        #print 'params: ', params

        return query, params

qg = NodeQueryGenerator()

qg.create(labels=["user", "redmart"], properties={"name": "Josh", "age": 25, "dob": 56986356996}, merge=False, name="i")

qg.update(labels=["user", "redmart"], properties={"name": "Josh", "age": 25, "dob": 56986356996},
          newlabels=["my"], newproperties={"address": "BLVD 64384"}, merge=False, name="i")

qg.delete(labels=["user", "redmart"], properties={"name": "Josh", "age": 25, "dob": 56986356996}, name="i")