__author__ = 'guilherme'

from predictry.query.generator.processes import RecommendationQueryGenerator
from predictry.query.executor.queryexecutor import QueryExecutor
from predictry.compute import basket

class RecommendationHandler:

    def __init__(self):
        self.resource = "recommendation"

    def handle_request(self, args):

        #start = datetime.now()

        #authenticate user, append organization parameter
        #verify request
        #go


        args["organization"] = "redmart"

        qgen = RecommendationQueryGenerator()
        qexec = QueryExecutor()

        query, params = qgen.generate(args)
        output, err = qexec.run(query, params)
        #return dict(o=output, e=err)

        response = self.generate_response(args, output)

        #end = datetime.now()

        #print (end-start).microseconds/1000.0, 'ms\n\n'

        return response

    def generate_response(self, args, output):

        response = {"data": None, "message": None, "error": None, "status": 200}

        if args["type"] in ["oivt", "oipt", "oiv", "oip", "pav", "vap", "vip", "piv"]:

            collections = []
            #sessionId, items, basketSize
            for record in output:
                collections.append({"id": record["collectionId"],
                                    "items": record["items"]})

            if collections:
                limit = args["limit"] if "limit" in args else 10
                most_popular_items = basket.rank_most_popular_items(collections, key="items", n=limit)
                response["data"] = {}
                response["data"]["items"] = most_popular_items

        return response