__author__ = 'guilherme'

from predictry.query.generator.resources import ItemQueryGenerator, UserQueryGenerator, ActionQueryGenerator
from predictry.query.executor.queryexecutor import QueryExecutor
from predictry.models.schema import ItemSchema, UserSchema
from predictry.api.server.errors import error
import predictry.utils.graph.node as Node


class ItemHandler:

    def __init__(self):
        self.resource = "item"

    def handle_request(self, args):

        args = Text.encode(args)

        args["organization"] = "redmart"

        qgen = ItemQueryGenerator()
        qexec = QueryExecutor()

        commit = False

        if args["method"] == "post":
            if "id" not in args:
                return error('ResourceIdNotProvided', self.resource)

            exists, err = Node.exists(labels=[args["organization"].upper(), ItemSchema.get_label()],
                                      properties={"id": args["id"]})
            if err:
                return err
            if exists:
                return error('ResourceAlreadyExists', self.resource)

            query, params = qgen.create(args)
            commit = True

        if args["method"] == "get":
            query, params = qgen.read(args)

        elif args["method"] == "put":
            query, params = qgen.update(args)
            commit = True

        elif args["method"] == "delete":
            query, params = qgen.delete(args)
            commit = True

        #read/delete/update/output is the same
        output, err = qexec.run(query, params, commit=commit)

        if err:
            return err

        response = self.generate_response(args, output)

        return Payload.minify(response)

    def generate_response(self, args, output):

        response = {"data": None, "message": None, "error": None, "status": 200}

        method = args["method"]

        if method == "post":
            if len(output) == 0:
                return error('Unknown')
            response["data"] = {}
            response["data"]["items"] = output

        elif method == "get":
            if len(output) == 0:
                #item not found
                return error('ResourceDoesNotExist', self.resource)
            else:
                response["data"] = {}
                response["data"]["items"] = output

        elif method == "put":
            if len(output) == 0:
                #item not found
                return error('ResourceDoesNotExist', self.resource)
            else:
                response["data"] = {}
                response["data"]["items"] = output

        elif method == "delete":
            if len(output) == 0:
                return error('ResourceDoesNotExist', self.resource)

        return response

class UserHandler:

    def __init__(self):
        self.resource = "user"

    def handle_request(self, args):

        args = Text.encode(args)

        args["organization"] = "redmart"

        qgen = UserQueryGenerator()
        qexec = QueryExecutor()
        commit = False

        if args["method"] == "post":
            if "id" not in args:
                return error('ResourceIdNotProvided', self.resource)

            exists, err = Node.exists(labels=[args["organization"].upper(), UserSchema.get_label()],
                                      properties={"id": args["id"]})

            if err:
                return err
            if exists:
                return error('ResourceAlreadyExists', self.resource)

            query, params = qgen.create(args)
            commit = True

        if args["method"] == "get":
            query, params = qgen.read(args)

        elif args["method"] == "delete":
            query, params = qgen.delete(args)
            commit = True

        #read/delete/update/output is the same
        output, err = qexec.run(query, params, commit)

        if err:
            return err

        response = self.generate_response(args, output)

        return Payload.minify(response)

    def generate_response(self, args, output):

        response = {"data": None, "message": None, "error": None, "status": 200}

        method = args["method"]

        if method == "post":
            if len(output) == 0:
                return error('Unknown', self.resource)
            response["data"] = {}
            response["data"]["users"] = output

        elif method == "get":
            if len(output) == 0:
                #item not found
                return error('ResourceDoesNotExist', self.resource)
            else:
                response["data"] = {}
                response["data"]["users"] = output

        elif method == "delete":
            if len(output) == 0:
                return error('ResourceDoesNotExist', self.resource)

        return response


class ActionHandler:

    def __init__(self):
        self.resource = "action"

    def handle_request(self, args):

        args = Text.encode(args)

        args["organization"] = "redmart"
        flags = {"item": {}, "user": {}}

        qgen = ActionQueryGenerator()
        qexec = QueryExecutor()

        commit = False

        if args["method"] == "post":
            if "id" not in args:
                return error('ResourceIdNotProvided', self.resource)

            for p in ["type", "userId", "itemId"]:
                if p not in args:
                    return error('MissingParameter', self.resource, p)

            exists, err = Node.exists(labels=[args["organization"].upper(), ItemSchema.get_label()],
                                      properties={"id": args["itemId"]})
            if err:
                return err
            if exists:
                flags["item"]["created"] = False
            else:
                flags["item"]["created"] = True

            exists, err = Node.exists(labels=[args["organization"].upper(), UserSchema.get_label()],
                                      properties={"id": args["userId"]})
            if err:
                return err
            if exists:
                flags["user"]["created"] = False
            else:
                flags["user"]["created"] = True

            query, params = qgen.create(args)
            commit = True

        if args["method"] == "get":
            query, params = qgen.read(args)

        elif args["method"] == "put":
            if "id" not in args:
                return error('ResourceIdNotProvided', self.resource)
            query, params = qgen.update(args)
            commit = True

        elif args["method"] == "delete":
            if "id" not in args:
                return error('ResourceIdNotProvided', self.resource)
            query, params = qgen.delete(args)
            commit = True

        output, err = qexec.run(query, params, commit)

        if err:
            return err

        response = self.generate_response(args, output)

        if response["status"] == 200:
            response["data"]["flags"] = flags

        return Payload.minify(response)

    def generate_response(self, args, output):

        response = {"data": None, "message": None, "error": None, "status": 200}

        method = args["method"]

        if method == "post":
            if len(output) == 0:
                return error('Unknown')
            response["data"] = {}
            response["data"]["actions"] = output

        elif method == "get":
            if len(output) == 0:
                #item not found
                return error('ResourceDoesNotExist', self.resource)
            else:
                response["data"] = {}
                response["data"]["items"] = output

        elif method == "put":
            if len(output) == 0:
                #item not found
                return error('ResourceDoesNotExist', self.resource)
            else:
                response["data"] = {}
                response["data"]["actions"] = output

        elif method == "delete":
            if len(output) == 0:
                return error('ResourceDoesNotExist', self.resource)
            response["data"] = {}
            response["data"]["actions"] = output

        return response


class CategoryHandler:

    def __init__(self):
        pass

    def handle_request(self, args):
        pass

    def generate_response(self, args, output):
        pass