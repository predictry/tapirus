__author__ = 'guilherme'

#todo: Make this operation configuration (e.g. if clientT sends actionX read it this way

import os
import json
import ast
import gzip
import math
import dateutil.parser, dateutil.tz
import pytz
import boto.sqs
from boto.sqs.message import Message
from boto.s3.connection import S3Connection
from boto.s3.key import Key

from tapirus.utils import jsonuri
from tapirus.utils import config
from tapirus.core.db import neo4j
from tapirus.models import store
from tapirus.utils.logger import Logger

SRC_ROOT = os.path.dirname(os.path.abspath(__file__))
CONFIG_FILE = os.path.join(SRC_ROOT, "../../../config.json")

LOG_FILE_COLUMN_SEPARATOR = "\t"


SESSION_ID = "session_id"
TENANT_ID = "tenant_id"
ITEM_ID = "item_id"
USER_ID = "user_id"
AGENT_ID = "browser_id"
USER = "user"
AGENT = "browser"
ACTION = "action"
NAME = "name"
QUANTITY = "qty"
TOTAL = "total"
SUB_TOTAL = "sub_total"
ITEMS = "items"
KEYWORDS = "keywords"


def get_file_from_queue():

    conf = config.load_configuration()

    conn = boto.sqs.connect_to_region(conf["region"])

    queue = conn.get_queue(conf["queue"])

    if queue:
        #10 minutes
        rs = queue.get_messages(1, visibility_timeout=60*10)
        message = rs[0]
        f = message.get_body()

    else:
        print("Couldn't read from queue '{0}'@'{1}'".format(conf["queue"], conf["region"]))

        f, message = None, None

    return f, message


def download_log_from_s3(s3_log, file_path):

    conn = S3Connection()

    bucket = conn.get_bucket('trackings-test')

    key = Key(bucket)
    key.key = "action-logs/ER1VHJSBZAAAA.2015-01-15-09.8b10c614.gz"

    #download
    key.get_contents_to_filename('/tmp/ER1VHJSBZAAAA.2015-01-15-09.8b10c614.gz')

    #todo: return file address

    return "/tmp/ER1VHJSBZAAAA.2015-01-12-08.3cd14307.gz"


