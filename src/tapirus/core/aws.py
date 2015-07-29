import boto.sqs
from boto.sqs.message import Message
from boto.s3.connection import S3Connection
from boto.s3.key import Key
from boto.exception import S3ResponseError

from tapirus.core import errors
from tapirus.utils.logger import Logger


class S3(object):

    @classmethod
    def list_bucket_keys(cls, bucketname, pattern=""):

        conn = S3Connection()

        bucket = conn.get_bucket(bucketname)

        rs = bucket.list(prefix=pattern)

        return [key.name for key in rs]

    @classmethod
    def list_buckets(cls):

        conn = S3Connection()

        buckets = conn.get_all_buckets()

        return [b.name for b in buckets]

    @classmethod
    def download_file(cls, s3_key, file_path):
        """

        :param s3_key:
        :param file_path:
        :return:
        """

        conn = S3Connection()

        bucket = conn.get_bucket(s3_key.split('/')[0])

        key = Key(bucket)
        key.key = '/'.join(s3_key.split('/')[1:])

        Logger.info("Downloading file from S3: {0}".format(s3_key))

        try:
            key.get_contents_to_filename(file_path)
        except boto.exception.S3ResponseError as exc:

            Logger.error(exc)

            return file_path, exc.status
        else:

            return file_path, 200

    @classmethod
    def upload_file(cls, s3_key, file_path):

        conn = S3Connection()

        bucket = conn.get_bucket(s3_key.split('/')[0])

        key = Key(bucket)
        key.key = '/'.join(s3_key.split('/')[1:])

        try:
            key.set_contents_from_filename(file_path)
        except boto.exception.S3ResponseError as exc:

            Logger.error(exc)

            return file_path, exc.status

        else:

            return file_path, 200

    @classmethod
    def exists(cls, s3_key):

        conn = S3Connection()
        bucket = conn.get_bucket(s3_key.split('/')[0])

        key = Key(bucket)
        key.key = '/'.join(s3_key.split('/')[1:])

        try:
            return key.exists()
        except boto.exception.S3ResponseError as exc:

            Logger.error(exc)
            raise errors.ProcessFailureError


class SQS(object):

    @classmethod
    def read(cls, region, queue_name, visibility_timeout, count=1):
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

    @classmethod
    def delete_message(cls, region, queue_name, msg):
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
