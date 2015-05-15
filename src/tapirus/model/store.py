__author__ = 'guilherme'


from tapirus.model.constants import *


# TODO: Model events. Parse logs into entities and events. Feed these to data importers

class Session(object):

    def __init__(self, id, tenant, timestamp):

        self.id = id
        self.tenant = tenant
        self.timestamp = timestamp

    def __key(self):

        return self.id, self.tenant

    def __hash__(self):
        return hash(self.__key())

    def __eq__(self, other):

        if not isinstance(other, self.__class__):
            return False

        return self.id == other.id and self.tenant == other.tenant

    def __ne__(self, other):

        return not self.__eq__(other)

    def __str__(self):

        return "Session(id={0}, tenant={1}, timestamp={2})".format(
            self.id, self.tenant, self.timestamp
        )

    @property
    def properties(self):

        return self.__dict__


class User(object):

    def __init__(self, id, tenant, timestamp):

        self.id = id
        self.tenant = tenant
        self.timestamp = timestamp

    def __key(self):

        return self.id, self.tenant

    def __hash__(self):

        return hash(self.__key())

    def __eq__(self, other):

        if not isinstance(other, self.__class__):
            return False

        return self.id == other.id and self.tenant == other.tenant

    def __ne__(self, other):

        return not self.__eq__(other)

    def __str__(self):

        return "User(id={0}, tenant={1}, timestamp={2})".format(
            self.id, self.tenant, self.timestamp
        )

    @property
    def properties(self):

        return self.__dict__


class Agent(object):

    def __init__(self, id, tenant, timestamp):

        self.id = id
        self.tenant = tenant
        self.timestamp = timestamp

    def __key(self):

        return self.id, self.tenant

    def __hash__(self):

        return hash(self.__key())

    def __eq__(self, other):

        if not isinstance(other, self.__class__):
            return False

        return self.id == other.id and self.tenant == other.tenant

    def __ne__(self, other):

        return not self.__eq__(other)

    def __str__(self):

        return "Agent(id={0}, tenant={1}, timestamp={2})".format(
            self.id, self.tenant, self.timestamp
        )

    @property
    def properties(self):

        return self.__dict__


class Item(object):

    def __init__(self, id, tenant, timestamp):

        self.id = id
        self.tenant = tenant
        self.timestamp = timestamp

    def __key(self):

        return self.id, self.tenant

    def __hash__(self):

        return hash(self.__key())

    def __eq__(self, other):

        if not isinstance(other, self.__class__):
            return False

        return self.id == other.id and self.tenant == other.tenant

    def __ne__(self, other):

        return not self.__eq__(other)

    def __str__(self):

        return "Agent(id={0}, tenant={1}, timestamp={2})".format(
            self.id, self.tenant, self.timestamp
        )

    @property
    def properties(self):

        return self.__dict__


class Action(object):

    def __init__(self, name, tenant, user, agent, session, item, timestamp):

        self.name = name
        self.tenant = tenant
        self.user = user
        self.agent = agent
        self.session = session
        self.item = item
        self.timestamp = timestamp

    def __key(self):

        return self.name, self.tenant, self.session, self.item, self.timestamp

    def __hash__(self):

        return hash(self.__key())

    def __eq__(self, other):

        if not isinstance(other, self.__class__):
            return False

        return self.name == other.name and self.tenant == other.tenant and self.session == other.session and \
               self.item == other.item and self.timestamp == other.timestamp

    def __ne__(self, other):

        return not self.__eq__(other)

    def __str__(self):

        return "Action(name={0}, tenant={1}, user={2}, agent={3}, session={4}, item={5}, timestamp={6})".format(
            self.name, self.tenant, self.user, self.agent, self.session, self.item, self.timestamp
        )

    @property
    def properties(self):

        return self.__dict__


