import os
import os.path
import tempfile
import datetime

import luigi
import luigi.file

from tapirus import constants
from tapirus.core import aws
from tapirus.dao import RecordDAO, LogFileDAO
from tapirus.entities import Record, LogFile
from tapirus.utils import config
from tapirus.utils.logger import Logger

if os.name == 'posix':
    tempfile.tempdir = '/tmp'
else:
    tempfile.tempdir = 'out'


class DownloadedRecordTarget(luigi.Target):

    def __init__(self, date, hour):
        self.date = date
        self.hour = hour

    def exists(self):

        timestamp = datetime.datetime(
            year=self.date.year,
            month=self.date.month,
            day=self.date.day,
            hour=self.hour
        )

        if RecordDAO.exists(timestamp=timestamp):

            record = RecordDAO.read(timestamp=timestamp)

            if record.status in (constants.STATUS_PENDING, constants.STATUS_NOT_FOUND):
                return False

        else:

            record = Record(id=None, timestamp=timestamp, last_updated=None,
                            status=constants.STATUS_PENDING,
                            uri=None
                            )

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
#             if record.status in ('PENDING',):
#                 return False
#
#         else:
#
#             record = Record(None, self.date, self.hour, None, 'PENDING', None)
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

        timestamp = datetime.datetime(
            year=self.date.year,
            month=self.date.month,
            day=self.date.day,
            hour=self.hour
        )

        s3 = config.get('s3')
        bucket = s3['bucket']
        prefix = s3['prefix']

        pattern = ''.join([prefix, str(self.date), '-', '{:02d}'.format(self.hour)])

        keys = aws.S3.list_bucket_keys(bucket, pattern)
        files = []

        record = RecordDAO.read(timestamp=timestamp)

        for key in keys:

            s3_key = '/'.join([bucket, key])
            filename = os.path.join(tempfile.gettempdir(), key)

            if not os.path.exists(os.path.dirname(filename)):

                Logger.debug('Creating directory {0}'.format(os.path.dirname(filename)))

                os.makedirs(os.path.dirname(filename))

            files.append(filename)

            Logger.info('Downloading {0} from bucket {1}'.format(key, bucket))

            aws.S3.download_file(s3_key, filename)

            logfile = LogFile(id=None, record=record.id, filepath=filename)

            _ = LogFileDAO.create(logfile)

        if not files or not keys:
            record.status = constants.STATUS_NOT_FOUND
            Logger.info('No logs found for timestamp {0}-{1}'.format(self.date, self.hour))
        elif files:
            Logger.info('Found {0} logs for timestamp {0}-{1}'.format(self.date, self.hour))
            record.status = constants.STATUS_DOWNLOADED

        assert isinstance(record, Record)
        _ = RecordDAO.update(record)


class ParseLogs(luigi.Task):

    date = luigi.DateParameter()
    hour = luigi.IntParameter()


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


# if __name__ == '__main__':
#
#     print(aws.S3.list_bucket_keys('trackings', pattern='action-logs/ER1VHJSBZAAAA.2015-05-11-11'))
#
#     exists = aws.S3.exists('trackings/action-logs/ER1VHJSBZAAAA.2015-03-21-06.742c8d99.gz')
#
#     print(exists)

if __name__ == '__main__':

    luigi.run()
