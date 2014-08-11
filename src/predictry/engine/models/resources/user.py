__author__ = 'guilherme'


class UserSchema:

    resource = "user"

    def __init__(self):
        pass

    @staticmethod
    def get_properties(identifiers=False):

        p = ['email']

        if identifiers:
            p.extend(["id", "domain"])

        return p

    @staticmethod
    def get_label():
        return UserSchema.resource.upper()
