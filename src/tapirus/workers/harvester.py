__author__ = 'guilherme'

#todo: Make this operation configurable (e.g. if clientT sends actionX read it this way
#todo: Unit tests

import os
import os.path
import json
import gzip
import tempfile
import traceback

import requests
import requests.exceptions

from tapirus.utils import jsonuri
from tapirus.utils import config
from tapirus.core.db import neo4j
from tapirus.core import aws
from tapirus.operator import schema
from tapirus.utils.logger import Logger
from tapirus.utils import io

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

                queries.extend(schema.generate_queries(date, time, ip, path, payload))
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


def is_acceptable_data_type(e):
    """

    :param e:
    :return:
    """

    #todo: remove func

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
        io.delete_file(file_path)

        if "log_keeper" in conf:
            log_keeper = conf["log_keeper"]

            url = '/'.join([log_keeper["url"], log_keeper["endpoint"]])

            if not notify_log_keeper(url, file_name, status="processed"):
                add_log_keeper_file(file_name)
            else:
                notify_log_keeper_of_backlogs(url)

        if "delete" in conf["sqs"]:
            if conf["sqs"]["delete"] is True:
                aws.delete_message_from_queue(region, queue_name, message)

    else:

        Logger.error("Couldn't retrieve file from SQS queue. Stopping process")

    return


if __name__ == "__main__":
    run()