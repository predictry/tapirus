__author__ = 'guilherme'

#internal modules
from v1.predictry.query.executor.base import QueryExecutorBase
from v1.predictry.utils.helpers import text as Text
import v1.predictry.utils.config.conn as Conn

from py2neo import cypher


url = 'http://localhost:7474/db/data/'

if Conn.is_db_running(url) is False:
    print dict(error="Database connection error", message="The database at " + url + " seems to be offline",
                    status=500)

    #return {}, dict(error="Internal server error", message="There was an error with internal server processes",
    #                status=500)


session = cypher.Session(url)
tx = session.create_transaction()

def new_session():
    global tx
    tx = session.create_transaction()

class QueryExecutor(QueryExecutorBase):

    def __init__(self):
        pass

    def run(self, query=None, params=None, batch=None, commit=False):

        query = Text.encode(query)

        url = 'http://localhost:7474/db/data/'

        if Conn.is_db_running(url) is False:
            print dict(error="Database connection error", message="The database at " + url + " seems to be offline",
                            status=500)

            return {}, dict(error="Internal server error", message="There was an error with internal server processes",
                            status=500)

        session = cypher.Session(url)
        tx = session.create_transaction()

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

#batch = [
#    dict(query="MATCH (i :ITEM :REDMART {id: {id}}) RETURN i.description AS description", params=dict(id=5550)),
#    dict(query="MATCH (i :ITEM :REDMART {id: {id}}) RETURN i.description AS description", params=dict(id=8000)),
#    dict(query="MATCH (i :ITEM :REDMART {id: {id}}) RETURN i.description AS description", params=dict(id=8317)),
#    dict(query="MATCH (i :ITEM :REDMART {id: {id}}) RETURN i.description AS description", params=dict(id=9965))
#]

#coll, err = QueryExecutor().run(batch)

#if err:
#    print err
#else:
#    for records in coll:
#        print records

