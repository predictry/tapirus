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
                    strlabels += " :%s " % l

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
            qbuild.append("RETURN %s" % name)

        qbuild.append("\n")

        query = ''.join(qbuild)

        #print 'query: ', query
        #print 'params: ', params

        return query, params

    #TODO: match(exactly equal {var,value}), searchpattern(string{var,pattern},"case-sensitivity"), higher/lower(numerical), within range ({var, range})
    def read(self, labels, properties, limit=10, skip=0, merge=False, name="x"):


        return None, None

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
                    strlabels += " :%s " % l

        if merge:
            qbuild.append("MERGE (%s %s { %s })\n" % (name, strlabels, strproperties))
        else:
            qbuild.append("MATCH (%s %s { %s })\n" % (name, strlabels, strproperties))

        if newlabels and type(newlabels) is list:
            for l in newlabels:
                if type(l) is str:
                    qbuild.append("SET %s :%s\n" % (name, l))

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

        return query, params

    def delete(self, labels, properties, name="x"):
        #TODO: split operation (delete rels first, and then run a second query to delete nodes). For cases where number of # of nodes and rels that match pattern is very high

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
                    strlabels += " :%s " % l

        qbuild.append("MATCH (%s %s { %s })\n" % (name, strlabels, strproperties))

        if properties and type(properties) is dict:
            qbuild.append("WITH %s" % name)
            c = 1
            for p in properties:
                qbuild.append("%s %s.%s AS %s " % (sep(), name, p, p))
                c += 1
            qbuild.append("\n")

        qbuild.append("OPTIONAL MATCH (%s)-[r]-()\n" % name)
        qbuild.append("DELETE r\n")

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

        return query, params