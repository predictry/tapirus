__author__ = 'guilherme'

#todo: Make this operation configurable (e.g. if clientT sends actionX read it this way
#todo: Unit tests

import os
import os.path
import json
import gzip
import tempfile
import dateutil.parser
import dateutil.tz
import traceback

import requests
import requests.exceptions

from tapirus.utils import jsonuri
from tapirus.utils import config
from tapirus.core.db import neo4j
from tapirus.core import aws
from tapirus.model import store
from tapirus.operator import schema
from tapirus.utils.logger import Logger

LOG_FILE_COLUMN_SEPARATOR = "\t"
LOG_KEEPER_FILE_NAME = "log.keeper.list.db"
LOG_KEEPER_DB = os.path.join(os.path.dirname(os.path.realpath(__file__)), "../../../{0}".format(LOG_KEEPER_FILE_NAME))

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
LOCATION = "locations"
CITY = "city"
COUNTRY = "country"


def get_file_from_queue():
    """

    :return:
    """

    conf = config.load_configuration()

    if not conf:
        Logger.critical("Aborting `Queue Read` operation. Configuration `")

        return None, None

    region = conf["sqs"]["region"]
    queue_name = conf["sqs"]["queue"]
    visibility_timeout = conf["sqs"]["visibility_timeout"]
    count = 1

    messages = aws.read_queue(region, queue_name, visibility_timeout, count)

    if messages and len(messages) > 0:

        msg = messages[0]
        f = json.loads(msg.get_body(), encoding="utf-8")

        return f["data"]["full_path"], msg

    else:

        return None, None


