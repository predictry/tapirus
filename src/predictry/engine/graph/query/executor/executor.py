from predictry.utils.helpers import text

__author__ = 'guilherme'

#internal modules
from predictry.engine.graph.query.executor.base import QueryExecutorBase
from predictry.utils.neo4j import conn

from py2neo import cypher

tx = None
url = 'http://localhost:7474/db/data/'


def new_session(force=True):
    global tx

    if not tx or force:
        if conn.is_db_running(url) is False:
            print dict(error="Database connection error", message="The database at " + url + " seems to be offline",
                       status=500)
        else:
            session = cypher.Session(url)
            tx = session.create_transaction()


class QueryExecutor(QueryExecutorBase):

    def __init__(self):
        pass

    def run(self, query=None, params=None, batch=None, commit=False):

        query = text.encode(query)

        if not tx:
            new_session()
            if not tx:
                return {}, dict(error="Internal server error",
                                message="There was an error with internal server processes", status=500)

        if query is not None:
            tx.append(query, params)
            result = tx.execute()[0]

            if commit:
                tx.commit()
                new_session()

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
                new_session()

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