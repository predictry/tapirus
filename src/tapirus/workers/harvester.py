__author__ = 'guilherme'

import os
import json
import gzip
import boto.sqs
from boto.sqs.message import Message
from boto.s3.connection import S3Connection
from boto.s3.key import Key

from tapirus.utils import jsonuri
import timeit


SRC_ROOT = os.path.dirname(os.path.abspath(__file__))
CONFIG_FILE = os.path.join(SRC_ROOT, "../../../config.json")

LOG_SEPARATOR = "\t"


def get_file_from_queue():

    with open(CONFIG_FILE, "r") as f:
        config = json.load(f)
        conf = config["sqs"]

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

    return "/tmp/ER1VHJSBZAAAA.2015-01-12-08.3cd14307.gz"


def parse_log_records(filename):

    with gzip.open(filename, 'rb') as f:

        c = 0

        for line in f:

            #print(line.decode(encoding="utf-8").split("\t"))
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

            l = line.decode(encoding="utf-8").split(LOG_SEPARATOR)
            #print(l)

            if len(l) >= 12:

                c += 1

                date, time, ip, path, status = l[0], l[1], l[4], l[7], int(l[8])

                if ".gif" not in path or status not in [0, 200, 304]:
                    continue

                try:
                    payload = jsonuri.deserialize(l[11])
                except ValueError:
                    print("Error: [{0}]".format(l[11]))
                    continue

                with open("out.json", "w") as tmp:
                    json.dump(payload, tmp, indent=4)

                print("[`{0}`][`{1}`][`{2}`][{3}]".format(date, time, status, payload))

            if c >= 16:
                break


def insert_data_to_db():
    #validate
    #check site domain
    #validate
    pass


if __name__ == "__main__":

    #filename = download_log_from_s3(None, None)
    filename = "/tmp/ER1VHJSBZAAAA.2015-01-15-09.8b10c614.gz"

    parse_log_records(filename)
