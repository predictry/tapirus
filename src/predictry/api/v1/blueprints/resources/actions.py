__author__ = 'guilherme'

from predictry.api.v1.handlers.resources.actions import ActionHandler
from predictry.api.v1.blueprints.blueprint import BlueprintBase
from predictry.api.v1.request import validate_request
from flask_restful import request


class ActionAPI(BlueprintBase):

    def __init__(self):
        super(ActionAPI, self).__init__()

    def get(self, id):

        args = dict(request.values.iteritems())

        err = validate_request(args)

        if err:
            return err, err['status']

        args["id"] = id

        response = ActionHandler.get(args)

        return response, response['status']

    def put(self, id):

        args = dict(request.values.iteritems())

        err = validate_request(args)

        if err:
            return err, err['status']

        data = request.json

        args["id"] = id

        response = ActionHandler.put(args, data)

        return response, response['status']

    def delete(self, id):

        args = dict(request.values.iteritems())

        err = validate_request(args)

        if err:
            return err, err['status']

        args["id"] = id

        response = ActionHandler.delete(args)

        return response, response['status']


class ActionListAPI(BlueprintBase):

    def __init__(self):
        super(ActionListAPI, self).__init__()

    def post(self):

        args = dict(request.values.iteritems())

        err = validate_request(args)

        if err:
            return err, err['status']

        data = request.json

        response = post(args, data)

        return response, response['status']

    def get(self):

        args = dict(request.values.iteritems())

        err = validate_request(args)

        if err:
            return err, err['status']

        response = ActionHandler.get(args)

        return response, response['status']