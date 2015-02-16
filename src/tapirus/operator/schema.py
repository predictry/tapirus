__author__ = 'guilherme'

import jsonschema

from tapirus.model import store
from tapirus.utils.logger import Logger

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
            "session_id": {"type": "string"},
            "tenant_id": {"type": "string"},
            "action": {
                "type": "object",
                "properties": {
                    "name": {"type": "string"},
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
            "session_id": {"type": "string"},
            "tenant_id": {"type": "string"},
            "action": {
                "type": "object",
                "properties": {
                    "name": {
                        "enum": ["search"]
                    },
                    "keywords": {"type": "string"}
                },
                "required": ["name", "keywords"]
            },
            "user": {
                "type": "object",
                "properties": {
                    "user_id": {"type": ["integer", "number", "string"]},
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
            "session_id": {"type": "string"},
            "tenant_id": {"type": "string"},
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
                    "user_id": {"type": ["integer", "number", "string"]},
                },
                "required": ["user_id"]
            },
            "items": {
                "type": "array",
                "items": {
                    "type": ["boolean", "integer", "null", "number", "object", "string", "array"],
                    "properties": {
                        "item_id": {"type": ["integer", "number", "string"]},
                        "locations": {
                            "type": "object",
                            "properties": {
                                "country": {"type": "string"},
                                "city": {"type": "string"}
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
            "session_id": {"type": "string"},
            "tenant_id": {"type": "string"},
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
                    "user_id": {"type": ["integer", "number", "string"]},
                },
                "required": ["user_id"]
            },
            "items": {
                "type": "array",
                "items": {
                    "type": ["boolean", "integer", "null", "number", "object", "string", "array"],
                    "properties": {
                        "item_id": {"type": ["integer", "number", "string"]},
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
            "session_id": {"type": "string"},
            "tenant_id": {"type": "string"},
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
                    "user_id": {"type": ["integer", "number", "string"]},
                },
                "required": ["user_id"]
            },
            "items": {
                "type": "array",
                "items": {
                    "type": ["boolean", "integer", "null", "number", "object", "string", "array"],
                    "properties": {
                        "item_id": {"type": ["integer", "number", "string"]},
                        "locations": {
                            "type": "object",
                            "properties": {
                                "country": {"type": "string"},
                                "city": {"type": "string"}
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
            "session_id": {"type": "string"},
            "tenant_id": {"type": "string"},
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
                    "user_id": {"type": ["integer", "number", "string"]},
                },
                "required": ["user_id"]
            },
            "items": {
                "type": "array",
                "items": {
                    "type": ["boolean", "integer", "null", "number", "object", "string", "array"],
                    "properties": {
                        "item_id": {"type": ["integer", "number", "string"]},
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