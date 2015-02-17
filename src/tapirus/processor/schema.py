__author__ = 'guilherme'

import dateutil.parser
import dateutil.tz

import jsonschema

from tapirus.core.db import neo4j
from tapirus.model import store
from tapirus.utils.logger import Logger

#todo: {'action': {'name': 'check_delete_item'}, 'widget_instance_id': 1789} -> DELETE ITEM

SCHEMA_BASE = "Base"

SCHEMA_KEY_SESSION_ID = "session_id"
SCHEMA_KEY_TENANT_ID = "tenant_id"
SCHEMA_KEY_ITEM_ID = "item_id"
SCHEMA_KEY_USER_ID = "user_id"
SCHEMA_KEY_AGENT_ID = "browser_id"
SCHEMA_KEY_USER = "user"
SCHEMA_KEY_AGENT = "browser"
SCHEMA_KEY_ACTION = "action"
SCHEMA_KEY_NAME = "name"
SCHEMA_KEY_QUANTITY = "qty"
SCHEMA_KEY_TOTAL = "total"
SCHEMA_KEY_SUBTOTAL = "sub_total"
SCHEMA_KEY_ITEMS = "items"
SCHEMA_KEY_KEYWORDS = "keywords"
SCHEMA_KEY_LOCATION = "locations"
SCHEMA_KEY_CITY = "city"
SCHEMA_KEY_COUNTRY = "country"


