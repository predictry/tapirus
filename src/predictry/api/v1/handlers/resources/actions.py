__author__ = 'guilherme'

from predictry.api.v1.errors import error
from predictry.engine.graph.query.generator.resources.action import ActionQueryGenerator
from predictry.engine.graph.query.executor.executor import QueryExecutor
from predictry.engine.models.resources.user import UserSchema
from predictry.engine.models.resources.item import ItemSchema
from predictry.utils.neo4j import node
from predictry.utils.helpers import text
from predictry.utils.helpers import payload


class ActionHandler:

    def __init__(self):
        pass

    resource = "action"

    type = staticmethod(lambda x: {
        "VIEWED": "view",
        "BOUGHT": "buy",
        "RATED": "rate",
        "ADDED_TO_CART": "addToCart"
    }[x])

    @staticmethod
    def get(args):

        args = text.encode(args)

        qgen = ActionQueryGenerator()
        qexec = QueryExecutor()

        query, params = qgen.read(args)
        commit = False

        output, err = qexec.run(query, params, commit=commit)

        if err:
            return err

        response = {"data": None, "message": None, "error": None, "status": 200}

        if len(output) == 0:
            return error('ResourceDoesNotExist', ActionHandler.resource)
        else:
            response["data"] = {}

            for action in output:
                if "type" in action:
                    action['type'] = ActionHandler.type(action['type'])

            response["data"]["actions"] = output

        return payload.minify(response)

    @staticmethod
    def put(args):

        args = text.encode(args)

        qgen = ActionQueryGenerator()
        qexec = QueryExecutor()

        if "id" not in args:
            return error('ResourceIdNotProvided', ActionHandler.resource)

        query, params = qgen.update(args)
        commit = True

        output, err = qexec.run(query, params, commit=commit)

        if err:
            return err

        response = {"data": None, "message": None, "error": None, "status": 200}

        if len(output) == 0:
            return error('ResourceDoesNotExist', ActionHandler.resource)
        else:
            response["data"] = {}

            for action in output:
                if "type" in action:
                    action['type'] = ActionHandler.type(action['type'])
            response["data"]["actions"] = output

        return payload.minify(response)

    @staticmethod
    def post(args):

        args = text.encode(args)

        qgen = ActionQueryGenerator()
        qexec = QueryExecutor()

        if "id" not in args:
            return error('ResourceIdNotProvided', ActionHandler.resource)

        for p in ["type", "userId", "itemId"]:
            if p not in args:
                return error('MissingParameter', ActionHandler.resource, p)

        exists, err = node.exists(labels=[args["domain"].upper(), ItemSchema.get_label()],
                                  properties={"id": args["itemId"]})
        if err:
            return err
        if not exists:
            return error('ResourceDoesNotExist', object='item')

        exists, err = node.exists(labels=[args["domain"].upper(), UserSchema.get_label()],
                                  properties={"id": args["userId"]})
        if err:
            return err
        if not exists:
            return error('ResourceDoesNotExist', object='user')

        query, params = qgen.create(args)
        commit = True

        output, err = qexec.run(query, params, commit=commit)

        if err:
            return err

        response = {"data": None, "message": None, "error": None, "status": 200}

        if len(output) == 0:
            return error('Unknown')
        response["data"] = {}

        for action in output:
            if "type" in action:
                action['type'] = ActionHandler.type(action['type'])

        response["data"]["actions"] = output

        return payload.minify(response)

    @staticmethod
    def delete(args):

        args = text.encode(args)

        qgen = ActionQueryGenerator()
        qexec = QueryExecutor()

        if "id" not in args:
            return error('ResourceIdNotProvided', ActionHandler.resource)
        query, params = qgen.delete(args)
        commit = True

        output, err = qexec.run(query, params, commit=commit)

        if err:
            return err

        response = {"data": None, "message": None, "error": None, "status": 200}

        if len(output) == 0:
            return error('ResourceDoesNotExist', ActionHandler.resource)
        response["data"] = {}

        for action in output:
            if "type" in action:
                action['type'] = ActionHandler.type(action['type'])
        response["data"]["actions"] = output

        return payload.minify(response)