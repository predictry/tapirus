__author__ = 'guilherme'


#TODO: separate schema by action type
class ActionSchema:

    resource = "action"

    def __init__(self):
        pass

    @staticmethod
    def get_properties(identifiers=False):
        p = ["timestamp", "ipAddress", "sessionId", "guid", "agent", "quantum", "cartId"]

        if identifiers:
            p.extend(["id", "domain"])

        return p

    @staticmethod
    def get_label():
        return ActionSchema.resource.upper()