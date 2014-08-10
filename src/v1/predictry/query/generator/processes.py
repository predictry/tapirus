__author__ = 'guilherme'

from v1.predictry.query.generator.base import ProcessQueryGeneratorBase

class RecommendationQueryGenerator(ProcessQueryGeneratorBase):

    def __init__(self):
        pass

    def generate(self, args):

        organization = args["organization"].upper()

        query = []
        params = {}

        qtype = args["type"]

        #other items viewed/purchased together
        if qtype in ["oivt", "oipt"]:

            action = lambda x: {
                "oivt": "VIEWED",
                "oipt": "BOUGHT"
            }[x]

            query.append("MATCH (u :%s:USER)-[r1 :%s]->(i :%s:ITEM {id: {itemId}})\n" % (organization, action(qtype), organization))
            query.append("MATCH (u)-[r2 :%s]->(x :%s:ITEM)\n" % (action(qtype), organization))
            query.append("WHERE r1.sessionid = r2.sessionid AND x <> i\n")
            query.append("RETURN u.id AS collectionId, COLLECT(DISTINCT r1.sessionid) AS sessions, COLLECT(DISTINCT x.id) AS items, COUNT(x.id) AS basketSize\n")
            query.append("LIMIT {limit}\n")

            params["itemId"] = args["itemId"]
            params["limit"] = 100

        #other items viewed
        elif qtype in ["oiv", "oip"]:

            action = lambda x: {
                "oiv": "VIEWED",
                "oip": "BOUGHT"
            }[x]

            """
                    MATCH (i :STORE:ITEM)
                    USING INDEX i:ITEM(id)
                    WHERE i.id = {itemId}
                    WITH i AS i
                        MATCH (u :STORE:USER)-[:VIEWED]->(i)
                        WITH i AS i, u AS u
                            MATCH (u)-[:VIEWED]->(x :SHOP:ITEM)
                            WHERE x <> i
                            WITH i AS i, u AS u, x AS x
                            RETURN u.id AS collectionId, COLLECT(DISTINCT x.id) AS items
                            LIMIT {limit}"""


            query.append("MATCH (i :%s:ITEM)\n" % organization)
            query.append("USING INDEX i:ITEM(id)\n")
            query.append("WHERE i.id = {itemId}\n")
            query.append("WITH i AS i\n")
            query.append("    MATCH (u :%s:USER)-[:%s]->(i)\n" % (organization, action(qtype)))
            query.append("    WITH i AS i, u AS u\n")
            query.append("        MATCH (u)-[:%s]->(x :%s:ITEM)\n" % (action(qtype), organization))
            query.append("        WHERE x <> i\n")
            query.append("        WITH i AS i, u AS u, x AS x\n")
            query.append("        RETURN u.id AS collectionId, COLLECT(DISTINCT x.id) AS items\n")
            query.append("        LIMIT {limit}\n")

            params["itemId"] = args["itemId"]
            params["limit"] = 100

        elif qtype in ["vap", "pav"]:

            action = []
            if qtype == "vap":
                action.append("BOUGHT")
                action.append("VIEWED")
            else:
                action.append("VIEWED")
                action.append("BOUGHT")

            #place filtering on the where clause (x-[r]-y)
            query.append("MATCH (u :%s:USER)-[first_rel :%s]->(i :%s:ITEM {id:{itemId}})\n" % (organization, action[0], organization))
            query.append("WITH u,first_rel,i\n")
            query.append("MATCH (u)-[sec_rel :%s]->(i2 :%s:ITEM)\n" % (action[1], organization))
            query.append("WHERE first_rel.sessionid = sec_rel.sessionid AND first_rel.dt_added < sec_rel.dt_added AND i <> i2\n")
            query.append("RETURN i.id AS collectionId, COLLECT(DISTINCT sec_rel.sessionid) AS collections, COLLECT(i2.id) AS items\n")
            #query.append("ORDER BY COALESCE(collectionId, -5000) DESC\n")
            query.append("LIMIT {limit}")

            params["itemId"] = args["itemId"]
            params["limit"] = 100

        #print 'query: ', ''.join(query)
        #print 'params: ', params

        return ''.join(query), params