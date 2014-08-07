__author__ = 'guilherme'

from v1.predictry.query.executor.queryexecutor import QueryExecutor

#TODO: [LATER][R: py2neo] create utility (helper) functions for nodes (exists, get labels, has label, get properties, etc)
#TODO: [LATER][R: py2neo] look into the viability of using py2neo instead of cypher( e.g. find on takes 1 label and 1 parameter to match)
def exists(labels, properties):

    l = ""
    p = ""
    params = {}

    for label in labels:
        l += " :%s" % label

    c = 0
    for k, v in properties.iteritems():
        if c > 0:
            p += ","
        p += " %s : {%s} " % (k, k)
        params[k] = v
        c += 1

    q = ["MATCH (x %s { %s })\n" % (l, p), "RETURN x"]

    query = Text.encode(''.join(q))

    #print query

    qexec = QueryExecutor()
    output, err = qexec.run(query, params)

    if err:
        return {}, err

    #print query, params

    if len(output) == 0:
        return False, None
    else:
        return True, None