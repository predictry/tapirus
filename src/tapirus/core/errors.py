__author__ = 'guilherme'


class InvalidRelationshipTypeError(Exception):
    """
    Relationship type is not valid in Neo4j
    """
    pass


class InvalidLabelError(Exception):
    """
    Label is not a valid Neo4j label
    """
    pass