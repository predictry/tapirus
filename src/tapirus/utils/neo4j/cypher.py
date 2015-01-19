__author__ = 'guilherme'

from tapirus.utils.helpers import text
from tapirus.engine.graph.query.executor.executor import QueryExecutor


class Node:

    def __init__(self, labels, properties):

        self.labels = labels
        self.properties = properties


def node_exists(labels, properties):

    l = []
    p = []
    params = {}

    for label in labels:
        l.append(" :%s" % label)

    c = 0
    for k, v in properties.iteritems():
        if c > 0:
            p.append(",")
        p.append(" %s : {%s} " % (k, k))
        params[k] = v
        c += 1

    q = ["MATCH (x %s { %s })\n" % (''.join(l), ''.join(p)), "RETURN x"]

    query = text.encode(''.join(q))

    qexec = QueryExecutor()
    output, err = qexec.run(query, params)

    if err:
        return {}, err

    if len(output) == 0:
        return False, None
    else:
        return True, None


def get_node_properties(ids, properties, label, domain):

    if type(ids) is not list or not ids:
        return None

    if not properties:
        return None

    q = []
    params = dict(ids=ids)

    q.append("MATCH (x:%s:%s)\n" % (domain, label))
    q.append("WHERE x.id IN {ids}\n")
    q.append("RETURN x.id AS id")

    for p in [x for x in properties if x != "id"]:
        q.append(", x.%s AS %s" % (p, p))

    query = text.encode(''.join(q))

    qexec = QueryExecutor()
    output, err = qexec.run(query, params)

    if err:
        return {}, err

    if len(output) == 0:
        return None, err
    else:
        return output, err