__author__ = 'guilherme'

from tapirus.api.v1.handlers.services.recommendation import RecommendationHandler
from tapirus.api.v1.blueprints.blueprint import BlueprintBase
from tapirus.api.v1.request import parse_params
from flask_restful import request


class RecommendationAPI(BlueprintBase):

    def __init__(self):
        super(RecommendationAPI, self).__init__()

    def get(self):

        args = dict(request.values.iteritems())

        err = parse_params(args)

        if err:
            return err, err['status']

        response = RecommendationHandler.get(args)

        return response, response['status']