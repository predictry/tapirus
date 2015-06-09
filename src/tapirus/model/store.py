

from tapirus.model.constants import *


# TODO: Model events. Parse logs into entities and events. Feed these to data importers

class Session(object):

    def __init__(self, id, tenant, timestamp, fields):

        self.id = id
        self.tenant = tenant
        self.timestamp = timestamp
        self.fields = fields

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

    def __init__(self, id, tenant, timestamp, fields):

        self.id = id
        self.tenant = tenant
        self.timestamp = timestamp
        self.fields = fields

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

    def __init__(self, id, tenant, timestamp, fields):

        self.id = id
        self.tenant = tenant
        self.timestamp = timestamp
        self.fields = fields

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

    def __init__(self, id, tenant, timestamp, fields):

        self.id = id
        self.tenant = tenant
        self.timestamp = timestamp
        self.fields = fields

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

        return "Item(id={0}, tenant={1}, timestamp={2})".format(
            self.id, self.tenant, self.timestamp
        )

    @property
    def properties(self):

        return self.__dict__


class Action(object):

    def __init__(self, name, tenant, user, agent, session, item, timestamp, fields):

        self.name = name
        self.tenant = tenant
        self.user = user
        self.agent = agent
        self.session = session
        self.item = item
        self.timestamp = timestamp
        self.fields = fields

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

    def __init__(self, name, api_key, fields):
        self.name = name
        self.api_key = api_key
        self.fields = fields

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

    # TODO: log any missing data

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

            if SCHEMA_KEY_SUBTOTAL not in item:
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

    elif data[SCHEMA_KEY_ACTION][SCHEMA_KEY_NAME].lower() == REL_ACTION_TYPE_CHECK_DELETE_ITEM.lower():

        if SCHEMA_KEY_ITEM_ID not in data:
            return False
        if type(data[SCHEMA_KEY_ITEM_ID]) is not str:
            return False
        if len(data[SCHEMA_KEY_ITEM_ID]) < 1:
            return False
        if not _is_valid_data(data[SCHEMA_KEY_ITEM_ID]):
            return False

    elif data[SCHEMA_KEY_ACTION][SCHEMA_KEY_NAME].lower() == REL_ACTION_TYPE_DELETE_ITEM.lower():

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


def parse_entities_from_data(data):

    dt = data["datetime"]
    tenant = data[SCHEMA_KEY_TENANT_ID]

    if is_valid_schema(data) is False:
        return []

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

        # collect items
        for item_data in data[SCHEMA_KEY_ITEMS]:

            item = Item(id=item_data[SCHEMA_KEY_ITEM_ID], tenant=tenant, timestamp=dt, fields={})

            fields = {}
            for k, v in item_data.items():

                if k != SCHEMA_KEY_ITEM_ID and is_acceptable_data_type(v):
                    fields[k] = v

            item.fields = fields
            # TODO: Location

            items.add(item)

            action = Action(name=REL_ACTION_TYPE_VIEW, tenant=tenant, user=user.id,
                            agent=agent.id, session=session.id, item=item.id, timestamp=dt,
                            fields={})

            actions.append(action)

    elif data[SCHEMA_KEY_ACTION][SCHEMA_KEY_NAME].upper() == REL_ACTION_TYPE_ADD_TO_CART:

        # collect items
        for item_data in data[SCHEMA_KEY_ITEMS]:

            item = Item(id=item_data[SCHEMA_KEY_ITEM_ID], tenant=tenant, timestamp=dt, fields={})

            items.add(item)

            action = Action(name=REL_ACTION_TYPE_ADD_TO_CART, tenant=tenant, user=user.id,
                            agent=agent.id, session=session.id, item=item.id, timestamp=dt,
                            fields={"qty": item_data[SCHEMA_KEY_QUANTITY]})

            actions.append(action)

    elif data[SCHEMA_KEY_ACTION][SCHEMA_KEY_NAME].upper() == REL_ACTION_TYPE_BUY:

        # collect items
        for item_data in data[SCHEMA_KEY_ITEMS]:

            item = Item(id=item_data[SCHEMA_KEY_ITEM_ID], tenant=tenant, timestamp=dt, fields={})

            items.add(item)

            action = Action(name=REL_ACTION_TYPE_BUY, tenant=tenant, user=user.id,
                            agent=agent.id, session=session.id, item=item.id, timestamp=dt,
                            fields={"qty": item_data[SCHEMA_KEY_QUANTITY],
                                    "sub_total": item_data[SCHEMA_KEY_SUBTOTAL]})

            actions.append(action)

    elif data[SCHEMA_KEY_ACTION][SCHEMA_KEY_NAME].upper() == REL_ACTION_TYPE_STARTED_CHECKOUT:

        # collect items
        for item_data in data[SCHEMA_KEY_ITEMS]:

            item = Item(id=item_data[SCHEMA_KEY_ITEM_ID], tenant=tenant, timestamp=dt, fields={})

            items.add(item)

            action = Action(name=REL_ACTION_TYPE_STARTED_CHECKOUT, tenant=tenant, user=user.id,
                            agent=agent.id, session=session.id, item=item.id, timestamp=dt,
                            fields={})

            actions.append(action)

    elif data[SCHEMA_KEY_ACTION][SCHEMA_KEY_NAME].upper() == REL_ACTION_TYPE_SEARCH:

        action = Action(name=REL_ACTION_TYPE_SEARCH, tenant=tenant, user=user.id,
                        agent=agent.id, session=session.id, item=None, timestamp=dt,
                        fields={"keywords": data[SCHEMA_KEY_ACTION][SCHEMA_KEY_KEYWORDS]})

        actions.append(action)

    elif data[SCHEMA_KEY_ACTION][SCHEMA_KEY_NAME].upper() == REL_ACTION_TYPE_CHECK_DELETE_ITEM:

        action = Action(name=REL_ACTION_TYPE_CHECK_DELETE_ITEM, tenant=tenant, user=None,
                        agent=agent.id, session=session.id, item=data[SCHEMA_KEY_ITEM_ID],
                        timestamp=dt, fields={})

        actions.append(action)

    elif data[SCHEMA_KEY_ACTION][SCHEMA_KEY_NAME].upper() == REL_ACTION_TYPE_DELETE_ITEM:

        for item_data in data[SCHEMA_KEY_ITEMS]:

            action = Action(name=REL_ACTION_TYPE_DELETE_ITEM, tenant=tenant, user=None,
                            agent=agent.id, session=session.id, item=item_data[SCHEMA_KEY_ITEM_ID],
                            timestamp=dt, fields={})

            actions.append(action)

    return session, agent, user, items, actions
