__author__ = 'guilherme'

#TODO: delete organization from identifiers list
class ItemSchema:

    resource = "item"

    def __init__(self):
        pass

    @staticmethod
    def get_properties(identifiers=False):
        p = ["name", "brand", "model", "tags", "description", "price", "category", "dateAdded", "itemURL", "imageURL"]

        if identifiers:
            p.extend(["id", "organization"])

        return p

    @staticmethod
    def get_label():
        return ItemSchema.resource.upper()


class UserSchema:

    resource = "user"

    def __init__(self):
        pass

    @staticmethod
    def get_properties(identifiers=False):
        p = []

        if identifiers:
            p.extend(["id", "organization"])

        return p

    @staticmethod
    def get_label():
        return UserSchema.resource.upper()


class ActionSchema:

    resource = "action"

    def __init__(self):
        pass

    @staticmethod
    def get_properties(identifiers=False):
        p = ["timestamp", "ipAddress", "sessionId", "guid", "agent", "quantum"]

        if identifiers:
            p.extend(["id", "organization"])

        return p

    @staticmethod
    def get_label():
        return ActionSchema.resource.upper()