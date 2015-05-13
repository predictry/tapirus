__author__ = 'guilherme'


from tapirus.model.constants import *


# TODO: Model events. Parse logs into entities and events. Feed these to data importers

class Session(object):

    def __init__(self, id, domain, uuid):
        self.id = id
        self.domain = domain
        self.uuid = uuid


class User(object):

    def __init__(self, id, domain, uuid):
        self.id = id
        self.domain = domain
        self.uuid = uuid


class Agent(object):

    def __init__(self, id, domain, uuid):
        self.id = id
        self.domain = domain
        self.uuid = uuid


class Item(object):

    def __init__(self, id, domain, uuid):
        self.id = id
        self.domain = domain
        self.uuid = uuid


class Tenant(object):

    def __init__(self, name, api_key):
        self.name = name
        self.api_key = api_key


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