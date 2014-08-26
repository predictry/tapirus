__author__ = 'guilherme'

from predictry.engine.graph.query.generator.resources.base import ResourceQueryGeneratorBase
from predictry.engine.models.resources.user import UserSchema


class UserQueryGenerator(ResourceQueryGeneratorBase):
    def __init__(self):
        pass

    def create(self, args, data={}):

        domain = args["domain"]

        query = []
        params = {}

        str_labels = " :%s:%s " % (domain, UserSchema.get_label())
        str_properties = []

        c = 0
        s = lambda: ", " if c > 0 else " "

        for k, v in data.iteritems():
            str_properties.append("%s %s : {%s} " % (s(), k, k))
            if type(data[k]) is str:
                data[k] = data[k].strip()
            params[k] = data[k]
            c += 1

        query.append("CREATE (u %s { %s })\n" % (str_labels, ''.join(str_properties)))
        query.append("RETURN ")

        c = 0
        for k, v in data.iteritems():
            query.append("%s u.%s AS %s" % (s(), k, k))
            c += 1

        query.append("\n")

        #print 'query: ', ''.join(query)
        #print 'params: ', params

        return ''.join(query), params

    def read(self, args):

        domain = args["domain"]

        query = []
        params = {}

        if "id" in args:
            query.append("MATCH (u :%s:%s { id : {id}})\n" %
                         (domain, UserSchema.get_label()))
            params["id"] = args["id"]

        else:
            query.append("MATCH (u :%s:%s )\n" %
                         (domain, UserSchema.get_label()))

        #RETURN
        query.append("RETURN u.id AS id")

        if "fields" in args:
            fields = [x for x in args["fields"].split(',') if x != "id"]
            for field in fields:
                query.append(", u.%s AS %s " % (field, field))

        query.append("\n")

        #LIMIT/OFFSET
        if "id" not in args:
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

    def update(self, args, data={}):

        domain = args["domain"]

        query = []
        params = {}

        query.append("MATCH (u :%s:%s { id : {id}})\n" %
                     (domain, UserSchema.get_label()))
        params["id"] = args["id"]

        c = 0
        s = lambda: "SET" if c == 0 else ","

        for k, v in data.iteritems():
            query.append("%s u.%s = {%s} " % (s(), k, k))
            params[k] = data[k]
            c += 1

        query.append("\n")

        query.append("RETURN ")

        c = 0
        s = lambda: ", " if c > 0 else " "

        for k, v in data.iteritems():
            query.append("%s u.%s AS %s" % (s(), k, k))
            c += 1

        query.append("\n")

        #print 'query: ', ''.join(query)
        #print 'params: ', params

        return ''.join(query), params

    def delete(self, args):

        domain = args["domain"]

        query = []
        params = {}

        query.append("MATCH (u :%s:%s { id : {id}})\n" %
                     (domain, UserSchema.get_label()))
        params["id"] = args["id"]

        query.append("WITH u, u.id AS id\n")
        query.append("OPTIONAL MATCH (u)-[r]-()\n")
        query.append("DELETE r,u\n")
        query.append("RETURN id\n")

        #print 'query: ', ''.join(query)
        #print 'params: ', params

        return ''.join(query), params