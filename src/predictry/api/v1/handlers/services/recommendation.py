__author__ = 'guilherme'

from predictry.engine.graph.query.generator.processes.recommendation import RecommendationQueryGenerator
from predictry.engine.graph.query.executor.executor import QueryExecutor
from predictry.utils.helpers import text
from predictry.utils.helpers import payload
from predictry.api.v1.errors import error
from predictry.engine.compute import ranking
from predictry.utils.neo4j import node
from predictry.utils.log.logger import Logger


class RecommendationHandler:

    resource = "recommendation"

    @staticmethod
    def post(args):

        args = text.encode(args)

        if args["type"] in ["oivt", "oipt", "oiv", "oip"]:
            if "item_id" not in args:
                err = error('MissingParameter', RecommendationHandler.resource, "item_id")
                Logger.warning(err)
                error

        qgen = RecommendationQueryGenerator()
        qexec = QueryExecutor()

        query, params = qgen.generate(args)
        output, err = qexec.run(query, params)

        if err:
            Logger.error(err)
            return err

        response = {"data": None, "message": None, "error": None, "status": 200}

        if args["type"] in ["oivt", "oipt", "oiv", "oip"]:

            collections = []
            for record in output:
                collections.append({"id": record["collection_id"],
                                    "items": record["items"]})

            if collections:
                limit = args["limit"] if "limit" in args else 10
                most_popular_items = ranking.rank_most_popular_items(collections, key="items", n=limit)

                #print collections
                if "fields" in args:
                    ids = [item["id"] for item in most_popular_items]

                    #print ids
                    items, err = node.get_node_properties(ids, args['fields'].split(','), "ITEM", args['domain'])

                    #print items
                    if err:
                        Logger.error(err)
                        #log error
                    else:
                        for p in most_popular_items:
                            for item in items:
                                if p['id'] == item['id']:
                                    for k, v in item.iteritems():
                                        if k != "id":
                                            p[k] = v

                response["data"] = {}
                response["data"]["items"] = most_popular_items

        return payload.minify(response)