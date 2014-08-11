__author__ = 'guilherme'

#new startDate, endDate, subcategory, location
class ItemSchema:

    resource = "item"

    def __init__(self):
        pass

    @staticmethod
    def get_properties(identifiers=False):
        p = ["name", "brand", "model", "tags", "description", "price", "category", "subcategory",
             "dateAdded", "itemURL", "imageURL", "startDate", "endDate", "locations"]

        if identifiers:
            p.extend(["id", "domain"])

        return p

    @staticmethod
    def get_label():
        return ItemSchema.resource.upper()