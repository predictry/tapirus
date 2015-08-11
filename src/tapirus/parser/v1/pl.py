import enum

from tapirus.constants import *
from tapirus.entities import Session, User, Agent, Item, Action
from tapirus.utils import text
from tapirus.core import errors
from tapirus.repo import models


class ErrorCause(enum.Enum):
    UNSUPPORTED_DATA_TYPE = 'error.UnsupportedDataType'
    WRONG_DATA_TYPE = 'error.WrongDataType'
    INVALID_VALUE = 'error.InvalidValue'
    MISSING_KEY = 'error.MissingKey'
    JSON_FORMAT = 'error.JsonFormat'


class DataType(enum.Enum):
    TEXT = 'Text'
    NUMERIC = 'Numeric'
    LIST = 'List'
    MAP = 'Map'
    BOOLEAN = 'Boolean'


# TODO: Model events. Parse logs into entities and events. Feed these to data importers
# TODO: Parse recommended item


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

    if SCHEMA_KEY_SESSION_ID not in data:
        return False
    if type(data[SCHEMA_KEY_SESSION_ID]) is not str:
        return False
    if len(data[SCHEMA_KEY_SESSION_ID]) < 1:
        return False
    if not _is_valid_data(data[SCHEMA_KEY_SESSION_ID]):
        return False

    if SCHEMA_KEY_TENANT_ID not in data:
        return False
    if type(data[SCHEMA_KEY_TENANT_ID]) is not str:
        return False
    if len(data[SCHEMA_KEY_TENANT_ID]) < 1:
        return False
    if not _is_valid_data(data[SCHEMA_KEY_TENANT_ID]):
        return False

    if SCHEMA_KEY_ACTION not in data:
        return False

    if SCHEMA_KEY_NAME not in data[SCHEMA_KEY_ACTION]:
        return False
    if type(data[SCHEMA_KEY_ACTION][SCHEMA_KEY_NAME]) is not str:
        return False
    if len(data[SCHEMA_KEY_ACTION][SCHEMA_KEY_NAME]) < 1:
        return False
    if not _is_valid_data(data[SCHEMA_KEY_ACTION][SCHEMA_KEY_NAME]):
        return False

    if SCHEMA_KEY_USER in data:

        if SCHEMA_KEY_USER_ID not in data[SCHEMA_KEY_USER]:
            return False
        if type(data[SCHEMA_KEY_USER][SCHEMA_KEY_USER_ID]) is not str:
            return False
        if len(data[SCHEMA_KEY_USER][SCHEMA_KEY_USER_ID]) < 1:
            return False
        if not _is_valid_data(data[SCHEMA_KEY_USER][SCHEMA_KEY_USER_ID]):
            return False

    if SCHEMA_KEY_RECOMMENDATION in data[SCHEMA_KEY_ACTION]:
        if type(data[SCHEMA_KEY_ACTION][SCHEMA_KEY_RECOMMENDATION]) is not str:
            return False

        if text.boolean(data[SCHEMA_KEY_ACTION][SCHEMA_KEY_RECOMMENDATION]) is None:
            return False

    if SCHEMA_KEY_RECOMMENDATION_ORI in data[SCHEMA_KEY_ACTION]:
        if type(data[SCHEMA_KEY_ACTION][SCHEMA_KEY_RECOMMENDATION_ORI]) is not dict:
            return False

        # other rec parameters must be a flat dictionary/map (no nested dictionaries)
        for k in data[SCHEMA_KEY_ACTION][SCHEMA_KEY_RECOMMENDATION_ORI]:

            if _is_valid_data(data[SCHEMA_KEY_ACTION][SCHEMA_KEY_RECOMMENDATION_ORI][k]) is False:
                return False

    if data[SCHEMA_KEY_ACTION][SCHEMA_KEY_NAME].lower() == REL_ACTION_TYPE_SEARCH.lower():

        if SCHEMA_KEY_KEYWORDS not in data[SCHEMA_KEY_ACTION]:
            return False
        if type(data[SCHEMA_KEY_ACTION][SCHEMA_KEY_KEYWORDS]) is not str:
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
            if type(item[SCHEMA_KEY_ITEM_ID]) is not str:
                return False
            if len(item[SCHEMA_KEY_ITEM_ID]) < 1:
                return False
            if not _is_valid_data(item[SCHEMA_KEY_ITEM_ID]):
                return False

            if SCHEMA_KEY_LOCATION in item:

                if type(item[SCHEMA_KEY_LOCATION]) is not dict:
                    return False

                if SCHEMA_KEY_COUNTRY in item[SCHEMA_KEY_LOCATION]:
                    if type(item[SCHEMA_KEY_LOCATION][SCHEMA_KEY_COUNTRY]) is not str:
                        return False
                    if len(item[SCHEMA_KEY_LOCATION][SCHEMA_KEY_COUNTRY]) < 1:
                        return False

                if SCHEMA_KEY_CITY in item[SCHEMA_KEY_LOCATION]:
                    if type(item[SCHEMA_KEY_LOCATION][SCHEMA_KEY_CITY]) is not str:
                        return False
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
            if type(item[SCHEMA_KEY_ITEM_ID]) is not str:
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
                    if type(item[SCHEMA_KEY_LOCATION][SCHEMA_KEY_COUNTRY]) is not str:
                        return False
                    if len(item[SCHEMA_KEY_LOCATION][SCHEMA_KEY_COUNTRY]) < 1:
                        return False

                if SCHEMA_KEY_CITY in item[SCHEMA_KEY_LOCATION]:
                    if type(item[SCHEMA_KEY_LOCATION][SCHEMA_KEY_CITY]) is not str:
                        return False
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
            if type(item[SCHEMA_KEY_ITEM_ID]) is not str:
                return False
            if len(item[SCHEMA_KEY_ITEM_ID]) < 1:
                return False
            if not _is_valid_data(item[SCHEMA_KEY_ITEM_ID]):
                return False

            if SCHEMA_KEY_LOCATION in item:

                if type(item[SCHEMA_KEY_LOCATION]) is not dict:
                    return False

                if SCHEMA_KEY_COUNTRY in item[SCHEMA_KEY_LOCATION]:
                    if type(item[SCHEMA_KEY_LOCATION][SCHEMA_KEY_COUNTRY]) is not str:
                        return False
                    if len(item[SCHEMA_KEY_LOCATION][SCHEMA_KEY_COUNTRY]) < 1:
                        return False

                if SCHEMA_KEY_CITY in item[SCHEMA_KEY_LOCATION]:
                    if type(item[SCHEMA_KEY_LOCATION][SCHEMA_KEY_CITY]) is not str:
                        return False
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
            if type(item[SCHEMA_KEY_ITEM_ID]) is not str:
                return False
            if len(item[SCHEMA_KEY_ITEM_ID]) < 1:
                return False
            if not _is_valid_data(item[SCHEMA_KEY_ITEM_ID]):
                return False

            if SCHEMA_KEY_QUANTITY not in item:
                return False
            if type(item[SCHEMA_KEY_QUANTITY]) is not str:
                return False
            if len(item[SCHEMA_KEY_QUANTITY]) < 1:
                return False

            if SCHEMA_KEY_SUBTOTAL not in item:
                return False
            if type(item[SCHEMA_KEY_SUBTOTAL]) is not str:
                return False
            if len(item[SCHEMA_KEY_SUBTOTAL]) < 1:
                return False

            if SCHEMA_KEY_LOCATION in item:

                if type(item[SCHEMA_KEY_LOCATION]) is not dict:
                    return False

                if SCHEMA_KEY_COUNTRY in item[SCHEMA_KEY_LOCATION]:
                    if type(item[SCHEMA_KEY_LOCATION][SCHEMA_KEY_COUNTRY]) is not str:
                        return False
                    if len(item[SCHEMA_KEY_LOCATION][SCHEMA_KEY_COUNTRY]) < 1:
                        return False

                if SCHEMA_KEY_CITY in item[SCHEMA_KEY_LOCATION]:
                    if type(item[SCHEMA_KEY_LOCATION][SCHEMA_KEY_CITY]) is not str:
                        return False
                    if len(item[SCHEMA_KEY_LOCATION][SCHEMA_KEY_CITY]) < 1:
                        return False

    elif data[SCHEMA_KEY_ACTION][SCHEMA_KEY_NAME].lower() in [REL_ACTION_TYPE_CHECK_DELETE_ITEM.lower(),
                                                              REL_ACTION_TYPE_DELETE_ITEM.lower()]:

        # if SCHEMA_KEY_ITEM_ID not in data:
        #     return False
        # if type(data[SCHEMA_KEY_ITEM_ID]) is not str:
        #     return False
        # if len(data[SCHEMA_KEY_ITEM_ID]) < 1:
        #     return False
        # if not _is_valid_data(data[SCHEMA_KEY_ITEM_ID]):
        #     return False

        if SCHEMA_KEY_ITEMS not in data:
            return False

        if type(data[SCHEMA_KEY_ITEMS]) is not list:
            return False

        for item in data[SCHEMA_KEY_ITEMS]:

            if type(item) is not dict:
                return False

            if SCHEMA_KEY_ITEM_ID not in item:
                return False
            if type(item[SCHEMA_KEY_ITEM_ID]) is not str:
                return False
            if len(item[SCHEMA_KEY_ITEM_ID]) < 1:
                return False
            if not _is_valid_data(item[SCHEMA_KEY_ITEM_ID]):
                return False

    return True


