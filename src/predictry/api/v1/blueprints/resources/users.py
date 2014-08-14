__author__ = 'guilherme'

from predictry.api.v1.handlers.resources.users import UserHandler
from predictry.api.v1.blueprints.blueprint import BlueprintBase
from flask_restful import reqparse


class UserAPI(BlueprintBase):

    def __init__(self):
        super(UserAPI, self).__init__()

    def get(self, id):

        reqparser = reqparse.RequestParser()
        reqparser.add_argument('fields', type=str, location='args')
        reqparser.add_argument('appid', type=str, location='args', required=True,
                               choices=['pongo'])
        reqparser.add_argument('domain', type=str, location='args', required=True)

        requestargs = reqparser.parse_args()
        args = {}
        for k, v in requestargs.iteritems():
            if v is not None:
                args[k] = v

        args["id"] = id

        response = UserHandler.get(args)

        return response, response['status']

    def put(self, id):

        reqparser = reqparse.RequestParser()
        reqparser.add_argument('email', type=str, location='json', required=True)
        reqparser.add_argument('appid', type=str, location='args', required=True,
                               choices=['pongo'])
        reqparser.add_argument('domain', type=str, location='args', required=True)

        requestargs = reqparser.parse_args()
        args = {}
        for k, v in requestargs.iteritems():
            if v is not None:
                args[k] = v

        args["id"] = id

        response = UserHandler.put(args)

        return response, response['status']

    def delete(self, id):

        reqparser = reqparse.RequestParser()
        reqparser.add_argument('appid', type=str, location='args', required=True,
                               choices=['pongo'])
        reqparser.add_argument('domain', type=str, location='args', required=True)

        requestargs = reqparser.parse_args()
        args = {}
        for k, v in requestargs.iteritems():
            if v is not None:
                args[k] = v

        args["id"] = id

        response = UserHandler.delete(args)

        return response, response['status']


class UserListAPI(BlueprintBase):
    def __init__(self):
        super(UserListAPI, self).__init__()

    def post(self):

        reqparser = reqparse.RequestParser()
        reqparser.add_argument('id', type=int, location='json', required=True)
        reqparser.add_argument('email', type=str, location='json', required=True)
        reqparser.add_argument('appid', type=str, location='args', required=True,
                               choices=['pongo'])
        reqparser.add_argument('domain', type=str, location='args', required=True)

        requestargs = reqparser.parse_args()
        args = {}
        for k, v in requestargs.iteritems():
            if v is not None:
                args[k] = v

        response = UserHandler.post(args)

        return response, response['status']

    def get(self):

        reqparser = reqparse.RequestParser()
        reqparser.add_argument('fields', type=str, location='args')
        reqparser.add_argument('limit', type=int, location='args')
        reqparser.add_argument('offset', type=int, location='args')
        reqparser.add_argument('appid', type=str, location='args', required=True,
                               choices=['pongo'])
        reqparser.add_argument('domain', type=str, location='args', required=True)

        requestargs = reqparser.parse_args()
        args = {}
        for k, v in requestargs.iteritems():
            if v is not None:
                args[k] = v

        response = UserHandler.get(args)

        return response, response['status']