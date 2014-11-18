__author__ = 'guilherme'


#TODO: separate schema by action type
class ActionSchema:

    resource = "action"

    def __init__(self):
        pass

    @staticmethod
    def get_properties(identifiers=False):
        p = ["timestamp", "ip_address", "session_id", "guid", "agent", "quantum", "cart_id"]

        if identifiers:
            p.extend(["id", "domain"])

        return p

    @staticmethod
    def get_label():
        return ActionSchema.resource.upper()