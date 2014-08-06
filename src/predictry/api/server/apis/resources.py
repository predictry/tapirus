__author__ = 'guilherme'
__author__ = 'guilherme'

from flask import jsonify, make_response
from flask.ext.httpauth import HTTPBasicAuth

from predictry.api.handlers.resources import ItemHandler, UserHandler, ActionHandler

auth = HTTPBasicAuth()

@auth.get_password
def get_password(username):
    if username == 'username':
        return 'password'
    return None

@auth.error_handler
def unauthorized():
    return make_response(jsonify({'message': 'Unauthorized access'}), 403)


class ItemAPI(Resource):
    #decorators = [auth.login_required]

    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument('name', type=str, location='json')
        self.reqparse.add_argument('brand', type=str, location='json')
        self.reqparse.add_argument('model', type=str, location='json')
        self.reqparse.add_argument('description', type=str, location='json')
        self.reqparse.add_argument('tags', type=str, location='json')
        self.reqparse.add_argument('price', type=float, location='json')
        self.reqparse.add_argument('category', type=str, location='json')
        self.reqparse.add_argument('dateAdded', type=float, location='json')
        self.reqparse.add_argument('itemURL', type=str, location='json')
        self.reqparse.add_argument('imageURL', type=str, location='json')
        self.reqparse.add_argument('organization', type=str, location='json')

        self.reqparse.add_argument('fields', type=str, location='args')
        super(ItemAPI, self).__init__()

    def get(self, id):
        requestargs = self.reqparse.parse_args()
        args = {}
        for k, v in requestargs.iteritems():
            if v is not None:
                args[k] = v
                #print k, ":", v

        args["id"] = id
        args["method"] = "get"
        handler = ItemHandler()

        response = handler.handle_request(args)

        return response

    def put(self, id):

        requestargs = self.reqparse.parse_args()
        args = {}
        for k, v in requestargs.iteritems():
            if v is not None:
                args[k] = v
                #print k, ":", v

        args["id"] = id
        args["method"] = "put"
        handler = ItemHandler()

        response = handler.handle_request(args)

        return response

    def delete(self, id):
        requestargs = self.reqparse.parse_args()
        args = {}
        for k, v in requestargs.iteritems():
            if v is not None:
                args[k] = v
                #print k, ":", v

        args["id"] = id
        args["method"] = "delete"
        handler = ItemHandler()

        response = handler.handle_request(args)

        return response


class ItemListAPI(Resource):
    #decorators = [auth.login_required]

    def __init__(self):
        self.reqparse = reqparse.RequestParser()

        self.reqparse.add_argument('id', type=int, location='json')
        self.reqparse.add_argument('name', type=str, location='json')
        self.reqparse.add_argument('brand', type=str, location='json')
        self.reqparse.add_argument('model', type=str, location='json')
        self.reqparse.add_argument('description', type=str, location='json')
        self.reqparse.add_argument('tags', type=str, location='json')
        self.reqparse.add_argument('price', type=float, location='json')
        self.reqparse.add_argument('category', type=str, location='json')
        self.reqparse.add_argument('dateAdded', type=float, location='json')
        self.reqparse.add_argument('itemURL', type=str, location='json')
        self.reqparse.add_argument('imageURL', type=str, location='json')
        self.reqparse.add_argument('organization', type=str, location='json')

        self.reqparse.add_argument('fields', type=str, location='args')
        self.reqparse.add_argument('limit', type=int, location='args')
        self.reqparse.add_argument('offset', type=int, location='args')
        self.reqparse.add_argument('q', type=str, location='args')
        self.reqparse.add_argument('priceFloor', type=float, location='args')
        self.reqparse.add_argument('priceCeiling', type=float, location='args')
        self.reqparse.add_argument('tags', type=str, location='args')
        super(ItemListAPI, self).__init__()

    def post(self):

        requestargs = self.reqparse.parse_args()
        args = {}
        for k, v in requestargs.iteritems():
            if v is not None:
                args[k] = v
                #print k, ":", v

        args["method"] = "post"
        handler = ItemHandler()

        response = handler.handle_request(args)

        return response

    def get(self):

        requestargs = self.reqparse.parse_args()
        args = {}
        for k, v in requestargs.iteritems():
            if v is not None:
                args[k] = v
                #print k, ":", v

        args["method"] = "get"
        handler = ItemHandler()

        response = handler.handle_request(args)

        return response


class UserAPI(Resource):

    def __init__(self):
        self.reqparse = reqparse.RequestParser()

        self.reqparse.add_argument('fields', type=str, location='args')

        super(UserAPI, self).__init__()

    def get(self, id):

        requestargs = self.reqparse.parse_args()
        args = {}
        for k, v in requestargs.iteritems():
            if v is not None:
                args[k] = v
                #print k, ":", v

        args["id"] = id
        args["method"] = "get"
        handler = UserHandler()

        response = handler.handle_request(args)

        return response

    def delete(self, id):
        requestargs = self.reqparse.parse_args()
        args = {}
        for k, v in requestargs.iteritems():
            if v is not None:
                args[k] = v
                #print k, ":", v

        args["id"] = id
        args["method"] = "delete"
        handler = UserHandler()

        response = handler.handle_request(args)

        return response


