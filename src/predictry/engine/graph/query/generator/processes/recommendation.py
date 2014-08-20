__author__ = 'guilherme'

from predictry.engine.graph.query.generator.processes.base import ProcessQueryGeneratorBase

class RecommendationQueryGenerator(ProcessQueryGeneratorBase):

    def __init__(self):
        pass

    def generate(self, args):

        domain = args["domain"].upper()

        query = []
        params = {}

        qtype = args["type"]
        c = 0
        sep = lambda: "AND" if c > 0 else ""

        #other items viewed/purchased together
        if qtype in ["oivt", "oipt"]:

            action = lambda x: {
                "oivt": "VIEWED",
                "oipt": "BOUGHT"
            }[x]

            query.append("MATCH (u :%s:USER)-[r1 :%s]->(i :%s:ITEM {id: {itemId}})\n" % (domain, action(qtype), domain))
            query.append("MATCH (u)-[r2 :%s]->(x :%s:ITEM)\n" % (action(qtype), domain))
            query.append("WHERE r1.sessionId = r2.sessionId AND x <> i ")
            c += 1

            if "priceFloor" in args:
                query.append(" %s x.price >= {priceFloor} " % (sep()))
                params["priceFloor"] = args["priceFloor"]
                c += 1

            if "priceCeiling" in args:
                query.append(" %s x.price <= {priceCeiling} " % (sep()))
                params["priceCeiling"] = args["priceCeiling"]
                c += 1

            if "locations" in args:
                query.append(" %s ANY(location in x.locations WHERE location in {locations}) " % (sep()))
                params["locations"] = args["locations"]
                c += 1

            if "tags" in args:
                query.append(" %s ANY(tag in x.tags WHERE tag in {tags}) " % (sep()))
                params["tags"] = args["tags"]
                c += 1

            if "category" in args:
                query.append(" %s x.category = {category} " % (sep()))
                params["category"] = args["category"]
                c += 1

            if "subcategory" in args:
                query.append(" %s x.subcategory = {subcategory} " % (sep()))
                params["subcategory"] = args["subcategory"]
                c += 1

            query.append("\n")
            query.append("RETURN u.id AS collectionId, COLLECT(DISTINCT r1.sessionId) AS sessions, "
                         "COLLECT(DISTINCT x.id) AS items, COUNT(x.id) AS basketSize\n")
            query.append("LIMIT {limit}\n")

            params["itemId"] = args["itemId"]
            params["limit"] = 100

        #other items viewed
        elif qtype in ["oiv", "oip"]:

            action = lambda x: {
                "oiv": "VIEWED",
                "oip": "BOUGHT"
            }[x]

            query.append("MATCH (i :%s:ITEM)\n" % domain)
            query.append("WHERE i.id = {itemId}\n")
            query.append("WITH i AS i\n")
            query.append("    MATCH (u :%s:USER)-[:%s]->(i)\n" % (domain, action(qtype)))
            query.append("    WITH i AS i, u AS u\n")
            query.append("        MATCH (u)-[:%s]->(x :%s:ITEM)\n" % (action(qtype), domain))
            query.append("        WHERE x <> i ")
            c += 1

            if "priceFloor" in args:
                query.append(" %s x.price >= {priceFloor} " % (sep()))
                params["priceFloor"] = args["priceFloor"]
                c += 1

            if "priceCeiling" in args:
                query.append(" %s x.price <= {priceCeiling} " % (sep()))
                params["priceCeiling"] = args["priceCeiling"]
                c += 1

            if "locations" in args:
                query.append(" %s ANY(location in x.locations WHERE location in {locations}) " % (sep()))
                params["locations"] = args["locations"]
                c += 1

            if "tags" in args:
                query.append(" %s ANY(tag in x.tags WHERE tag in {tags}) " % (sep()))
                params["tags"] = args["tags"]
                c += 1

            if "category" in args:
                query.append(" %s x.category = {category} " % (sep()))
                params["category"] = args["category"]
                c += 1

            if "subcategory" in args:
                query.append(" %s x.subcategory = {subcategory} " % (sep()))
                params["subcategory"] = args["subcategory"]
                c += 1

            query.append("\n")
            query.append("        WITH i AS i, u AS u, x AS x\n")
            query.append("        RETURN u.id AS collectionId, COLLECT(DISTINCT x.id) AS items\n")
            query.append("        LIMIT {limit}\n")

            params["itemId"] = args["itemId"]
            params["limit"] = 100

        return ''.join(query), params