SCHEMAS = {

    SCHEMA_BASE: {
        "$schema": "http://json-schema.org/draft-04/schema#",
        "title": "Item",
        "description": "An item from a store/marketplace",
        "type": "object",
        "properties": {
            "session_id": {"type": "string", "minLength": 1},
            "tenant_id": {"type": "string", "minLength": 1},
            "action": {
                "type": "object",
                "properties": {
                    "name": {"type": "string", "minLength": 1},
                },
                "required": ["name"]
            }
        },
        "required": ["session_id", "tenant_id", "action"]
    },
    store.REL_ACTION_TYPE_SEARCH: {
        "$schema": "http://json-schema.org/draft-04/schema#",
        "title": "Item",
        "description": "An item from a store/marketplace",
        "type": "object",
        "properties": {
            "session_id": {"type": "string", "minLength": 1},
            "tenant_id": {"type": "string", "minLength": 1},
            "action": {
                "type": "object",
                "properties": {
                    "name": {
                        "enum": ["search"]
                    },
                    "keywords": {"type": "string", "minLength": 1}
                },
                "required": ["name", "keywords"]
            },
            "user": {
                "type": "object",
                "properties": {
                    "user_id": {"type": ["integer", "number", "string"], "minLength": 1},
                },
                "required": ["user_id"]
            }
        },
        "required": ["session_id", "tenant_id", "action"]
    },
    store.REL_ACTION_TYPE_VIEW: {
        "$schema": "http://json-schema.org/draft-04/schema#",
        "title": "Item",
        "description": "An item from a store/marketplace",
        "type": "object",
        "properties": {
            "session_id": {"type": "string", "minLength": 1},
            "tenant_id": {"type": "string", "minLength": 1},
            "action": {
                "type": "object",
                "properties": {
                    "name": {
                        "enum": ["view"]
                    }
                },
                "required": ["name"]
            },
            "user": {
                "type": "object",
                "properties": {
                    "user_id": {"type": ["integer", "number", "string"], "minLength": 1},
                },
                "required": ["user_id"]
            },
            "items": {
                "type": "array",
                "items": {
                    "type": ["boolean", "integer", "null", "number", "object", "string", "array"],
                    "properties": {
                        "item_id": {"type": ["integer", "number", "string"], "minLength": 1},
                        "locations": {
                            "type": "object",
                            "properties": {
                                "country": {"type": "string", "minLength": 1},
                                "city": {"type": "string", "minLength": 1}
                            }
                        }
                    },
                    "required": ["item_id"]
                }
            }
        },
        "required": ["session_id", "tenant_id", "action", "items"]
    },
    store.REL_ACTION_TYPE_ADD_TO_CART: {
        "$schema": "http://json-schema.org/draft-04/schema#",
        "title": "Item",
        "description": "An item from a store/marketplace",
        "type": "object",
        "properties": {
            "session_id": {"type": "string", "minLength": 1},
            "tenant_id": {"type": "string", "minLength": 1},
            "action": {
                "type": "object",
                "properties": {
                    "name": {
                        "enum": ["add_to_cart"]
                    }
                },
                "required": ["name"]
            },
            "user": {
                "type": "object",
                "properties": {
                    "user_id": {"type": ["integer", "number", "string"], "minLength": 1},
                },
                "required": ["user_id"]
            },
            "items": {
                "type": "array",
                "items": {
                    "type": ["boolean", "integer", "null", "number", "object", "string", "array"],
                    "properties": {
                        "item_id": {"type": ["integer", "number", "string"], "minLength": 1},
                        "qty": {
                            "type": ["integer", "number", "string"]
                        }
                    },
                    "required": ["item_id", "qty"]
                }
            }
        },
        "required": ["session_id", "tenant_id", "action", "items"]
    },
    store.REL_ACTION_TYPE_STARTED_CHECKOUT: {
        "$schema": "http://json-schema.org/draft-04/schema#",
        "title": "Item",
        "description": "An item from a store/marketplace",
        "type": "object",
        "properties": {
            "session_id": {"type": "string", "minLength": 1},
            "tenant_id": {"type": "string", "minLength": 1},
            "action": {
                "type": "object",
                "properties": {
                    "name": {
                        "enum": ["started_checkout"]
                    }
                },
                "required": ["name"]
            },
            "user": {
                "type": "object",
                "properties": {
                    "user_id": {"type": ["integer", "number", "string"], "minLength": 1},
                },
                "required": ["user_id"]
            },
            "items": {
                "type": "array",
                "items": {
                    "type": ["boolean", "integer", "null", "number", "object", "string", "array"],
                    "properties": {
                        "item_id": {"type": ["integer", "number", "string"], "minLength": 1},
                        "locations": {
                            "type": "object",
                            "properties": {
                                "country": {"type": "string", "minLength": 1},
                                "city": {"type": "string", "minLength": 1}
                            }
                        }
                    },
                    "required": ["item_id"]
                }
            }
        },
        "required": ["session_id", "tenant_id", "action", "items"]
    },
    store.REL_ACTION_TYPE_BUY: {
        "$schema": "http://json-schema.org/draft-04/schema#",
        "title": "Item",
        "description": "An item from a store/marketplace",
        "type": "object",
        "properties": {
            "session_id": {"type": "string", "minLength": 1},
            "tenant_id": {"type": "string", "minLength": 1},
            "action": {
                "type": "object",
                "properties": {
                    "name": {
                        "enum": ["buy"]
                    }
                },
                "required": ["name"]
            },
            "user": {
                "type": "object",
                "properties": {
                    "user_id": {"type": ["integer", "number", "string"], "minLength": 1},
                },
                "required": ["user_id"]
            },
            "items": {
                "type": "array",
                "items": {
                    "type": ["boolean", "integer", "null", "number", "object", "string", "array"],
                    "properties": {
                        "item_id": {"type": ["integer", "number", "string"], "minLength": 1},
                        "qty": {
                            "type": ["integer", "number", "string"]
                        },
                        "sub_total": {
                            "type": ["integer", "number", "string"]
                        }
                    },
                    "required": ["item_id", "qty", "sub_total"]
                }
            }
        },
        "required": ["session_id", "tenant_id", "action", "items"]
    },
    store.REL_ACTION_TYPE_CHECK_DELETE_ITEM: {
        "$schema": "http://json-schema.org/draft-04/schema#",
        "title": "Item",
        "description": "An item from a store/marketplace",
        "type": "object",
        "properties": {
            "session_id": {"type": "string", "minLength": 1},
            "tenant_id": {"type": "string", "minLength": 1},
            "action": {
                "type": "object",
                "properties": {
                    "name": {
                        "enum": ["check_delete_item"]
                    }
                },
                "required": ["name"]
            },
            "item_id": {"type": ["integer", "number", "string"], "minLength": 1}
        },
        "required": ["session_id", "tenant_id", "action", "item_id"]
    }
}


def __validate_data_schema(data, schema_name):

        try:
            jsonschema.validate(data, SCHEMAS[schema_name])
        except jsonschema.ValidationError as err:
            raise err