class Tenant(object):

    def __init__(self, name, api_key):
        self.name = name
        self.api_key = api_key

    def __key(self):

        return self.name

    def __hash__(self):
        return hash(self.__key())

    def __eq__(self, other):

        if not isinstance(other, self.__class__):
            return False

        return self.name == other.name

    def __ne__(self, other):

        return not self.__eq__(other)


def is_acceptable_data_type(e):
    """

    :param e:
    :return:
    """

    if type(e) in [bool, int, float, complex, str, bytes, list, set]:

        if type(e) is list or set:

            for elem in e:
                if type(elem) is dict:
                    return False
        else:
            return True

    else:
        return False

    return True


def _is_valid_data(value):

    chars = ("[", "]", ".")

    if any([c in value for c in chars]):
        return False

    return True


def is_valid_schema(data):
    """
    :param data:
    :return:
    """

    # todo: log any missing data

    if SCHEMA_KEY_SESSION_ID not in data:
        return False
    if len(data[SCHEMA_KEY_SESSION_ID]) < 1:
        return False
    if not _is_valid_data(data[SCHEMA_KEY_SESSION_ID]):
        return False

    if SCHEMA_KEY_TENANT_ID not in data:
        return False
    if len(data[SCHEMA_KEY_TENANT_ID]) < 1:
        return False
    if not _is_valid_data(data[SCHEMA_KEY_TENANT_ID]):
        return False

    if SCHEMA_KEY_ACTION not in data:
        return False

    if SCHEMA_KEY_NAME not in data[SCHEMA_KEY_ACTION]:
        return False
    if len(data[SCHEMA_KEY_ACTION][SCHEMA_KEY_NAME]) < 1:
        return False
    if not _is_valid_data(data[SCHEMA_KEY_ACTION][SCHEMA_KEY_NAME]):
        return False

    if SCHEMA_KEY_USER in data:

        if SCHEMA_KEY_USER_ID not in data[SCHEMA_KEY_USER]:
            return False
        if len(data[SCHEMA_KEY_USER][SCHEMA_KEY_USER_ID]) < 1:
            return False
        if not _is_valid_data(data[SCHEMA_KEY_USER][SCHEMA_KEY_USER_ID]):
            return False

    if data[SCHEMA_KEY_ACTION][SCHEMA_KEY_NAME].lower() == REL_ACTION_TYPE_SEARCH.lower():

        if SCHEMA_KEY_KEYWORDS not in data[SCHEMA_KEY_ACTION]:
            return False
        if len(data[SCHEMA_KEY_ACTION][SCHEMA_KEY_KEYWORDS]) < 1:
            return False

    elif data[SCHEMA_KEY_ACTION][SCHEMA_KEY_NAME].lower() == REL_ACTION_TYPE_VIEW.lower():

        if SCHEMA_KEY_ITEMS not in data:
            return False

        if type(data[SCHEMA_KEY_ITEMS]) is not list:
            return False

        for item in data[SCHEMA_KEY_ITEMS]:

            if type(item) is not dict:
                return False

            if SCHEMA_KEY_ITEM_ID not in item:
                return False
            if len(item[SCHEMA_KEY_ITEM_ID]) < 1:
                return False
            if not _is_valid_data(item[SCHEMA_KEY_ITEM_ID]):
                return False

            if SCHEMA_KEY_LOCATION in item:

                if type(item[SCHEMA_KEY_LOCATION]) is not dict:
                    return False

                if SCHEMA_KEY_COUNTRY in item[SCHEMA_KEY_LOCATION]:
                    if len(item[SCHEMA_KEY_LOCATION][SCHEMA_KEY_COUNTRY]) < 1:
                        return False

                if SCHEMA_KEY_CITY in item[SCHEMA_KEY_LOCATION]:
                    if len(item[SCHEMA_KEY_LOCATION][SCHEMA_KEY_CITY]) < 1:
                        return False

    elif data[SCHEMA_KEY_ACTION][SCHEMA_KEY_NAME].lower() == REL_ACTION_TYPE_ADD_TO_CART.lower():

        if SCHEMA_KEY_ITEMS not in data:
            return False

        if type(data[SCHEMA_KEY_ITEMS]) is not list:
            return False

        for item in data[SCHEMA_KEY_ITEMS]:

            if type(item) is not dict:
                return False

            if SCHEMA_KEY_ITEM_ID not in item:
                return False
            if len(item[SCHEMA_KEY_ITEM_ID]) < 1:
                return False
            if not _is_valid_data(item[SCHEMA_KEY_ITEM_ID]):
                return False

            if SCHEMA_KEY_QUANTITY not in item:
                return False

            if SCHEMA_KEY_LOCATION in item:

                if type(item[SCHEMA_KEY_LOCATION]) is not dict:
                    return False

                if SCHEMA_KEY_COUNTRY in item[SCHEMA_KEY_LOCATION]:
                    if len(item[SCHEMA_KEY_LOCATION][SCHEMA_KEY_COUNTRY]) < 1:
                        return False

                if SCHEMA_KEY_CITY in item[SCHEMA_KEY_LOCATION]:
                    if len(item[SCHEMA_KEY_LOCATION][SCHEMA_KEY_CITY]) < 1:
                        return False

    elif data[SCHEMA_KEY_ACTION][SCHEMA_KEY_NAME].lower() == REL_ACTION_TYPE_STARTED_CHECKOUT.lower():

        if SCHEMA_KEY_ITEMS not in data:
            return False

        if type(data[SCHEMA_KEY_ITEMS]) is not list:
            return False

        for item in data[SCHEMA_KEY_ITEMS]:

            if type(item) is not dict:
                return False

            if SCHEMA_KEY_ITEM_ID not in item:
                return False
            if len(item[SCHEMA_KEY_ITEM_ID]) < 1:
                return False
            if not _is_valid_data(item[SCHEMA_KEY_ITEM_ID]):
                return False

            if SCHEMA_KEY_LOCATION in item:

                if type(item[SCHEMA_KEY_LOCATION]) is not dict:
                    return False

                if SCHEMA_KEY_COUNTRY in item[SCHEMA_KEY_LOCATION]:
                    if len(item[SCHEMA_KEY_LOCATION][SCHEMA_KEY_COUNTRY]) < 1:
                        return False

                if SCHEMA_KEY_CITY in item[SCHEMA_KEY_LOCATION]:
                    if len(item[SCHEMA_KEY_LOCATION][SCHEMA_KEY_CITY]) < 1:
                        return False

    elif data[SCHEMA_KEY_ACTION][SCHEMA_KEY_NAME].lower() == REL_ACTION_TYPE_BUY.lower():

        if SCHEMA_KEY_ITEMS not in data:
            return False

        if type(data[SCHEMA_KEY_ITEMS]) is not list:
            return False

        for item in data[SCHEMA_KEY_ITEMS]:

            if type(item) is not dict:
                return False

            if SCHEMA_KEY_ITEM_ID not in item:
                return False
            if len(item[SCHEMA_KEY_ITEM_ID]) < 1:
                return False
            if not _is_valid_data(item[SCHEMA_KEY_ITEM_ID]):
                return False

            if SCHEMA_KEY_QUANTITY not in item:
                return False

            if SCHEMA_KEY_SUBTOTAL not in item:
                return False

            if SCHEMA_KEY_LOCATION in item:

                if type(item[SCHEMA_KEY_LOCATION]) is not dict:
                    return False

                if SCHEMA_KEY_COUNTRY in item[SCHEMA_KEY_LOCATION]:
                    if len(item[SCHEMA_KEY_LOCATION][SCHEMA_KEY_COUNTRY]) < 1:
                        return False

                if SCHEMA_KEY_CITY in item[SCHEMA_KEY_LOCATION]:
                    if len(item[SCHEMA_KEY_LOCATION][SCHEMA_KEY_CITY]) < 1:
                        return False

    elif data[SCHEMA_KEY_ACTION][SCHEMA_KEY_NAME].lower() == REL_ACTION_TYPE_CHECK_DELETE_ITEM.lower():

        if SCHEMA_KEY_ITEM_ID not in data:
            return False
        if len(data[SCHEMA_KEY_ITEM_ID]) < 1:
            return False
        if not _is_valid_data(data[SCHEMA_KEY_ITEM_ID]):
            return False

    return True


