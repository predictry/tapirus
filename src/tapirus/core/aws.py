__author__ = 'guilherme'

import boto.sqs
from boto.sqs.message import Message
from boto.s3.connection import S3Connection
from boto.s3.key import Key
from boto.exception import S3ResponseError

from tapirus.utils.logger import Logger


def download_file_from_s3(s3_key, file_path):
    """

    :param s3_key:
    :param file_path:
    :return:
    """

    conn = S3Connection()

    bucket = conn.get_bucket(s3_key.split("/")[0])

    key = Key(bucket)
    key.key = '/'.join(s3_key.split("/")[1:])

    Logger.info("Downloading file from S3: {0}".format(s3_key))

    try:
        key.get_contents_to_filename(file_path)
    except boto.exception.S3ResponseError as exc:

        Logger.error(exc)

        return file_path, exc.status
    else:

        return file_path, 200


def read_queue(region, queue_name, visibility_timeout, count=1):
    """

    :return:
    """

    conn = boto.sqs.connect_to_region(region)

    queue = conn.get_queue(queue_name)
    vs_timeout = int(visibility_timeout)

    messages = []

    if queue:
        rs = queue.get_messages(count, visibility_timeout=vs_timeout)

        for msg in rs:
            messages.append(msg)

    else:
        Logger.error("Couldn't read from queue '{0}'@'{1}'".format(queue_name, region))

    return messages


def delete_message_from_queue(region, queue_name, msg):
    """

    :param msg:
    :return:
    """

    conn = boto.sqs.connect_to_region(region)

    queue = conn.get_queue(queue_name)

    if queue:
        rs = queue.delete_message(msg)

        return rs

    else:
        Logger.error("Couldn't read from queue '{0}'@'{1}'".format(queue_name, region))

        return False