def is_data_valid(data):
    """

    :param data:
    :return:
    """

    try:
        jsonschema.validate(data, SCHEMAS[SCHEMA_BASE])

        schema_name = "{0}".format(data[SCHEMA_KEY_ACTION][SCHEMA_KEY_NAME]).upper()

        __validate_data_schema(data, schema_name)

    except jsonschema.ValidationError as err:

        Logger.error(err)
        return False

    except KeyError as err:

        Logger.error("Unidentified payload action:\n\t{0}".format(err))
        return False

    else:

        return True


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


#todo: parse data
def generate_queries(date, time, ip, path, data):
    """

    :param date:
    :param time:
    :param ip:
    :param path:
    :param data:
    :return:
    """

    #items, session, user, agent
    #session -> item
    #session -> user
    #session -> agent

    dt = dateutil.parser.parse(''.join([date, "T", time, "Z"]))

    if is_data_valid(data) is False:
        return []

    queries = []

    #session
    query = ["MERGE (n :`{SESSION_LABEL}` :`{STORE_ID}` {{id: {{id}} }})".format(
        SESSION_LABEL=store.LABEL_SESSION,
        STORE_ID=data[SCHEMA_KEY_TENANT_ID]
    )]

    params = [neo4j.Parameter("id", data[SCHEMA_KEY_SESSION_ID])]

    queries.append(neo4j.Query(''.join(query), params))

    #user
    if SCHEMA_KEY_USER in data:
        #todo: if user is not given, use anonymous user id?

        query = ["MERGE (n :`{USER_LABEL}` :`{STORE_ID}` {{id: {{id}} }})".format(
            USER_LABEL=store.LABEL_USER,
            STORE_ID=data[SCHEMA_KEY_TENANT_ID]
        )]

        params = [neo4j.Parameter("id", data[SCHEMA_KEY_USER][SCHEMA_KEY_USER_ID])]

        for k, v in data[SCHEMA_KEY_USER].items():

            if k != SCHEMA_KEY_USER_ID and is_acceptable_data_type(v):

                params.append(neo4j.Parameter(k, v))
                query.append("\nSET n.{0} = {{ {0} }}".format(
                    k
                ))

        queries.append(neo4j.Query(''.join(query), params))

        #(session)-[r]-(user)

        q = "MERGE (s :`{SESSION_LABEL}` :`{STORE_ID}` {{id: {{session_id}} }})" \
            "\nMERGE (i :`{USER_LABEL}` :`{STORE_ID}` {{id: {{user_id}} }})" \
            "\nMERGE (s)-[r :`{REL}`]->(i)"

        query = [q.format(
            SESSION_LABEL=store.LABEL_SESSION,
            USER_LABEL=store.LABEL_USER,
            STORE_ID=data[SCHEMA_KEY_TENANT_ID],
            REL=store.REL_SESSION_TO_USER
        )]

        params = [neo4j.Parameter("datetime", dt),
                  neo4j.Parameter("user_id", data[SCHEMA_KEY_USER][SCHEMA_KEY_USER_ID]),
                  neo4j.Parameter("session_id", data[SCHEMA_KEY_SESSION_ID])]

        queries.append(neo4j.Query(''.join(query), params))

    #agent
    if SCHEMA_KEY_AGENT_ID in data:

        query = ["MERGE (n :`{AGENT_LABEL}` :`{STORE_ID}` {{id: {{id}} }})".format(
            AGENT_LABEL=store.LABEL_AGENT,
            STORE_ID=data[SCHEMA_KEY_TENANT_ID]
        )]

        params = [neo4j.Parameter("id", data[SCHEMA_KEY_AGENT_ID])]

        queries.append(neo4j.Query(''.join(query), params))

        #(session)-[r]-(agent)
        q = "MERGE (s :`{SESSION_LABEL}` :`{STORE_ID}` {{id: {{session_id}} }})" \
            "\nMERGE (i :`{AGENT_LABEL}` :`{STORE_ID}` {{id: {{agent_id}} }})" \
            "\nMERGE (s)-[r :`{REL}`]->(i)"
            #"(i :`{AGENT_LABEL}` :`{STORE_ID}` {{id: {{agent_id}} }})"

        query = [q.format(
            SESSION_LABEL=store.LABEL_SESSION,
            AGENT_LABEL=store.LABEL_AGENT,
            STORE_ID=data[SCHEMA_KEY_TENANT_ID],
            REL=store.REL_SESSION_TO_AGENT
        )]

        params = [neo4j.Parameter("datetime", dt),
                  neo4j.Parameter("agent_id", data[SCHEMA_KEY_AGENT_ID]),
                  neo4j.Parameter("session_id", data[SCHEMA_KEY_SESSION_ID])]

        queries.append(neo4j.Query(''.join(query), params))

    #actions
    if data[SCHEMA_KEY_ACTION][SCHEMA_KEY_NAME].upper() == store.REL_ACTION_TYPE_VIEW:

        #collect items
        for item in data[SCHEMA_KEY_ITEMS]:

            q = "MERGE (n :`{ITEM_LABEL}` :`{STORE_ID}` {{id: {{id}} }})"

            query = [q.format(
                ITEM_LABEL=store.LABEL_ITEM,
                STORE_ID=data[SCHEMA_KEY_TENANT_ID]
            )]

            params = [neo4j.Parameter("id", item[SCHEMA_KEY_ITEM_ID])]

            for k, v in item.items():

                if k != SCHEMA_KEY_ITEM_ID and is_acceptable_data_type(v):

                    params.append(neo4j.Parameter(k, v))
                    query.append("\nSET n.{0} = {{ {0} }}".format(
                        k
                    ))

            queries.append(neo4j.Query(''.join(query), params))

            #(item)-[r]-(location)

            if SCHEMA_KEY_LOCATION in item:

                if SCHEMA_KEY_COUNTRY in item[SCHEMA_KEY_LOCATION]:

                    q = "MERGE (l:`{LOCATION_LABEL}` :`{LOCATION_COUNTRY}` :`{STORE_ID}` {{name: {{name}} }})" \
                        "\nMERGE (i :`{ITEM_LABEL}` :`{STORE_ID}` {{id: {{item_id}} }})" \
                        "\nMERGE (i)-[:`{REL}`]->(l)"

                    query = [q.format(
                        LOCATION_LABEL=store.LABEL_LOCATION,
                        LOCATION_COUNTRY=store.LABEL_LOCATION_COUNTRY,
                        ITEM_LABEL=store.LABEL_ITEM,
                        STORE_ID=data[SCHEMA_KEY_TENANT_ID],
                        REL=store.REL_ITEM_LOCATION
                    )]

                    params = [neo4j.Parameter("name", item[SCHEMA_KEY_LOCATION][SCHEMA_KEY_COUNTRY]),
                              neo4j.Parameter("item_id", item[SCHEMA_KEY_ITEM_ID])]

                    queries.append(neo4j.Query(''.join(query), params))

                if SCHEMA_KEY_CITY in item[SCHEMA_KEY_LOCATION]:

                    q = "MERGE (l:`{LOCATION_LABEL}` :`{LOCATION_CITY}` :`{STORE_ID}` {{name: {{name}} }})" \
                        "\nMERGE (i :`{ITEM_LABEL}` :`{STORE_ID}` {{id: {{item_id}} }})" \
                        "\nMERGE (i)-[:`{REL}`]->(l)"

                    query = [q.format(
                        LOCATION_LABEL=store.LABEL_LOCATION,
                        LOCATION_CITY=store.LABEL_LOCATION_CITY,
                        ITEM_LABEL=store.LABEL_ITEM,
                        STORE_ID=data[SCHEMA_KEY_TENANT_ID],
                        REL=store.REL_ITEM_LOCATION
                    )]

                    params = [neo4j.Parameter("name", item[SCHEMA_KEY_LOCATION][SCHEMA_KEY_CITY]),
                              neo4j.Parameter("item_id", item[SCHEMA_KEY_ITEM_ID])]

                    queries.append(neo4j.Query(''.join(query), params))

            #(item)-[r]-(session)

            q = "MERGE (s :`{SESSION_LABEL}` :`{STORE_ID}` {{id: {{session_id}} }})" \
                "\nMERGE (i :`{ITEM_LABEL}` :`{STORE_ID}` {{id: {{item_id}} }})" \
                "\nMERGE (s)-[r :`{REL}`]->(i)"

            query = [q.format(
                SESSION_LABEL=store.LABEL_SESSION,
                ITEM_LABEL=store.LABEL_ITEM,
                STORE_ID=data[SCHEMA_KEY_TENANT_ID],
                REL=store.REL_ACTION_TYPE_VIEW
            )]

            params = [neo4j.Parameter("datetime", dt),
                      neo4j.Parameter("item_id", item[SCHEMA_KEY_ITEM_ID]),
                      neo4j.Parameter("session_id", data[SCHEMA_KEY_SESSION_ID])]

            query.append("\nSET r.{0} = {{ {0} }}".format(
                "datetime"
            ))

            queries.append(neo4j.Query(''.join(query), params))

    elif data[SCHEMA_KEY_ACTION][SCHEMA_KEY_NAME].upper() == store.REL_ACTION_TYPE_ADD_TO_CART:

        #collect items
        for item in data[SCHEMA_KEY_ITEMS]:

            q = "MERGE (n :`{ITEM_LABEL}` :`{STORE_ID}` {{id: {{id}} }})"

            query = [q.format(
                ITEM_LABEL=store.LABEL_ITEM,
                STORE_ID=data[SCHEMA_KEY_TENANT_ID]
            )]

            params = [neo4j.Parameter("id", item[SCHEMA_KEY_ITEM_ID])]

            queries.append(neo4j.Query(''.join(query), params))

            #(item)-[r]-(session)

            q = "MERGE (s :`{SESSION_LABEL}` :`{STORE_ID}` {{id: {{session_id}} }})" \
                "\nMERGE (i :`{ITEM_LABEL}` :`{STORE_ID}` {{id: {{item_id}} }})" \
                "\nMERGE (s)-[r :`{REL}`]->(i)"
                #"(i :`{ITEM_LABEL}` :`{STORE_ID}` {{id: {{item_id}} }})"

            query = [q.format(
                SESSION_LABEL=store.LABEL_SESSION,
                ITEM_LABEL=store.LABEL_ITEM,
                STORE_ID=data[SCHEMA_KEY_TENANT_ID],
                REL=store.REL_ACTION_TYPE_ADD_TO_CART
            )]

            params = [neo4j.Parameter("datetime", dt),
                      neo4j.Parameter("qty", item[SCHEMA_KEY_QUANTITY]),
                      neo4j.Parameter("item_id", item[SCHEMA_KEY_ITEM_ID]),
                      neo4j.Parameter("session_id", data[SCHEMA_KEY_SESSION_ID])]

            query.append("\nSET r.{0} = {{ {0} }}".format(
                "datetime"
            ))

            query.append("\nSET r.{0} = {{ {0} }}".format(
                "qty"
            ))

            queries.append(neo4j.Query(''.join(query), params))

    elif data[SCHEMA_KEY_ACTION][SCHEMA_KEY_NAME].upper() == store.REL_ACTION_TYPE_BUY:

        #collect items
        for item in data[SCHEMA_KEY_ITEMS]:

            q = "MERGE (n :`{ITEM_LABEL}` :`{STORE_ID}` {{id: {{id}} }})"

            query = [q.format(
                ITEM_LABEL=store.LABEL_ITEM,
                STORE_ID=data[SCHEMA_KEY_TENANT_ID]
            )]

            params = [neo4j.Parameter("id", item[SCHEMA_KEY_ITEM_ID])]

            queries.append(neo4j.Query(''.join(query), params))

            #(item)-[r]-(session)

            q = "MERGE (s :`{SESSION_LABEL}` :`{STORE_ID}` {{id: {{session_id}} }})" \
                "\nMERGE (i :`{ITEM_LABEL}` :`{STORE_ID}` {{id: {{item_id}} }})" \
                "\nMERGE (s)-[r :`{REL}`]->(i)"

            query = [q.format(
                SESSION_LABEL=store.LABEL_SESSION,
                ITEM_LABEL=store.LABEL_ITEM,
                STORE_ID=data[SCHEMA_KEY_TENANT_ID],
                REL=store.REL_ACTION_TYPE_BUY
            )]

            params = [neo4j.Parameter("datetime", dt),
                      neo4j.Parameter("qty", item[SCHEMA_KEY_QUANTITY]),
                      neo4j.Parameter("sub_total", item[SCHEMA_KEY_SUBTOTAL]),
                      neo4j.Parameter("item_id", item[SCHEMA_KEY_ITEM_ID]),
                      neo4j.Parameter("session_id", data[SCHEMA_KEY_SESSION_ID])]

            query.append("\nSET r.{0} = {{ {0} }}".format(
                "datetime"
            ))

            query.append("\nSET r.{0} = {{ {0} }}".format(
                "qty"
            ))

            query.append("\nSET r.{0} = {{ {0} }}".format(
                "sub_total"
            ))

            queries.append(neo4j.Query(''.join(query), params))

    elif data[SCHEMA_KEY_ACTION][SCHEMA_KEY_NAME].upper() == store.REL_ACTION_TYPE_STARTED_CHECKOUT:

        #collect items
        for item in data[SCHEMA_KEY_ITEMS]:

            q = "MERGE (n :`{ITEM_LABEL}` :`{STORE_ID}` {{id: {{id}} }})"

            query = [q.format(
                ITEM_LABEL=store.LABEL_ITEM,
                STORE_ID=data[SCHEMA_KEY_TENANT_ID]
            )]

            params = [neo4j.Parameter("id", item[SCHEMA_KEY_ITEM_ID])]

            queries.append(neo4j.Query(''.join(query), params))

            #(item)-[r]-(session)

            q = "MERGE (s :`{SESSION_LABEL}` :`{STORE_ID}` {{id: {{session_id}} }})" \
                "\nMERGE (i :`{ITEM_LABEL}` :`{STORE_ID}` {{id: {{item_id}} }})" \
                "\nMERGE (s)-[r :`{REL}`]->(i)"

            query = [q.format(
                SESSION_LABEL=store.LABEL_SESSION,
                ITEM_LABEL=store.LABEL_ITEM,
                STORE_ID=data[SCHEMA_KEY_TENANT_ID],
                REL=store.REL_ACTION_TYPE_STARTED_CHECKOUT
            )]

            params = [neo4j.Parameter("datetime", dt),
                      neo4j.Parameter("item_id", item[SCHEMA_KEY_ITEM_ID]),
                      neo4j.Parameter("session_id", data[SCHEMA_KEY_SESSION_ID])]

            query.append("\nSET r.{0} = {{ {0} }}".format(
                "datetime"
            ))

            queries.append(neo4j.Query(''.join(query), params))

    elif data[SCHEMA_KEY_ACTION][SCHEMA_KEY_NAME].upper() == store.REL_ACTION_TYPE_SEARCH:

        q = "MERGE (s :`{SESSION_LABEL}` :`{STORE_ID}` {{ id: {{session_id}} }})" \
            "\nMERGE (n :`{SEARCH_LABEL}` :`{STORE_ID}` {{ keywords: {{keywords}} }})" \
            "\nMERGE (s)-[r :`{REL}`]->(n)"

        #collect items
        query = [q.format(
            SEARCH_LABEL=store.LABEL_SEARCH,
            SESSION_LABEL=store.LABEL_SESSION,
            STORE_ID=data[SCHEMA_KEY_TENANT_ID],
            REL=store.REL_ACTION_TYPE_SEARCH
        )]

        params = [neo4j.Parameter("keywords", data[SCHEMA_KEY_ACTION][SCHEMA_KEY_KEYWORDS]),
                  neo4j.Parameter("session_id", data[SCHEMA_KEY_SESSION_ID]),
                  neo4j.Parameter("datetime", dt)]

        queries.append(neo4j.Query(''.join(query), params))

        for k, v in data[SCHEMA_KEY_ACTION].items():

            if k != SCHEMA_KEY_KEYWORDS and is_acceptable_data_type(v):

                params.append(neo4j.Parameter(k, v))
                query.append("\nSET n.{0} = {{ {0} }}".format(
                    k
                ))

        query.append("\nSET r.{0} = {{ {0} }}".format(
            "datetime"
        ))

        queries.append(neo4j.Query(''.join(query), params))

    elif data[SCHEMA_KEY_ACTION][SCHEMA_KEY_NAME].upper() == store.REL_ACTION_TYPE_CHECK_DELETE_ITEM:

        q = "MATCH (n :`{ITEM_LABEL}` :`{STORE_ID}` {{id: {{id}} }})" \
            "\nOPTIONAL MATCH (n)-[r]-(x)" \
            "\nDELETE r, n"

        query = [q.format(
            ITEM_LABEL=store.LABEL_ITEM,
            STORE_ID=data[SCHEMA_KEY_TENANT_ID]
        )]

        params = [neo4j.Parameter("id", data[SCHEMA_KEY_ITEM_ID])]

        queries.append(neo4j.Query(''.join(query), params))

    return queries