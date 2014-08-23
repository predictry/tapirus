__author__ = 'guilherme'

from predictry.engine.graph.query.generator.processes.base import ProcessQueryGeneratorBase
from predictry.utils import timer
from predictry.engine.models.resources.user import UserSchema
from predictry.engine.models.resources.item import ItemSchema


class RecommendationQueryGenerator(ProcessQueryGeneratorBase):

    def __init__(self):
        pass

    @timer.timefunc
    def generate(self, args):

        domain = args["domain"]

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

            query.append("MATCH (u :%s:%s)-[r1 :%s]->(i :%s:%s {id: {item_id}})\n" %
                         (domain, UserSchema.get_label(), action(qtype), domain, ItemSchema.get_label()))
            query.append("MATCH (u)-[r2 :%s]->(x :%s:%s)\n" %
                         (action(qtype), domain, ItemSchema.get_label()))
            query.append("WHERE r1.session_id = r2.session_id AND x <> i ")
            c += 1

            if "price_floor" in args:
                query.append(" %s x.price >= {price_floor} " % (sep()))
                params["price_floor"] = args["price_floor"]
                c += 1

            if "price_ceiling" in args:
                query.append(" %s x.price <= {price_ceiling} " % (sep()))
                params["price_ceiling"] = args["price_ceiling"]
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
            query.append("RETURN u.id AS collection_id, COLLECT(DISTINCT r1.session_id) AS sessions, "
                         "COLLECT(DISTINCT x.id) AS items, COUNT(x.id) AS basket_size\n")
            query.append("LIMIT {limit}\n")

            params["item_id"] = args["item_id"]
            params["limit"] = 100

        #other items viewed
        elif qtype in ["oiv", "oip"]:

            action = lambda x: {
                "oiv": "VIEWED",
                "oip": "BOUGHT"
            }[x]

            query.append("MATCH (i :%s:%s)\n" %
                         (domain, ItemSchema.get_label()))
            query.append("WHERE i.id = {item_id}\n")
            query.append("WITH i AS i\n")
            query.append("    MATCH (u :%s:USER)-[:%s]->(i)\n" % (domain, action(qtype)))
            query.append("    WITH i AS i, u AS u\n")
            query.append("        MATCH (u)-[:%s]->(x :%s:%s)\n" %
                         (action(qtype), domain, ItemSchema.get_label()))
            query.append("        WHERE x <> i ")
            c += 1

            if "price_floor" in args:
                query.append(" %s x.price >= {price_floor} " % (sep()))
                params["price_floor"] = args["price_floor"]
                c += 1

            if "price_ceiling" in args:
                query.append(" %s x.price <= {price_ceiling} " % (sep()))
                params["price_ceiling"] = args["price_ceiling"]
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
            query.append("        RETURN u.id AS collection_id, COLLECT(DISTINCT x.id) AS items\n")
            query.append("        LIMIT {limit}\n")

            params["item_id"] = args["item_id"]
            params["limit"] = 100

        return ''.join(query), params