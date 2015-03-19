__author__ = 'guilherme'

#todo: Make this operation configurable (e.g. if clientT sends actionX read it this way
#todo: Unit tests

import os
import os.path
import json
import tempfile

from tapirus.utils import config
from tapirus.core.db import neo4j
from tapirus.core import aws
from tapirus.processor import log
from tapirus.processor import log_keeper
from tapirus.utils.logger import Logger
from tapirus.utils import io


def execute_batch_transactions(queries):

    neo4j.run_batch_query(queries, commit=True, timeout=300)


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

        #Download file from
        aws.download_log_from_s3(s3_file_path, file_path)

        #Process log
        log.process_log(file_path, batch_size, execute_batch_transactions)

        #Delete downloaded file
        io.delete_file(file_path)

        if os.path.exists(file_path) is False:
            Logger.info("Deleted file `{0}`".format(file_path))
        else:
            Logger.warning("Failed to delete file `{0}`".format(file_path))

        if "log_keeper" in conf:
            log_keeper_conf = conf["log_keeper"]

            url = '/'.join([log_keeper_conf["url"], log_keeper_conf["endpoint"]])

            if not log_keeper.notify_log_keeper(url, file_name, status="processed"):
                log_keeper.add_log_keeper_file(file_name)
            else:
                log_keeper.notify_log_keeper_of_backlogs(url)

        if "delete" in conf["sqs"]:
            if conf["sqs"]["delete"] is True:

                if aws.delete_message_from_queue(region, queue_name, message):
                    Logger.info("Deleted file `{0}` from queue `{1}`".format(file_name, queue_name))
                else:
                    Logger.info("Failed to delete file `{0}` from queue `{1}`".format(file_name, queue_name))

    else:

        Logger.error("Couldn't retrieve file from SQS queue. Stopping process")

    return


if __name__ == "__main__":
    run()