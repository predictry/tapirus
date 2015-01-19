__author__ = 'guilherme'

from tapirus.api.v1.handlers.resources.actions import ActionHandler
from tapirus.api.v1.blueprints.blueprint import BlueprintBase
from tapirus.api.v1.request import parse_params
from flask_restful import request


class ActionAPI(BlueprintBase):

    def __init__(self):
        super(ActionAPI, self).__init__()

    def get(self, id):

        args = dict(request.values.iteritems())

        err = parse_params(args)

        if err:
            return err, err['status']

        args["id"] = id

        response = ActionHandler.get(args)

        return response, response['status']

    def put(self, id):

        args = dict(request.values.iteritems())
        data = request.json

        err = parse_params(args, data)

        if err:
            return err, err['status']

        args["id"] = id

        response = ActionHandler.put(args, data)

        return response, response['status']

    def delete(self, id):

        args = dict(request.values.iteritems())

        err = parse_params(args)

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
        data = request.json

        err = parse_params(args, data)

        if err:
            return err, err['status']

        response = ActionHandler.post(args, data)

        return response, response['status']

    def get(self):

        args = dict(request.values.iteritems())

        err = parse_params(args)

        if err:
            return err, err['status']

        response = ActionHandler.get(args)

        return response, response['status']