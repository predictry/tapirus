__author__ = 'guilherme'

from datetime import datetime

from flask import request
from flask.ext.restful import Resource, reqparse
from v1.predictry.api.handlers.services import RecommendationHandler


class RecommendationAPI(Resource):

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

        requestargs = self.reqparse.parse_args()
        args = {}
        for k, v in requestargs.iteritems():
            if v is not None:
                args[k] = v

        handler = RecommendationHandler()
        response = handler.handle_request(args)

        return response