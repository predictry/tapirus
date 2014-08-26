__author__ = 'guilherme'

from predictry.api.v1.handlers.resources.items import ItemHandler
from predictry.api.v1.blueprints.blueprint import BlueprintBase
from predictry.api.v1.request import validate_request
from flask_restful import request


class ItemAPI(BlueprintBase):

    def __init__(self):
        super(ItemAPI, self).__init__()

    def get(self, id):

        args = dict(request.values.iteritems())

        err = validate_request(args)

        if err:
            return err, err['status']

        args["id"] = id

        response = ItemHandler.get(args)

        return response, response['status']

    def put(self, id):

        args = dict(request.values.iteritems())

        err = validate_request(args)

        if err:
            return err, err['status']

        data = request.json

        args["id"] = id

        response = ItemHandler.put(args, data)

        return response, response['status']

    def delete(self, id):

        args = dict(request.values.iteritems())

        err = validate_request(args)

        if err:
            return err, err['status']

        args["id"] = id

        response = ItemHandler.delete(args)

        return response, response['status']


class ItemListAPI(BlueprintBase):

    def __init__(self):
        super(ItemListAPI, self).__init__()

    def post(self):

        args = dict(request.values.iteritems())

        err = validate_request(args)

        if err:
            return err, err['status']

        data = request.json

        response = ItemHandler.post(args, data)

        return response, response['status']

    def get(self):

        args = dict(request.values.iteritems())

        err = validate_request(args)

        if err:
            return err, err['status']

        response = ItemHandler.get(args)

        return response, response['status']