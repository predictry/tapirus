__author__ = 'guilherme'

import json
import os
import tempfile
import argparse

from tapirus import Logger
from tapirus.core import errors, aws
from tapirus.processor import log, log_keeper
from tapirus.utils import config, multitasking, io
from tapirus.transformers.neo4j import Neo4jEventHandler
from tapirus.utils.access import get_tenant_prediction_access_key
from tapirus.transformers.predictionio import PredictionIOEventHandler


NEO4_SERVICE = "neo4j"
PREDICTION_IO_SERVICE = "predictionio"

TRANSFORMERS = lambda x: {
    NEO4_SERVICE: Neo4jEventHandler,
    PREDICTION_IO_SERVICE: PredictionIOEventHandler
}[x]


def neo4j_service(entries):

    service = Neo4jEventHandler()

    service.handle_events(entries)


def prediction_io_service(entries):

    tenants = dict()

    for entry in entries:

        tenant_id = entry["tenant_id"]

        if entry["tenant_id"] not in tenants:
            tenants[tenant_id] = list()

        tenants[tenant_id].append(entry)

    for k, v in tenants.items():

        cfg = config.get("predictionio")
        access_key = get_tenant_prediction_access_key(k)
        url = cfg["url"]
        threads = cfg["threads"]
        qsize = cfg["qsize"]

        if access_key is None:
            Logger.info("No key was found for tenant `{0}`. Skipping data entry")
            return

        service = PredictionIOEventHandler(access_key=access_key, url=url, threads=threads, qsize=qsize)

        service.handle_events(v)


def run(service):
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
                if sqs["delete"].lower() == "true":

                    if aws.delete_message_from_queue(region, queue_name, message):
                        Logger.info("Deleted file `{0}` from queue `{1}`".format(file_name, queue_name))
                    else:
                        Logger.info("Failed to delete file `{0}` from queue `{1}`".format(file_name, queue_name))
                else:
                    Logger.info("Not deleting `{0}` from queue `{1}`".format(file_name, queue_name))

            else:

                Logger.info("Delete option was not found in queue configuration. No action taken")

            return

        #Process log
        try:

            entries = log.process_log(file_path)

            if service == NEO4_SERVICE:
                neo4j_service(entries)
            elif service == PREDICTION_IO_SERVICE:
                prediction_io_service(entries)

        except errors.ProcessFailure:

            io.delete_file(file_path)

            if os.path.exists(file_path) is False:
                Logger.info("Deleted file `{0}`".format(file_path))
            else:
                Logger.info("Failed to delete file `{0}`".format(file_path))

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
                if sqs["delete"].lower() == "true":

                    if aws.delete_message_from_queue(region, queue_name, message):
                        Logger.info("Deleted file `{0}` from queue `{1}`".format(file_name, queue_name))
                    else:
                        Logger.info("Failed to delete file `{0}` from queue `{1}`".format(file_name, queue_name))
                else:
                    Logger.info("Not deleting `{0}` from queue `{1}`".format(file_name, queue_name))

            else:

                Logger.info("Delete option was not found in queue configuration. No action taken")

    else:

        Logger.error("Couldn't retrieve file from SQS queue. Stopping process")

    return


if __name__ == "__main__":

    harv = config.get("harvester")

    interval = int(harv["interval"])
    worker = harv["service"]

    multitasking.repeat(interval, run, args=(worker,), wait=True)
