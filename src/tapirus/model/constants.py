__author__ = 'guilherme'


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


REL_SESSION_TO_AGENT = "FROM"
REL_SESSION_TO_USER = "BY"
REL_ITEM_LOCATION = "AVAILABLE_AT"

LABEL_SESSION = "Session"
LABEL_AGENT = "Agent"
LABEL_USER = "User"
LABEL_ITEM = "Item"
LABEL_SEARCH = "Search"
LABEL_LOCATION = "Location"
LABEL_LOCATION_COUNTRY = "Country"
LABEL_LOCATION_CITY = "City"

REL_ACTION_TYPE_SEARCH = "SEARCH"
REL_ACTION_TYPE_VIEW = "VIEW"
REL_ACTION_TYPE_ADD_TO_CART = "ADD_TO_CART"
REL_ACTION_TYPE_BUY = "BUY"
REL_ACTION_TYPE_STARTED_CHECKOUT = "STARTED_CHECKOUT"
REL_ACTION_TYPE_STARTED_PAYMENT = "STARTED_PAYMENT"
REL_ACTION_TYPE_CHECK_DELETE_ITEM = "CHECK_DELETE_ITEM"
