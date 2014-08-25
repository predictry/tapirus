__author__ = 'guilherme'

from predictry.api.v1.handlers.resources.users import UserHandler
from predictry.api.v1.blueprints.blueprint import BlueprintBase
from predictry.api.v1.request import validate_request
from flask_restful import reqparse, request


class UserAPI(BlueprintBase):

    def __init__(self):
        super(UserAPI, self).__init__()

    def get(self, id):

        args = dict(request.values.iteritems())

        err = validate_request(args)

        if err:
            return err, err['status']

        args["id"] = id

        response = UserHandler.get(args)

        return response, response['status']

    def put(self, id):

        args = dict(request.values.iteritems())

        err = validate_request(args)

        if err:
            return err, err['status']

        data = request.json

        args["id"] = id
        #args.update(data)

        response = UserHandler.put(args, data)

        return response, response['status']

    def delete(self, id):

        args = dict(request.values.iteritems())

        err = validate_request(args)

        if err:
            return err, err['status']

        args["id"] = id

        response = UserHandler.delete(args)

        return response, response['status']


class UserListAPI(BlueprintBase):
    def __init__(self):
        super(UserListAPI, self).__init__()

    def post(self):

        args = dict(request.values.iteritems())

        err = validate_request(args)

        if err:
            return err, err['status']

        data = request.json

        #args.update(data)

        response = UserHandler.post(args, data)

        return response, response['status']

    def get(self):

        args = dict(request.values.iteritems())

        err = validate_request(args)

        if err:
            return err, err['status']

        response = UserHandler.get(args)

        return response, response['status']