__author__ = 'guilherme'

from predictry.engine.graph.query.generator.services.base import ProcessQueryGeneratorBase
from predictry.engine.models.resources.user import UserSchema
from predictry.engine.models.resources.item import ItemSchema
from predictry.engine.models.resources.session import SessionSchema

FILTER_TOKEN_SEPARATOR = "$"
FILTER_SEPARATOR = "|"
FILTER_LAYOUT = "variable$op$value$data_type$ls"
FILTER_DATA_TYPES = ["bool", "num", "str", "date"]
FILTER_OPS = ["e", "gt", "gte", "lt", "lte", "cti", "ncti"]
FILTER_ATOMIC_OPS = ["e", "gt", "gte", "lt", "lte"]
FILTER_LIST_OPS = ["cti", "ncti"]


def parse_filters(q):

    filters = []
    flts = q.split(FILTER_SEPARATOR)

    for flt in flts:
        tokens = flt.split(FILTER_TOKEN_SEPARATOR)

        if len(tokens) == 4:
            if tokens[3] in FILTER_DATA_TYPES:
                if tokens[1] in FILTER_OPS:
                    variable = tokens[0]
                    op = tokens[1]
                    data_type = tokens[3]

                    value = parse_data_type(tokens[2], data_type)

                    filters.append(Filter(variable, op, value, data_type))

        elif len(tokens) == 5:
            if tokens[4] == "ls":
                if tokens[3] in FILTER_DATA_TYPES:
                    if tokens[1] in FILTER_OPS:
                        variable = tokens[0]
                        op = tokens[1]
                        data_type = tokens[3]

                        value = parse_data_type(tokens[2].split(","), data_type, is_list=True)

                        filters.append(Filter(variable, op, value, data_type))

    return filters


def parse_data_type(s, data_type, is_list=False):

    if is_list:
        values = []
        for token in s:
            if data_type == "num":
                values.append(float(token))
            elif data_type == "date":
                values.append(long(token))
            elif data_type == "bool":
                return bool(token)
            else:
                values.append(token.strip())
        return values
    else:
        if data_type == "num":
            return float(s)
        elif data_type == "date":
            return long(s)
        elif data_type == "bool":
            return bool(s)
        else:
            return s.strip()


def translate_filters(filters, ref, concatenate=False):

    cypher_statements = []
    params = {}

    op = lambda op: {
        "e": "=",
        "gt": ">",
        "gte": ">=",
        "lt": "<",
        "lte": "<=",
    }[op]

    if type(filters) is list:

        c = 0

        for flt in filters:

            set_value = False

            cypher = []
            if isinstance(flt, Filter):
                if flt.op in FILTER_ATOMIC_OPS:
                    if flt.data_type in FILTER_DATA_TYPES:

                        if flt.data_type == "bool":
                            if flt.op == "e":
                                set_value = True
                        else:
                            set_value = True

                        if set_value:
                            cypher.append(ref + "." + flt.variable)
                            cypher.append(op(flt.op))
                            cypher.append("{" + flt.variable + "}")

                            params[flt.variable] = flt.value

                #assumes target property is a list
                elif flt.op in FILTER_LIST_OPS:
                    if flt.data_type in FILTER_DATA_TYPES:

                        if type(flt.value) is list:
                            # HAS (x.region) AND ALL(v in ["a", "k"] WHERE v IN x.region)

                            cypher.append("HAS")
                            cypher.append("(" + ref + "." + flt.variable + ")")
                            cypher.append("AND")

                            if flt.op == "cti":
                                cypher.append("ALL(")
                            else:
                                cypher.append("NONE(")

                            cypher.append("x IN")
                            cypher.append("{" + flt.variable + "}")
                            cypher.append("WHERE")
                            cypher.append("x IN")
                            cypher.append(ref + "." + flt.variable)
                            cypher.append(")")

                        else:
                            #HAS (x.region) AND v IN x.region

                            cypher.append("HAS")
                            cypher.append("(" + ref + "." + flt.variable + ")")
                            cypher.append("AND")
                            cypher.append("{" + flt.variable + "}")
                            cypher.append("IN")
                            cypher.append(ref + "." + flt.variable)

                        params[flt.variable] = flt.value
                        set_value = True

            if concatenate and set_value:
                cypher_statements.append(" AND ")
            else:
                if c > 0 and set:
                    cypher_statements.append(" AND ")
                else:
                    cypher_statements.append(" ")

            if set_value:
                c += 1

            cypher_statements.append(' '.join(cypher))

    return ''.join(cypher_statements), params


