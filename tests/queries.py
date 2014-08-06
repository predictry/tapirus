__author__ = 'guilherme'

from py2neo import cypher
from datetime import datetime
#["oiv", "oip"]:
#items: 11318, 5550

def other_products_viewed():
    session = cypher.Session("http://localhost:7474")
    tx = session.create_transaction()

    #query = "MATCH (i:ITEM:REDMART) USING INDEX i:ITEM(id) WHERE i.id={id} RETURN i.id"
    query = """MATCH (i :ITEM:REDMART {id : {itemId}})<-[ :VIEWED]-(u :USER:REDMART)\n
            MATCH (x :ITEM:REDMART)<-[r :VIEWED]-(u)\n
            WHERE i <> x\n
            RETURN u.id AS collectionId, COLLECT(DISTINCT x.id) AS items\n
            LIMIT {limit}\n"""

    """
            MATCH (i :ITEM:REDMART)
            USING INDEX i:ITEM(id)
            WHERE i.id = {itemId}
            WITH i AS i
                MATCH (u :USER:REDMART)-[:VIEWED]->(i)
                WITH i AS i, u AS u
                    MATCH (u)-[:VIEWED]->(x :ITEM:REDMART)
                    WHERE x <> i
                    WITH i AS i, u AS u, x AS x
                    RETURN u.id AS collectionId, COLLECT(DISTINCT x.id) AS items
                    LIMIT {limit}"""


    params = dict(itemId=11318, limit=100)

    tx.append(query, params)

    start = datetime.now()
    r = tx.execute()[0]
    end = datetime.now()

    print (end-start).microseconds/1000, "ms"
    print r


def other_products_purchased():
    session = cypher.Session("http://localhost:7474")
    tx = session.create_transaction()

    #query = "MATCH (i:ITEM:REDMART) USING INDEX i:ITEM(id) WHERE i.id={id} RETURN i.id"
    query = """MATCH (i :ITEM:REDMART {id : {itemId}})<-[ :VIEWED]-(u :USER:REDMART)\n
            MATCH (x :ITEM:REDMART)<-[r :VIEWED]-(u)\n
            WHERE i <> x\n
            RETURN u.id AS collectionId, COLLECT(DISTINCT x.id) AS items\n
            LIMIT {limit}\n"""

    """
            MATCH (i :ITEM:REDMART)
            USING INDEX i:ITEM(id)
            WHERE i.id = {itemId}
            WITH i AS i
                MATCH (u :USER:REDMART)-[:BOUGHT]->(i)
                WITH i AS i, u AS u
                    MATCH (u)-[:BOUGHT]->(x :ITEM:REDMART)
                    WHERE x <> i
                    WITH i AS i, u AS u, x AS x
                    RETURN u.id AS collectionId, COLLECT(DISTINCT x.id) AS items
                    LIMIT {limit}"""


    params = dict(itemId=11318, limit=100)

    tx.append(query, params)

    start = datetime.now()
    r = tx.execute()[0]
    end = datetime.now()

    print (end-start).microseconds/1000, "ms"
    print r

other_products_viewed()
#other_products_purchased()