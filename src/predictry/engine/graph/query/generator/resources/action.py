__author__ = 'guilherme'

from predictry.engine.graph.query.generator.resources.base import ResourceQueryGeneratorBase
from predictry.engine.models.resources.item import ItemSchema
from predictry.engine.models.resources.session import SessionSchema
from predictry.engine.models.resources.browser import BrowserSchema
from predictry.engine.models.resources.user import UserSchema
from predictry.utils.neo4j import node


class ActionQueryGenerator(ResourceQueryGeneratorBase):
    def __init__(self):
        pass

    def create(self, args, data):

        domain = args["domain"]

        query = []
        params = {}

        str_properties = []

        s = lambda: ", " if c > 0 else " "

        params["item_id"] = data["item_id"]
        params["session_id"] = data["session_id"]
        params["browser_id"] = data["browser_id"]

        #check session

        create_flags = dict(session=False, browser=False)
        connect_flags = dict(user=False)

        exists, err = node.exists(labels=[args["domain"], SessionSchema.get_label()],
                                  properties={"id": data["session_id"]})
        if not exists:
            create_flags["session"] = True

        #check browser
        exists, err = node.exists(labels=[args["domain"], BrowserSchema.get_label()],
                                  properties={"id": data["browser_id"]})
        if not exists:
            create_flags["browser"] = True

        #check if action is attached to a user
        if "user_id" in data:
            params["user_id"] = data["user_id"]
            connect_flags["user"] = True

        c = 0
        for k, v in data.iteritems():
            if k not in ["item_id", "browser_id", "session_id", "user_id", "type"]:
                str_properties.append("%s %s : {%s} " % (s(), k, k))
                if type(data[k]) is str:
                    data[k] = data[k].strip()
                params[k] = data[k]
                c += 1

        #item
        query.append("MATCH (i :%s:%s {id: {item_id}})\n"
                     % (domain, ItemSchema.get_label()))
        query.append("WITH i\n")
        #session
        if create_flags["session"]:

            if "timestamp" in data:
                query.append("CREATE (s :%s:%s {id: {session_id}, timestamp: {timestamp}})\n"
                             % (domain, SessionSchema.get_label()))
            else:
                query.append("CREATE (s :%s:%s {id: {session_id}, timestamp: timestamp() })\n"
                             % (domain, SessionSchema.get_label()))
        else:
            query.append("MATCH (s :%s:%s {id: {session_id}})\n"
                         % (domain, SessionSchema.get_label()))
        query.append("WITH i, s\n")

        #browser
        if create_flags["browser"]:
            query.append("CREATE (b :%s:%s {id: {browser_id}})\n"
                         % (domain, BrowserSchema.get_label()))
            query.append("WITH i, s, b\n")
            query.append("CREATE (s)-[r_on :on]->(b)\n")

        else:
            query.append("MATCH (b :%s:%s {id: {browser_id}})\n"
                         % (domain, BrowserSchema.get_label()))
        query.append("WITH i, s, b\n")

        if connect_flags["user"]:
            query.append("MATCH (u :%s:%s {id:{user_id}})\n"
                         % (domain, UserSchema.get_label()))
            query.append("WITH i, s, b, u\n")

        #connection
        #query.append("CREATE")
        #query.append(" (s)-[r_on :on]->(b), ")
        query.append("CREATE (s)-[r_action :%s {%s}]->(i)" %
                     (data["type"], ''.join(str_properties)))
        if connect_flags["user"]:
            query.append(", (s)-[r_by :by]->(u)")

        query.append("\n")

        query.append("RETURN ")

        c = 0
        for k, v in data.iteritems():
            if k not in ["item_id", "browser_id", "session_id", "user_id", "type"]:
                query.append("%s r_action.%s AS %s " % (s(), k, k))
                c += 1

        query.append("%s type(r_action) AS type " % (s()))

        query.append("\n")

        print 'query: ', ''.join(query)
        print 'params: ', params

        return ''.join(query), params

    def read(self, args):

        domain = args["domain"]

        query = []
        params = {}

        if "id" in args:
            query.append("MATCH (s :%s:%s )-[r {id: {id}}]->(i :%s:%s )\n" %
                         (domain, SessionSchema.get_label(), domain, ItemSchema.get_label()))
            params["id"] = args["id"]

        else:
            if "type" in args:
                query.append("MATCH (s :%s:%s)-[r :%s]->(i :%s:%s)\n" %
                             (domain, SessionSchema.get_label(), args["type"], domain, ItemSchema.get_label()))
            else:
                query.append("MATCH (s :%s:%s)-[r]->(i :%s:%s)\n" %
                             (domain, SessionSchema.get_label(), domain, ItemSchema.get_label()))

        c = 0
        s = lambda: ", " if c > 0 else " "

        #RETURN
        query.append("RETURN r.id AS id")

        if "fields" in args:
            fields = [x for x in args["fields"].split(',') if x not in ["id", "type"]]
            for field in fields:
                query.append(", r.%s AS %s " % (field, field))

        query.append(", type(r) AS type ")
        query.append("\n")

        #LIMIT/OFFSET
        if "id" not in args:
            #not a 1 item request
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

    def update(self, args, data):

        domain = args["domain"]

        query = []
        params = {}

        query.append("MATCH (s :%s:%s)-[r {id: {id}}]->(i :%s:%s)\n" %
                     (domain, SessionSchema.get_label(), domain, ItemSchema.get_label()))
        params["id"] = args["id"]

        #properties = ActionSchema.get_properties()

        c = 0
        s = lambda: "SET" if c == 0 else ","
        for k, v in data.iteritems():
            query.append("%s r.%s = {%s} " % (s(), k, k))
            params[k] = data[k]
            c += 1

        query.append("\n")

        #RESULT
        query.append("RETURN ")
        c = 0
        s = lambda: ", " if c > 0 else " "
        for k, v in data.iteritems():
            query.append("%s r.%s AS %s" % (s(), k, k))
            c += 1
        query.append("%s type(r) AS type " % (s()))

        query.append("\n")

        #print 'query: ', ''.join(query)
        #print 'params: ', params

        return ''.join(query), params

    def delete(self, args):

        domain = args["domain"]

        query = []
        params = {}

        query.append("MATCH (s :%s:%s)-[r {id: {id}}]->(i :%s:%s)\n" %
                     (domain, SessionSchema.get_label(), domain, ItemSchema.get_label()))
        params["id"] = args["id"]
        query.append("WITH r, r.id AS id\n")
        query.append("DELETE r\n")
        query.append("RETURN id, type(r) AS type\n")

        #print 'query: ', ''.join(query)
        #print 'params: ', params

        return ''.join(query), params