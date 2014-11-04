__author__ = 'guilherme'

from py2neo import cypher
from py2neo.packages.httpstream.http import SocketError
from predictry.engine.graph.query.executor.base import QueryExecutorBase
from predictry.utils.helpers import text
from predictry.utils.log.logger import Logger
from predictry.utils.config import config

if config:
    url = config["neo4j"]["endpoints"]["data"]
else:
    url = 'http://localhost:7474/db/data/'


class QueryExecutor(QueryExecutorBase):

    def __init__(self):
        pass

    def run(self, query=None, params=None, batch=None, commit=False):

        #start_session = datetime.now()
        try:
            session = cypher.Session(url)
            tx = session.create_transaction()
        except SocketError as err:
            Logger.error(err)
            return None, dict(error="Internal server error",
                            message="There was an error with internal server processes", status=500)
        #end_session = datetime.now()

        #print "creating session took", (end_session - start_session).microseconds/1000.0, "ms"

        #start_encode_query = datetime.now()

        query = text.encode(query)

        #end_encode_query = datetime.now()

        #print "encoding query took", (end_encode_query-start_encode_query).microseconds/1000.0, "ms"

        #start_exec_query = datetime.now()

        if query is not None:
            tx.append(query, params)
            result = tx.execute()[0]

            if commit:
                tx.commit()

            #end_exec_query = datetime.now()

            #print "executing query took", (end_exec_query-start_exec_query).microseconds/1000.0, "ms"

            #start_parse_query_result = datetime.now()

            records = []
            for row in result:
                record = {}

                for i in range(0, len(row.columns)):
                    record[row.columns[i]] = row.values[i]
                records.append(record)

            #end_parse_query_result = datetime.now()

            #print "parsing query result took", (end_parse_query_result-start_parse_query_result).microseconds/1000.0, "ms"

            return records, None

        elif batch is not None:

            for bp in batch:
                tx.append(bp["query"], bp["params"])

            #notice that we don't take the first result only, but all of them
            result = tx.execute()

            if commit:
                tx.commit()

            collection = []
            for r in result:
                records = []
                for row in r:
                    record = {}

                    for i in range(0, len(row.columns)):
                        record[row.columns[i]] = row.values[i]
                    records.append(record)

                collection.append(records)

            return collection, None