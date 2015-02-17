__author__ = 'guilherme'

import os
import os.path
import json
import tempfile
import subprocess
import shutil

from tapirus.core import aws
from tapirus.utils import io
from tapirus.utils import config
from tapirus.utils.logger import Logger
from tapirus.processor import log
from tapirus.processor import log_keeper

NEO4J_SHELL = "neo4j-shell"
PATHS = ["/usr/local/bin"]


def neo4j_shell_import(queries):

    for path in PATHS:
        os.environ["PATH"] = ''.join([os.environ["PATH"], os.pathsep, path])

    neo4j_shell_path = shutil.which(NEO4J_SHELL)

    if not neo4j_shell_path:
        raise ChildProcessError("Couldn't find {0} executable path".format(NEO4J_SHELL))

    file_path = "/tmp/{0}".format('__'.join([__name__, "cypher.query"]))

    with open(file_path, "w", encoding="UTF-8") as f:

        for query in queries:

            for k, v in query.parameters.items():
                if type(v) is str:
                    s = u"export {0}={1}\n".format(k, repr(v))
                else:
                    s = u"export {0}={1}\n".format(k, v)
                f.write(s)

            s = u"{0};\n".format(query.query)
            f.write(s)

    p = subprocess.Popen([neo4j_shell_path, "-file", file_path], stdout=subprocess.PIPE, shell=False)

    output, err = p.communicate()

    if p.returncode == 1:

        Logger.error("Error importing data via {0}:\n\t{1}".format(NEO4J_SHELL, err))

        raise ChildProcessError("There a problem executing the cypher queries.")

    elif p.returncode == 0:

        Logger.info("Successfully executed [{0}] queries".format(len(queries)))

    io.delete_file(file_path)


def run():
    """

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
        log.process_log(file_path, batch_size, neo4j_shell_import)

        #Delete downloaded file
        io.delete_file(file_path)

        if "log_keeper" in conf:
            log_keeper_conf = conf["log_keeper"]

            url = '/'.join([log_keeper_conf["url"], log_keeper_conf["endpoint"]])

            if not log_keeper.notify_log_keeper(url, file_name, status="processed"):
                log_keeper.add_log_keeper_file(file_name)
            else:
                log_keeper.notify_log_keeper_of_backlogs(url)

        if "delete" in conf["sqs"]:
            if conf["sqs"]["delete"] is True:
                aws.delete_message_from_queue(region, queue_name, message)

    else:

        Logger.error("Couldn't retrieve file from SQS queue. Stopping process")

    return


if __name__ == "__main__":
    run()