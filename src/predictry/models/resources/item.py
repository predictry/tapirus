__author__ = 'guilherme'


class ItemSchema:

    resource = "item"

    def __init__(self):
        pass

    @staticmethod
    def get_properties(identifiers=False):
        p = ["name", "brand", "model", "tags", "description", "price", "category", "dateAdded", "itemURL", "imageURL"]

        if identifiers:
            p.extend(["id", "domain"])

        return p

    @staticmethod
    def get_label():
        return ItemSchema.resource.upper()