def process_log(file_name, batch_size):
    """

    :param file_name:
    :return:
    """

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

            if len(l) >= 12:

                date, time, ip, path, status = l[0], l[1], l[4], l[7], int(l[8])

                if ".gif" not in path or status not in [0, 200, 304]:
                    continue

                try:

                    payload = jsonuri.deserialize(l[11])

                except ValueError as e:

                    Logger.error("Error in deserialization of payload: [{0}]\n\t{1}".format(l[11], e))

                    continue

                queries.extend(build_queries(date, time, ip, path, payload))
                count += 1

            if count % batch_size == 0 and count > 0:

                #upload
                #run queries
                try:
                    rs = neo4j.run_batch_query(queries, commit=True)

                except Exception as e:
                    Logger.error(traceback.format_exc())
                    raise e
                else:

                    print("[Processed {0} actions {{Total: {1}}}, with {2} queries]".format(
                        (count//batch_size + 1)*batch_size - count,
                        count,
                        len(queries))
                    )

                    Logger.info("[Processed {0} actions {{Total: {1}}}, with {2} queries]".format(
                        (count//batch_size + 1)*batch_size - count,
                        count,
                        len(queries))
                    )

                    queries.clear()

        if queries:
            try:

                rs = neo4j.run_batch_query(queries, commit=True)

            except Exception as e:
                Logger.error(traceback.format_exc())
                raise e

            else:
                print("[Processed {0} actions {{Total: {1}}}, with {2} queries.".format(
                    (count//batch_size + 1)*batch_size - count,
                    count,
                    len(queries))
                )

                Logger.info("[Processed {0} actions {{Total: {1}}}, with {2} queries.".format(
                    (count//batch_size + 1)*batch_size - count,
                    count,
                    len(queries))
                )

                queries.clear()

    Logger.info("Processed [`{0}`] records in log file [`{1}`]".format(count, file_name.split("/")[-1]))


def build_queries(date, time, ip, path, payload):
    """

    :param date:
    :param time:
    :param ip:
    :param path:
    :param payload:
    :return:
    """

    #todo: deal with extra parameters (location)
    #items, session, user, agent
    #session -> item
    #session -> user
    #session -> agent

    dt = dateutil.parser.parse(''.join([date, "T", time, "Z"]))

    if schema.is_data_valid(payload) is False:
        return []

    queries = []

    #session
    query = ["MERGE (n :`{SESSION_LABEL}` :`{STORE_ID}` {{id: {{id}} }})".format(
        SESSION_LABEL=store.LABEL_SESSION,
        STORE_ID=payload[TENANT_ID]
    )]

    params = [neo4j.Parameter("id", payload[SESSION_ID])]

    queries.append(neo4j.Query(''.join(query), params))

    #user
    if USER in payload:
        #todo: if user is not given, use anonymous user id?

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

        #(session)-[r]-(user)

        q = "MERGE (s :`{SESSION_LABEL}` :`{STORE_ID}` {{id: {{session_id}} }})" \
            "\nMERGE (i :`{USER_LABEL}` :`{STORE_ID}` {{id: {{user_id}} }})" \
            "\nMERGE (s)-[r :`{REL}`]->(i)"

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

    #agent
    if AGENT_ID in payload:

        query = ["MERGE (n :`{AGENT_LABEL}` :`{STORE_ID}` {{id: {{id}} }})".format(
            AGENT_LABEL=store.LABEL_AGENT,
            STORE_ID=payload[TENANT_ID]
        )]

        params = [neo4j.Parameter("id", payload[AGENT_ID])]

        queries.append(neo4j.Query(''.join(query), params))

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

            #(item)-[r]-(location)

            if LOCATION in item:

                if COUNTRY in item[LOCATION]:

                    q = "MERGE (l:`{LOCATION_LABEL}` :`{LOCATION_COUNTRY}` :`{STORE_ID}` {{name: {{name}} }})" \
                        "\nMERGE (i :`{ITEM_LABEL}` :`{STORE_ID}` {{id: {{item_id}} }})" \
                        "\nMERGE (i)-[:`{REL}`]->(l)"

                    query = [q.format(
                        LOCATION_LABEL=store.LABEL_LOCATION,
                        LOCATION_COUNTRY=store.LABEL_LOCATION_COUNTRY,
                        ITEM_LABEL=store.LABEL_ITEM,
                        STORE_ID=payload[TENANT_ID],
                        REL=store.REL_ITEM_LOCATION
                    )]

                    params = [neo4j.Parameter("name", item[LOCATION][COUNTRY]),
                              neo4j.Parameter("item_id", item[ITEM_ID])]

                    queries.append(neo4j.Query(''.join(query), params))

                if CITY in item[LOCATION]:

                    q = "MERGE (l:`{LOCATION_LABEL}` :`{LOCATION_CITY}` :`{STORE_ID}` {{name: {{name}} }})" \
                        "\nMERGE (i :`{ITEM_LABEL}` :`{STORE_ID}` {{id: {{item_id}} }})" \
                        "\nMERGE (i)-[:`{REL}`]->(l)"

                    query = [q.format(
                        LOCATION_LABEL=store.LABEL_LOCATION,
                        LOCATION_CITY=store.LABEL_LOCATION_CITY,
                        ITEM_LABEL=store.LABEL_ITEM,
                        STORE_ID=payload[TENANT_ID],
                        REL=store.REL_ITEM_LOCATION
                    )]

                    params = [neo4j.Parameter("name", item[LOCATION][CITY]),
                              neo4j.Parameter("item_id", item[ITEM_ID])]

                    queries.append(neo4j.Query(''.join(query), params))

            #(item)-[r]-(session)

            q = "MERGE (s :`{SESSION_LABEL}` :`{STORE_ID}` {{id: {{session_id}} }})" \
                "\nMERGE (i :`{ITEM_LABEL}` :`{STORE_ID}` {{id: {{item_id}} }})" \
                "\nMERGE (s)-[r :`{REL}`]->(i)"

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

            #(item)-[r]-(session)

            q = "MERGE (s :`{SESSION_LABEL}` :`{STORE_ID}` {{id: {{session_id}} }})" \
                "\nMERGE (i :`{ITEM_LABEL}` :`{STORE_ID}` {{id: {{item_id}} }})" \
                "\nMERGE (s)-[r :`{REL}`]->(i)"
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

            #(item)-[r]-(session)

            q = "MERGE (s :`{SESSION_LABEL}` :`{STORE_ID}` {{id: {{session_id}} }})" \
                "\nMERGE (i :`{ITEM_LABEL}` :`{STORE_ID}` {{id: {{item_id}} }})" \
                "\nMERGE (s)-[r :`{REL}`]->(i)"

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

            #(item)-[r]-(session)

            q = "MERGE (s :`{SESSION_LABEL}` :`{STORE_ID}` {{id: {{session_id}} }})" \
                "\nMERGE (i :`{ITEM_LABEL}` :`{STORE_ID}` {{id: {{item_id}} }})" \
                "\nMERGE (s)-[r :`{REL}`]->(i)"

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

    elif payload[ACTION][NAME].lower() == store.REL_ACTION_TYPE_SEARCH.lower():

        q = "MERGE (s :`{SESSION_LABEL}` :`{STORE_ID}` {{ id: {{session_id}} }})" \
            "\nMERGE (n :`{SEARCH_LABEL}` :`{STORE_ID}` {{ keywords: {{keywords}} }})" \
            "\nMERGE (s)-[r :`{REL}`]->(n)"

        #collect items
        query = [q.format(
            SEARCH_LABEL=store.LABEL_SEARCH,
            SESSION_LABEL=store.LABEL_SESSION,
            STORE_ID=payload[TENANT_ID],
            REL=store.REL_ACTION_TYPE_SEARCH
        )]

        params = [neo4j.Parameter("keywords", payload[ACTION][KEYWORDS]),
                  neo4j.Parameter("session_id", payload[SESSION_ID]),
                  neo4j.Parameter("datetime", dt)]

        queries.append(neo4j.Query(''.join(query), params))

        for k, v in payload[ACTION].items():

            if k != KEYWORDS and is_acceptable_data_type(v):

                params.append(neo4j.Parameter(k, v))
                query.append("\nSET n.{0} = {{ {0} }}".format(
                    k
                ))

        query.append("\nSET r.{0} = {{ {0} }}".format(
            "datetime"
        ))

        queries.append(neo4j.Query(''.join(query), params))

    return queries


def is_acceptable_data_type(e):
    """

    :param e:
    :return:
    """

    if type(e) in [bool, int, float, complex, str, bytes, list, set]:

        if type(e) is list or set:

            for elem in e:
                if type(elem) is dict:
                    return False
        else:
            return True

    else:
        return False

    return True


def delete_file(file_name):
    """

    :param file_name:
    :return:
    """

    #todo: check for IO errors/exceptions
    #todo: return True/False

    os.remove(file_name)


def notify_log_keeper(url, file_name, status):
    """

    :param file_name:
    :param status:
    :return:
    """

    uri = '/'.join([url, file_name])
    payload = dict(status=status)

    try:
        response = requests.put(url=uri, json=payload)
    except requests.exceptions.ConnectionError as e:
        Logger.error("Connection error while trying to notify LogKeeper@{0}:\n\t{1}".format(uri, e))
        return False
    except requests.exceptions.HTTPError as e:
        Logger.error("HTTP error while trying to notify LogKeeper@{0}:\n\t{1}".format(uri, e))
        return False
    except Exception as e:
        Logger.error("Unexpected error while trying to notify LogKeeper@{0}:\n\t{1}".format(uri, e))
        return False
    else:

        if response.status_code != 200:

            Logger.error("LogKeeper@{0} Response:\n\t`{1}`".format(uri, response.status_code))
            return False

        else:

            Logger.info("Notified LogKeeper of processed file `{0}`".format(file_name))
            return True


def notify_log_keeper_of_backlogs(url):
    """
    Tries notify the log keeper of all files in the waiting list
    :return:
    """

    file_names = get_log_keeper_files()

    for file_name in file_names:

        if notify_log_keeper(url, file_name, status="processed"):
            remove_log_keeper_file(file_name)


def add_log_keeper_file(file_name):
    """
    Adds a file to the list of files to notify the log keeper about
    :param file_name:
    :return:
    """

    files_names = get_log_keeper_files()

    if file_name not in files_names:

        with open(LOG_KEEPER_DB, "a+") as f:
            f.write(''.join([file_name, "\n"]))


def remove_log_keeper_file(file_name):
    """
    Removes a file from the log keeper's pending notification list
    :param file_name:
    :return:
    """

    files_names = get_log_keeper_files()

    #if file is present, remove it
    if file_name in files_names:
        files_names.remove(file_name)

        #update file (or just re-write it)
        with open(LOG_KEEPER_DB, "w+") as f:
            for file_name in set(files_names):
                f.write(''.join([file_name, "\n"]))


def get_log_keeper_files():
    """
    Gets the list of files pending notification to the log keeper
    :return:
    """

    file_names = []

    if os.path.exists(LOG_KEEPER_DB):

        with open(LOG_KEEPER_DB, "r") as f:

            for line in f:
                file_names.append(line.strip())

    return file_names


def run():
    """
    Execute harvesting procedure.
    :return:
    """

    #Read configuration
    conf = config.load_configuration()

    if not conf:
        Logger.critical("Aborting `Queue Read` operation. Couldn't read app configuration `")
        return

    region = conf["sqs"]["region"]
    queue_name = conf["sqs"]["queue"]
    visibility_timeout = conf["sqs"]["visibility_timeout"]
    count = 1
    batch_size = conf["app"]["batch"]["write"]["size"]

    #Get name of file to download from SQS
    messages = aws.read_queue(region, queue_name, visibility_timeout, count)

    if messages and len(messages) > 0:

        msg = messages[0]
        f = json.loads(msg.get_body(), encoding="utf-8")

        s3_file_path, message = f["data"]["full_path"], msg

        file_name = s3_file_path.split("/")[-1]
        file_path = os.path.join(tempfile.gettempdir(), file_name)

        #Download file from S3
        aws.download_log_from_s3(s3_file_path, file_path)

        #Process log
        process_log(file_path, batch_size)

        #Delete downloaded file
        delete_file(file_path)

        if "log_keeper" in conf:
            log_keeper = conf["log_keeper"]

            url = '/'.join([log_keeper["url"], log_keeper["endpoint"]])

            if not notify_log_keeper(url, file_name, status="processed"):
                add_log_keeper_file(file_name)

        if "delete" in conf["sqs"]:
            if conf["sqs"]["delete"] is True:
                aws.delete_message_from_queue(region, queue_name, message)

        notify_log_keeper_of_backlogs(url)

    else:

        Logger.error("Couldn't retrieve file from SQS queue. Stopping process")

    return


if __name__ == "__main__":
    run()