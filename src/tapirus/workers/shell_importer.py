__author__ = 'guilherme'

import os
import os.path
import json
import tempfile
import subprocess
import shutil
import uuid

from tapirus.core import aws
from tapirus.utils import io
from tapirus.utils import config
from tapirus.utils.logger import Logger
from tapirus.processor import log
from tapirus.processor import log_keeper
from tapirus.core import errors

NEO4J_SHELL = "neo4j-shell"
PATHS = ["/usr/local/bin"]


def neo4j_shell_import(queries):

    if os.name == 'posix':
        for path in PATHS:
            os.environ["PATH"] = ''.join([os.environ["PATH"], os.pathsep, path])

    neo4j_shell_path = shutil.which(NEO4J_SHELL)

    if not neo4j_shell_path:
        raise ChildProcessError("Couldn't find {0} executable path".format(NEO4J_SHELL))

    #use random uuid for file name. avoid race conditions
    file_name = str(uuid.uuid4())
    tmp_folder = tempfile.gettempdir()
    file_path = os.path.join(tmp_folder, file_name)

    Logger.info("Writing queries to file `{0}`".format(file_path))

    with open(file_path, "w", encoding="UTF-8") as f:

        for query in queries:

            for k, v in query.parameters.items():
                if type(v) is str:
                    value = repr(v).strip("'")
                    s = u"\nexport {0}={1}\n".format(k, value)
                else:
                    s = u"\nexport {0}={1}\n".format(k, v)
                f.write(s)

            s = u"{0};\n".format(query.query)
            f.write(s)

    p = subprocess.Popen([neo4j_shell_path, "-file", file_path], stdout=subprocess.PIPE, shell=False)

    output, err = p.communicate()

    io.delete_file(file_path)

    if p.returncode == 1:

        msg = "Error importing data via {0}:\n\t{1}".format(NEO4J_SHELL, output)
        Logger.error(msg)

        raise ChildProcessError(msg)

    elif p.returncode == 0:

        Logger.info("Successfully executed [{0}] queries".format(len(queries)))


def run():
    """

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

        #Download file from S3
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
        log.process_log(file_path, batch_size, neo4j_shell_import)

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