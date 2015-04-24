__author__ = 'guilherme'

import os
import os.path
import json
import tempfile
import time

import py2neo.cypher.error.transaction
from py2neo.packages.httpstream import http

from tapirus.utils import config
from tapirus.core.db import neo4j
from tapirus.core import aws
from tapirus.processor import log
from tapirus.processor import log_keeper
from tapirus.utils.logger import Logger
from tapirus.utils import io
from tapirus.core import errors


def execute_batch_transactions(queries):

    try:

        neo4j.run_batch_query(queries, commit=True, timeout=60)

    except py2neo.cypher.error.transaction.DeadlockDetected as exc:

        Logger.error(exc)

        nap_time = 10

        Logger.info("Sleeping for {0}s".format(nap_time))
        time.sleep(10)

        raise errors.ProcessFailure("Neo4j deadlock")

    except http.SocketError as exc:

        Logger.error(exc)

        raise errors.ProcessFailure("Socket timeout")


def run():
    """
    Execute harvesting procedure.
    :return:
    """

    #Read configuration
    try:
        sqs = config.get("sqs")
        queue_manager = config.get("queue-manager")
        harv = config.get("harvester")
    except errors.ConfigurationError as exc:
        Logger.error(exc)
        Logger.critical("Aborting `Queue Read` operation. Couldn't read app configuration `")
        return

    region = sqs["region"]
    queue_name = sqs["queue"]
    visibility_timeout = int(sqs["visibility-timeout"])
    count = 1
    batch_size = int(harv["batch-size"])

    #Get name of file to download from SQS
    messages = aws.read_queue(region, queue_name, visibility_timeout, count)

    if messages and len(messages) > 0:

        msg = messages[0]
        f = json.loads(msg.get_body(), encoding="utf-8")

        s3_file_path, message = f["data"]["full_path"], msg

        file_name = s3_file_path.split("/")[-1]
        file_path = os.path.join(tempfile.gettempdir(), file_name)

        #Download file from
        _, status = aws.download_file_from_s3(s3_file_path, file_path)

        if os.path.exists(file_path) is False or os.path.isfile(file_path) is False:

            Logger.warning("File {0} wasn't downloaded".format(file_path))

            if "delete" in sqs and status == 404:
                if sqs["delete"] is True:

                    if aws.delete_message_from_queue(region, queue_name, message):
                        Logger.info("Deleted file `{0}` from queue `{1}`".format(file_name, queue_name))
                    else:
                        Logger.info("Failed to delete file `{0}` from queue `{1}`".format(file_name, queue_name))

            return

        #Process log
        try:
            log.process_log(file_path, batch_size, execute_batch_transactions)

        except errors.ProcessFailure:

            io.delete_file(file_path)

            if os.path.exists(file_path) is False:
                Logger.info("Deleted file `{0}`".format(file_path))
        else:

            #Delete downloaded file
            io.delete_file(file_path)

            if os.path.exists(file_path) is False:
                Logger.info("Deleted file `{0}`".format(file_path))
            else:
                Logger.warning("Failed to delete file `{0}`".format(file_path))

            url = '/'.join([queue_manager["url"], queue_manager["endpoint"]])

            if not log_keeper.notify_log_keeper(url, file_name, status="processed"):
                log_keeper.add_log_keeper_file(file_name)
            else:
                log_keeper.notify_log_keeper_of_backlogs(url)

            if "delete" in sqs:
                if sqs["delete"] is True:

                    if aws.delete_message_from_queue(region, queue_name, message):
                        Logger.info("Deleted file `{0}` from queue `{1}`".format(file_name, queue_name))
                    else:
                        Logger.info("Failed to delete file `{0}` from queue `{1}`".format(file_name, queue_name))

    else:

        Logger.error("Couldn't retrieve file from SQS queue. Stopping process")

    return


if __name__ == "__main__":
    run()