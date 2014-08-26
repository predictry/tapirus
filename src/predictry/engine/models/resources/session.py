__author__ = 'guilherme'


class SessionSchema:

    resource = "session"

    def __init__(self):
        pass

    @staticmethod
    def get_properties(identifiers=False):

        p = {}

        if identifiers:
            p.extend(["id", "domain"])

        return p

    @staticmethod
    def get_label():
        return SessionSchema.resource
