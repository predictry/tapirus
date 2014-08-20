__author__ = 'guilherme'

from predictry.engine.graph.query.generator.resources.base import ResourceQueryGeneratorBase
from predictry.engine.models.resources.action import ActionSchema


class ActionQueryGenerator(ResourceQueryGeneratorBase):
    def __init__(self):
        pass

    def create(self, args):

        domain = args["domain"].upper()

        query = []
        params = {}

        strproperties = ""

        s = lambda: ", " if c > 0 else " "

        params["userId"] = args["userId"]
        params["itemId"] = args["itemId"]

        reltype = lambda x: {
            "view": "VIEWED",
            "buy": "BOUGHT",
            "rate": "RATED",
            "addToCart": "ADDED_TO_CART"
        }[x]

        c = 0
        for p in ActionSchema.get_properties(True):
            if p in args:
                strproperties += "%s %s : {%s} " % (s(), p, p)
                if type(args[p]) is str:
                    args[p] = args[p].strip()
                params[p] = args[p]
                c += 1

        query.append("MATCH (u :%s:USER)\n" % domain)
        query.append("WHERE u.id = {userId}\n")
        query.append("WITH u AS u\n")
        query.append("  MATCH (i:%s:ITEM)\n" % domain)
        query.append("  WHERE i.id = {itemId}\n")
        query.append("  WITH u AS u, i AS i\n")
        query.append("      CREATE (u)-[r :%s { %s }]->(i)\n" %
                     (reltype(args["type"]), strproperties))

        query.append("      RETURN ")

        c = 0
        for p in ActionSchema.get_properties(True):
            query.append("%s r.%s AS %s" % (s(), p, p))
            c += 1
        query.append("%s type(r) AS type " % (s()))

        query.append("\n")

        #print 'query: ', ''.join(query)
        #print 'params: ', params

        return ''.join(query), params

    def read(self, args):

        domain = args["domain"].upper()

        query = []
        params = {}
        label = lambda x: {
            "view": "VIEWED",
            "buy": "BOUGHT",
            "rate": "RATED",
            "addToCart": "ADDED_TO_CART"
        }[x]

        if "id" in args:
            #single item GET
            query.append("MATCH (u :%s:USER )-[r {id: {id}}]->(i :%s:ITEM )\n" % (domain, domain))
            params["id"] = args["id"]

        else:
            #multiple items GET
            c = 0
            s = lambda: "WHERE" if c == 0 else "AND"

            if "type" in args:
                query.append("MATCH (u :%s:USER)-[r :%s]->(i :%s:ITEM)\n" % (domain, label(args["type"]), domain))
            else:
                query.append("MATCH (u :%s:USER)-[r]->(i :%s:ITEM)\n" % (domain, domain))

            if "occurredBefore" in args:
                query.append("%s r.timestamp < {timeCeiling} " % s())
                params["timeCeiling"] = args["occurredBefore"]
                c += 1
            if "occurredAfter" in args:
                query.append("%s r.timestamp > {floor} " % s())
                params["timeFloor"] = args["occurredAfter"]
                c += 1

        c = 0
        s = lambda: ", " if c > 0 else " "
        #RETURN
        if "fields" in args:

            query.append("RETURN ")
            fields = args["fields"].split(',')
            for field in fields:
                query.append("%s r.%s AS %s " % (s(), field, field))
                c += 1
        else:

            query.append("RETURN ")
            c = 0
            s = lambda: ", " if c > 0 else " "
            for p in ActionSchema.get_properties(True):
                query.append("%s r.%s AS %s" % (s(), p, p))
                c += 1

        query.append("%s type(r) AS type " % (s()))
        query.append("\n")

        #LIMIT/OFFSET
        if "id" not in args:
            #not a 1 item request
            query.append("SKIP {offset}\n")
            if "offset" in args:
                params["offset"] = args["offset"]
            else:
                params["offset"] = 0

            query.append("LIMIT {limit}\n")
            if "limit" in args:
                params["limit"] = args["limit"]
            else:
                params["limit"] = 10

        #print 'query: ', ''.join(query)
        #print 'params: ', params

        return ''.join(query), params

    def update(self, args):

        domain = args["domain"].upper()

        query = []
        params = {}

        query.append("MATCH (u :%s:USER)-[r {id: {id}}]->(i :%s:ITEM)\n" % (domain, domain))
        params["id"] = args["id"]

        properties = ActionSchema.get_properties()

        c = 0
        s = lambda: "SET" if c == 0 else ","
        for p in properties:
            if p in args:
                query.append("%s r.%s = {%s} " % (s(), p, p))
                params[p] = args[p]
                c += 1

        query.append("\n")

        #RESULT
        query.append("RETURN ")
        c = 0
        s = lambda: ", " if c > 0 else " "
        for p in ActionSchema.get_properties(True):
            query.append("%s r.%s AS %s" % (s(), p, p))
            c += 1
        query.append("%s type(r) AS type " % (s()))

        query.append("\n")

        #print 'query: ', ''.join(query)
        #print 'params: ', params

        return ''.join(query), params

    def delete(self, args):

        domain = args["domain"].upper()

        query = []
        params = {}

        query.append("MATCH (u :%s:USER)-[r {id: {id}}]->(i :%s:ITEM)\n" % (domain, domain))
        params["id"] = args["id"]
        query.append("WITH r, r.id AS id\n")
        query.append("DELETE r\n")
        query.append("RETURN id, type(r) AS type\n")

        #print 'query: ', ''.join(query)
        #print 'params: ', params

        return ''.join(query), params