def parse_entities_from_data(data):

    dt = data["datetime"]
    tenant = data[SCHEMA_KEY_TENANT_ID]

    if is_valid_schema(data) is False:
        return []

    session = None
    agent = None
    user = None
    items = set()
    actions = []

    # Session
    session = Session(id=data[SCHEMA_KEY_SESSION_ID], tenant=tenant, timestamp=dt)

    # User
    if SCHEMA_KEY_USER in data:
        user = User(id=data[SCHEMA_KEY_USER][SCHEMA_KEY_USER_ID], tenant=tenant, timestamp=dt)
    else:
        user = User(id=data[SCHEMA_KEY_SESSION_ID], tenant=tenant, timestamp=dt)

    # Agent
    if SCHEMA_KEY_AGENT_ID in data:
        agent = Agent(id=data[SCHEMA_KEY_AGENT_ID], tenant=tenant, timestamp=dt)

    # Actions
    if data[SCHEMA_KEY_ACTION][SCHEMA_KEY_NAME].upper() == REL_ACTION_TYPE_VIEW:

        # collect items
        for item_data in data[SCHEMA_KEY_ITEMS]:

            item = Item(id=item_data[SCHEMA_KEY_ITEM_ID], tenant=tenant, timestamp=dt)

            for k, v in item_data.items():

                if k != SCHEMA_KEY_ITEM_ID and is_acceptable_data_type(v):
                    item.__dict__[k] = v

            # (item_data)-[r]-(location)
            #
            # if SCHEMA_KEY_LOCATION in item_data:
            #
            #     if SCHEMA_KEY_COUNTRY in item_data[SCHEMA_KEY_LOCATION]:
            #         template = "MERGE (l:`{LOCATION_LABEL}` :`{LOCATION_COUNTRY}` :`{STORE_ID}` {{name: {{name}} }})" \
            #                    "\nMERGE (i :`{ITEM_LABEL}` :`{STORE_ID}` {{id: {{item_id}} }})" \
            #                    "\nMERGE (i)-[:`{REL}`]->(l)"
            #
            #         statements = [template.format(
            #             LOCATION_LABEL=LABEL_LOCATION,
            #             LOCATION_COUNTRY=LABEL_LOCATION_COUNTRY,
            #             ITEM_LABEL=LABEL_ITEM,
            #             STORE_ID=data[SCHEMA_KEY_TENANT_ID],
            #             REL=REL_ITEM_LOCATION
            #         )]
            #
            #         params = [neo4j.Parameter("name", item_data[SCHEMA_KEY_LOCATION][SCHEMA_KEY_COUNTRY]),
            #                   neo4j.Parameter("item_id", item_data[SCHEMA_KEY_ITEM_ID])]
            #
            #         queries.append(neo4j.Query(''.join(statements), params))
            #
            #     if SCHEMA_KEY_CITY in item_data[SCHEMA_KEY_LOCATION]:
            #         template = "MERGE (l:`{LOCATION_LABEL}` :`{LOCATION_CITY}` :`{STORE_ID}` {{name: {{name}} }})" \
            #                    "\nMERGE (i :`{ITEM_LABEL}` :`{STORE_ID}` {{id: {{item_id}} }})" \
            #                    "\nMERGE (i)-[:`{REL}`]->(l)"
            #
            #         statements = [template.format(
            #             LOCATION_LABEL=LABEL_LOCATION,
            #             LOCATION_CITY=LABEL_LOCATION_CITY,
            #             ITEM_LABEL=LABEL_ITEM,
            #             STORE_ID=data[SCHEMA_KEY_TENANT_ID],
            #             REL=REL_ITEM_LOCATION
            #         )]
            #
            #         params = [neo4j.Parameter("name", item_data[SCHEMA_KEY_LOCATION][SCHEMA_KEY_CITY]),
            #                   neo4j.Parameter("item_id", item_data[SCHEMA_KEY_ITEM_ID])]
            #
            #         queries.append(neo4j.Query(''.join(statements), params))
            #
            # # (item_data)-[r]-(session)
            #
            # template = "MERGE (s :`{SESSION_LABEL}` :`{STORE_ID}` {{id: {{session_id}} }})" \
            #            "\nMERGE (i :`{ITEM_LABEL}` :`{STORE_ID}` {{id: {{item_id}} }})" \
            #            "\nMERGE (s)-[r :`{REL}`]->(i)"
            #
            # statements = [template.format(
            #     SESSION_LABEL=LABEL_SESSION,
            #     ITEM_LABEL=LABEL_ITEM,
            #     STORE_ID=data[SCHEMA_KEY_TENANT_ID],
            #     REL=REL_ACTION_TYPE_VIEW
            # )]
            #
            # params = [neo4j.Parameter("datetime", dt),
            #           neo4j.Parameter("item_id", item_data[SCHEMA_KEY_ITEM_ID]),
            #           neo4j.Parameter("session_id", data[SCHEMA_KEY_SESSION_ID])]
            #
            # statements.append("\nSET r.{0} = {{ {0} }}".format(
            #     "datetime"
            # ))
            #
            # queries.append(neo4j.Query(''.join(statements), params))
    #
    # elif data[SCHEMA_KEY_ACTION][SCHEMA_KEY_NAME].upper() == REL_ACTION_TYPE_ADD_TO_CART:
    #
    #     # collect items
    #     for item_data in data[SCHEMA_KEY_ITEMS]:
    #         template = "MERGE (n :`{ITEM_LABEL}` :`{STORE_ID}` {{id: {{id}} }})"
    #
    #         statements = [template.format(
    #             ITEM_LABEL=LABEL_ITEM,
    #             STORE_ID=data[SCHEMA_KEY_TENANT_ID]
    #         )]
    #
    #         params = [neo4j.Parameter("id", item_data[SCHEMA_KEY_ITEM_ID])]
    #
    #         queries.append(neo4j.Query(''.join(statements), params))
    #
    #         # (item_data)-[r]-(session)
    #
    #         template = "MERGE (s :`{SESSION_LABEL}` :`{STORE_ID}` {{id: {{session_id}} }})" \
    #                    "\nMERGE (i :`{ITEM_LABEL}` :`{STORE_ID}` {{id: {{item_id}} }})" \
    #                    "\nMERGE (s)-[r :`{REL}`]->(i)"
    #         # "(i :`{ITEM_LABEL}` :`{STORE_ID}` {{id: {{item_id}} }})"
    #
    #         statements = [template.format(
    #             SESSION_LABEL=LABEL_SESSION,
    #             ITEM_LABEL=LABEL_ITEM,
    #             STORE_ID=data[SCHEMA_KEY_TENANT_ID],
    #             REL=REL_ACTION_TYPE_ADD_TO_CART
    #         )]
    #
    #         params = [neo4j.Parameter("datetime", dt),
    #                   neo4j.Parameter("qty", item_data[SCHEMA_KEY_QUANTITY]),
    #                   neo4j.Parameter("item_id", item_data[SCHEMA_KEY_ITEM_ID]),
    #                   neo4j.Parameter("session_id", data[SCHEMA_KEY_SESSION_ID])]
    #
    #         statements.append("\nSET r.{0} = {{ {0} }}".format(
    #             "datetime"
    #         ))
    #
    #         statements.append("\nSET r.{0} = {{ {0} }}".format(
    #             "qty"
    #         ))
    #
    #         queries.append(neo4j.Query(''.join(statements), params))
    #
    # elif data[SCHEMA_KEY_ACTION][SCHEMA_KEY_NAME].upper() == REL_ACTION_TYPE_BUY:
    #
    #     # collect items
    #     for item_data in data[SCHEMA_KEY_ITEMS]:
    #         template = "MERGE (n :`{ITEM_LABEL}` :`{STORE_ID}` {{id: {{id}} }})"
    #
    #         statements = [template.format(
    #             ITEM_LABEL=LABEL_ITEM,
    #             STORE_ID=data[SCHEMA_KEY_TENANT_ID]
    #         )]
    #
    #         params = [neo4j.Parameter("id", item_data[SCHEMA_KEY_ITEM_ID])]
    #
    #         queries.append(neo4j.Query(''.join(statements), params))
    #
    #         # (item_data)-[r]-(session)
    #
    #         template = "MERGE (s :`{SESSION_LABEL}` :`{STORE_ID}` {{id: {{session_id}} }})" \
    #                    "\nMERGE (i :`{ITEM_LABEL}` :`{STORE_ID}` {{id: {{item_id}} }})" \
    #                    "\nMERGE (s)-[r :`{REL}`]->(i)"
    #
    #         statements = [template.format(
    #             SESSION_LABEL=LABEL_SESSION,
    #             ITEM_LABEL=LABEL_ITEM,
    #             STORE_ID=data[SCHEMA_KEY_TENANT_ID],
    #             REL=REL_ACTION_TYPE_BUY
    #         )]
    #
    #         params = [neo4j.Parameter("datetime", dt),
    #                   neo4j.Parameter("qty", item_data[SCHEMA_KEY_QUANTITY]),
    #                   neo4j.Parameter("sub_total", item_data[SCHEMA_KEY_SUBTOTAL]),
    #                   neo4j.Parameter("item_id", item_data[SCHEMA_KEY_ITEM_ID]),
    #                   neo4j.Parameter("session_id", data[SCHEMA_KEY_SESSION_ID])]
    #
    #         statements.append("\nSET r.{0} = {{ {0} }}".format(
    #             "datetime"
    #         ))
    #
    #         statements.append("\nSET r.{0} = {{ {0} }}".format(
    #             "qty"
    #         ))
    #
    #         statements.append("\nSET r.{0} = {{ {0} }}".format(
    #             "sub_total"
    #         ))
    #
    #         queries.append(neo4j.Query(''.join(statements), params))
    #
    # elif data[SCHEMA_KEY_ACTION][SCHEMA_KEY_NAME].upper() == REL_ACTION_TYPE_STARTED_CHECKOUT:
    #
    #     # collect items
    #     for item_data in data[SCHEMA_KEY_ITEMS]:
    #         template = "MERGE (n :`{ITEM_LABEL}` :`{STORE_ID}` {{id: {{id}} }})"
    #
    #         statements = [template.format(
    #             ITEM_LABEL=LABEL_ITEM,
    #             STORE_ID=data[SCHEMA_KEY_TENANT_ID]
    #         )]
    #
    #         params = [neo4j.Parameter("id", item_data[SCHEMA_KEY_ITEM_ID])]
    #
    #         queries.append(neo4j.Query(''.join(statements), params))
    #
    #         # (item_data)-[r]-(session)
    #
    #         template = "MERGE (s :`{SESSION_LABEL}` :`{STORE_ID}` {{id: {{session_id}} }})" \
    #                    "\nMERGE (i :`{ITEM_LABEL}` :`{STORE_ID}` {{id: {{item_id}} }})" \
    #                    "\nMERGE (s)-[r :`{REL}`]->(i)"
    #
    #         statements = [template.format(
    #             SESSION_LABEL=LABEL_SESSION,
    #             ITEM_LABEL=LABEL_ITEM,
    #             STORE_ID=data[SCHEMA_KEY_TENANT_ID],
    #             REL=REL_ACTION_TYPE_STARTED_CHECKOUT
    #         )]
    #
    #         params = [neo4j.Parameter("datetime", dt),
    #                   neo4j.Parameter("item_id", item_data[SCHEMA_KEY_ITEM_ID]),
    #                   neo4j.Parameter("session_id", data[SCHEMA_KEY_SESSION_ID])]
    #
    #         statements.append("\nSET r.{0} = {{ {0} }}".format(
    #             "datetime"
    #         ))
    #
    #         queries.append(neo4j.Query(''.join(statements), params))
    #
    # elif data[SCHEMA_KEY_ACTION][SCHEMA_KEY_NAME].upper() == REL_ACTION_TYPE_SEARCH:
    #
    #     template = "MERGE (s :`{SESSION_LABEL}` :`{STORE_ID}` {{ id: {{session_id}} }})" \
    #                "\nMERGE (n :`{SEARCH_LABEL}` :`{STORE_ID}` {{ keywords: {{keywords}} }})" \
    #                "\nMERGE (s)-[r :`{REL}`]->(n)"
    #
    #     #collect items
    #     statements = [template.format(
    #         SEARCH_LABEL=LABEL_SEARCH,
    #         SESSION_LABEL=LABEL_SESSION,
    #         STORE_ID=data[SCHEMA_KEY_TENANT_ID],
    #         REL=REL_ACTION_TYPE_SEARCH
    #     )]
    #
    #     params = [neo4j.Parameter("keywords", data[SCHEMA_KEY_ACTION][SCHEMA_KEY_KEYWORDS]),
    #               neo4j.Parameter("session_id", data[SCHEMA_KEY_SESSION_ID]),
    #               neo4j.Parameter("datetime", dt)]
    #
    #     queries.append(neo4j.Query(''.join(statements), params))
    #
    #     for k, v in data[SCHEMA_KEY_ACTION].items():
    #
    #         if k != SCHEMA_KEY_KEYWORDS and is_acceptable_data_type(v):
    #             params.append(neo4j.Parameter(k, v))
    #             statements.append("\nSET n.{0} = {{ {0} }}".format(
    #                 k
    #             ))
    #
    #     statements.append("\nSET r.{0} = {{ {0} }}".format(
    #         "datetime"
    #     ))
    #
    #     queries.append(neo4j.Query(''.join(statements), params))
    #
    # elif data[SCHEMA_KEY_ACTION][SCHEMA_KEY_NAME].upper() == REL_ACTION_TYPE_CHECK_DELETE_ITEM:
    #
    #     template = "MATCH (n :`{ITEM_LABEL}` :`{STORE_ID}` {{id: {{id}} }})" \
    #                "\nOPTIONAL MATCH (n)-[r]-(x)" \
    #                "\nDELETE r, n"
    #
    #     statements = [template.format(
    #         ITEM_LABEL=LABEL_ITEM,
    #         STORE_ID=data[SCHEMA_KEY_TENANT_ID]
    #     )]
    #
    #     params = [neo4j.Parameter("id", data[SCHEMA_KEY_ITEM_ID])]
    #
    #     queries.append(neo4j.Query(''.join(statements), params))
    #
    # return queries

    return session, agent, user, items, actions


# if __name__ == "__main__":
#
#     import datetime
#     tmp = datetime.datetime.now()
#     user = User(1, "AB", tmp)
#     print(User(1, "AB", tmp) == User(1, "AB", tmp))
#     print(User(1, "AB", tmp) == User(2, "AB", tmp))
#
#     user.house = "Me"
#     user.__dict__["place"] = "My Place"
#
#     print(user)
