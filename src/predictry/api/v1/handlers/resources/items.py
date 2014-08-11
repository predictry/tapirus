__author__ = 'guilherme'

from predictry.api.v1.errors import error
from predictry.engine.graph.query.generator.resources.item import ItemQueryGenerator
from predictry.engine.graph.query.executor.executor import QueryExecutor
from predictry.engine.models.resources.item import ItemSchema
from predictry.utils.neo4j import node
from predictry.utils.helpers import text
from predictry.utils.helpers import payload


class ItemHandler:

    def __init__(self):
        pass

    resource = "item"

    @staticmethod
    def get(args):

        args = text.encode(args)

        qgen = ItemQueryGenerator()
        qexec = QueryExecutor()

        query, params = qgen.read(args)
        commit = False

        output, err = qexec.run(query, params, commit=commit)

        if err:
            return err

        response = {"data": None, "message": None, "error": None, "status": 200}

        if len(output) == 0:
            return error('ResourceDoesNotExist', ItemHandler.resource)
        else:
            response["data"] = {}
            response["data"]["items"] = output

        return payload.minify(response)

    @staticmethod
    def put(args):

        args = text.encode(args)

        qgen = ItemQueryGenerator()
        qexec = QueryExecutor()

        query, params = qgen.update(args)
        commit = True

        output, err = qexec.run(query, params, commit=commit)

        if err:
            return err

        response = {"data": None, "message": None, "error": None, "status": 200}

        if len(output) == 0:
            #item not found
            return error('ResourceDoesNotExist', ItemHandler.resource)
        else:
            response["data"] = {}
            response["data"]["items"] = output

        return payload.minify(response)

    @staticmethod
    def post(args):

        args = text.encode(args)

        qgen = ItemQueryGenerator()
        qexec = QueryExecutor()

        if "id" not in args:
            return error('ResourceIdNotProvided', ItemHandler.resource)

        exists, err = node.exists(labels=[args["domain"].upper(), ItemSchema.get_label()],
                                  properties={"id": args["id"]})
        if err:
            return err
        if exists:
            return error('ResourceAlreadyExists', ItemHandler.resource)

        query, params = qgen.create(args)
        commit = True

        output, err = qexec.run(query, params, commit=commit)

        if err:
            return err

        response = {"data": None, "message": None, "error": None, "status": 200}

        if len(output) == 0:
            return error('Unknown')

        response["data"] = {}
        response["data"]["items"] = output

        return payload.minify(response)

    @staticmethod
    def delete(args):

        args = text.encode(args)

        qgen = ItemQueryGenerator()
        qexec = QueryExecutor()

        query, params = qgen.delete(args)
        commit = True

        output, err = qexec.run(query, params, commit=commit)

        if err:
            return err

        if len(output) == 0:
            return error('ResourceDoesNotExist', ItemHandler.resource)

        response = {"data": None, "message": None, "error": None, "status": 200}
        response["data"] = {}
        response["data"]["items"] = output

        return payload.minify(response)