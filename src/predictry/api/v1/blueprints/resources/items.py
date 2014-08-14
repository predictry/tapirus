__author__ = 'guilherme'

from predictry.api.v1.handlers.resources.items import ItemHandler
from predictry.api.v1.blueprints.blueprint import BlueprintBase
from flask_restful import reqparse


class ItemAPI(BlueprintBase):

    def __init__(self):
        super(ItemAPI, self).__init__()

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

        response = ItemHandler.get(args)

        return response, response['status']

    def put(self, id):


        reqparser = reqparse.RequestParser()
        reqparser.add_argument('name', type=str, location='json')
        reqparser.add_argument('brand', type=str, location='json')
        reqparser.add_argument('model', type=str, location='json')
        reqparser.add_argument('description', type=str, location='json')
        reqparser.add_argument('tags', type=str, location='json')
        reqparser.add_argument('price', type=float, location='json')
        reqparser.add_argument('category', type=str, location='json')
        reqparser.add_argument('subcategory', type=str, location='json')
        reqparser.add_argument('dateAdded', type=long, location='json')
        reqparser.add_argument('itemURL', type=str, location='json')
        reqparser.add_argument('imageURL', type=str, location='json')
        reqparser.add_argument('startDate', type=long, location='json')
        reqparser.add_argument('endDate', type=long, location='json')
        reqparser.add_argument('locations', type=str, location='json')

        reqparser.add_argument('appid', type=str, location='args', required=True,
                               choices=['pongo'])
        reqparser.add_argument('domain', type=str, location='args', required=True)

        requestargs = reqparser.parse_args()
        args = {}
        for k, v in requestargs.iteritems():
            if v is not None:
                args[k] = v

        args["id"] = id

        response = ItemHandler.put(args)

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

        response = ItemHandler.delete(args)

        return response, response['status']


class ItemListAPI(BlueprintBase):

    def __init__(self):
        super(ItemListAPI, self).__init__()

    def get(self):

        reqparser = reqparse.RequestParser()
        reqparser.add_argument('fields', type=str, location='args')
        reqparser.add_argument('limit', type=int, location='args')
        reqparser.add_argument('offset', type=int, location='args')
        reqparser.add_argument('q', type=str, location='args')
        reqparser.add_argument('priceFloor', type=float, location='args')
        reqparser.add_argument('priceCeiling', type=float, location='args')
        reqparser.add_argument('tags', type=str, location='args')
        reqparser.add_argument('locations', type=str, location='args')
        reqparser.add_argument('appid', type=str, location='args', required=True,
                               choices=['pongo'])
        reqparser.add_argument('domain', type=str, location='args', required=True)

        requestargs = reqparser.parse_args()
        args = {}
        for k, v in requestargs.iteritems():
            if v is not None:
                args[k] = v

        response = ItemHandler.get(args)

        return response, response['status']

    def post(self):

        reqparser = reqparse.RequestParser()
        reqparser.add_argument('id', type=int, location='json', required=True)
        reqparser.add_argument('name', type=str, location='json')
        reqparser.add_argument('brand', type=str, location='json')
        reqparser.add_argument('model', type=str, location='json')
        reqparser.add_argument('description', type=str, location='json')
        reqparser.add_argument('tags', type=str, location='json')
        reqparser.add_argument('price', type=float, location='json')
        reqparser.add_argument('category', type=str, location='json')
        reqparser.add_argument('subcategory', type=str, location='json')
        reqparser.add_argument('dateAdded', type=long, location='json')
        reqparser.add_argument('itemURL', type=str, location='json')
        reqparser.add_argument('imageURL', type=str, location='json')
        reqparser.add_argument('startDate', type=long, location='json')
        reqparser.add_argument('endDate', type=long, location='json')
        reqparser.add_argument('locations', type=str, location='json')
        reqparser.add_argument('appid', type=str, location='args', required=True,
                               choices=['pongo'])
        reqparser.add_argument('domain', type=str, location='args', required=True)

        requestargs = reqparser.parse_args()
        args = {}
        for k, v in requestargs.iteritems():
            if v is not None:
                args[k] = v

        response = ItemHandler.post(args)

        return response, response['status']