class UserListAPI(Resource):
    def __init__(self):
        self.reqparse = reqparse.RequestParser()

        self.reqparse.add_argument('id', type=int, location='json')

        self.reqparse.add_argument('fields', type=int, location='args')

        super(UserListAPI, self).__init__()

    def post(self):
        requestargs = self.reqparse.parse_args()
        args = {}
        for k, v in requestargs.iteritems():
            if v is not None:
                args[k] = v
                #print k, ":", v

        args["method"] = "post"
        handler = UserHandler()

        response = handler.handle_request(args)

        return response

    def get(self):
        requestargs = self.reqparse.parse_args()
        args = {}
        for k, v in requestargs.iteritems():
            if v is not None:
                args[k] = v
                #print k, ":", v

        args["method"] = "get"
        handler = UserHandler()

        response = handler.handle_request(args)

        return response

class ActionAPI(Resource):
    #decorators = [auth.login_required]

    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument('timestamp', type=float, location='json')
        self.reqparse.add_argument('ipAddress', type=str, location='json')
        self.reqparse.add_argument('sessionId', type=str, location='json')
        self.reqparse.add_argument('guid', type=str, location='json')
        self.reqparse.add_argument('agent', type=str, location='json')
        self.reqparse.add_argument('type', type=str, location='json', choices=['view', 'buy', 'rate', 'addToCart'])
        self.reqparse.add_argument('userId', type=int, location='json')
        self.reqparse.add_argument('itemId', type=int, location='json')

        self.reqparse.add_argument('fields', type=str, location='args')
        super(ActionAPI, self).__init__()

    def get(self, id):
        requestargs = self.reqparse.parse_args()
        args = {}
        for k, v in requestargs.iteritems():
            if v is not None:
                args[k] = v
                #print k, ":", v

        args["id"] = id
        args["method"] = "get"
        handler = ActionHandler()

        response = handler.handle_request(args)

        return response

    def put(self, id):
        requestargs = self.reqparse.parse_args()
        args = {}
        for k, v in requestargs.iteritems():
            if v is not None:
                args[k] = v
                #print k, ":", v

        args["id"] = id
        args["method"] = "put"
        handler = ActionHandler()

        response = handler.handle_request(args)

        return response

    def delete(self, id):
        requestargs = self.reqparse.parse_args()
        args = {}
        for k, v in requestargs.iteritems():
            if v is not None:
                args[k] = v
                #print k, ":", v

        args["id"] = id
        args["method"] = "delete"
        handler = ActionHandler()

        response = handler.handle_request(args)

        return response


class ActionListAPI(Resource):
    #decorators = [auth.login_required]

    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument('id', type=int, location='json')
        self.reqparse.add_argument('timestamp', type=float, location='json')
        self.reqparse.add_argument('ipAddress', type=str, location='json')
        self.reqparse.add_argument('sessionId', type=str, location='json')
        self.reqparse.add_argument('guid', type=str, location='json')
        self.reqparse.add_argument('agent', type=str, location='json')
        self.reqparse.add_argument('type', type=str, location='json', choices=['view', 'buy', 'rate', 'addToCart'])
        self.reqparse.add_argument('userId', type=int, location='json')
        self.reqparse.add_argument('itemId', type=int, location='json')

        self.reqparse.add_argument('fields', type=str, location='args')
        self.reqparse.add_argument('limit', type=int, location='args')
        self.reqparse.add_argument('offset', type=int, location='args')
        self.reqparse.add_argument('q', type=str, location='args', choices=['view', 'buy', 'rate', 'addToCart'])
        self.reqparse.add_argument('occurredBefore', type=float, location='args')
        self.reqparse.add_argument('occurredAfter', type=float, location='args')
        super(ActionListAPI, self).__init__()

    def post(self):
        requestargs = self.reqparse.parse_args()
        args = {}
        for k, v in requestargs.iteritems():
            if v is not None:
                args[k] = v
                #print k, ":", v

        args["method"] = "post"
        handler = ActionHandler()

        response = handler.handle_request(args)

        return response

    def get(self):

        requestargs = self.reqparse.parse_args()
        args = {}
        for k, v in requestargs.iteritems():
            if v is not None:
                args[k] = v
                #print k, ":", v

        args["method"] = "get"
        handler = ActionHandler()

        response = handler.handle_request(args)

        return response

#TODO: create an endpoint for "category"
#TODO: include metadata in response (when client sets limit, return total data count)
