import os
import os.path
import errno
import tempfile
import shutil
import csv
import json
import time

import luigi
import luigi.file

if os.name == 'posix':
    tempfile.tempdir = "/tmp"
else:
    tempfile.tempdir = "out"


import luigi
import luigi.file

from tapirus.core import aws
from tapirus.dao import RecordDAO, LogFileDAO
from tapirus.entities import Record, LogFile
from tapirus.core import errors
from tapirus import constants
from tapirus.utils import config
from tapirus.utils.logger import Logger


class DownloadedRecordTarget(luigi.Target):

    def __init__(self, date, hour):
        self.date = date
        self.hour = hour

    def exists(self):

        if RecordDAO.exists(self.date, self.hour):

            record = RecordDAO.read(self.date, self.hour)

            if record.status == constants.STATUS_PENDING:
                return False

        else:

            record = Record(None, self.date, self.hour, None, constants.STATUS_PENDING, None)

            _ = RecordDAO.create(record)

            return False

        return True
#
#
# class ExistingRecordTarget(luigi.Target):
#
#     def __init__(self, date, hour):
#         self.date = date
#         self.hour = hour
#
#     def exists(self):
#
#         if RecordDAO.exists(self.date, self.hour):
#
#             record = RecordDAO.read(self.date, self.hour)
#
#             if record.status in ("PENDING",):
#                 return False
#
#         else:
#
#             record = Record(None, self.date, self.hour, None, "PENDING", None)
#
#             _ = RecordDAO.create(record)
#
#             return False
#
#         return True


class DownloadLogsTask(luigi.Task):

    date = luigi.DateParameter()
    hour = luigi.IntParameter()

    def output(self):

        return DownloadedRecordTarget(self.date, self.hour)

    def run(self):

        s3 = config.get('s3')
        bucket = s3['bucket']
        prefix = s3['prefix']

        pattern = ''.join([prefix, str(self.date), '-', '{:02d}'.format(self.hour)])

        keys = aws.S3.list_bucket_keys(bucket, pattern)
        files = []

        record = RecordDAO.read(self.date, self.hour)

        for key in keys:

            s3_key = '/'.join([bucket, key])
            filename = os.path.join(tempfile.gettempdir(), key)
            files.append(filename)
            aws.S3.download_file(s3_key, filename)

            logfile = LogFile(None, record.id, filename)

            _ = LogFileDAO.create(logfile)

        record.status = constants.STATUS_DOWNLOADED

        assert isinstance(record, Record)
        RecordDAO.update(record)


# class HarvestLogsTask(luigi.Task):
#
#     date = luigi.DateParameter()
#     hour = luigi.IntParameter()
#
#     def output(self):
#
#         return UnproceseedRecordTarget(self.date, self.hour)
#
#     def run(self):
#
#         s3 = config.get('s3')
#         bucket = s3['bucket']
#         prefix = s3['prefix']
#
#         pattern = ''.join([prefix, str(self.date), '-', '{:02d}'.format(self.hour)])
#
#         keys = aws.S3.list_bucket_keys(bucket, pattern)
#         files = []
#
#         for key in keys:
#
#             s3_key = '/'.join(bucket, key)
#             filename = os.path.join(tempfile.gettempdir(), key)
#             files.append(filename)
#             aws.S3.download_file(s3_key, filename)
#
#         #process file


# if __name__ == "__main__":
#
#     print(aws.S3.list_bucket_keys('trackings', pattern='action-logs/ER1VHJSBZAAAA.2015-05-11-11'))
#
#     exists = aws.S3.exists('trackings/action-logs/ER1VHJSBZAAAA.2015-03-21-06.742c8d99.gz')
#
#     print(exists)

if __name__ == "__main__":

    luigi.run()