class Filter:

    def __init__(self, variable, op, value, data_type):
        self.variable = variable
        self.op = op
        self.value = value
        self.data_type = data_type

'''
MATCH (u:user:redmart {id:54762})-[]-()-[vr :view]-(x:redmart:item)
OPTIONAL MATCH (u)-[]-()-[br :buy]-(x:redmart:item)
WHERE vr.timestamp < br.timestamp AND br is NULL
WITH u,vr,x
ORDER BY vr.timestamp DESC
LIMIT 100
RETURN DISTINCT x.id AS id, COUNT(x) AS matches
ORDER BY matches DESC
LIMIT 5
'''

class RecommendationQueryGenerator(ProcessQueryGeneratorBase):

    def __init__(self):
        pass

    def generate(self, args):

        domain = args["domain"]

        query = []
        params = {}

        rtype = args["type"]

        filters = []
        if "q" in args:
            filters = parse_filters(args["q"])

        #other items viewed/purchased together
        if rtype in ["oivt", "oipt"]:

            action = lambda x: {
                "oivt": "view",
                "oipt": "buy"
            }[x]

            query.append("MATCH (i :%s:%s{id:{item_id}})<-[r :%s]"
                         "-(s :%s:%s)-[:%s]"
                         "->(x :%s:%s)\n"
                         "WHERE i <> x"
                         % (domain, ItemSchema.get_label(), action(rtype),
                            domain, SessionSchema.get_label(), action(rtype),
                            domain, ItemSchema.get_label()))

            if filters:
                q, params = translate_filters(filters, ref="x", concatenate=True)
                query.append(q)
                params.update(params)

            query.append("\n")
            query.append("RETURN DISTINCT x.id AS id, COUNT(x.id) AS matches")

            if "fields" in args:
                fields = [x for x in args["fields"].split(",") if x not in ["id"]]
                for field in fields:
                    query.append(", x.%s AS %s" % (field, field))

            query.append("\n")
            query.append("ORDER BY matches DESC\n"
                         "LIMIT {limit}")

            params["item_id"] = int(args["item_id"])

            if "limit" in args:
                params["limit"] = int(args["limit"])
            else:
                params["limit"] = 5

        #other items viewed/purchased
        elif rtype in ["oiv", "oip"]:
            #this query looks for items purchased/viewed by
            #this same user when he/she did not purchase/or view
            #a particular item x

            action = lambda x: {
                "oiv": "view",
                "oip": "buy"
            }[x]

            query.append("MATCH (i :%s:%s {id:{item_id}})<-[r1 :%s]"
                         "-(s1 :%s:%s)-[:by]->(u :%s:%s)<-[:by]"
                         "-(s2 :%s:%s)-[:%s]->(x :%s:%s)\n"
                         "WHERE i <> x AND s1 <> s2"
                         % (domain, ItemSchema.get_label(), action(rtype),
                            domain, SessionSchema.get_label(), domain, UserSchema.get_label(),
                            domain, SessionSchema.get_label(), action(rtype), domain, ItemSchema.get_label()))

            if filters:
                q, params = translate_filters(filters, ref="x", concatenate=True)
                query.append(q)
                params.update(params)

            query.append("\n")
            query.append("RETURN x.id AS id")

            if "fields" in args:
                fields = [x for x in args["fields"].split(",") if x not in ["id"]]
                for field in fields:
                    query.append(", x.%s AS %s" % (field, field))

            query.append("\n")
            query.append("LIMIT {limit}")
            params["item_id"] = int(args["item_id"])

            params["limit"] = 300

        elif rtype in ["trv", "trp", "trac"]:

            query.append("MATCH (n :%s:%s {rtype: {rtype}})\n"
                         % (domain, "trend"))
            query.append("RETURN n.items AS items, n.matches AS matches")

            params["rtype"] = rtype


        elif rtype in ["utrp", "utrv", "utrac"]:

            action = lambda x: {
                "utrv": "view",
                "utrp": "buy",
                "utrac": "add_to_cart"
            }[x]

            '''
            MATCH (u:%s:%s {id:{item_id}})
            WITH u
            MATCH (u)<-[:by]-(s:%s:%s)
            WITH DISTINCT s
            MATCH (s)-[r :%s]->(x:%s:%s)
            WITH r, x
            ORDER BY r.timestamp DESC
            LIMIT {ntx}
            RETURN DISTINCT x.id AS id, COUNT(x) AS matches
            ORDER BY matches DESC
            LIMIT {limit}
            '''

            query.append("MATCH (u:%s:%s {id:{user_id}})\n"
                         "WITH u\n"
                         "MATCH (u)<-[:by]-(s :%s:%s)\n"
                         "WITH DISTINCT s\n"
                         "MATCH (s)-[r :%s]->(x :%s:%s)\n"
                         "WITH r, x\n"
                         "ORDER BY r.timestamp DESC\n"
                         "LIMIT {ntx}\n"
                         % (domain, UserSchema.get_label(),
                            domain, SessionSchema.get_label(), action(rtype),
                            domain, ItemSchema.get_label()))

            query.append("RETURN DISTINCT x.id AS id, COUNT(x.id) AS matches")

            if "fields" in args:
                fields = [x for x in args["fields"].split(",") if x not in ["id"]]
                for field in fields:
                    query.append(", x.%s AS %s" % (field, field))

            query.append("\n")
            query.append("ORDER BY matches DESC\n"
                         "LIMIT {limit}")

            params["user_id"] = int(args["user_id"])
            params["ntx"] = 50

            if "limit" in args:
                params["limit"] = int(args["limit"])
            else:
                params["limit"] = 5

        elif rtype in ["uvnp"]: #todo: merge with uacnp, and replace query

            action = lambda x: ["view", "buy"][x]

            query.append("MATCH (u :%s:%s {id:{user_id}})<-[:by]-(:%s:%s)-[vr :%s]->(x :%s:%s)\n"
                         "WITH DISTINCT vr, x, u\n"
                         "ORDER BY vr.timestamp DESC\n"
                         "LIMIT {ntx}\n"
                         "OPTIONAL MATCH (u)<-[:by]-(:%s:%s)-[br :%s]->(x)\n"
                         "WHERE br is NULL\n"
                         % (domain, UserSchema.get_label(),
                            domain, SessionSchema.get_label(), action(0),
                            domain, ItemSchema.get_label(),
                            domain, SessionSchema.get_label(), action(1)))

            query.append("RETURN DISTINCT x.id AS id, COUNT(x.id) AS matches")

            if "fields" in args:
                fields = [x for x in args["fields"].split(",") if x not in ["id"]]
                for field in fields:
                    query.append(", x.%s AS %s" % (field, field))

            query.append("\n")
            query.append("ORDER BY matches DESC\n"
                         "LIMIT {limit}")

            params["user_id"] = int(args["user_id"])
            params["ntx"] = 50

            if "limit" in args:
                params["limit"] = int(args["limit"])
            else:
                params["limit"] = 5

        elif rtype in ["uacnp"]:

            action = lambda x: ["add_to_cart", "buy"][x]

            query.append("MATCH (u :%s:%s {id:{user_id}})<-[:by]-(s:%s:%s)-[vr :%s]->(x :%s:%s)\n"
                         "WITH DISTINCT s, vr, x\n"
                         "ORDER BY vr.timestamp DESC\n"
                         "LIMIT {ntx}\n"
                         "OPTIONAL MATCH (u)<-[:by]-(s)-[br :%s]->(x)\n"
                         "WHERE br is NULL\n"
                         % (domain, UserSchema.get_label(),
                            domain, SessionSchema.get_label(), action(0),
                            domain, ItemSchema.get_label(),
                            action(1)))

            query.append("RETURN DISTINCT x.id AS id, COUNT(x.id) AS matches")

            if "fields" in args:
                fields = [x for x in args["fields"].split(",") if x not in ["id"]]
                for field in fields:
                    query.append(", x.%s AS %s" % (field, field))

            query.append("\n")
            query.append("ORDER BY matches DESC\n"
                         "LIMIT {limit}")

            params["user_id"] = int(args["user_id"])
            params["ntx"] = 50

            if "limit" in args:
                params["limit"] = int(args["limit"])
            else:
                params["limit"] = 5

        #print "query:", ''.join(query)
        #print params

        return ''.join(query), params
