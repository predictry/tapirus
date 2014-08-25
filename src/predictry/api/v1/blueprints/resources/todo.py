__author__ = 'guilherme'

from predictry.api.v1.blueprints.blueprint import BlueprintBase
from predictry.api.v1.request import validate_request
from flask_restful import reqparse, request


class TodoAPI(BlueprintBase):

    def __init__(self):
        super(TodoAPI, self).__init__()

    def get(self, id):

        args = dict(request.values.iteritems())

        err = validate_request(args)

        if err:
            return err, err['status']

        return {"args": args, "type": str(type(args))}, 200

    def put(self, id):

        args = request.values
        data = dict(request.json)

        return {"args": args, "data": data}, 200

    def delete(self, id):

        args = request.values

        return {"args": args}, 200


class TodoListAPI(BlueprintBase):

    def __init__(self):
        super(TodoListAPI, self).__init__()

    def get(self):

        args = request.values

        return {"args": args}, 200

    def post(self):

        args = request.values

        data = dict(request.json)

        return {"args": args, "data": data}, 200