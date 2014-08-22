__author__ = 'guilherme'

from predictry.api.v1.handlers.services.recommendation import RecommendationHandler
from predictry.api.v1.blueprints.blueprint import BlueprintBase
from predictry.api.v1.request import validate_request
from flask_restful import reqparse


class RecommendationAPI(BlueprintBase):

    def __init__(self):
        super(RecommendationAPI, self).__init__()

    def post(self):

        reqparser = reqparse.RequestParser()
        reqparser.add_argument('itemId', type=int, location='json')
        #reqparser.add_argument('userId', type=int, location='json')
        reqparser.add_argument('type', type=str, location='json', required=True,
                                   choices=['oiv', 'oivt', 'oip', 'oipt'])
        reqparser.add_argument('fields', type=str, location='json')
        reqparser.add_argument('limit', type=int, location='json')
        reqparser.add_argument('priceFloor', type=float, location='json')
        reqparser.add_argument('priceCeiling', type=float, location='json')
        reqparser.add_argument('locations', type=str, location='json')
        reqparser.add_argument('category', type=str, location='json')
        reqparser.add_argument('subcategory', type=str, location='json')
        reqparser.add_argument('tags', type=str, location='json')
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

        response = RecommendationHandler.post(args)

        return response, response['status']