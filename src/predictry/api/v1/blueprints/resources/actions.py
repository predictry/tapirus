__author__ = 'guilherme'

from predictry.api.v1.handlers.resources.actions import ActionHandler
from predictry.api.v1.blueprints.blueprint import BlueprintBase
from predictry.api.v1.request import validate_request
from flask_restful import reqparse


class ActionAPI(BlueprintBase):

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

        err = validate_request(args)
        if err:
            return err, err['status']

        response = ActionHandler.get(args)

        return response, response['status']

    def put(self, id):

        reqparser = reqparse.RequestParser()
        reqparser.add_argument('timestamp', type=float, location='json')
        reqparser.add_argument('ip_address', type=str, location='json')
        reqparser.add_argument('session_id', type=str, location='json')
        reqparser.add_argument('guid', type=str, location='json')
        reqparser.add_argument('agent', type=str, location='json')
        reqparser.add_argument('quantum', type=float, location='json')
        reqparser.add_argument('cart_id', type=int, location='json')

        reqparser.add_argument('appid', type=str, location='args', required=True,
                               choices=['pongo'])
        reqparser.add_argument('domain', type=str, location='args', required=True)

        requestargs = reqparser.parse_args()
        args = {}
        for k, v in requestargs.iteritems():
            if v is not None:
                args[k] = v

        args["id"] = id

        err = validate_request(args)
        if err:
            return err, err['status']

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

        err = validate_request(args)
        if err:
            return err, err['status']

        response = ActionHandler.delete(args)

        return response, response['status']


class ActionListAPI(BlueprintBase):

    def __init__(self):
        super(ActionListAPI, self).__init__()

    def post(self):

        reqparser = reqparse.RequestParser()
        reqparser.add_argument('id', type=int, location='json', required=True)
        reqparser.add_argument('user_id', type=int, location='json', required=True)
        reqparser.add_argument('item_id', type=int, location='json', required=True)
        reqparser.add_argument('type', type=str, location='json', choices=['view', 'buy', 'rate', 'add_to_cart'],
                               required=True)
        reqparser.add_argument('timestamp', type=long, location='json')
        reqparser.add_argument('ip_address', type=str, location='json')
        reqparser.add_argument('session_id', type=str, location='json')
        reqparser.add_argument('guid', type=str, location='json')
        reqparser.add_argument('agent', type=str, location='json')
        reqparser.add_argument('quantum', type=float, location='json')
        reqparser.add_argument('cart_id', type=int, location='json')

        reqparser.add_argument('appid', type=str, location='args', required=True,
                               choices=['pongo'])
        reqparser.add_argument('domain', type=str, location='args', required=True)

        requestargs = reqparser.parse_args()
        args = {}
        for k, v in requestargs.iteritems():
            if v is not None:
                args[k] = v

        err = validate_request(args)
        if err:
            return err, err['status']

        response = ActionHandler.post(args)

        return response, response['status']

    def get(self):

        reqparser = reqparse.RequestParser()
        reqparser.add_argument('fields', type=str, location='args')
        reqparser.add_argument('limit', type=int, location='args')
        reqparser.add_argument('offset', type=int, location='args')
        reqparser.add_argument('type', type=str, location='args', choices=['view', 'buy', 'rate', 'add_to_cart'])
        reqparser.add_argument('occurred_before', type=long, location='args')
        reqparser.add_argument('occurred_after', type=long, location='args')

        reqparser.add_argument('appid', type=str, location='args', required=True,
                               choices=['pongo'])
        reqparser.add_argument('domain', type=str, location='args', required=True)

        requestargs = reqparser.parse_args()
        args = {}
        for k, v in requestargs.iteritems():
            if v is not None:
                args[k] = v

        err = validate_request(args)
        if err:
            return err, err['status']

        response = ActionHandler.get(args)

        return response, response['status']