def detect_schema_errors(error):
    """
    :param error:
    :return:
    """

    assert isinstance(error, models.Error)

    default_flags = {
        'code': error.code
    }

    def find(key, string):

        assert isinstance(string, str)
        assert isinstance(key, str)

        key_start_index = string.find(key)

        if key_start_index >= 0:

            partial = string[key_start_index:]
            key_end_index = partial.find("=")
            last_index = partial.find("&")

            if key_end_index and last_index:

                return partial[key_end_index+1:last_index]

        return None

    # TODO: action to upper
    if isinstance(error.data, dict) is False:

        if isinstance(error.data, str):

            flags = {
                'tenant': SCHEMA_KEY_TENANT_ID,
                'action': ':'.join([SCHEMA_KEY_ACTION, SCHEMA_KEY_NAME])
            }

            for k, v in flags.items():
                if find(v, error.data):
                    default_flags[k] = find(v, error.data)

    else:

        if SCHEMA_KEY_TENANT_ID in error.data and isinstance(error.data[SCHEMA_KEY_TENANT_ID], str):
            default_flags['tenant'] = error.data[SCHEMA_KEY_TENANT_ID]

        if SCHEMA_KEY_ACTION in error.data and isinstance(error.data[SCHEMA_KEY_ACTION], dict):

            if SCHEMA_KEY_NAME in error.data[SCHEMA_KEY_ACTION] and isinstance(
                    error.data[SCHEMA_KEY_ACTION][SCHEMA_KEY_NAME], str):
                default_flags['action'] = error.data[SCHEMA_KEY_ACTION][SCHEMA_KEY_NAME]

    # TODO: place repetitive code in a function (checking data type, len, missing key in payload)?

    def fault(key, cause, message, **kwargs):

        return {
            'key': key,
            'cause': cause.value,
            'message': message,
            'timestamp': str(error.timestamp),
            'tags': dict(default_flags, **{k: str(v) for k, v in kwargs.items()})
        }

    def mix(*args):

        return '.'.join([str(x) for x in args])

    def expected(data_type):

        return 'Expected {0}'.format(data_type)

    faults = []

    if isinstance(error.data, dict) is False:

        # implementation issues
        faults.append(
            fault(
                'root',
                ErrorCause.JSON_FORMAT,
                'Check JSON syntax',
            )
        )

        return faults

    data = error.data

    if SCHEMA_KEY_SESSION_ID not in data:
        faults.append(
            fault(
                mix(SCHEMA_KEY_SESSION_ID),
                ErrorCause.MISSING_KEY,
                None
            )
        )

    else:

        if type(data[SCHEMA_KEY_SESSION_ID]) is not str:
            faults.append(
                fault(
                    mix(SCHEMA_KEY_SESSION_ID),
                    ErrorCause.WRONG_DATA_TYPE,
                    expected(DataType.TEXT)
                )
            )

        else:

            if len(data[SCHEMA_KEY_SESSION_ID]) < 1:
                faults.append(
                    fault(
                        mix(SCHEMA_KEY_SESSION_ID),
                        ErrorCause.INVALID_VALUE,
                        None
                    )
                )

            if not _is_valid_data(data[SCHEMA_KEY_SESSION_ID]):
                faults.append(
                    fault(
                        mix(SCHEMA_KEY_SESSION_ID),
                        ErrorCause.INVALID_VALUE,
                        None
                    )
                )

    if SCHEMA_KEY_TENANT_ID not in data:
        faults.append(
            fault(
                mix(SCHEMA_KEY_TENANT_ID),
                ErrorCause.MISSING_KEY,
                None
            )
        )

    else:

        if type(data[SCHEMA_KEY_TENANT_ID]) is not str:
            faults.append(
                fault(
                    mix(SCHEMA_KEY_TENANT_ID),
                    ErrorCause.WRONG_DATA_TYPE,
                    expected(DataType.TEXT)
                )
            )

        else:

            if len(data[SCHEMA_KEY_TENANT_ID]) < 1:
                faults.append(
                    fault(
                        mix(SCHEMA_KEY_TENANT_ID),
                        ErrorCause.INVALID_VALUE,
                        None
                    )
                )

            if not _is_valid_data(data[SCHEMA_KEY_TENANT_ID]):
                faults.append(
                    fault(
                        mix(SCHEMA_KEY_TENANT_ID),
                        ErrorCause.INVALID_VALUE,
                        None
                    )
                )

    if SCHEMA_KEY_USER in data:

        if SCHEMA_KEY_USER_ID not in data[SCHEMA_KEY_USER]:
            faults.append(
                fault(
                    mix(SCHEMA_KEY_USER, SCHEMA_KEY_USER_ID),
                    ErrorCause.MISSING_KEY,
                    None
                )
            )

        if type(data[SCHEMA_KEY_USER][SCHEMA_KEY_USER_ID]) is not str:
            faults.append(
                fault(
                    mix(SCHEMA_KEY_USER, SCHEMA_KEY_USER_ID),
                    ErrorCause.WRONG_DATA_TYPE,
                    expected(DataType.TEXT)
                )
            )

        else:

            if len(data[SCHEMA_KEY_USER][SCHEMA_KEY_USER_ID]) < 1:
                faults.append(
                    fault(
                        mix(SCHEMA_KEY_USER, SCHEMA_KEY_USER_ID),
                        ErrorCause.INVALID_VALUE,
                        None
                    )
                )

            if not _is_valid_data(data[SCHEMA_KEY_USER][SCHEMA_KEY_USER_ID]):
                faults.append(
                    fault(
                        mix(SCHEMA_KEY_USER, SCHEMA_KEY_USER_ID),
                        ErrorCause.INVALID_VALUE,
                        None
                    )
                )

    if SCHEMA_KEY_ACTION not in data:
        faults.append(
            fault(
                mix(SCHEMA_KEY_ACTION),
                ErrorCause.MISSING_KEY,
                None
            )
        )

    else:

        if SCHEMA_KEY_NAME not in data[SCHEMA_KEY_ACTION]:
            faults.append(
                fault(
                    mix(SCHEMA_KEY_ACTION, SCHEMA_KEY_NAME),
                    ErrorCause.MISSING_KEY,
                    None
                )
            )

        else:

            if type(data[SCHEMA_KEY_ACTION][SCHEMA_KEY_NAME]) is not str:
                faults.append(
                    fault(
                        mix(SCHEMA_KEY_ACTION, SCHEMA_KEY_NAME),
                        ErrorCause.WRONG_DATA_TYPE,
                        expected(DataType.TEXT)
                    )
                )

            else:

                if len(data[SCHEMA_KEY_ACTION][SCHEMA_KEY_NAME]) < 1:
                    faults.append(
                        fault(
                            mix(SCHEMA_KEY_ACTION, SCHEMA_KEY_NAME),
                            ErrorCause.INVALID_VALUE,
                            None
                        )
                    )

                if not _is_valid_data(data[SCHEMA_KEY_ACTION][SCHEMA_KEY_NAME]):
                    faults.append(
                        fault(
                            mix(SCHEMA_KEY_ACTION, SCHEMA_KEY_NAME),
                            ErrorCause.INVALID_VALUE,
                            None
                        )
                    )

        if SCHEMA_KEY_RECOMMENDATION in data[SCHEMA_KEY_ACTION]:
            if type(data[SCHEMA_KEY_ACTION][SCHEMA_KEY_RECOMMENDATION]) is not str:
                faults.append(
                    fault(
                        mix(SCHEMA_KEY_ACTION, SCHEMA_KEY_RECOMMENDATION),
                        ErrorCause.WRONG_DATA_TYPE,
                        expected(DataType.TEXT)
                    )
                )

            else:

                if text.boolean(data[SCHEMA_KEY_ACTION][SCHEMA_KEY_RECOMMENDATION]) is None:
                    faults.append(
                        fault(
                            mix(SCHEMA_KEY_ACTION, SCHEMA_KEY_RECOMMENDATION),
                            ErrorCause.INVALID_VALUE,
                            None
                        )
                    )

        if SCHEMA_KEY_RECOMMENDATION_ORI in data[SCHEMA_KEY_ACTION]:
            if type(data[SCHEMA_KEY_ACTION][SCHEMA_KEY_RECOMMENDATION_ORI]) is not dict:
                faults.append(
                    fault(
                        mix(SCHEMA_KEY_ACTION, SCHEMA_KEY_RECOMMENDATION_ORI),
                        ErrorCause.WRONG_DATA_TYPE,
                        expected(DataType.MAP)
                    )
                )

            # other rec parameters must be a flat dictionary/map (no nested dictionaries)
            for k in data[SCHEMA_KEY_ACTION][SCHEMA_KEY_RECOMMENDATION_ORI]:

                if _is_valid_data(data[SCHEMA_KEY_ACTION][SCHEMA_KEY_RECOMMENDATION_ORI][k]) is False:
                    faults.append(
                        fault(
                            mix(SCHEMA_KEY_ACTION, SCHEMA_KEY_RECOMMENDATION_ORI, k),
                            ErrorCause.INVALID_VALUE,
                            None
                        )
                    )

        if data[SCHEMA_KEY_ACTION][SCHEMA_KEY_NAME].lower() == REL_ACTION_TYPE_SEARCH.lower():

            if SCHEMA_KEY_KEYWORDS not in data[SCHEMA_KEY_ACTION]:
                faults.append(
                    fault(
                        mix(SCHEMA_KEY_ACTION, REL_ACTION_TYPE_SEARCH, SCHEMA_KEY_KEYWORDS),
                        ErrorCause.MISSING_KEY,
                        None
                    )
                )

            else:

                if type(data[SCHEMA_KEY_ACTION][SCHEMA_KEY_KEYWORDS]) is not str:
                    faults.append(
                        fault(
                            mix(SCHEMA_KEY_ACTION, REL_ACTION_TYPE_SEARCH, SCHEMA_KEY_KEYWORDS),
                            ErrorCause.WRONG_DATA_TYPE,
                            expected(DataType.TEXT)
                        )
                    )

                else:

                    if len(data[SCHEMA_KEY_ACTION][SCHEMA_KEY_KEYWORDS]) < 1:
                        faults.append(
                            fault(
                                mix(SCHEMA_KEY_ACTION, REL_ACTION_TYPE_SEARCH, SCHEMA_KEY_KEYWORDS),
                                ErrorCause.INVALID_VALUE,
                                None
                            )
                        )

        elif data[SCHEMA_KEY_ACTION][SCHEMA_KEY_NAME].lower() == REL_ACTION_TYPE_VIEW.lower():

            if SCHEMA_KEY_ITEMS not in data:
                faults.append(
                    fault(
                        mix(SCHEMA_KEY_ACTION, REL_ACTION_TYPE_VIEW, SCHEMA_KEY_ITEMS),
                        ErrorCause.MISSING_KEY,
                        None
                    )
                )

            else:

                if type(data[SCHEMA_KEY_ITEMS]) is not list:
                    faults.append(
                        fault(
                            mix(SCHEMA_KEY_ACTION, REL_ACTION_TYPE_VIEW, SCHEMA_KEY_ITEMS),
                            ErrorCause.WRONG_DATA_TYPE,
                            expected(DataType.LIST)
                        )
                    )

                else:

                    for item in data[SCHEMA_KEY_ITEMS]:

                        if type(item) is not dict:
                            faults.append(
                                fault(
                                    mix(SCHEMA_KEY_ACTION, REL_ACTION_TYPE_VIEW, SCHEMA_KEY_ITEMS, 'Item'),
                                    ErrorCause.WRONG_DATA_TYPE,
                                    expected(DataType.MAP)
                                )
                            )

                        else:

                            if SCHEMA_KEY_ITEM_ID not in item:
                                faults.append(
                                    fault(
                                        mix(SCHEMA_KEY_ACTION, REL_ACTION_TYPE_VIEW, SCHEMA_KEY_ITEMS, 'Item',
                                            SCHEMA_KEY_ITEM_ID),
                                        ErrorCause.MISSING_KEY,
                                        None
                                    )
                                )

                            else:

                                if type(item[SCHEMA_KEY_ITEM_ID]) is not str:
                                    faults.append(
                                        fault(
                                            mix(SCHEMA_KEY_ACTION, REL_ACTION_TYPE_VIEW, SCHEMA_KEY_ITEMS, 'Item',
                                                SCHEMA_KEY_ITEM_ID),
                                            ErrorCause.WRONG_DATA_TYPE,
                                            expected(DataType.TEXT)
                                        )
                                    )

                                else:

                                    if len(item[SCHEMA_KEY_ITEM_ID]) < 1:
                                        faults.append(
                                            fault(
                                                mix(SCHEMA_KEY_ACTION, REL_ACTION_TYPE_VIEW, SCHEMA_KEY_ITEMS, 'Item',
                                                    SCHEMA_KEY_ITEM_ID),
                                                ErrorCause.INVALID_VALUE,
                                                None
                                            )
                                        )

                                    if not _is_valid_data(item[SCHEMA_KEY_ITEM_ID]):
                                        faults.append(
                                            fault(
                                                mix(SCHEMA_KEY_ACTION, REL_ACTION_TYPE_VIEW, SCHEMA_KEY_ITEMS, 'Item',
                                                    SCHEMA_KEY_ITEM_ID),
                                                ErrorCause.INVALID_VALUE,
                                                None
                                            )
                                        )

                            if SCHEMA_KEY_LOCATION in item:

                                if type(item[SCHEMA_KEY_LOCATION]) is not dict:
                                    faults.append(
                                        fault(
                                            mix(SCHEMA_KEY_ACTION, REL_ACTION_TYPE_VIEW, SCHEMA_KEY_ITEMS, 'Item',
                                                SCHEMA_KEY_LOCATION),
                                            ErrorCause.WRONG_DATA_TYPE,
                                            expected(DataType.MAP)
                                        )
                                    )

                                else:

                                    if SCHEMA_KEY_COUNTRY in item[SCHEMA_KEY_LOCATION]:
                                        if type(item[SCHEMA_KEY_LOCATION][SCHEMA_KEY_COUNTRY]) is not str:
                                            faults.append(
                                                fault(
                                                    mix(SCHEMA_KEY_ACTION, REL_ACTION_TYPE_VIEW, SCHEMA_KEY_ITEMS,
                                                        'Item',
                                                        SCHEMA_KEY_LOCATION,
                                                        SCHEMA_KEY_COUNTRY),
                                                    ErrorCause.WRONG_DATA_TYPE,
                                                    expected(DataType.TEXT)
                                                )
                                            )

                                        else:

                                            if len(item[SCHEMA_KEY_LOCATION][SCHEMA_KEY_COUNTRY]) < 1:
                                                faults.append(
                                                    fault(
                                                        mix(SCHEMA_KEY_ACTION, REL_ACTION_TYPE_VIEW, SCHEMA_KEY_ITEMS,
                                                            'Item',
                                                            SCHEMA_KEY_LOCATION,
                                                            SCHEMA_KEY_COUNTRY),
                                                        ErrorCause.INVALID_VALUE,
                                                        None
                                                    )
                                                )

                                    if SCHEMA_KEY_CITY in item[SCHEMA_KEY_LOCATION]:
                                        if type(item[SCHEMA_KEY_LOCATION][SCHEMA_KEY_CITY]) is not str:
                                            faults.append(
                                                fault(
                                                    mix(SCHEMA_KEY_ACTION, REL_ACTION_TYPE_VIEW, SCHEMA_KEY_ITEMS,
                                                        'Item',
                                                        SCHEMA_KEY_LOCATION,
                                                        SCHEMA_KEY_CITY),
                                                    ErrorCause.WRONG_DATA_TYPE,
                                                    expected(DataType.TEXT)
                                                )
                                            )

                                        else:

                                            if len(item[SCHEMA_KEY_LOCATION][SCHEMA_KEY_CITY]) < 1:
                                                faults.append(
                                                    fault(
                                                        mix(SCHEMA_KEY_ACTION, REL_ACTION_TYPE_VIEW, SCHEMA_KEY_ITEMS,
                                                            'Item',
                                                            SCHEMA_KEY_LOCATION,
                                                            SCHEMA_KEY_CITY),
                                                        ErrorCause.INVALID_VALUE,
                                                        None
                                                    )
                                                )

        elif data[SCHEMA_KEY_ACTION][SCHEMA_KEY_NAME].lower() == REL_ACTION_TYPE_ADD_TO_CART.lower():

            if SCHEMA_KEY_ITEMS not in data:
                faults.append(
                    fault(
                        mix(SCHEMA_KEY_ACTION, REL_ACTION_TYPE_ADD_TO_CART, SCHEMA_KEY_ITEMS),
                        ErrorCause.MISSING_KEY,
                        None
                    )
                )

            else:

                if type(data[SCHEMA_KEY_ITEMS]) is not list:
                    faults.append(
                        fault(
                            mix(SCHEMA_KEY_ACTION, REL_ACTION_TYPE_ADD_TO_CART, SCHEMA_KEY_ITEMS),
                            ErrorCause.WRONG_DATA_TYPE,
                            expected(DataType.LIST)
                        )
                    )

                else:

                    for item in data[SCHEMA_KEY_ITEMS]:

                        if type(item) is not dict:
                            faults.append(
                                fault(
                                    mix(SCHEMA_KEY_ACTION, REL_ACTION_TYPE_ADD_TO_CART, SCHEMA_KEY_ITEMS, 'Item'),
                                    ErrorCause.WRONG_DATA_TYPE,
                                    expected(DataType.MAP)
                                )
                            )

                        else:

                            if SCHEMA_KEY_ITEM_ID not in item:
                                faults.append(
                                    fault(
                                        mix(SCHEMA_KEY_ACTION, REL_ACTION_TYPE_ADD_TO_CART, SCHEMA_KEY_ITEMS, 'Item',
                                            SCHEMA_KEY_ITEM_ID),
                                        ErrorCause.MISSING_KEY,
                                        None
                                    )
                                )

                            else:

                                if type(item[SCHEMA_KEY_ITEM_ID]) is not str:
                                    faults.append(
                                        fault(
                                            mix(SCHEMA_KEY_ACTION, REL_ACTION_TYPE_ADD_TO_CART, SCHEMA_KEY_ITEMS,
                                                'Item',
                                                SCHEMA_KEY_ITEM_ID),
                                            ErrorCause.WRONG_DATA_TYPE,
                                            expected(DataType.TEXT)
                                        )
                                    )

                                else:

                                    if len(item[SCHEMA_KEY_ITEM_ID]) < 1:
                                        faults.append(
                                            fault(
                                                mix(SCHEMA_KEY_ACTION, REL_ACTION_TYPE_ADD_TO_CART, SCHEMA_KEY_ITEMS,
                                                    'Item',
                                                    SCHEMA_KEY_ITEM_ID),
                                                ErrorCause.INVALID_VALUE,
                                                None
                                            )
                                        )

                                    if not _is_valid_data(item[SCHEMA_KEY_ITEM_ID]):
                                        faults.append(
                                            fault(
                                                mix(SCHEMA_KEY_ACTION, REL_ACTION_TYPE_ADD_TO_CART, SCHEMA_KEY_ITEMS,
                                                    'Item',
                                                    SCHEMA_KEY_ITEM_ID),
                                                ErrorCause.INVALID_VALUE,
                                                None
                                            )
                                        )

                            if SCHEMA_KEY_QUANTITY not in item:
                                faults.append(
                                    fault(
                                        mix(SCHEMA_KEY_ACTION, REL_ACTION_TYPE_ADD_TO_CART, SCHEMA_KEY_ITEMS, 'Item',
                                            SCHEMA_KEY_QUANTITY),
                                        ErrorCause.MISSING_KEY,
                                        None
                                    )
                                )

                            else:

                                if type(item[SCHEMA_KEY_QUANTITY]) is not str:
                                    faults.append(
                                        fault(
                                            mix(SCHEMA_KEY_ACTION, REL_ACTION_TYPE_BUY, SCHEMA_KEY_ITEMS, 'Item',
                                                SCHEMA_KEY_QUANTITY),
                                            ErrorCause.WRONG_DATA_TYPE,
                                            expected(DataType.TEXT)
                                        )
                                    )

                                else:

                                    if len(item[SCHEMA_KEY_QUANTITY]) < 1:
                                        faults.append(
                                            fault(
                                                mix(SCHEMA_KEY_ACTION, REL_ACTION_TYPE_BUY, SCHEMA_KEY_ITEMS, 'Item',
                                                    SCHEMA_KEY_QUANTITY),
                                                ErrorCause.INVALID_VALUE,
                                                None
                                            )
                                        )

                            if SCHEMA_KEY_LOCATION in item:

                                if type(item[SCHEMA_KEY_LOCATION]) is not dict:
                                    faults.append(
                                        fault(
                                            mix(SCHEMA_KEY_ACTION, REL_ACTION_TYPE_ADD_TO_CART, SCHEMA_KEY_ITEMS,
                                                'Item',
                                                SCHEMA_KEY_LOCATION),
                                            ErrorCause.WRONG_DATA_TYPE,
                                            expected(DataType.MAP)
                                        )
                                    )

                                else:

                                    if SCHEMA_KEY_COUNTRY in item[SCHEMA_KEY_LOCATION]:
                                        if type(item[SCHEMA_KEY_LOCATION][SCHEMA_KEY_COUNTRY]) is not str:
                                            faults.append(
                                                fault(
                                                    mix(SCHEMA_KEY_ACTION, REL_ACTION_TYPE_ADD_TO_CART,
                                                        SCHEMA_KEY_ITEMS, 'Item',
                                                        SCHEMA_KEY_LOCATION, SCHEMA_KEY_COUNTRY),
                                                    ErrorCause.WRONG_DATA_TYPE,
                                                    expected(DataType.TEXT)
                                                )
                                            )

                                        else:

                                            if len(item[SCHEMA_KEY_LOCATION][SCHEMA_KEY_COUNTRY]) < 1:
                                                faults.append(
                                                    fault(
                                                        mix(SCHEMA_KEY_ACTION, REL_ACTION_TYPE_ADD_TO_CART,
                                                            SCHEMA_KEY_ITEMS, 'Item',
                                                            SCHEMA_KEY_LOCATION, SCHEMA_KEY_COUNTRY),
                                                        ErrorCause.INVALID_VALUE,
                                                        None
                                                    )
                                                )

                                    if SCHEMA_KEY_CITY in item[SCHEMA_KEY_LOCATION]:
                                        if type(item[SCHEMA_KEY_LOCATION][SCHEMA_KEY_CITY]) is not str:
                                            faults.append(
                                                fault(
                                                    mix(SCHEMA_KEY_ACTION, REL_ACTION_TYPE_ADD_TO_CART,
                                                        SCHEMA_KEY_ITEMS, 'Item',
                                                        SCHEMA_KEY_LOCATION, SCHEMA_KEY_CITY),
                                                    ErrorCause.WRONG_DATA_TYPE,
                                                    expected(DataType.TEXT)
                                                )
                                            )

                                        else:

                                            if len(item[SCHEMA_KEY_LOCATION][SCHEMA_KEY_CITY]) < 1:
                                                faults.append(
                                                    fault(
                                                        mix(SCHEMA_KEY_ACTION, REL_ACTION_TYPE_ADD_TO_CART,
                                                            SCHEMA_KEY_ITEMS, 'Item',
                                                            SCHEMA_KEY_LOCATION, SCHEMA_KEY_CITY),
                                                        ErrorCause.INVALID_VALUE,
                                                        None
                                                    )
                                                )

        elif data[SCHEMA_KEY_ACTION][SCHEMA_KEY_NAME].lower() == REL_ACTION_TYPE_STARTED_CHECKOUT.lower():

            if SCHEMA_KEY_ITEMS not in data:
                faults.append(
                    fault(
                        mix(SCHEMA_KEY_ACTION, REL_ACTION_TYPE_STARTED_CHECKOUT, SCHEMA_KEY_ITEMS),
                        ErrorCause.MISSING_KEY,
                        None
                    )
                )

            else:

                if type(data[SCHEMA_KEY_ITEMS]) is not list:
                    faults.append(
                        fault(
                            mix(SCHEMA_KEY_ACTION, REL_ACTION_TYPE_STARTED_CHECKOUT, SCHEMA_KEY_ITEMS),
                            ErrorCause.WRONG_DATA_TYPE,
                            expected(DataType.LIST)
                        )
                    )

                else:

                    for item in data[SCHEMA_KEY_ITEMS]:

                        if type(item) is not dict:
                            faults.append(
                                fault(
                                    mix(SCHEMA_KEY_ACTION, REL_ACTION_TYPE_STARTED_CHECKOUT, SCHEMA_KEY_ITEMS, 'Item'),
                                    ErrorCause.WRONG_DATA_TYPE,
                                    expected(DataType.MAP)
                                )
                            )

                        else:

                            if SCHEMA_KEY_ITEM_ID not in item:
                                faults.append(
                                    fault(
                                        mix(SCHEMA_KEY_ACTION, REL_ACTION_TYPE_STARTED_CHECKOUT, SCHEMA_KEY_ITEMS,
                                            'Item',
                                            SCHEMA_KEY_ITEM_ID),
                                        ErrorCause.MISSING_KEY,
                                        None
                                    )
                                )

                            else:

                                if type(item[SCHEMA_KEY_ITEM_ID]) is not str:
                                    faults.append(
                                        fault(
                                            mix(SCHEMA_KEY_ACTION, REL_ACTION_TYPE_STARTED_CHECKOUT, SCHEMA_KEY_ITEMS,
                                                'Item',
                                                SCHEMA_KEY_ITEM_ID),
                                            ErrorCause.WRONG_DATA_TYPE,
                                            expected(DataType.TEXT)
                                        )
                                    )

                                else:

                                    if len(item[SCHEMA_KEY_ITEM_ID]) < 1:
                                        faults.append(
                                            fault(
                                                mix(SCHEMA_KEY_ACTION, REL_ACTION_TYPE_STARTED_CHECKOUT,
                                                    SCHEMA_KEY_ITEMS, 'Item',
                                                    SCHEMA_KEY_ITEM_ID),
                                                ErrorCause.INVALID_VALUE,
                                                None
                                            )
                                        )

                                    if not _is_valid_data(item[SCHEMA_KEY_ITEM_ID]):
                                        faults.append(
                                            fault(
                                                mix(SCHEMA_KEY_ACTION, REL_ACTION_TYPE_STARTED_CHECKOUT,
                                                    SCHEMA_KEY_ITEMS, 'Item',
                                                    SCHEMA_KEY_ITEM_ID),
                                                ErrorCause.INVALID_VALUE,
                                                None
                                            )
                                        )

                            if SCHEMA_KEY_LOCATION in item:

                                if type(item[SCHEMA_KEY_LOCATION]) is not dict:
                                    faults.append(
                                        fault(
                                            mix(SCHEMA_KEY_ACTION, REL_ACTION_TYPE_STARTED_CHECKOUT, SCHEMA_KEY_ITEMS,
                                                'Item',
                                                SCHEMA_KEY_LOCATION),
                                            ErrorCause.WRONG_DATA_TYPE,
                                            expected(DataType.MAP)
                                        )
                                    )

                                if SCHEMA_KEY_COUNTRY in item[SCHEMA_KEY_LOCATION]:
                                    if type(item[SCHEMA_KEY_LOCATION][SCHEMA_KEY_COUNTRY]) is not str:
                                        faults.append(
                                            fault(
                                                mix(SCHEMA_KEY_ACTION, REL_ACTION_TYPE_STARTED_CHECKOUT,
                                                    SCHEMA_KEY_ITEMS, 'Item',
                                                    SCHEMA_KEY_LOCATION, SCHEMA_KEY_COUNTRY),
                                                ErrorCause.WRONG_DATA_TYPE,
                                                expected(DataType.TEXT)
                                            )
                                        )

                                    else:

                                        if len(item[SCHEMA_KEY_LOCATION][SCHEMA_KEY_COUNTRY]) < 1:
                                            faults.append(
                                                fault(
                                                    mix(SCHEMA_KEY_ACTION, REL_ACTION_TYPE_STARTED_CHECKOUT,
                                                        SCHEMA_KEY_ITEMS, 'Item',
                                                        SCHEMA_KEY_LOCATION, SCHEMA_KEY_COUNTRY),
                                                    ErrorCause.INVALID_VALUE,
                                                    None
                                                )
                                            )

                                if SCHEMA_KEY_CITY in item[SCHEMA_KEY_LOCATION]:
                                    if type(item[SCHEMA_KEY_LOCATION][SCHEMA_KEY_CITY]) is not str:
                                        faults.append(
                                            fault(
                                                mix(SCHEMA_KEY_ACTION, REL_ACTION_TYPE_STARTED_CHECKOUT,
                                                    SCHEMA_KEY_ITEMS, 'Item',
                                                    SCHEMA_KEY_LOCATION, SCHEMA_KEY_CITY),
                                                ErrorCause.WRONG_DATA_TYPE,
                                                expected(DataType.TEXT)
                                            )
                                        )

                                    else:

                                        if len(item[SCHEMA_KEY_LOCATION][SCHEMA_KEY_CITY]) < 1:
                                            faults.append(
                                                fault(
                                                    mix(SCHEMA_KEY_ACTION, REL_ACTION_TYPE_STARTED_CHECKOUT,
                                                        SCHEMA_KEY_ITEMS, 'Item',
                                                        SCHEMA_KEY_LOCATION, SCHEMA_KEY_CITY),
                                                    ErrorCause.INVALID_VALUE,
                                                    None
                                                )
                                            )

        elif data[SCHEMA_KEY_ACTION][SCHEMA_KEY_NAME].lower() == REL_ACTION_TYPE_BUY.lower():

            if SCHEMA_KEY_ITEMS not in data:
                faults.append(
                    fault(
                        mix(SCHEMA_KEY_ACTION, REL_ACTION_TYPE_BUY, SCHEMA_KEY_ITEMS),
                        ErrorCause.MISSING_KEY,
                        None
                    )
                )

            else:

                if type(data[SCHEMA_KEY_ITEMS]) is not list:
                    faults.append(
                        fault(
                            mix(SCHEMA_KEY_ACTION, REL_ACTION_TYPE_BUY, SCHEMA_KEY_ITEMS),
                            ErrorCause.WRONG_DATA_TYPE,
                            expected(DataType.LIST)
                        )
                    )

                else:

                    for item in data[SCHEMA_KEY_ITEMS]:

                        if type(item) is not dict:
                            faults.append(
                                fault(
                                    mix(SCHEMA_KEY_ACTION, REL_ACTION_TYPE_BUY, SCHEMA_KEY_ITEMS, 'Item'),
                                    ErrorCause.WRONG_DATA_TYPE,
                                    expected(DataType.MAP)
                                )
                            )

                        else:

                            if SCHEMA_KEY_ITEM_ID not in item:
                                faults.append(
                                    fault(
                                        mix(SCHEMA_KEY_ACTION, REL_ACTION_TYPE_BUY, SCHEMA_KEY_ITEMS, 'Item',
                                            SCHEMA_KEY_ITEM_ID),
                                        ErrorCause.MISSING_KEY,
                                        None
                                    )
                                )

                            else:

                                if type(item[SCHEMA_KEY_ITEM_ID]) is not str:
                                    faults.append(
                                        fault(
                                            mix(SCHEMA_KEY_ACTION, REL_ACTION_TYPE_BUY, SCHEMA_KEY_ITEMS, 'Item',
                                                SCHEMA_KEY_ITEM_ID),
                                            ErrorCause.WRONG_DATA_TYPE,
                                            expected(DataType.TEXT)
                                        )
                                    )

                                else:

                                    if len(item[SCHEMA_KEY_ITEM_ID]) < 1:
                                        faults.append(
                                            fault(
                                                mix(SCHEMA_KEY_ACTION, REL_ACTION_TYPE_BUY, SCHEMA_KEY_ITEMS, 'Item',
                                                    SCHEMA_KEY_ITEM_ID),
                                                ErrorCause.INVALID_VALUE,
                                                None
                                            )
                                        )

                                    if not _is_valid_data(item[SCHEMA_KEY_ITEM_ID]):
                                        faults.append(
                                            fault(
                                                mix(SCHEMA_KEY_ACTION, REL_ACTION_TYPE_BUY, SCHEMA_KEY_ITEMS, 'Item',
                                                    SCHEMA_KEY_ITEM_ID),
                                                ErrorCause.INVALID_VALUE,
                                                None
                                            )
                                        )

                            if SCHEMA_KEY_QUANTITY not in item:
                                faults.append(
                                    fault(
                                        mix(SCHEMA_KEY_ACTION, REL_ACTION_TYPE_BUY, SCHEMA_KEY_ITEMS, 'Item',
                                            SCHEMA_KEY_QUANTITY),
                                        ErrorCause.MISSING_KEY,
                                        None
                                    )
                                )

                            else:

                                if type(item[SCHEMA_KEY_QUANTITY]) is not str:
                                    faults.append(
                                        fault(
                                            mix(SCHEMA_KEY_ACTION, REL_ACTION_TYPE_BUY, SCHEMA_KEY_ITEMS, 'Item',
                                                SCHEMA_KEY_QUANTITY),
                                            ErrorCause.WRONG_DATA_TYPE,
                                            expected(DataType.TEXT)
                                        )
                                    )

                                else:

                                    if len(item[SCHEMA_KEY_QUANTITY]) < 1:
                                        faults.append(
                                            fault(
                                                mix(SCHEMA_KEY_ACTION, REL_ACTION_TYPE_BUY, SCHEMA_KEY_ITEMS, 'Item',
                                                    SCHEMA_KEY_QUANTITY),
                                                ErrorCause.INVALID_VALUE,
                                                None
                                            )
                                        )

                            if SCHEMA_KEY_SUBTOTAL not in item:
                                faults.append(
                                    fault(
                                        mix(SCHEMA_KEY_ACTION, REL_ACTION_TYPE_BUY, SCHEMA_KEY_ITEMS, 'Item',
                                            SCHEMA_KEY_SUBTOTAL),
                                        ErrorCause.MISSING_KEY,
                                        None
                                    )
                                )

                            else:

                                if type(item[SCHEMA_KEY_SUBTOTAL]) is not str:
                                    faults.append(
                                        fault(
                                            mix(SCHEMA_KEY_ACTION, REL_ACTION_TYPE_BUY, SCHEMA_KEY_ITEMS, 'Item',
                                                SCHEMA_KEY_SUBTOTAL),
                                            ErrorCause.WRONG_DATA_TYPE,
                                            expected(DataType.TEXT)
                                        )
                                    )

                                else:

                                    if len(item[SCHEMA_KEY_SUBTOTAL]) < 1:
                                        faults.append(
                                            fault(
                                                mix(SCHEMA_KEY_ACTION, REL_ACTION_TYPE_BUY, SCHEMA_KEY_ITEMS, 'Item',
                                                    SCHEMA_KEY_SUBTOTAL),
                                                ErrorCause.INVALID_VALUE,
                                                None
                                            )
                                        )

                            if SCHEMA_KEY_LOCATION in item:

                                if type(item[SCHEMA_KEY_LOCATION]) is not dict:
                                    faults.append(
                                        fault(
                                            mix(SCHEMA_KEY_ACTION, REL_ACTION_TYPE_BUY, SCHEMA_KEY_ITEMS, 'Item',
                                                SCHEMA_KEY_LOCATION),
                                            ErrorCause.WRONG_DATA_TYPE,
                                            expected(DataType.MAP)
                                        )
                                    )

                                else:

                                    if SCHEMA_KEY_COUNTRY in item[SCHEMA_KEY_LOCATION]:
                                        if type(item[SCHEMA_KEY_LOCATION][SCHEMA_KEY_COUNTRY]) is not str:
                                            faults.append(
                                                fault(
                                                    mix(SCHEMA_KEY_ACTION, REL_ACTION_TYPE_BUY, SCHEMA_KEY_ITEMS,
                                                        'Item',
                                                        SCHEMA_KEY_LOCATION, SCHEMA_KEY_COUNTRY),
                                                    ErrorCause.WRONG_DATA_TYPE,
                                                    expected(DataType.TEXT)
                                                )
                                            )

                                        else:

                                            if len(item[SCHEMA_KEY_LOCATION][SCHEMA_KEY_COUNTRY]) < 1:
                                                faults.append(
                                                    fault(
                                                        mix(SCHEMA_KEY_ACTION, REL_ACTION_TYPE_BUY, SCHEMA_KEY_ITEMS,
                                                            'Item',
                                                            SCHEMA_KEY_LOCATION, SCHEMA_KEY_COUNTRY),
                                                        ErrorCause.INVALID_VALUE,
                                                        None
                                                    )
                                                )

                                    if SCHEMA_KEY_CITY in item[SCHEMA_KEY_LOCATION]:
                                        if type(item[SCHEMA_KEY_LOCATION][SCHEMA_KEY_CITY]) is not str:
                                            faults.append(
                                                fault(
                                                    mix(SCHEMA_KEY_ACTION, REL_ACTION_TYPE_BUY, SCHEMA_KEY_ITEMS,
                                                        'Item',
                                                        SCHEMA_KEY_LOCATION, SCHEMA_KEY_CITY),
                                                    ErrorCause.WRONG_DATA_TYPE,
                                                    expected(DataType.TEXT)
                                                )
                                            )

                                        else:

                                            if len(item[SCHEMA_KEY_LOCATION][SCHEMA_KEY_CITY]) < 1:
                                                faults.append(
                                                    fault(
                                                        mix(SCHEMA_KEY_ACTION, REL_ACTION_TYPE_BUY, SCHEMA_KEY_ITEMS,
                                                            'Item',
                                                            SCHEMA_KEY_LOCATION, SCHEMA_KEY_CITY),
                                                        ErrorCause.INVALID_VALUE,
                                                        None
                                                    )
                                                )

        elif data[SCHEMA_KEY_ACTION][SCHEMA_KEY_NAME].lower() in [REL_ACTION_TYPE_CHECK_DELETE_ITEM.lower(),
                                                                  REL_ACTION_TYPE_DELETE_ITEM.lower()]:

            if SCHEMA_KEY_ITEMS not in data:
                faults.append(
                    fault(
                        mix(SCHEMA_KEY_ACTION, REL_ACTION_TYPE_DELETE_ITEM, SCHEMA_KEY_ITEMS),
                        ErrorCause.MISSING_KEY,
                        None
                    )
                )

            else:

                if type(data[SCHEMA_KEY_ITEMS]) is not list:
                    faults.append(
                        fault(
                            mix(SCHEMA_KEY_ACTION, REL_ACTION_TYPE_DELETE_ITEM, SCHEMA_KEY_ITEMS),
                            ErrorCause.WRONG_DATA_TYPE,
                            expected(DataType.LIST)
                        )
                    )

                else:

                    for item in data[SCHEMA_KEY_ITEMS]:

                        if type(item) is not dict:
                            faults.append(
                                fault(
                                    mix(SCHEMA_KEY_ACTION, REL_ACTION_TYPE_DELETE_ITEM, SCHEMA_KEY_ITEMS, 'Item'),
                                    ErrorCause.WRONG_DATA_TYPE,
                                    expected(DataType.MAP)
                                )
                            )

                        else:

                            if SCHEMA_KEY_ITEM_ID not in item:
                                faults.append(
                                    fault(
                                        mix(SCHEMA_KEY_ACTION, REL_ACTION_TYPE_DELETE_ITEM, SCHEMA_KEY_ITEMS, 'Item',
                                            SCHEMA_KEY_ITEM_ID),
                                        ErrorCause.MISSING_KEY,
                                        None
                                    )
                                )

                            else:

                                if type(item[SCHEMA_KEY_ITEM_ID]) is not str:
                                    faults.append(
                                        fault(
                                            mix(SCHEMA_KEY_ACTION, REL_ACTION_TYPE_DELETE_ITEM, SCHEMA_KEY_ITEMS,
                                                'Item',
                                                SCHEMA_KEY_ITEM_ID),
                                            ErrorCause.WRONG_DATA_TYPE,
                                            expected(DataType.TEXT)
                                        )
                                    )

                                else:

                                    if len(item[SCHEMA_KEY_ITEM_ID]) < 1:
                                        faults.append(
                                            fault(
                                                mix(SCHEMA_KEY_ACTION, REL_ACTION_TYPE_DELETE_ITEM, SCHEMA_KEY_ITEMS,
                                                    'Item',
                                                    SCHEMA_KEY_ITEM_ID),
                                                ErrorCause.INVALID_VALUE,
                                                None
                                            )
                                        )

                                    if not _is_valid_data(item[SCHEMA_KEY_ITEM_ID]):
                                        faults.append(
                                            fault(
                                                mix(SCHEMA_KEY_ACTION, REL_ACTION_TYPE_DELETE_ITEM, SCHEMA_KEY_ITEMS,
                                                    'Item',
                                                    SCHEMA_KEY_ITEM_ID),
                                                ErrorCause.INVALID_VALUE,
                                                None
                                            )
                                        )

    return faults


