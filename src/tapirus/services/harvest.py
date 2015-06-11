import os
import os.path
import tempfile
import datetime
import json

import luigi
import luigi.file

from tapirus import constants
from tapirus.core import aws
from tapirus.dao import RecordDAO, LogFileDAO
from tapirus.entities import Record, LogFile
from tapirus.processor import log
from tapirus.model import store
from tapirus.utils import io
from tapirus.utils import config
from tapirus.utils.logger import Logger

if os.name == 'posix':
    tempfile.tempdir = '/tmp'
else:
    tempfile.tempdir = 'out'


class _DownloadedRecordTarget(luigi.Target):

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


class _ProcessedRecordTarget(luigi.Target):

    def __init__(self, date, hour):

        self.date = date
        self.hour = hour

    def exists(self):

        # check if file exists locally
        timestamp = datetime.datetime(
            year=self.date.year,
            month=self.date.month,
            day=self.date.day,
            hour=self.hour
        )

        s3 = config.get('s3')
        bucket = s3['bucket']
        folder = s3['records']

        year = timestamp.date().year
        month = '{:02d}'.format(timestamp.date().month)
        day = '{:02d}'.format(timestamp.date().day)
        hour = '{:02d}'.format(timestamp.hour)

        filename = "{year}-{month}-{day}-{hour}.json".format(
            year=year,
            month=month,
            day=day,
            hour=hour
        )

        uri = '{bucket}/{folder}/{year}/{month}/{day}/{file}.json'.format(
            bucket=bucket,
            folder=folder,
            year=year,
            month=month,
            day=day,
            file=filename
        )

        return aws.S3.exists(s3_key=uri)


class DownloadRecordLogsTask(luigi.Task):

    date = luigi.DateParameter()
    hour = luigi.IntParameter()

    def output(self):

        return _DownloadedRecordTarget(date=self.date, hour=self.hour)

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


class ProcessRecordTask(luigi.Task):

    date = luigi.DateParameter()
    hour = luigi.IntParameter()

    def requires(self):

        return DownloadRecordLogsTask(date=self.date, hour=self.hour)

    def output(self):

        return _ProcessedRecordTarget(date=self.date, hour=self.hour)

    def run(self):

        # TODO: read log list
        # TODO: for each file
        # TODO: parse and append log entries (users, items, sessions, agents, events) into separate files
        # TODO: combine output from files into a single file, and delete separate files
        # TODO: upload file to S3
        # TODO: delete separate files

        timestamp = datetime.datetime(
            year=self.date.year,
            month=self.date.month,
            day=self.date.day,
            hour=self.hour
        )

        record = RecordDAO.read(timestamp=timestamp)

        record.status = constants.STATUS_PENDING
        _ = RecordDAO.update(record)

        logfiles = LogFileDAO.get_logfiles(record_id=record.id)

        errors = []

        prefix = '{0}-{1}'.format(str(self.date), self.hour)

        sessionfp = os.path.join(tempfile.gettempdir(), '-'.join([prefix, 'session']))
        agentfp = os.path.join(tempfile.gettempdir(), '-'.join([prefix, 'agent']))
        userfp = os.path.join(tempfile.gettempdir(), '-'.join([prefix, 'user']))
        itemfp = os.path.join(tempfile.gettempdir(), '-'.join([prefix, 'item']))
        actionfp = os.path.join(tempfile.gettempdir(), '-'.join([prefix, 'action']))

        # remove files if they exist, since they'll be appended to
        for file in (sessionfp, agentfp, userfp, itemfp, actionfp):
            if os.path.exists(file):
                os.remove(file)

        for logfile in logfiles:

            try:
                payloads = log.process_log(logfile.filepath, errors=errors)

                for payload in payloads:
                    session, agent, user, items, actions = store.parse_entities_from_data(payload)

                    assert isinstance(session, store.Session)
                    assert isinstance(agent, store.Agent)
                    assert isinstance(user, store.User)
                    assert isinstance(items, set)
                    for item in items:
                        assert isinstance(item, store.Item)
                    assert isinstance(actions, list)
                    for action in actions:
                        assert isinstance(action, store.Action)

                    with open(sessionfp, 'a') as fp:
                        json.dump(session.properties, fp, cls=io.DateTimeEncoder)
                        fp.write('\n')

                    with open(agentfp, 'a') as fp:
                        json.dump(agent.properties, fp, cls=io.DateTimeEncoder)
                        fp.write('\n')

                    with open(userfp, 'a') as fp:
                        json.dump(user.properties, fp, cls=io.DateTimeEncoder)
                        fp.write('\n')

                    with open(itemfp, 'a') as fp:
                        for item in items:
                            json.dump(item.properties, fp, cls=io.DateTimeEncoder)
                            fp.write('\n')

                    with open(actionfp, 'a') as fp:
                        for action in actions:
                            json.dump(action.properties, fp, cls=io.DateTimeEncoder)
                            fp.write('\n')

            except EOFError:
                pass
            except OSError:
                pass

        sessions = []
        agents = []
        users = []
        items = []
        actions = []

        filename = os.path.join(tempfile.gettempdir(), '.'.join([prefix, 'json']))

        if os.path.exists(filename):
            os.remove(filename)

        with open(filename, 'w') as fp:

            metadata = {
                'date': str(timestamp.date()),
                'hour': timestamp.hour,
                'processed': str(datetime.datetime.now())
            }

            with open(sessionfp, 'r') as inp:

                for line in inp:
                    session = json.loads(line, encoding='UTF-8')

                    sessions.append(session)

            with open(agentfp, 'r') as inp:

                for line in inp:
                    agent = json.loads(line, encoding='UTF-8')
                    agents.append(agent)

            with open(userfp, 'r') as inp:

                for line in inp:
                    user = json.loads(line, encoding='UTF-8')
                    users.append(user)

            with open(itemfp, 'r') as inp:

                for line in inp:
                    item = json.loads(line, encoding='UTF-8')
                    items.append(item)

            with open(itemfp, 'r') as inp:

                for line in inp:
                    action = json.loads(line, encoding='UTF-8')
                    actions.append(action)

            data = dict(
                metadata=metadata,
                sessions=sessions,
                agents=agents,
                users=users,
                items=items,
                actions=actions
            )

            json.dump(data, fp)

        def upload(timestamp, filepath, record=record):

            s3 = config.get('s3')
            bucket = s3['bucket']
            folder = s3['records']

            year = timestamp.date().year
            month = '{:02d}'.format(timestamp.date().month)
            day = '{:02d}'.format(timestamp.date().day)
            hour = '{:02d}'.format(timestamp.hour)

            filename = "{year}-{month}-{day}-{hour}.json".format(
                year=year,
                month=month,
                day=day,
                hour=hour
            )

            uri = '{bucket}/{folder}/{year}/{month}/{day}/{file}.json'.format(
                bucket=bucket,
                folder=folder,
                year=year,
                month=month,
                day=day,
                file=filename
            )

            r, status = aws.S3.upload_file(uri, filepath)

            if status == 200:
                record.status = constants.STATUS_PROCESSED
                record.uri = uri
                _ = RecordDAO.update(record)

                Logger.info(
                    'Uploaded file {0} to {1}'.format(
                        filepath, uri
                    )
                )

            else:

                Logger.error('Error uploading file to S3: \n{0}'.format(status))

        upload(timestamp=timestamp, filepath=filename, record=record)

        for file in (sessionfp, agentfp, userfp, itemfp, actionfp, filename):
            if os.path.exists(file):
                os.remove(file)


if __name__ == '__main__':

    luigi.run()
