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
                "oivt": "view",
                "oipt": "buy"
            }[x]

            #MATCH (i:redmart:item{id:5124})<-[r:VIEW]-(s:session:redmart)-[:VIEW]->(x:redmart:item)
            #WHERE i <> x
            #RETURN DISTINCT x.id AS id, COUNT(x.id) AS matches
            #ORDER BY matches DESC
            #LIMIT 5

            query.append("MATCH (i :%s:%s{id:{item_id}})<-[r :%s]"
                         "-(s :%s:%s)-[:%s]"
                         "->(x :%s:%s)\n"
                         "WHERE i <> x\n"
                         "RETURN DISTINCT x.id AS id, COUNT(x.id) AS matches"
            #             "WITH i\n"
            #             "MATCH (s :%s:%s)-[r :%s]->(i)\n"
            #             "WITH i,s\n"
            #             "MATCH (s)-[r :%s]->(x :%s:%s)\n"
            #             "WHERE x <> i\n"
            #             "RETURN DISTINCT x.id AS id, COUNT(x.id) AS matches"
                         % (domain, ItemSchema.get_label(), action(rtype),
                            domain, SessionSchema.get_label(), action(rtype),
                            domain, ItemSchema.get_label()))

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
            #todo: this query looks for items purchased/viewed by this same user when he/she did not purchase/or view
            #a particular item x

            action = lambda x: {
                "oiv": "view",
                "oip": "buy"
            }[x]

            query.append("MATCH (i :%s:%s {id:{item_id}})<-[r1 :%s]"
                         "-(s1 :%s:%s)-[:by]->(u :%s:%s)<-[:by]"
                         "-(s2 :%s:%s)-[:%s]->(x :%s:%s)\n"
                         "WHERE i <> x AND s1 <> s2\n"
                         "RETURN x.id AS id"
                         % (domain, ItemSchema.get_label(), action(rtype),
                            domain, SessionSchema.get_label(), domain, UserSchema.get_label(),
                            domain, SessionSchema.get_label(), action(rtype), domain, ItemSchema.get_label()))

            #query.append("MATCH (i :%s:%s {id:{item_id}})\n"
            #             "WITH i\n"
            #             "MATCH (s :%s:%s)-[r :%s]->(i)\n"
            #             "WITH i,s\n"
            #             "MATCH (s)-[r :BY]->(u:%s:%s)\n"
            #             "WITH i,s,u\n"
            #             "MATCH (s2 :%s:%s)-[r :BY]->(u)\n"
            #             "WITH i,s,u,s2\n"
            #             "MATCH (s2)-[r :%s]->(x :%s:%s)\n"
            #             "WHERE s <> s2\n"
            #             "RETURN DISTINCT x.id AS id, COUNT(x.id) AS matches"
            #             % (domain, ItemSchema.get_label(),
            #                domain, SessionSchema.get_label(), action(rtype),
            #                domain, UserSchema.get_label(),
            #                domain, SessionSchema.get_label(),
            #                action(rtype), domain, ItemSchema.get_label()))

            if "fields" in args:
                fields = [x for x in args["fields"].split(",") if x not in ["id"]]
                for field in fields:
                    query.append(", x.%s AS %s" % (field, field))

            query.append("\n")
            query.append("LIMIT {limit}")
            params["item_id"] = int(args["item_id"])

            #if "limit" in args:
            #    params["limit"] = args["limit"]
            #else:
            #   params["limit"] = 10
            params["limit"] = 300

        elif rtype in ["trv", "trp", "trac"]:

            action = lambda x: {
                "trv": "view",
                "trp": "buy",
                "trac": "add_to_cart"
            }[x]

            query.append("MATCH (s :%s:%s)-[r :%s]->(x :%s:%s)\n"
                         "WITH s,r,x\n"
                         "ORDER BY r.timestamp DESC\n"
                         "LIMIT 500\n"
                         "RETURN DISTINCT x.id AS id, COUNT(x.id) AS matches"
                         % (domain, SessionSchema.get_label(), action(rtype),
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

        print "query:", ''.join(query)
        print params

        return ''.join(query), params