__author__ = 'guilherme'

from predictry.query.generator.processes.recommendation import RecommendationQueryGenerator
from predictry.query.executor.queryexecutor import QueryExecutor
from predictry.utils.helpers import text
from predictry.api.v1.errors import error
from predictry.compute import basket

class RecommendationHandler:

    def __init__(self):
        self.resource = "recommendation"

    def get(self, args):

        args = text.encode(args)

        if args["type"] in ["oivt", "oipt", "oiv", "oip", "pav", "vap"]:
            if "itemId" not in args:
                return error('MissingParameter', self.resource, "itemId")

        qgen = RecommendationQueryGenerator()
        qexec = QueryExecutor()

        query, params = qgen.generate(args)
        output, err = qexec.run(query, params)

        response = {"data": None, "message": None, "error": None, "status": 200}

        if args["type"] in ["oivt", "oipt", "oiv", "oip", "pav", "vap"]:

            collections = []
            for record in output:
                collections.append({"id": record["collectionId"],
                                    "items": record["items"]})

            if collections:
                limit = args["limit"] if "limit" in args else 10
                most_popular_items = basket.rank_most_popular_items(collections, key="items", n=limit)
                response["data"] = {}
                response["data"]["items"] = most_popular_items

        return response