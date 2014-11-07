__author__ = 'guilherme'

from predictry.api.v1.errors import error
from predictry.engine.graph.query.generator.resources.action import ActionQueryGenerator
from predictry.engine.graph.query.executor.executor import QueryExecutor
from predictry.engine.models.resources.item import ItemSchema
from predictry.engine.models.resources.user import UserSchema
from predictry.utils.neo4j import cypher
from predictry.utils.helpers import text
from predictry.utils.helpers import payload
from predictry.utils.log.logger import Logger


class ActionHandler():

    def __init__(self):
        pass

    resource = "action"

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
            err = error('ResourceDoesNotExist', ActionHandler.resource)
            Logger.warning(err)
            return err
        else:
            response["data"] = {}

            response["data"]["actions"] = output

        return payload.minify(response)

    @staticmethod
    def put(args, data):

        args = text.encode(args)
        data = text.encode(data)

        if "id" not in args:
            err = error('ResourceIdNotProvided', ActionHandler.resource)
            Logger.warning(err)
            return err

        qgen = ActionQueryGenerator()
        qexec = QueryExecutor()

        query, params = qgen.update(args, data)
        commit = True

        output, err = qexec.run(query, params, commit=commit)
        if err:
            return err

        response = {"data": None, "message": None, "error": None, "status": 200}

        if len(output) == 0:
            err = error('ResourceDoesNotExist', ActionHandler.resource)
            Logger.warning(err)
            return err
        else:
            response["data"] = {}

            response["data"]["actions"] = output

        return payload.minify(response)

    @staticmethod
    def delete(args):

        args = text.encode(args)

        if "id" not in args:
            err = error('ResourceIdNotProvided', ActionHandler.resource)
            Logger.warning(err)
            return err

        qgen = ActionQueryGenerator()
        qexec = QueryExecutor()

        query, params = qgen.delete(args)
        commit = True

        output, err = qexec.run(query, params, commit=commit)

        if err:
            return err

        response = {"data": None, "message": None, "error": None, "status": 200}

        if len(output) == 0:
            err = error('ResourceDoesNotExist', ActionHandler.resource)
            Logger.warning(err)
            return err

        response["data"] = {}

        response["data"]["actions"] = output

        return payload.minify(response)

    @staticmethod
    def post(args, data):

        args = text.encode(args)

        if "id" not in data:
            err = error('ResourceIdNotProvided', ActionHandler.resource)
            Logger.warning(err)
            return err

        qgen = ActionQueryGenerator()
        qexec = QueryExecutor()

        for p in ["type", "browser_id", "session_id", "item_id"]:
            if p not in data:
                err = error('MissingParameter', ActionHandler.resource, p)
                Logger.warning(err)
                return err

        #only the item must exist
        #todo: don't check for either user or item

        exists, err = cypher.node_exists(labels=[args["domain"], ItemSchema.get_label()],
                                         properties={"id": data["item_id"]})
        if err:
            return err
        if not exists:
            err = error('ResourceDoesNotExist', e='item')
            Logger.warning(err)
            return err

        #if user_id is given

        if "user_id" in data:
            exists, err = cypher.node_exists(labels=[args["domain"], UserSchema.get_label()],
                                             properties={"id": data["user_id"]})
            if err:
                return err
            if not exists:
                err = error('ResourceDoesNotExist', e='user')
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

        response["data"]["actions"] = output

        return payload.minify(response)