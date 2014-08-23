__author__ = 'guilherme'

from predictry.engine.graph.query.generator.resources.base import ResourceQueryGeneratorBase
from predictry.engine.models.resources.action import ActionSchema
from predictry.engine.models.resources.user import UserSchema
from predictry.engine.models.resources.item import ItemSchema


class ActionQueryGenerator(ResourceQueryGeneratorBase):
    def __init__(self):
        pass

    def create(self, args):

        domain = args["domain"]

        query = []
        params = {}

        str_properties = []

        s = lambda: ", " if c > 0 else " "

        params["user_id"] = args["user_id"]
        params["item_id"] = args["item_id"]

        reltype = lambda x: {
            "view": "VIEWED",
            "buy": "BOUGHT",
            "rate": "RATED",
            "add_to_cart": "ADDED_TO_CART"
        }[x]

        c = 0
        for p in ActionSchema.get_properties(True):
            if p in args:
                str_properties.append("%s %s : {%s} " % (s(), p, p))
                if type(args[p]) is str:
                    args[p] = args[p].strip()
                params[p] = args[p]
                c += 1

        query.append("MATCH (u :%s:%s)\n" % (domain, UserSchema.get_label()))
        query.append("WHERE u.id = {user_id}\n")
        query.append("WITH u AS u\n")
        query.append("  MATCH (i:%s:%s)\n" % (domain, ItemSchema.get_label()))
        query.append("  WHERE i.id = {item_id}\n")
        query.append("  WITH u AS u, i AS i\n")
        query.append("      CREATE (u)-[r :%s { %s }]->(i)\n" %
                     (reltype(args["type"]), ''.join(str_properties)))

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

        domain = args["domain"]

        query = []
        params = {}
        label = lambda x: {
            "view": "VIEWED",
            "buy": "BOUGHT",
            "rate": "RATED",
            "add_to_cart": "ADDED_TO_CART"
        }[x]

        if "id" in args:
            #single item GET
            query.append("MATCH (u :%s:%s )-[r {id: {id}}]->(i :%s:%s )\n" %
                         (domain, UserSchema.get_label(), domain, ItemSchema.get_label()))
            params["id"] = args["id"]

        else:
            #multiple items GET
            c = 0
            s = lambda: "WHERE" if c == 0 else "AND"

            if "type" in args:
                query.append("MATCH (u :%s:%s)-[r :%s]->(i :%s:%s)\n" %
                             (domain, UserSchema.get_label(), label(args["type"]), domain, ItemSchema.get_label()))
            else:
                query.append("MATCH (u :%s:%s)-[r]->(i :%s:%s)\n" %
                             (domain, UserSchema.get_label(), domain, ItemSchema.get_label()))

            if "occurred_before" in args:
                query.append("%s r.timestamp < {time_ceiling} " % s())
                params["time_ceiling"] = args["occurred_before"]
                c += 1
            if "occurred_after" in args:
                query.append("%s r.timestamp > {floor} " % s())
                params["time_floor"] = args["occurred_after"]
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

        domain = args["domain"]

        query = []
        params = {}

        query.append("MATCH (u :%s:%s)-[r {id: {id}}]->(i :%s:%s)\n" %
                     (domain, UserSchema.get_label(), domain, ItemSchema.get_label()))
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

        domain = args["domain"]

        query = []
        params = {}

        query.append("MATCH (u :%s:%s)-[r {id: {id}}]->(i :%s:%s)\n" %
                     (domain, UserSchema.get_label(), domain, ItemSchema.get_label()))
        params["id"] = args["id"]
        query.append("WITH r, r.id AS id\n")
        query.append("DELETE r\n")
        query.append("RETURN id, type(r) AS type\n")

        #print 'query: ', ''.join(query)
        #print 'params: ', params

        return ''.join(query), params