def process_errors(log_errors):
    for error in log_errors:
        yield detect_schema_errors(error)


def parse_entities_from_data(data):
    dt = data["datetime"]
    tenant = data[SCHEMA_KEY_TENANT_ID]

    if is_valid_schema(data) is False:
        raise errors.BadSchemaError('Invalid schema')

    def parse_recommendation():

        if SCHEMA_KEY_RECOMMENDATION in data[SCHEMA_KEY_ACTION]:
            recommended = text.boolean(data[SCHEMA_KEY_ACTION][SCHEMA_KEY_RECOMMENDATION])
        else:
            recommended = False

        if SCHEMA_KEY_RECOMMENDATION_ORI in data[SCHEMA_KEY_ACTION]:
            parameters = data[SCHEMA_KEY_ACTION][SCHEMA_KEY_RECOMMENDATION_ORI]
        else:
            parameters = {}

        return dict(recommended=recommended, parameters=parameters)

    # session = None
    agent = None
    # user = None
    items = set()
    actions = []

    # Session
    session = Session(id=data[SCHEMA_KEY_SESSION_ID], tenant=tenant, timestamp=dt, fields={})

    # User
    if SCHEMA_KEY_USER in data:
        user = User(id=data[SCHEMA_KEY_USER][SCHEMA_KEY_USER_ID], tenant=tenant, timestamp=dt, fields={})
    else:
        user = User(id=data[SCHEMA_KEY_SESSION_ID], tenant=tenant, timestamp=dt, fields={})

    # Agent
    if SCHEMA_KEY_AGENT_ID in data:
        agent = Agent(id=data[SCHEMA_KEY_AGENT_ID], tenant=tenant, timestamp=dt, fields={})

    # Actions
    if data[SCHEMA_KEY_ACTION][SCHEMA_KEY_NAME].upper() == REL_ACTION_TYPE_VIEW:

        recommendation = parse_recommendation()

        # collect items
        for item_data in data[SCHEMA_KEY_ITEMS]:

            item = Item(id=item_data[SCHEMA_KEY_ITEM_ID], tenant=tenant, timestamp=dt, fields={})

            fields = {}
            for k, v in item_data.items():

                if k != SCHEMA_KEY_ITEM_ID and is_acceptable_data_type(v):
                    fields[k] = v
                else:

                    if k == SCHEMA_KEY_RETURN:
                        rt = {}

                        if type(item_data[k]) is dict:
                            for rkey, rval in item_data[k].items():

                                if is_acceptable_data_type(rval):
                                    rt[rkey] = rval

                        if rt:
                            fields[SCHEMA_KEY_RETURN] = rt

            item.fields = fields
            # TODO: Location

            items.add(item)

            action = Action(name=REL_ACTION_TYPE_VIEW, tenant=tenant, user=user.id,
                            agent=agent.id, session=session.id, item=item.id, timestamp=dt,
                            fields={}, recommendation=recommendation)

            actions.append(action)

    elif data[SCHEMA_KEY_ACTION][SCHEMA_KEY_NAME].upper() == REL_ACTION_TYPE_ADD_TO_CART:

        recommendation = parse_recommendation()

        # collect items
        for item_data in data[SCHEMA_KEY_ITEMS]:
            item = Item(id=item_data[SCHEMA_KEY_ITEM_ID], tenant=tenant, timestamp=dt, fields={})

            items.add(item)

            action = Action(name=REL_ACTION_TYPE_ADD_TO_CART, tenant=tenant, user=user.id,
                            agent=agent.id, session=session.id, item=item.id, timestamp=dt,
                            fields={"quantity": item_data[SCHEMA_KEY_QUANTITY]},
                            recommendation=recommendation)

            actions.append(action)

    elif data[SCHEMA_KEY_ACTION][SCHEMA_KEY_NAME].upper() == REL_ACTION_TYPE_BUY:

        recommendation = parse_recommendation()

        # collect items
        for item_data in data[SCHEMA_KEY_ITEMS]:
            item = Item(id=item_data[SCHEMA_KEY_ITEM_ID], tenant=tenant, timestamp=dt, fields={})

            items.add(item)

            action = Action(name=REL_ACTION_TYPE_BUY, tenant=tenant, user=user.id,
                            agent=agent.id, session=session.id, item=item.id, timestamp=dt,
                            fields={"quantity": item_data[SCHEMA_KEY_QUANTITY],
                                    "sub_total": item_data[SCHEMA_KEY_SUBTOTAL]},
                            recommendation=recommendation)

            actions.append(action)

    elif data[SCHEMA_KEY_ACTION][SCHEMA_KEY_NAME].upper() == REL_ACTION_TYPE_STARTED_CHECKOUT:

        recommendation = parse_recommendation()

        # collect items
        for item_data in data[SCHEMA_KEY_ITEMS]:
            item = Item(id=item_data[SCHEMA_KEY_ITEM_ID], tenant=tenant, timestamp=dt, fields={})

            items.add(item)

            action = Action(name=REL_ACTION_TYPE_STARTED_CHECKOUT, tenant=tenant, user=user.id,
                            agent=agent.id, session=session.id, item=item.id, timestamp=dt,
                            fields={}, recommendation=recommendation)

            actions.append(action)

    elif data[SCHEMA_KEY_ACTION][SCHEMA_KEY_NAME].upper() == REL_ACTION_TYPE_SEARCH:

        action = Action(name=REL_ACTION_TYPE_SEARCH, tenant=tenant, user=user.id,
                        agent=agent.id, session=session.id, item=None, timestamp=dt,
                        fields={"keywords": data[SCHEMA_KEY_ACTION][SCHEMA_KEY_KEYWORDS]},
                        recommendation={})

        actions.append(action)

    elif data[SCHEMA_KEY_ACTION][SCHEMA_KEY_NAME].upper() in [REL_ACTION_TYPE_DELETE_ITEM,
                                                              REL_ACTION_TYPE_CHECK_DELETE_ITEM]:

        act = data[SCHEMA_KEY_ACTION][SCHEMA_KEY_NAME].upper()

        for item_data in data[SCHEMA_KEY_ITEMS]:
            action = Action(name=act, tenant=tenant, user=None,
                            agent=agent.id, session=session.id, item=item_data[SCHEMA_KEY_ITEM_ID],
                            timestamp=dt, fields={}, recommendation={})

            actions.append(action)

    return session, agent, user, items, actions
