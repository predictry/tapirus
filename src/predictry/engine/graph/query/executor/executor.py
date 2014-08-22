__author__ = 'guilherme'

from py2neo import cypher
from py2neo.packages.httpstream.http import SocketError

from predictry.engine.graph.query.executor.base import QueryExecutorBase
from predictry.utils.helpers import text
from predictry.utils.log.logger import Logger

url = 'http://localhost:7474/db/data/'


class QueryExecutor(QueryExecutorBase):

    def __init__(self):
        pass

    def run(self, query=None, params=None, batch=None, commit=False):

        try:
            session = cypher.Session(url)
            tx = session.create_transaction()
        except SocketError as err:
            Logger.error(err)
            return None, dict(error="Internal server error",
                            message="There was an error with internal server processes", status=500)

        query = text.encode(query)

        print "connection is set..."

        if query is not None:
            tx.append(query, params)
            result = tx.execute()[0]

            if commit:
                tx.commit()

            records = []
            for row in result:
                record = {}

                for i in range(0, len(row.columns)):
                    record[row.columns[i]] = row.values[i]
                records.append(record)

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