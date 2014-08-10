__author__ = 'guilherme'

from predictry.api.v1.errors import error
from predictry.query.generator.resources.user import UserQueryGenerator
from predictry.query.executor.queryexecutor import QueryExecutor
from predictry.models.resources.user import UserSchema
from predictry.utils.neo4j import node
from predictry.utils.helpers import text
from predictry.utils.helpers import payload


class UserHandler:

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
            return error('ResourceDoesNotExist', UserHandler.resource)
        else:
            response["data"] = {}
            response["data"]["users"] = output

        return payload.minify(response)

    @staticmethod
    def put(args):

        args = text.encode(args)

        qgen = UserQueryGenerator()
        qexec = QueryExecutor()

        if "id" not in args:
            return error('ResourceIdNotProvided', UserHandler.resource)

        exists, err = node.exists(labels=[args["domain"].upper(), UserSchema.get_label()],
                                  properties={"id": args["id"]})
        if err:
            return err
        if not exists:
            return error('ResourceDoesNotExist', UserHandler.resource)

        query, params = qgen.update(args)
        commit = True

        output, err = qexec.run(query, params, commit=commit)

        if err:
            return err

        response = {"data": None, "message": None, "error": None, "status": 200}

        if len(output) == 0:
            return error('ResourceDoesNotExist', UserHandler.resource)
        else:
            response["data"] = {}
            response["data"]["users"] = output

        return payload.minify(response)

    @staticmethod
    def post(args):

        args = text.encode(args)

        qgen = UserQueryGenerator()
        qexec = QueryExecutor()

        if "id" not in args:
            return error('ResourceIdNotProvided', UserHandler.resource)

        exists, err = node.exists(labels=[args["domain"].upper(), UserSchema.get_label()],
                                  properties={"id": args["id"]})
        if err:
            return err
        if exists:
            return error('ResourceAlreadyExists', UserHandler.resource)

        query, params = qgen.create(args)
        commit = True

        output, err = qexec.run(query, params, commit=commit)

        if err:
            return err

        response = {"data": None, "message": None, "error": None, "status": 200}

        if len(output) == 0:
            return error('Unknown', UserHandler.resource)
        response["data"] = {}
        response["data"]["users"] = output

        return payload.minify(response)

    @staticmethod
    def delete(args):

        args = text.encode(args)

        qgen = UserQueryGenerator()
        qexec = QueryExecutor()

        query, params = qgen.delete(args)
        commit = True

        output, err = qexec.run(query, params, commit=commit)

        if err:
            return err

        response = {"data": None, "message": None, "error": None, "status": 200}

        if len(output) == 0:
            return error('ResourceDoesNotExist', UserHandler.resource)
        response["data"] = {}
        response["data"]["users"] = output

        return payload.minify(response)