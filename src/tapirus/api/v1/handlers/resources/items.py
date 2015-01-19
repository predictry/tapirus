from tapirus.utils import text

__author__ = 'guilherme'

from tapirus.api.v1.errors import error
from tapirus.core.db.i2.query.generator.resources.item import ItemQueryGenerator
from tapirus.core.db.i2.query.executor.executor import QueryExecutor
from tapirus.models.item import ItemSchema
from tapirus.utils.neo4j import cypher
from tapirus.utils.helpers import payload
from tapirus.utils.logger import Logger


class ItemHandler():

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
            err = error('ResourceDoesNotExist', ItemHandler.resource)
            Logger.warning(err)
            return err
        else:
            response["data"] = {}
            response["data"]["items"] = output

        return payload.minify(response)

    @staticmethod
    def put(args, data):

        args = text.encode(args)
        data = text.encode(data)

        if "id" not in args:
            err = error('ResourceIdNotProvided', ItemHandler.resource)
            Logger.warning(err)
            return err

        qgen = ItemQueryGenerator()
        qexec = QueryExecutor()

        exists, err = cypher.node_exists(labels=[args["domain"], ItemSchema.get_label()],
                                  properties={"id": args["id"]})
        if err:
            return err
        if not exists:
            err = error('ResourceDoesNotExist', ItemHandler.resource)
            Logger.warning(err)
            return err

        query, params = qgen.update(args, data)
        commit = True

        output, err = qexec.run(query, params, commit=commit)

        if err:
            return err

        response = {"data": None, "message": None, "error": None, "status": 200}

        if len(output) == 0:
            err = error('ResourceDoesNotExist', ItemHandler.resource)
            Logger.warning(err)
            return err
        else:
            response["data"] = {}
            response["data"]["items"] = output

        return payload.minify(response)

    @staticmethod
    def post(args, data):

        args = text.encode(args)
        data = text.encode(data)

        if "id" not in data:
            err = error('ResourceIdNotProvided', ItemHandler.resource)
            Logger.warning(err)
            return err

        qgen = ItemQueryGenerator()
        qexec = QueryExecutor()

        exists, err = cypher.node_exists(labels=[args["domain"], ItemSchema.get_label()],
                                  properties={"id": data["id"]})
        if err:
            return err
        if exists:
            err = error('ResourceAlreadyExists', ItemHandler.resource)
            Logger.warning(err)
            return err

        query, params = qgen.create(args, data)
        commit = True

        output, err = qexec.run(query, params, commit=commit)

        if err:
            return err

        response = {"data": None, "message": None, "error": None, "status": 200}

        if len(output) == 0:
            err = error('Unknown')
            Logger.warning(err)
            return err

        response["data"] = {}
        response["data"]["items"] = output

        return payload.minify(response)

    @staticmethod
    def delete(args):

        args = text.encode(args)

        if "id" not in args:
            err = error('ResourceIdNotProvided', ItemHandler.resource)
            Logger.warning(err)
            return err

        qgen = ItemQueryGenerator()
        qexec = QueryExecutor()

        query, params = qgen.delete(args)
        commit = True

        output, err = qexec.run(query, params, commit=commit)

        if err:
            return err

        if len(output) == 0:
            err = error('ResourceDoesNotExist', ItemHandler.resource)
            Logger.warning(err)
            return err

        response = {"data": None, "message": None, "error": None, "status": 200}
        response["data"] = {}
        response["data"]["items"] = output

        return payload.minify(response)