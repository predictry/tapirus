__author__ = 'guilherme'

from predictry.api.v1.handlers.services.recommendation import RecommendationHandler
from flask_restful import Resource, reqparse


class RecommendationAPI(Resource):

    def __init__(self):
        super(RecommendationAPI, self).__init__()

    def get(self):

        reqparser = reqparse.RequestParser()
        reqparser.add_argument('itemId', type=int, location='args')
        reqparser.add_argument('userId', type=int, location='args')
        reqparser.add_argument('type', type=str, location='args', required=True,
                                   choices=['oiv', 'oivt', 'oip', 'oipt', 'pav', 'vap'])
        reqparser.add_argument('fields', type=str, location='args')
        reqparser.add_argument('limit', type=int, location='args')
        reqparser.add_argument('offset', type=int, location='args')
        reqparser.add_argument('q', type=str, location='args')
        reqparser.add_argument('priceFloor', type=float, location='args')
        reqparser.add_argument('priceCeiling', type=float, location='args')
        reqparser.add_argument('tags', type=str, location='args')
        reqparser.add_argument('appid', type=str, location='args', required=True,
                               choices=['pongo'])
        reqparser.add_argument('domain', type=str, location='args', required=True)

        requestargs = reqparser.parse_args()
        args = {}
        for k, v in requestargs.iteritems():
            if v is not None:
                args[k] = v

        response = RecommendationAPI.get(args)

        return response, response['status']