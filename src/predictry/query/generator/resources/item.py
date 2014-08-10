__author__ = 'guilherme'

from predictry.query.generator.resources.base import ResourceQueryGeneratorBase
from predictry.models.resources.item import ItemSchema


class ItemQueryGenerator(ResourceQueryGeneratorBase):
    def __init__(self):
        pass

    def create(self, args):

        domain = args["domain"].upper()

        query = []
        params = {}

        strlabels = " :%s:ITEM " % domain
        strproperties = ""

        c = 0
        s = lambda: ", " if c > 0 else " "
        for p in ItemSchema.get_properties(True):
            if p in args:
                strproperties += "%s %s : {%s} " % (s(), p, p)
                if type(args[p]) is str:
                    args[p] = args[p].strip()

                if p in ["tags"]:
                    args[p] = args[p].split(',')

                params[p] = args[p]
                c += 1

        query.append("CREATE (i %s { %s })\n" % (strlabels, strproperties))
        query.append("RETURN ")

        c = 0
        for p in ItemSchema.get_properties(True):
            query.append("%s i.%s AS %s" % (s(), p, p))
            c += 1

        query.append("\n")

        #print 'query: ', ''.join(query)
        #print 'params: ', params

        return ''.join(query), params

    def read(self, args):

        domain = args["domain"].upper()

        query = []
        params = {}

        if "id" in args:
            query.append("MATCH (i :%s:ITEM { id : {id}})\n" % domain)
            params["id"] = args["id"]

        else:
            #multiple items GET
            query.append("MATCH (i :%s:ITEM)\n" % domain)

            c = 0
            s = lambda: "WHERE" if c == 0 else "AND"
            #check for any other parameters
            #q
            if "q" in args:

                query.append("%s ( " % s())

                cq = 0
                sq = lambda: "" if cq == 0 else "OR"
                for keyword in args["q"]:
                    query.append("%s i.name =~ '(?i).*%s.*' " % (sq(), keyword))
                    cq += 1
                    query.append("%s i.description =~ '(?i).*%s.*' " % (sq(), keyword))
                    cq += 1
                    query.append("%s i.brand =~ '(?i).*%s.*' " % (sq(), keyword))
                    cq += 1
                    query.append("%s i.model =~ '(?i).*%s.*' " % (sq(), keyword))
                    cq += 1

                c += 1
                query.append(" ) ")

            #tags
            if "tags" in args:
                query.append("%s ANY(tag in i.tags WHERE tag in {tags}) " % s())
                params["tags"] = args["tags"].split(',')
                c += 1

            #priceFloor
            if "priceFloor" in args:
                query.append("%s i.price >= {priceFloor} " % s())
                params["priceFloor"] = args["priceFloor"]
                c += 1

                #priceCeiling
            if "priceCeiling" in args:
                query.append("%s i.price <= {priceCeiling} " % s())
                params["priceCeiling"] = args["priceCeiling"]
                c += 1

            if c > 0:
                query.append("\n")

        #RETURN
        if "fields" in args:

            query.append("RETURN ")

            c = 0
            fields = args["fields"].split(',')
            s = lambda: ", " if c > 0 else " "
            for field in fields:
                query.append("%s i.%s AS %s " % (s(), field, field))
                c += 1
        else:
            query.append("RETURN ")

            c = 0
            s = lambda: ", " if c > 0 else " "

            for p in ItemSchema.get_properties(True):
                query.append("%s i.%s AS %s" % (s(), p, p))
                c += 1

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

    def update(self, args):

        domain = args["domain"].upper()

        query = []
        params = {}

        query.append("MATCH (i :%s:ITEM { id : {id}})\n" % domain)
        params["id"] = args["id"]

        for p in ItemSchema.get_properties():
            if p in args:
                query.append("SET i.%s = {%s}\n" % (p, p))
                if p == "tags":
                    args[p] = args[p].split(',')
                params[p] = args[p]

        query.append("RETURN ")

        c = 0
        s = lambda: ", " if c > 0 else " "

        for p in ItemSchema.get_properties(True):
            query.append("%s i.%s AS %s" % (s(), p, p))
            c += 1

        query.append("\n")

        #print 'query: ', ''.join(query)
        #print 'params: ', params

        return ''.join(query), params

    def delete(self, args):

        domain = args["domain"].upper()

        query = []
        params = {}

        query.append("MATCH (i :%s:ITEM { id : {id}})\n" % domain)
        params["id"] = args["id"]

        query.append("WITH i, i.id AS id\n")
        query.append("OPTIONAL MATCH (i)-[r]-()\n")
        query.append("DELETE r,i\n")
        query.append("RETURN id\n")

        #print 'query: ', ''.join(query)
        #print 'params: ', params

        return ''.join(query), params