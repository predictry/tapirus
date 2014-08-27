__author__ = 'guilherme'

from predictry.engine.graph.query.generator.processes.base import ProcessQueryGeneratorBase
from predictry.engine.models.resources.user import UserSchema
from predictry.engine.models.resources.item import ItemSchema
from predictry.engine.models.resources.session import SessionSchema


class RecommendationQueryGenerator(ProcessQueryGeneratorBase):

    def __init__(self):
        pass

    def generate(self, args):

        domain = args["domain"]

        query = []
        params = {}

        rtype = args["type"]

        #other items viewed/purchased together
        if rtype in ["oivt", "oipt"]:

            action = lambda x: {
                "oivt": "VIEW",
                "oipt": "BUY"
            }[x]

            query.append("MATCH (i :%s:%s {id:{item_id}})\n"
                          "WITH i\n"
                          "MATCH (s :%s:%s)-[r :%s]->(i)\n"
                          "WITH i,s\n"
                          "MATCH (s)-[r :%s]->(x :%s:%s)\n"
                          "WHERE x <> i\n"
                          "RETURN DISTINCT x.id AS id, COUNT(x.id) AS matches"
                         % (domain, ItemSchema.get_label(),
                            domain, SessionSchema.get_label(), action(rtype),
                            action(rtype), domain, ItemSchema.get_label()))

            if "fields" in args:
                fields = [x for x in args["fields"].split(",") if x not in ["id"]]
                for field in fields:
                    query.append(", x.%s AS %s" % (field, field))

            query.append("\n")
            query.append("ORDER BY matches DESC\n"
                         "LIMIT {limit}")

            params["item_id"] = int(args["item_id"])

            if "limit" in args:
                params["limit"] = args["limit"]
            else:
                params["limit"] = 10

        #other items viewed/purchased
        elif rtype in ["oiv", "oip"]:

            action = lambda x: {
                "oiv": "VIEW",
                "oip": "BUY"
            }[x]

            query.append("MATCH (i :%s:%s {id:{item_id}})\n"
                         "WITH i\n"
                         "MATCH (s :%s:%s)-[r :%s]->(i)\n"
                         "WITH i,s\n"
                         "MATCH (s)-[r :BY]->(u:%s:%s)\n"
                         "WITH i,s,u\n"
                         "MATCH (s2 :%s:%s)-[r :BY]->(u)\n"
                         "WITH i,s,u,s2\n"
                         "MATCH (s2)-[r :%s]->(x :%s:%s)\n"
                         "WHERE x <> i\n"
                         "RETURN DISTINCT x.id AS id, COUNT(x.id) AS matches"
                         % (domain, ItemSchema.get_label(),
                            domain, SessionSchema.get_label(), action(rtype),
                            domain, UserSchema.get_label(),
                            domain, SessionSchema.get_label(),
                            action(rtype), domain, ItemSchema.get_label()))

            if "fields" in args:
                fields = [x for x in args["fields"].split(",") if x not in ["id"]]
                for field in fields:
                    query.append(", x.%s AS %s" % (field, field))

            query.append("\n")
            query.append("ORDER BY matches DESC\n"
                         "LIMIT {limit}")
            params["item_id"] = int(args["item_id"])

            if "limit" in args:
                params["limit"] = args["limit"]
            else:
                params["limit"] = 10

        elif rtype in ["rts"]:

            query.append("MATCH (s :%s:%s)-[r :BUY]->(x :%s:%s)\n"
                         "WITH s,r,x\n"
                         "ORDER BY r.timestamp DESC\n"
                         "LIMIT 1000\n"
                         "RETURN DISTINCT x.id AS id, COUNT(x.id) AS matches"
                         % (domain, SessionSchema.get_label(),
                            domain, ItemSchema.get_label()))

            if "fields" in args:
                fields = [x for x in args["fields"].split(",") if x not in ["id"]]
                for field in fields:
                    query.append(", x.%s AS %s" % (field, field))

            query.append("\n")
            query.append("ORDER BY matches DESC\n"
                         "LIMIT {limit}")

            if "limit" in args:
                params["limit"] = args["limit"]
            else:
                params["limit"] = 10

        #print "query:", ''.join(query)
        #print params

        return ''.join(query), params