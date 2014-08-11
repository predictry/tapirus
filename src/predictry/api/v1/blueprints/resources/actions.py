__author__ = 'guilherme'

from predictry.api.v1.handlers.resources.actions import ActionHandler
from flask_restful import Resource, reqparse


class ActionAPI(Resource):

    def __init__(self):
        super(ActionAPI, self).__init__()

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

        response = ActionHandler.get(args)

        return response, response['status']

    def put(self, id):

        reqparser = reqparse.RequestParser()
        reqparser.add_argument('timestamp', type=float, location='json')
        reqparser.add_argument('ipAddress', type=str, location='json')
        reqparser.add_argument('sessionId', type=str, location='json')
        reqparser.add_argument('guid', type=str, location='json')
        reqparser.add_argument('agent', type=str, location='json')
        reqparser.add_argument('quantum', type=float, location='json')
        reqparser.add_argument('type', type=str, location='json', choices=['view', 'buy', 'rate', 'addToCart'])
        reqparser.add_argument('appid', type=str, location='args', required=True,
                               choices=['pongo'])
        reqparser.add_argument('domain', type=str, location='args', required=True)

        requestargs = reqparser.parse_args()
        args = {}
        for k, v in requestargs.iteritems():
            if v is not None:
                args[k] = v

        args["id"] = id

        response = ActionHandler.put(args)

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

        response = ActionHandler.delete(args)

        return response, response['status']


class ActionListAPI(Resource):

    def __init__(self):
        super(ActionListAPI, self).__init__()

    def post(self):

        reqparser = reqparse.RequestParser()
        reqparser.add_argument('id', type=int, location='json', required=True)
        reqparser.add_argument('timestamp', type=long, location='json')
        reqparser.add_argument('ipAddress', type=str, location='json')
        reqparser.add_argument('sessionId', type=str, location='json')
        reqparser.add_argument('guid', type=str, location='json')
        reqparser.add_argument('agent', type=str, location='json')
        reqparser.add_argument('type', type=str, location='json', choices=['view', 'buy', 'rate', 'addToCart'])
        reqparser.add_argument('userId', type=int, location='json')
        reqparser.add_argument('itemId', type=int, location='json')
        reqparser.add_argument('quantum', type=float, location='json')
        reqparser.add_argument('appid', type=str, location='args', required=True,
                               choices=['pongo'])
        reqparser.add_argument('domain', type=str, location='args', required=True)

        requestargs = reqparser.parse_args()
        args = {}
        for k, v in requestargs.iteritems():
            if v is not None:
                args[k] = v

        response = ActionHandler.post(args)

        return response, response['status']

    def get(self):

        reqparser = reqparse.RequestParser()
        reqparser.add_argument('fields', type=str, location='args')
        reqparser.add_argument('limit', type=int, location='args')
        reqparser.add_argument('offset', type=int, location='args')
        reqparser.add_argument('type', type=str, location='args', choices=['view', 'buy', 'rate', 'addToCart'])
        reqparser.add_argument('occurredBefore', type=long, location='args')
        reqparser.add_argument('occurredAfter', type=long, location='args')
        reqparser.add_argument('appid', type=str, location='args', required=True,
                               choices=['pongo'])
        reqparser.add_argument('domain', type=str, location='args', required=True)

        requestargs = reqparser.parse_args()
        args = {}
        for k, v in requestargs.iteritems():
            if v is not None:
                args[k] = v

        response = ActionHandler.get(args)

        return response, response['status']