__author__ = 'guilherme'

from predictry.engine.graph.query.generator.services.recommendation import RecommendationQueryGenerator
from predictry.engine.graph.query.executor.executor import QueryExecutor
from predictry.engine.models.resources.item import ItemSchema
from predictry.engine.compute import ranking
from predictry.utils.helpers import text
from predictry.utils.helpers import payload
from predictry.utils.neo4j import node
from predictry.api.v1.errors import error
from predictry.utils.log.logger import Logger


class RecommendationHandler:

    def __init__(self):
        pass

    resource = "recommendation"

    rtype = ["oivt", "oipt", "oiv", "oip",
             "trp", "trv", "trac",
             "utrp", "utrv", "utrac", "uvnp", "uacnp"]

    @staticmethod
    def get(args):

        args = text.encode(args)

        if "type" not in args:
            err = error('MissingParameter', RecommendationHandler.resource, "type")
            Logger.warning(err)
            return err

        if args["type"] not in RecommendationHandler.rtype:
                err = error('InvalidParameter', RecommendationHandler.resource, property="type",
                            message="Options: %s" % ','.join(RecommendationHandler.rtype))
                Logger.warning(err)
                return err

        if args["type"] in ["oivt", "oipt", "oiv", "oip"]:
            if "item_id" not in args:
                err = error('MissingParameter', RecommendationHandler.resource, "item_id")
                Logger.warning(err)
                return err

        if args["type"] in ["utrp", "utrv", "utrac", "uvnp", "uacnp"]:
            if "user_id" not in args:
                err = error('MissingParameter', RecommendationHandler.resource, "user_id")
                Logger.warning(err)
                return err

        qgen = RecommendationQueryGenerator()
        qexec = QueryExecutor()

        query, params = qgen.generate(args)
        output, err = qexec.run(query, params)

        if err:
            Logger.error(err)
            return err

        response = {"data": None, "message": None, "error": None, "status": 200}

        if args["type"] in ["oiv", "oip"]:

            collections = []
            for record in output:
                collections.append(record)

            limit = args["limit"] if "limit" in args else 10
            most_popular_items = ranking.rank_most_popular_items(collections, key="id", n=limit)

            for item in most_popular_items:
                for record in collections:
                    if record["id"] == item["id"]:
                        item.update(record)
                        break

            output = most_popular_items

        elif args["type"] in ["trp", "trv", "trac"]:

            if output:
                if "limit" in args:
                    n = args["limit"]
                else:
                    n = len(output[0]["items"])

                ids = []
                for i in range(0, n):
                    ids.append(output[0]["items"][i])

                if "fields" in args:
                    properties = args["fields"].split(",")
                else:
                    properties = ["id"]

                items, err = node.get_node_properties(ids,
                                                      properties, domain=args["domain"], label=ItemSchema.get_label())

                if err:
                    return err

                output = items

        response["data"] = {}
        response["data"]["items"] = output

        return payload.minify(response)