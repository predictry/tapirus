'''
Created on 10 Jul, 2014

@author: frost
'''

from predictry.query.generator.base import ResourceQueryGeneratorBase
from predictry.models.schema import ItemSchema, UserSchema, ActionSchema

#TODO: refactor: Resources -> Nodes, Relationships (create, delete, update, retrieve), Services(run)
#TODO: use MERGE as opposed to CREATE where applicable... (note: MERGE requires all properties to match)
#TODO: [URGENT] Test everything on this file


class ItemQueryGenerator(ResourceQueryGeneratorBase):
    def __init__(self):
        pass

    def create(self, args):

        organization = args["organization"].upper()

        query = []
        params = {}

        strlabels = " :ITEM :%s " % organization
        strproperties = " id : {%s} " % "id"

        params["id"] = args["id"]

        for p in ItemSchema.get_properties():
            if p in args:
                strproperties += ", %s : {%s} " % (p, p)
                if type(args[p]) is str:
                    args[p] = args[p].strip()

                params[p] = args[p]

        query.append("CREATE (i %s { %s })\n" % (strlabels, strproperties))
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

    def read(self, args):

        organization = args["organization"].upper()

        query = []
        params = {}

        if "id" in args:
            #single item GET
            query.append("MATCH (i :%s :ITEM { id : {id}})\n" % organization)
            params["id"] = args["id"]

        else:
            #multiple items GET
            query.append("MATCH (i :%s :ITEM)\n" % organization)

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

            #brand
            #if "brand" in input:                
            #    query.append("%s i.brand = {brand} " % s())                
            #    params["brand"] = input["brand"]
            #    c += 1

            #tags
            if "tags" in args:
                tags = args["tags"].split(',')
                query.append("%s ANY(tag in i.tags WHERE tag in {tags}) " % s())
                params["tags"] = tags
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
            n = len(fields)
            for field in fields:

                if c == n - 1:
                    query.append("i.%s AS %s " % (field, field))
                else:
                    query.append("i.%s AS %s, " % (field, field))

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
                #not a 1 item request
                params["offset"] = 0

            query.append("LIMIT {limit}\n")
            if "limit" in args:
                params["limit"] = args["limit"]
            else:
                #not a 1 item request (cap response)
                params["limit"] = 10

        #print 'query: ', ''.join(query)
        #print 'params: ', params

        return ''.join(query), params

    def update(self, args):

        organization = args["organization"].upper()

        query = []
        params = {}

        query.append("MATCH (i :%s :ITEM { id : {id}})\n" % organization)
        params["id"] = args["id"]

        for p in ItemSchema.get_properties():
            if p in args:
                query.append("SET i.%s = {%s}\n" % (p, p))
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

        organization = args["organization"].upper()

        query = []
        params = {}

        query.append("MATCH (i :%s :ITEM { id : {id}})\n" % organization)
        params["id"] = args["id"]

        query.append("WITH i, i.id AS id\n")
        query.append("OPTIONAL MATCH (i)-[r]-()\n")
        query.append("DELETE r,i\n")
        query.append("RETURN id\n")

        #print 'query: ', ''.join(query)
        #print 'params: ', params

        return ''.join(query), params


