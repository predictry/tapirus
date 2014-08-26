__author__ = 'guilherme'

from predictry.engine.graph.query.generator.processes.recommendation import RecommendationQueryGenerator
from predictry.engine.graph.query.executor.executor import QueryExecutor
from predictry.utils.helpers import text
from predictry.utils.helpers import payload
from predictry.api.v1.errors import error
from predictry.utils.log.logger import Logger


class RecommendationHandler:

    def __init__(self):
        pass

    resource = "recommendation"

    @staticmethod
    def post(args, data):

        args = text.encode(args)
        data = text.encode(data)

        if "type" not in data:
            err = error('MissingParameter', RecommendationHandler.resource, "type")
            Logger.warning(err)
            return err

        if data["type"] not in ["oivt", "oipt", "oiv", "oip"]:
                err = error('InvalidParameter', RecommendationHandler.resource, property="type",
                            message="Options: oiv, oivt, oip, oipt")
                Logger.warning(err)
                return err

        if data["type"] in ["oivt", "oipt", "oiv", "oip"]:
            if "item_id" not in data:
                err = error('MissingParameter', RecommendationHandler.resource, "item_id")
                Logger.warning(err)
                return err

        qgen = RecommendationQueryGenerator()
        qexec = QueryExecutor()

        query, params = qgen.generate(args, data)
        output, err = qexec.run(query, params)

        if err:
            Logger.error(err)
            return err

        response = {"data": None, "message": None, "error": None, "status": 200}

        response["data"] = {}
        response["data"]["items"] = output

        return payload.minify(response)