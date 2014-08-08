__author__ = 'guilherme'

from datetime import datetime

from flask import request
from flask.ext.restful import Resource, reqparse
from v1.predictry.api.handlers.services import RecommendationHandler


class RecommendationAPI(Resource):
    #decorators = [auth.login_required]

    def __init__(self):
        self.reqparse = reqparse.RequestParser()

        self.reqparse.add_argument('itemId', type=int, location='args')
        self.reqparse.add_argument('userId', type=int, location='args')
        self.reqparse.add_argument('type', type=str, location='args', required=True,
                                   choices=['oiv', 'oivt', 'oip', 'oipt', 'pav', 'vap'])
        self.reqparse.add_argument('fields', type=str, location='args')
        self.reqparse.add_argument('limit', type=int, location='args')
        self.reqparse.add_argument('offset', type=int, location='args')
        self.reqparse.add_argument('q', type=str, location='args')
        self.reqparse.add_argument('priceFloor', type=float, location='args')
        self.reqparse.add_argument('priceCeiling', type=float, location='args')
        self.reqparse.add_argument('tags', type=str, location='args')
        self.reqparse.add_argument('appid', type=str, location='args', required=True,
                                   choices=['LjlLfujcZ1Xwol9RIrdUBA5IJP2byk5e1irzjdEk'])
        self.reqparse.add_argument('organization', type=str, required=True, location='args')

        super(RecommendationAPI, self).__init__()

    def get(self):

        #start = datetime.now()
        requestargs = self.reqparse.parse_args()
        args = {}
        for k, v in requestargs.iteritems():
            if v is not None:
                args[k] = v
                #print k, ":", v
        #end = datetime.now()
        #print "Argumen:", (end-start).microseconds/1000.0, "ms\n"

        #start = datetime.now()
        handler = RecommendationHandler()
        #end = datetime.now()
        #print "Constru:", (end-start).microseconds/1000.0, "ms\n"

        #start = datetime.now()
        response = handler.handle_request(args)
        #end = datetime.now()
        #print "Handler:", (end-start).microseconds/1000.0, 'ms\n'

        return response

class SystemAPI(Resource):
    #decorators = [auth.login_required]

    def __init__(self):

        super(SystemAPI, self).__init__()

    def shutdown_server(self):
        func = request.environ.get('werkzeug.server.shutdown')
        if func is None:
            raise RuntimeError('Not running with the Werkzeug Server')
        func()

    def get(self):
        #requestargs = self.reqparse.parse_args()
        self.shutdown_server()
        return {'message': 'Server shutting down...'}