class UserQueryGenerator(ResourceQueryGeneratorBase):
    def __init__(self):
        pass

    def create(self, args):

        organization = args["organization"].upper()

        query = []
        params = {}

        strlabels = " :%s :USER " % organization
        strproperties = " id : {%s} " % "id"
        params["id"] = args["id"]

        #TODO: [REPL: Use generic tool] change this and other create methods to use get_properties(True) and include id and org... use c and s()
        for p in UserSchema.get_properties():
            if p in args:
                strproperties += ", %s : {%s} " % (p, p)
                if type(args[p]) is str:
                    args[p] = args[p].strip()
                params[p] = args[p]

        query.append("CREATE (u %s { %s })\n" % (strlabels, strproperties))

        query.append("RETURN ")

        c = 0
        s = lambda: ", " if c > 0 else " "

        for p in UserSchema.get_properties(True):
            query.append("%s i.%s AS %s" % (s(), p, p))
            c += 1

        query.append("\n")

        #print 'query: ', ''.join(query)
        #print 'params: ', params

        return ''.join(query), params

    def read(self, args):

        organization = args["organization"].upper()

        query = []
        params = {}

        if "id" in args:
            query.append("MATCH (i :%s :USER { id : {id}})\n" % organization)
            params["id"] = args["id"]

        else:
            #multiple items GET
            query.append("MATCH (i :%s :USER )\n" % organization)

        #RETURN
        query.append("RETURN ")
        if "fields" in args:

            c = 0
            fields = args["fields"].split(',')
            n = len(fields)
            for field in fields:

                if c == n - 1:
                    query.append("i.%s AS %s " % (field, field))
                else:
                    query.append("i.%s AS %s, " % (field, field))

                c += 1
        else:
            c = 0
            s = lambda: ", " if c > 0 else " "

            for p in UserSchema.get_properties(True):
                query.append("%s i.%s AS %s" % (s(), p, p))
                c += 1

        query.append("\n")

        #LIMIT/OFFSET
        if "id" not in args:
            query.append("SKIP {offset}\n")
            if "offset" in args:
                params["offset"] = args["offset"]
            else:
                #not a 1 item request
                params["offset"] = 0

            query.append("LIMIT {limit}\n")
            if "limit" in args:
                params["limit"] = args["limit"]
            else:
                #not a 1 item request (cap response)
                params["limit"] = 10

        #print 'query: ', ''.join(query)
        #print 'params: ', params

        return ''.join(query), params

    def update(self, args):

        organization = args["organization"].upper()

        query = []
        params = {}

        query.append("MATCH (i :%s :USER { id : {id}})\n" % organization)
        params["id"] = args["id"]

        for p in UserSchema.get_properties():
            if p in args:
                query.append("SET i.%s = {%s}\n" % (p, p))
                params[p] = args[p]

        query.append("RETURN ")

        c = 0
        s = lambda: ", " if c > 0 else " "

        for p in UserSchema.get_properties(True):
            query.append("%s i.%s AS %s" % (s(), p, p))
            c += 1

        query.append("\n")

        #print 'query: ', ''.join(query)
        #print 'params: ', params

        return ''.join(query), params

    def delete(self, args):

        organization = args["organization"].upper()

        query = []
        params = {}

        query.append("MATCH (i :%s :USER { id : {id}})\n" % organization)
        params["id"] = args["id"]

        query.append("WITH i, i.id AS id\n")
        query.append("OPTIONAL MATCH (i)-[r]-()\n")
        query.append("DELETE r,i\n")
        query.append("RETURN id\n")

        #print 'query: ', ''.join(query)
        #print 'params: ', params

        return ''.join(query), params


