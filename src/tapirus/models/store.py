__author__ = 'guilherme'


REL_SESSION_TO_AGENT = "FROM"
REL_SESSION_TO_USER = "BY"

LABEL_SESSION = "Session"
LABEL_AGENT = "Agent"
LABEL_USER = "User"
LABEL_ITEM = "Item"

REL_ACTION_TYPE_SEARCH = "SEARCH"
REL_ACTION_TYPE_VIEW = "VIEW"
REL_ACTION_TYPE_ADD_TO_CART = "ADD_TO_CART"
REL_ACTION_TYPE_BUY = "BUY"
REL_ACTION_TYPE_STARTED_CHECKOUT = "STARTED_CHECKOUT"
REL_ACTION_TYPE_STARTED_PAYMENT = "STARTED_PAYMENT"


class Session:

    def __init__(self, id, domain, uuid):
        self.id = id
        self.domain = domain
        self.uuid = uuid


class User:

    def __init__(self, id, domain, uuid):
        self.id = id
        self.domain = domain
        self.uuid = uuid


class Agent:

    def __init__(self, id, domain, uuid):
        self.id = id
        self.domain = domain
        self.uuid = uuid


class Item:

    def __init__(self, id, domain, uuid):
        self.id = id
        self.domain
        self.uuid = uuid