def process_log(file_name):

    conf = config.load_configuration()

    batch_size = conf["app"]["batch"]["write"]["size"]
    queries = []

    with gzip.open(file_name, 'rb') as f:
        """
            #indeces
            #0: date
            #1: time
            #4: ip
            #5: method
            #6: server
            #7: path
            #8: status
            #9: source page
            #10: agent (encoded)
            #11: payload
        """

        count = 0

        for line in f:

            l = line.decode(encoding="utf-8").split(LOG_FILE_COLUMN_SEPARATOR)
            #print(l)

            if len(l) >= 12:

                count += 1

                date, time, ip, path, status = l[0], l[1], l[4], l[7], int(l[8])

                if ".gif" not in path or status not in [0, 200, 304]:
                    continue

                try:

                    payload = jsonuri.deserialize(l[11])

                except ValueError:

                    print("Error: [{0}]".format(l[11]))

                    with open("{1}-{0}.json".format(file_name, count), "w") as tmp:
                        json.dump(l[11], tmp, indent=4)

                    continue

                #print("[`{0}`][`{1}`][`{2}`][{3}]".format(date, time, status, payload))

                queries.extend(build_queries(date, time, ip, path, payload))

            if count % batch_size == 0:

                #upload
                #run queries
                #try:
                rs = neo4j.run_batch_query(queries, commit=True)

                #except Exception as e:
                #    print(e)

                print("[Processed {0} actions {{Total: {1}}}, with {2} queries.".format(
                    (count//batch_size + 1)*batch_size - count,
                    count,
                    len(queries))
                )

                queries.clear()

        #todo: run remaining queries
        rs = neo4j.run_batch_query(queries, commit=True)
        #for q in queries:
        #    rs = neo4j.run_query(q, commit=True)

        #todo: print counter
        print("[Processed {0} actions {{Total: {1}}}, with {2} queries.".format(
            (count//batch_size + 1)*batch_size - count,
            count,
            len(queries))
        )

        #todo: any data left upload
    Logger.info("Processed [`{0}`] records in log file [`{1}`]".format(count, file_name.split("/")[-1]))


def build_queries(date, time, ip, path, payload):
    #todo: deal with extra parameters
    #items, session, user, agent
    #session -> item
    #session -> user
    #session -> agent

    dt = dateutil.parser.parse(''.join([date, "T", time, "Z"]))
    #print("[`{0}`]".format(dt))

    if is_data_valid(payload) is False:
        return []

    queries = []

    #session
    query = ["MERGE (n :`{SESSION_LABEL}` :`{STORE_ID}` {{id: {{id}} }})".format(
        SESSION_LABEL=store.LABEL_SESSION,
        STORE_ID=payload[TENANT_ID]
    )]

    params = [neo4j.Parameter("id", payload[SESSION_ID])]

    queries.append(neo4j.Query(''.join(query), params))
    #print(''.join(query))

    #user
    if USER in payload:
        #todo: if user is not given, use anonymous user id

        query = ["MERGE (n :`{USER_LABEL}` :`{STORE_ID}` {{id: {{id}} }})".format(
            USER_LABEL=store.LABEL_USER,
            STORE_ID=payload[TENANT_ID]
        )]

        params = [neo4j.Parameter("id", payload[USER][USER_ID])]

        for k, v in payload[USER].items():

            if k != USER_ID and is_acceptable_data_type(v):

                params.append(neo4j.Parameter(k, v))
                query.append("\nSET n.{0} = {{ {0} }}".format(
                    k
                ))

        queries.append(neo4j.Query(''.join(query), params))
        #print(''.join(query))

        #(session)-[r]-(user)

        q = "MERGE (s :`{SESSION_LABEL}` :`{STORE_ID}` {{id: {{session_id}} }})" \
            "\nMERGE (i :`{USER_LABEL}` :`{STORE_ID}` {{id: {{user_id}} }})" \
            "\nMERGE (s)-[r :`{REL}`]->(i)"
            #"(i :`{USER_LABEL}` :`{STORE_ID}` {{id: {{user_id}} }})"

        query = [q.format(
            SESSION_LABEL=store.LABEL_SESSION,
            USER_LABEL=store.LABEL_USER,
            STORE_ID=payload[TENANT_ID],
            REL=store.REL_SESSION_TO_USER
        )]

        params = [neo4j.Parameter("datetime", dt),
                  neo4j.Parameter("user_id", payload[USER][USER_ID]),
                  neo4j.Parameter("session_id", payload[SESSION_ID])]

        queries.append(neo4j.Query(''.join(query), params))
        #print(''.join(query))

    #agent
    if AGENT_ID in payload:

        query = ["MERGE (n :`{AGENT_LABEL}` :`{STORE_ID}` {{id: {{id}} }})".format(
            AGENT_LABEL=store.LABEL_AGENT,
            STORE_ID=payload[TENANT_ID]
        )]

        params = [neo4j.Parameter("id", payload[AGENT_ID])]

        queries.append(neo4j.Query(''.join(query), params))
        #print(''.join(query))

        #(session)-[r]-(agent)
        q = "MERGE (s :`{SESSION_LABEL}` :`{STORE_ID}` {{id: {{session_id}} }})" \
            "\nMERGE (i :`{AGENT_LABEL}` :`{STORE_ID}` {{id: {{agent_id}} }})" \
            "\nMERGE (s)-[r :`{REL}`]->(i)"
            #"(i :`{AGENT_LABEL}` :`{STORE_ID}` {{id: {{agent_id}} }})"

        query = [q.format(
            SESSION_LABEL=store.LABEL_SESSION,
            AGENT_LABEL=store.LABEL_AGENT,
            STORE_ID=payload[TENANT_ID],
            REL=store.REL_SESSION_TO_AGENT
        )]

        params = [neo4j.Parameter("datetime", dt),
                  neo4j.Parameter("agent_id", payload[AGENT_ID]),
                  neo4j.Parameter("session_id", payload[SESSION_ID])]

        queries.append(neo4j.Query(''.join(query), params))
        #print(''.join(query))

    #actions
    if payload[ACTION][NAME].lower() == store.REL_ACTION_TYPE_VIEW.lower():

        q = "MERGE (n :`{ITEM_LABEL}` :`{STORE_ID}` {{id: {{id}} }})"

        #collect items
        for item in payload[ITEMS]:

            query = [q.format(
                ITEM_LABEL=store.LABEL_ITEM,
                STORE_ID=payload[TENANT_ID]
            )]

            params = [neo4j.Parameter("id", item[ITEM_ID])]

            for k, v in item.items():

                if k != ITEM_ID and is_acceptable_data_type(v):

                    params.append(neo4j.Parameter(k, v))
                    query.append("\nSET n.{0} = {{ {0} }}".format(
                        k
                    ))

            queries.append(neo4j.Query(''.join(query), params))
            #print(''.join(query))

            #(item)-[r]-(session)

            q = "MERGE (s :`{SESSION_LABEL}` :`{STORE_ID}` {{id: {{session_id}} }})" \
                "\nMERGE (i :`{ITEM_LABEL}` :`{STORE_ID}` {{id: {{item_id}} }})" \
                "\nMERGE (s)-[r :`{REL}`]->(i)" \
                #"(i :`{ITEM_LABEL}` :`{STORE_ID}` {{id: {{item_id}} }})"

            query = [q.format(
                SESSION_LABEL=store.LABEL_SESSION,
                ITEM_LABEL=store.LABEL_ITEM,
                STORE_ID=payload[TENANT_ID],
                REL=store.REL_ACTION_TYPE_VIEW
            )]

            params = [neo4j.Parameter("datetime", dt),
                      neo4j.Parameter("item_id", item[ITEM_ID]),
                      neo4j.Parameter("session_id", payload[SESSION_ID])]

            query.append("\nSET r.{0} = {{ {0} }}".format(
                "datetime"
            ))

            queries.append(neo4j.Query(''.join(query), params))
            #print(''.join(query))

    elif payload[ACTION][NAME].lower() == store.REL_ACTION_TYPE_ADD_TO_CART.lower():

        q = "MERGE (n :`{ITEM_LABEL}` :`{STORE_ID}` {{id: {{id}} }})"

        #collect items
        for item in payload[ITEMS]:

            query = [q.format(
                ITEM_LABEL=store.LABEL_ITEM,
                STORE_ID=payload[TENANT_ID]
            )]

            params = [neo4j.Parameter("id", item[ITEM_ID])]

            queries.append(neo4j.Query(''.join(query), params))
            #print(''.join(query))

            #(item)-[r]-(session)

            q = "MERGE (s :`{SESSION_LABEL}` :`{STORE_ID}` {{id: {{session_id}} }})" \
                "\nMERGE (i :`{ITEM_LABEL}` :`{STORE_ID}` {{id: {{item_id}} }})" \
                "\nMERGE (s)-[r :`{REL}`]->(i)" \
                #"(i :`{ITEM_LABEL}` :`{STORE_ID}` {{id: {{item_id}} }})"

            query = [q.format(
                SESSION_LABEL=store.LABEL_SESSION,
                ITEM_LABEL=store.LABEL_ITEM,
                STORE_ID=payload[TENANT_ID],
                REL=store.REL_ACTION_TYPE_ADD_TO_CART
            )]

            params = [neo4j.Parameter("datetime", dt),
                      neo4j.Parameter("qty", item[QUANTITY]),
                      neo4j.Parameter("item_id", item[ITEM_ID]),
                      neo4j.Parameter("session_id", payload[SESSION_ID])]

            query.append("\nSET r.{0} = {{ {0} }}".format(
                "datetime"
            ))

            query.append("\nSET r.{0} = {{ {0} }}".format(
                "qty"
            ))

            queries.append(neo4j.Query(''.join(query), params))
            #print(''.join(query))

    elif payload[ACTION][NAME].lower() == store.REL_ACTION_TYPE_BUY.lower():

        q = "MERGE (n :`{ITEM_LABEL}` :`{STORE_ID}` {{id: {{id}} }})"

        #collect items
        for item in payload[ITEMS]:

            query = [q.format(
                ITEM_LABEL=store.LABEL_ITEM,
                STORE_ID=payload[TENANT_ID]
            )]

            params = [neo4j.Parameter("id", item[ITEM_ID])]

            queries.append(neo4j.Query(''.join(query), params))
            #print(''.join(query))

            #(item)-[r]-(session)

            q = "MERGE (s :`{SESSION_LABEL}` :`{STORE_ID}` {{id: {{session_id}} }})" \
                "\nMERGE (i :`{ITEM_LABEL}` :`{STORE_ID}` {{id: {{item_id}} }})" \
                "\nMERGE (s)-[r :`{REL}`]->(i)" \
                #"(i :`{ITEM_LABEL}` :`{STORE_ID}` {{id: {{item_id}} }})"

            query = [q.format(
                SESSION_LABEL=store.LABEL_SESSION,
                ITEM_LABEL=store.LABEL_ITEM,
                STORE_ID=payload[TENANT_ID],
                REL=store.REL_ACTION_TYPE_BUY
            )]

            params = [neo4j.Parameter("datetime", dt),
                      neo4j.Parameter("qty", item[QUANTITY]),
                      neo4j.Parameter("sub_total", item[SUB_TOTAL]),
                      neo4j.Parameter("item_id", item[ITEM_ID]),
                      neo4j.Parameter("session_id", payload[SESSION_ID])]

            query.append("\nSET r.{0} = {{ {0} }}".format(
                "datetime"
            ))

            query.append("\nSET r.{0} = {{ {0} }}".format(
                "qty"
            ))

            query.append("\nSET r.{0} = {{ {0} }}".format(
                "sub_total"
            ))

            queries.append(neo4j.Query(''.join(query), params))
            #print(''.join(query))

    elif payload[ACTION][NAME].lower() == store.REL_ACTION_TYPE_STARTED_CHECKOUT.lower():

        q = "MERGE (n :`{ITEM_LABEL}` :`{STORE_ID}` {{id: {{id}} }})"

        #collect items
        for item in payload[ITEMS]:

            query = [q.format(
                ITEM_LABEL=store.LABEL_ITEM,
                STORE_ID=payload[TENANT_ID]
            )]

            params = [neo4j.Parameter("id", item[ITEM_ID])]

            queries.append(neo4j.Query(''.join(query), params))
            #print(''.join(query))

            #(item)-[r]-(session)

            q = "MERGE (s :`{SESSION_LABEL}` :`{STORE_ID}` {{id: {{session_id}} }})" \
                "\nMERGE (i :`{ITEM_LABEL}` :`{STORE_ID}` {{id: {{item_id}} }})" \
                "\nMERGE (s)-[r :`{REL}`]->(i)" \
                #"(i :`{ITEM_LABEL}` :`{STORE_ID}` {{id: {{item_id}} }})"

            query = [q.format(
                SESSION_LABEL=store.LABEL_SESSION,
                ITEM_LABEL=store.LABEL_ITEM,
                STORE_ID=payload[TENANT_ID],
                REL=store.REL_ACTION_TYPE_STARTED_CHECKOUT
            )]

            params = [neo4j.Parameter("datetime", dt),
                      neo4j.Parameter("item_id", item[ITEM_ID]),
                      neo4j.Parameter("session_id", payload[SESSION_ID])]

            query.append("\nSET r.{0} = {{ {0} }}".format(
                "datetime"
            ))

            queries.append(neo4j.Query(''.join(query), params))
            #print(''.join(query))

    elif payload[ACTION][NAME].lower() == store.REL_ACTION_TYPE_SEARCH.lower():
        #todo: Search node (action type)
        pass

    return queries


def is_data_valid(data):

    #todo: log any missing data

    if SESSION_ID not in data:
        return False

    if TENANT_ID not in data:
        return False

    if ACTION not in data:
        return False

    if NAME not in data[ACTION]:
        return False

    if USER in data:

        if USER_ID not in data[USER]:
            return False

    if data[ACTION][NAME].lower() == store.REL_ACTION_TYPE_SEARCH.lower():

        if KEYWORDS not in data[ACTION]:
            return False

    elif data[ACTION][NAME].lower() == store.REL_ACTION_TYPE_VIEW.lower():

        if ITEMS not in data:
            return False

        if type(data[ITEMS]) is not list:
            return False

        for item in data[ITEMS]:

            if ITEM_ID not in item:
                return False

            #if QUANTITY not in item:
            #    return False

    elif data[ACTION][NAME].lower() == store.REL_ACTION_TYPE_ADD_TO_CART.lower():

        if ITEMS not in data:
            return False

        if type(data[ITEMS]) is not list:
            return False

        for item in data[ITEMS]:

            if ITEM_ID not in item:
                return False

            if QUANTITY not in item:
                return False

    elif data[ACTION][NAME].lower() == store.REL_ACTION_TYPE_STARTED_CHECKOUT.lower():

        if ITEMS not in data:
            return False

        if type(data[ITEMS]) is not list:
            return False

        for item in data[ITEMS]:

            if ITEM_ID not in item:
                return False

    elif data[ACTION][NAME].lower() == store.REL_ACTION_TYPE_BUY.lower():

        if ITEMS not in data:
            return False

        if type(data[ITEMS]) is not list:
            return False

        for item in data[ITEMS]:

            if ITEM_ID not in item:
                return False
            if QUANTITY not in item:
                return False
            if SUB_TOTAL not in item:
                return False

    return True


def is_acceptable_data_type(e):

    if type(e) in [bool, int, float, complex, str, bytes, list, set]:

        if type(e) is list or set:

            for elem in e:
                if type(elem) is dict:
                    return False
        else:
            return True

    else:
        return False


def insert_data_to_db():
    #validate
    #check site domain
    #validate
    pass


#todo: Serialize & deserialize nested structures
'''
def __flatten_map(data, prefix="", call=0):

    if call == 0 and type(data) is not dict:
        return None

    object = {}

    if type(data) is dict:

        for k, v in data.items():

            sep = ""

            if prefix:
                if prefix[-1] != "]":
                    sep = "."

            object = dict(list(__flatten_map(v, ''.join([prefix, sep, k]), call + 1).items()) + list(object.items()))

    else:

        object[prefix] = data

    return object


def flatten_map(data):

    return __flatten_map(data, "", 0)
'''


def rebuild_map(target):

    pass

if __name__ == "__main__":

    #filename = download_log_from_s3(None, None)
    file_name = "/tmp/ER1VHJSBZAAAA.2015-01-15-09.8b10c614.gz"

    data = {

        "brand": "Samsung",
        "description": "GARANSI MESIN 1BULAN\r\nAKSESORIS TIDAK GARANSI DENGAN ALASAN APAPUN\r\n\r\nFAST RESPON JAM KERJA 8.00-18.00\r\n\r\nSETIAP PENGIRIMAN KITA CEK TERLEBIH DAHULU UNTUK MEMINIMALISASIKAN TERJADINYA RETUR\r\nDAN BILA TERJADI RETUR.. ONGKIR RETURAN FULL DITANGGUNG PEMBELI\r\n\r\nDENGAN MEMBELI BERARTI ANDA MENGIKUTI PROSEDUR DIATAS THX\r\n\r\nSELAMAT BERBELANJA",
        "img_url": "https://s0.bukalapak.com/system/images/1/4/4/6/3/5/8/0/large/nt57.jpg",
        "item_url": "https://www.bukalapak.com/p/handphone/hp-smartphone/ymit-jual-agen-suplier-replika-supercopy-samsung-note-3-5-7-quadcore-ram-2gb-sensor-2-arah-camera-13mp-mt6582-made-in-korea",
        "item_id": "ymit",
        "subcategory": [
            "HP & Smartphone"
        ],
        "price": "1230000",
        "name": "AGEN - SUPLIER REPLIKA SUPERCOPY SAMSUNG NOTE 3 5,7\" QUADCORE RAM 2GB SENSOR 2 ARAH CAMERA 13MP MT6582 MADE IN KOREA",
        "inventory_qty": "84",
        "category": "Handphone",
        "location": {
            "coordinates": {
                "lat": 12,
                "long": 15.3
            },
            "city": "KAO",
            "country": "Sanfrey"
        }
    }

    #print(flatten_map(data))
    process_log(file_name)



#q = "MERGE (n :`{SESSION_LABEL}` :`{STORE_ID}` {id: {{session_id}}})-[:`{REL}` {REL_PROPS}]->(x :`{ITEM_LABEL}` :`{STORE_ID}` {id: {{item_id}}})"
#print(jsonuri.deserialize("action:name=buy&action:total=120703&items%255B0%255D%255B0%255Ditem_id=3n910&items%255B0%255D%255B0%255Dqty=1&items%255B0%255D%255B0%255Dsub_total=112000&user:user_id=732515&user:email=r_gages%2540yahoo.com&session_id=jxYgCGZVhz7y3l1&user_id=gMxQfldyhI0UZQn&browser_id=9gACE5y06p3iden&tenant_id=bukalapak&api_key=8f44921c2dc2d5fe47aa44b3625f12c9"))
