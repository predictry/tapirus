__author__ = 'guilherme'

from predictry.api.v1.errors import error
from predictry.engine.graph.query.generator.resources.user import UserQueryGenerator
from predictry.engine.graph.query.executor.executor import QueryExecutor
from predictry.engine.models.resources.user import UserSchema
from predictry.utils.neo4j import cypher
from predictry.utils.helpers import text
from predictry.utils.helpers import payload
from predictry.utils.log.logger import Logger


class UserHandler():

    def __init__(self):
        pass

    resource = "user"

    @staticmethod
    def get(args):

        args = text.encode(args)

        qgen = UserQueryGenerator()
        qexec = QueryExecutor()

        query, params = qgen.read(args)
        commit = False

        output, err = qexec.run(query, params, commit=commit)

        if err:
            return err

        response = {"data": None, "message": None, "error": None, "status": 200}

        if len(output) == 0:
            err = error('ResourceDoesNotExist', UserHandler.resource)
            Logger.warning(err)
            return err
        else:
            response["data"] = {}
            response["data"]["users"] = output

        return payload.minify(response)

    @staticmethod
    def put(args, data):

        args = text.encode(args)
        data = text.encode(data)

        if "id" not in args:
            err = error('ResourceIdNotProvided', UserHandler.resource)
            Logger.warning(err)
            return err

        qgen = UserQueryGenerator()
        qexec = QueryExecutor()

        exists, err = cypher.node_exists(labels=[args["domain"], UserSchema.get_label()],
                                  properties={"id": args["id"]})
        if err:
            return err
        if not exists:
            err = error('ResourceDoesNotExist', UserHandler.resource)
            Logger.warning(err)
            return err

        query, params = qgen.update(args, data)
        commit = True

        output, err = qexec.run(query, params, commit=commit)

        if err:
            return err

        response = {"data": None, "message": None, "error": None, "status": 200}

        if len(output) == 0:
            err = error('ResourceDoesNotExist', UserHandler.resource)
            Logger.warning(err)
            return err
        else:
            response["data"] = {}
            response["data"]["users"] = output

        return payload.minify(response)

    @staticmethod
    def post(args, data):

        args = text.encode(args)
        data = text.encode(data)

        if "id" not in data:
            err = error('ResourceIdNotProvided', UserHandler.resource)
            Logger.warning(err)
            return err

        qgen = UserQueryGenerator()
        qexec = QueryExecutor()

        exists, err = cypher.node_exists(labels=[args["domain"], UserSchema.get_label()],
                                  properties={"id": data["id"]})
        if err:
            return err
        if exists:
            err = error('ResourceAlreadyExists', UserHandler.resource)
            Logger.warning(err)
            return err

        query, params = qgen.create(args, data)
        commit = True

        output, err = qexec.run(query, params, commit=commit)

        if err:
            return err

        response = {"data": None, "message": None, "error": None, "status": 200}

        if len(output) == 0:
            err = error('Unknown', UserHandler.resource)
            Logger.warning(err)
            return err

        response["data"] = {}
        response["data"]["users"] = output

        return payload.minify(response)

    @staticmethod
    def delete(args):

        args = text.encode(args)

        if "id" not in args:
            err = error('ResourceIdNotProvided', UserHandler.resource)
            Logger.warning(err)
            return err

        qgen = UserQueryGenerator()
        qexec = QueryExecutor()

        query, params = qgen.delete(args)
        commit = True

        output, err = qexec.run(query, params, commit=commit)

        if err:
            return err

        response = {"data": None, "message": None, "error": None, "status": 200}

        if len(output) == 0:
            err = error('ResourceDoesNotExist', UserHandler.resource)
            Logger.warning(err)
            return err

        response["data"] = {}
        response["data"]["users"] = output

        return payload.minify(response)