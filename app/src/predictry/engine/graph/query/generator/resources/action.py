__author__ = 'guilherme'

from predictry.engine.graph.query.generator.resources.base import ResourceQueryGeneratorBase
from predictry.engine.models.resources.item import ItemSchema
from predictry.engine.models.resources.session import SessionSchema
from predictry.engine.models.resources.browser import BrowserSchema
from predictry.engine.models.resources.user import UserSchema
from predictry.utils.neo4j import cypher


class ActionQueryGenerator(ResourceQueryGeneratorBase):
    def __init__(self):
        pass

    def create(self, args, data):

        domain = args["domain"]

        query = []
        params = {}

        action_properties = []
        return_properties = []

        s = lambda c: ", " if c > 0 else " "

        params["item_id"] = data["item_id"]
        params["session_id"] = data["session_id"]
        params["browser_id"] = data["browser_id"]
        if "user_id" in data:
            params["user_id"] = data["user_id"]

        c = 0
        for k, v in data.iteritems():
            if k not in ["item_id", "browser_id", "session_id", "user_id", "type"]:
                action_properties.append("{separator} {key} : {{ {key} }} ".format(
                    separator=s(c), key=k
                ))
                return_properties.append("{0}r_action.{1} AS {2}".format(
                    s(c), k, k))
                if type(data[k]) is str:
                    data[k] = data[k].strip()
                params[k] = data[k]
                c += 1

        return_properties.append("{0} TYPE(r_action) AS type".format(
            s(c)
        ))

        query.append("MERGE (i :{domain} :{item_label} {{id: {{item_id}} }})\n".format(
            domain=domain, item_label=ItemSchema.get_label()
        ))
        query.append("WITH i\n".format())
        query.append("MERGE (s :{domain} :{session_label} {{id: {{session_id}} }})\n".format(
            domain=domain, session_label=SessionSchema.get_label()
        ))
        query.append("ON CREATE SET s.timestamp = {{timestamp}}\n".format())
        query.append("WITH i, s\n".format())
        query.append("MERGE (b :{domain} :{browser_label} {{id: {{browser_id}} }})\n".format(
            domain=domain, browser_label=BrowserSchema.get_label()
        ))
        query.append("WITH i, s, b\n".format())
        query.append("MERGE (s)-[r_on :on]->(b)\n".format())
        query.append("MERGE (s)-[r_action :{type} {{{properties}}}]->(i)\n".format(
            type=data["type"], properties=''.join(action_properties)
        ))

        if "user_id" in data:
            query.append("MERGE (u :{domain} :{user_label} {{id: {{user_id}} }})\n".format(
                domain=domain, user_label=UserSchema.get_label()
            ))
            query.append("WITH i, s, b, u, r_action\n".format())

            query.append("MERGE (s)-[r_by :by]->(u)\n".format())
        query.append("RETURN {0}\n".format(
            ''.join(return_properties)
        ))

        #print 'query: ', ''.join(query)
        #print 'params: ', params

        return ''.join(query), params

    def read(self, args):

        domain = args["domain"]

        query = []
        params = {}

        if "id" in args:
            params["id"] = args["id"]
            query.append("MATCH (s :{domain} :{session_label} )-[r {{id: {{id}}}}]->(i :{domain} :{item_label} )\n".format(
                domain=domain, session_label=SessionSchema.get_label(), item_label=ItemSchema.get_label()
            ))
        else:
            if "type" in args:
                query.append("MATCH (s :{domain} :{session_label})-[r :{rtype}]->(i :{domain} :{item_label})\n".format(
                    domain=domain, session_label=SessionSchema.get_label(), item_label=ItemSchema.get_label(),
                    rtype=args["type"]
                ))
            else:
                query.append("MATCH (s :{domain} :{session_label})-[r]->(i :{domain} :{item_label})\n".format(
                    domain=domain, session_label=SessionSchema.get_label(), item_label=ItemSchema.get_label()
                ))

        c = 0
        s = lambda: ", " if c > 0 else " "

        #RETURN
        query.append("RETURN r.id AS id".format())

        if "fields" in args:
            fields = [x for x in args["fields"].split(',') if x not in ["id", "type"]]
            for field in fields:
                query.append(", r.{0} AS {0} ".format(field))

        query.append(", type(r) AS type ".format())
        query.append("\n".format())

        #LIMIT/OFFSET
        if "id" not in args:
            #not a 1 item request
            query.append("SKIP {{offset}}\n".format())
            if "offset" in args:
                params["offset"] = args["offset"]
            else:
                params["offset"] = 0

            query.append("LIMIT {{limit}}\n".format())
            if "limit" in args:
                params["limit"] = args["limit"]
            else:
                params["limit"] = 10

        #print 'query: ', ''.join(query)
        #print 'params: ', params

        return ''.join(query), params

    def update(self, args, data):

        domain = args["domain"]

        query = []
        params = {}

        params["id"] = args["id"]

        query.append("MATCH (s :{domain} :{session_label})-[r {{id: {{id}}}}]->(i :{domain} :{item_label})\n".format(
            domain=domain, session_label=SessionSchema.get_label(), item_label=ItemSchema.get_label()
        ))

        c = 0
        s = lambda: "SET" if c == 0 else ","
        for k, v in data.iteritems():
            query.append("{0} r.{1} = {1} ".format(s(), k))
            params[k] = data[k]
            c += 1

        query.append("\n".format())

        #RESULT
        query.append("RETURN ".format())
        c = 0
        s = lambda: ", " if c > 0 else " "
        for k, v in data.iteritems():
            query.append("{0} r.{1} AS {1}".format(s(), k))
            c += 1
        query.append("{0} type(r) AS type ".format(s()))

        query.append("\n".format())

        #print 'query: ', ''.join(query)
        #print 'params: ', params

        return ''.join(query), params

    def delete(self, args):

        domain = args["domain"]

        query = []
        params = {}

        params["id"] = args["id"]

        query.append("MATCH (s :{domain} :{session_label})-[r {{id: {{id}}}}]->(i :{domain} :{item_label})\n".format(
            domain=domain, session_label=SessionSchema.get_label(), item_label=ItemSchema.get_label()
        ))
        query.append("WITH r, r.id AS id\n".format())
        query.append("DELETE r\n".format())
        query.append("RETURN id, type(r) AS type\n".format())

        #print 'query: ', ''.join(query)
        #print 'params: ', params

        return ''.join(query), params