class ActionQueryGenerator(ResourceQueryGeneratorBase):
    def __init__(self):
        pass

    def create(self, args):

        organization = args["organization"].upper()

        query = []
        params = {}

        strproperties = " id : {%s} " % "id"

        params["id"] = args["id"]
        params["userId"] = args["userId"]
        params["itemId"] = args["itemId"]

        reltype = lambda x: {
            "view": "VIEWED",
            "buy": "BOUGHT",
            "rate": "RATED",
            "addToCart": "ADDED_TO_CART"
        }[x]

        for p in ActionSchema.get_properties():
            if p in args:
                strproperties += ", %s : {%s} " % (p, p)
                if type(args[p]) is str:
                    args[p] = args[p].strip()
                params[p] = args[p]

        query.append("MERGE (u :%s :USER { id: {userId} })-[r :%s { %s }]->(i :%s :ITEM { id: {itemId}})\n" %
                     (organization, reltype(args["type"]), p, organization))

        query.append("RETURN ")

        c = 0
        s = lambda: ", " if c > 0 else " "

        for p in ActionSchema.get_properties(True):
            query.append("%s i.%s AS %s" % (s(), p, p))
            c += 1

        query.append("\n")

        #print 'query: ', ''.join(query)
        #print 'params: ', params

        return ''.join(query), params

    def read(self, args):

        organization = args["organization"].upper()

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
            query.append("MATCH (u :%s :USER )-[r {id: {id}}]->(i :%s :ITEM )\n" % (organization, organization))
            params["id"] = args["id"]

        else:
            #multiple items GET
            c = 0
            s = lambda: "WHERE" if c == 0 else "AND"

            if "q" in args:
                query.append("MATCH (u :%s :USER)-[r :%s]->(i :ITEM :%s)\n" % (organization, label(args["q"]), organization))
            else:
                query.append("MATCH (u :%s :USER)-[r]->(i :ITEM :%s)\n" % (organization, organization))

            if "occurredBefore" in args:
                query.append("%s r.timestamp < {timeCeiling} " % s())
                params["timeCeiling"] = args["occurredBefore"]
                c += 1
            if "occurredAfter" in args:
                query.append("%s r.timestamp > {floor} " % s())
                params["timeFloor"] = args["occurredAfter"]
                c += 1

        #RETURN
        if "fields" in args:

            query.append("RETURN ")

            c = 0
            fields = args["fields"].split(',')
            n = len(fields)
            for field in fields:

                if c == n - 1:
                    query.append("r.%s AS %s " % (field, field))
                else:
                    query.append("r.%s AS %s, " % (field, field))

                c += 1

        else:

            query.append("RETURN ")
            c = 0
            s = lambda: ", " if c > 0 else " "
            for p in ActionSchema.get_properties(True):
                query.append("%s i.%s AS %s" % (s(), p, p))
                c += 1

        query.append("\n")

        #LIMIT/OFFSET
        if "id" not in args:
            query.append("SKIP {offset}\n")
            if "offset" in args:
                params["offset"] = args["offset"]
            else:
                #not a 1 item request
                params["offset"] = 0

            query.append("LIMIT {limit}\n")
            if "limit" in args:
                params["limit"] = args["limit"]
            else:
                #not a 1 item request (cap response)
                params["limit"] = 10

        #print 'query: ', ''.join(query)
        #print 'params: ', params

        return ''.join(query), params

    def update(self, args):

        organization = args["organization"].upper()

        query = []
        params = {}

        query.append("MATCH (u :USER :%s)-[r {id: {id}}]->(i :ITEM :%s)\n" % (organization, organization))
        params["id"] = args["id"]

        properties = ["timestamp", "ipAddress", "sessionId", "guid", "agent", "quantum"]

        c = 0
        s = lambda: "SET" if c == 0 else ","
        for p in properties:
            if p in args:
                query.append("%s r.%s = {%s} " % (s(), p, p))
                params[p] = args[p]
                c += 1

        #RESULT
        query.append("RETURN ")
        c = 0
        s = lambda: ", " if c > 0 else " "
        for p in ActionSchema.get_properties(True):
            query.append("%s i.%s AS %s" % (s(), p, p))
            c += 1

        query.append("\n")

        #print 'query: ', ''.join(query)
        #print 'params: ', params

        return ''.join(query), params

    def delete(self, args):

        organization = args["organization"].upper()

        query = []
        params = {}

        query.append("MATCH (u :USER :%s)-[r {id: {id}}]->(i :ITEM :%s)\n" % (organization, organization))
        params["id"] = args["id"]
        query.append("WITH r, r.id AS id\n")
        query.append("DELETE r\n")
        query.append("RETURN id\n")

        #print 'query: ', ''.join(query)
        #print 'params: ', params

        return ''.join(query), params