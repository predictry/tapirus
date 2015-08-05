import os
import os.path
import tempfile
import datetime
import json
import gzip
import concurrent.futures

import luigi
import luigi.file
import tapirus.entities
import tapirus.repo.models
from tapirus import constants
from tapirus.core import aws
from tapirus.core import errors as exceptions
from tapirus.repo.dao import RecordDAO, TenantRecordDAO, LogFileDAO
from tapirus.repo.models import Record, TenantRecord, LogFile, Error
from tapirus.processor import log
from tapirus.parser.v1 import pl
from tapirus.utils import io
from tapirus.utils import config
from tapirus.utils.logger import Logger


if os.name == 'posix':
    tempfile.tempdir = '/tmp'
else:
    tempfile.tempdir = 'out'


# TODO: run log read workflow
# TODO: open files once per process...


class _DownloadedRecordTarget(luigi.Target):
    def __init__(self, date, hour):
        self.date = date
        self.hour = hour

    def exists(self):

        Logger.info(
            'Checking Download status for Record @{0}-{1}'.format(
                str(self.date), self.hour
            )
        )

        timestamp = datetime.datetime(
            year=self.date.year,
            month=self.date.month,
            day=self.date.day,
            hour=self.hour
        )

        if RecordDAO.exists(timestamp=timestamp):

            record = RecordDAO.read(timestamp=timestamp)

            if record.status in (constants.STATUS_PENDING,):
                return False

        else:

            record = Record(id=None, timestamp=timestamp, last_updated=None,
                            status=constants.STATUS_PENDING)

            _ = RecordDAO.create(record)

            return False

        return True


class _ProcessedRecordTarget(luigi.Target):
    def __init__(self, date, hour):

        self.date = date
        self.hour = hour

    def exists(self):

        Logger.info(
            'Checking Processing status for Record @{0}-{1}'.format(
                str(self.date), self.hour
            )
        )

        timestamp = datetime.datetime(
            year=self.date.year,
            month=self.date.month,
            day=self.date.day,
            hour=self.hour
        )

        result = True

        if RecordDAO.exists(timestamp=timestamp):

            record = RecordDAO.read(timestamp=timestamp)

            if record.status != constants.STATUS_NOT_FOUND:

                if not [x for x in TenantRecordDAO.find(timestamp=timestamp)]:
                    result = False

                for tenant_record in TenantRecordDAO.find(timestamp=timestamp):

                    if aws.S3.exists(s3_key=tenant_record.uri):
                        pass
                    else:

                        tenant_record.uri = None
                        _ = TenantRecordDAO.update(tenant_record)

                        result = False
            else:
                result = False
        else:
            result = False

        return result


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

        logfiles = [x for x in LogFileDAO.get_logfiles(record.id)]

        for key in keys:

            s3_key = '/'.join([bucket, key])
            filename = key.split('/')[-1]
            filepath = os.path.join(tempfile.gettempdir(), filename)

            if not os.path.exists(os.path.dirname(filepath)):
                Logger.debug('Creating directory {0}'.format(os.path.dirname(filepath)))

                os.makedirs(os.path.dirname(filepath))

            files.append(filepath)

            Logger.info('Downloading {0} from bucket {1}'.format(key, bucket))

            aws.S3.download_file(s3_key, filepath)

            if filename not in [x.log for x in logfiles]:

                logfile = LogFile(id=None, record=record.id, log=filename, filepath=filepath)
                _ = LogFileDAO.create(logfile)

            else:

                for logfile in logfiles:

                    if logfile.log == filename:
                        logfile.filepath = filepath
                        _ = LogFileDAO.update(logfile)
                        break

        record.last_updated = datetime.datetime.utcnow()

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

        # read log list
        # for each file
        # parse and append log entries (users, items, sessions, agents, events) into separate files
        # combine output from files into a single file, and delete separate files
        # compress file
        # upload file to S3
        # delete separate files

        timestamp = datetime.datetime(
            year=self.date.year,
            month=self.date.month,
            day=self.date.day,
            hour=self.hour
        )

        template = lambda x: (str(self.date), self.hour, x)

        record = RecordDAO.read(timestamp=timestamp)

        record.status = constants.STATUS_BUILDING
        _ = RecordDAO.update(record)

        logfiles = [x for x in LogFileDAO.get_logfiles(record_id=record.id)]

        if not logfiles:
            record.status = constants.STATUS_NOT_FOUND
            _ = RecordDAO.update(record)

            return

        errors = []

        prefix = '{0}-{1}-{2}'

        sessionfp = os.path.join(tempfile.gettempdir(), '-'.join([prefix, 'session']))
        agentfp = os.path.join(tempfile.gettempdir(), '-'.join([prefix, 'agent']))
        userfp = os.path.join(tempfile.gettempdir(), '-'.join([prefix, 'user']))
        itemfp = os.path.join(tempfile.gettempdir(), '-'.join([prefix, 'item']))
        actionfp = os.path.join(tempfile.gettempdir(), '-'.join([prefix, 'action']))

        tenants = []

        def upload(tenant, filepath):

            s3 = config.get('s3')
            bucket = s3['bucket']
            folder = s3['records']

            year = timestamp.date().year
            month = '{:02d}'.format(timestamp.date().month)
            day = '{:02d}'.format(timestamp.date().day)
            hour = '{:02d}'.format(timestamp.hour)

            filename = "{year}-{month}-{day}-{hour}-{tenant}.gz".format(
                year=year,
                month=month,
                day=day,
                hour=hour,
                tenant=tenant
            )

            dirname = os.path.dirname(filepath)

            gzfile = os.path.join(dirname, filename)

            with open(filepath, 'rb') as fp, gzip.open(gzfile, 'wb') as gz:

                gz.writelines(fp)

            uri = '{bucket}/{folder}/{year}/{month}/{day}/{file}'.format(
                bucket=bucket,
                folder=folder,
                year=year,
                month=month,
                day=day,
                file=filename
            )

            r, status = aws.S3.upload_file(uri, gzfile)

            os.remove(gzfile)

            if status == 200:

                if TenantRecordDAO.exists(tenant, timestamp):

                    tenant_record = TenantRecordDAO.read(tenant, timestamp)
                    tenant_record.uri = uri
                    TenantRecordDAO.update(tenant_record)
                else:
                    tenant_record = TenantRecord(id=None, tenant=tenant, timestamp=timestamp,
                                                 last_updated=datetime.datetime.utcnow(),
                                                 uri=uri)
                    TenantRecordDAO.create(tenant_record)

                Logger.info(
                    'Uploaded file {0} to {1}'.format(
                        gzfile, uri
                    )
                )
            else:

                Logger.error('Error uploading file to S3: \n{0}'.format(status))

            return status

        def pack(tenant):

            sessions = []
            agents = []
            users = []
            items = []
            actions = []

            filename = os.path.join(
                tempfile.gettempdir(),
                '.'.join([prefix.format(str(timestamp.date()), timestamp.hour, tenant), 'hdfs'])
            )

            Logger.info(
                'Creating record file {0} for tenant {1}'.format(
                    filename, tenant
                )
            )

            if os.path.exists(filename):
                Logger.info('Deleting file {0}'.format(filename))
                os.remove(filename)

            with open(filename, 'w') as fp:

                metadata = {
                    'date': str(timestamp.date()),
                    'hour': timestamp.hour,
                    'processed': str(datetime.datetime.now())
                }

                if os.path.exists(sessionfp.format(*template(tenant))):
                    with open(sessionfp.format(str(timestamp.date()), timestamp.hour, tenant), 'r') as inp:

                        for line in inp:
                            session = json.loads(line, encoding='UTF-8')

                            sessions.append(session)

                if os.path.exists(agentfp.format(*template(tenant))):
                    with open(agentfp.format(*template(tenant)), 'r') as inp:

                        for line in inp:
                            agent = json.loads(line, encoding='UTF-8')
                            agents.append(agent)

                if os.path.exists(userfp.format(*template(tenant))):
                    with open(userfp.format(*template(tenant)), 'r') as inp:

                        for line in inp:
                            user = json.loads(line, encoding='UTF-8')
                            users.append(user)

                if os.path.exists(itemfp.format(*template(tenant))):
                    with open(itemfp.format(*template(tenant)), 'r') as inp:

                        for line in inp:
                            item = json.loads(line, encoding='UTF-8')
                            items.append(item)

                if os.path.exists(actionfp.format(*template(tenant))):
                    with open(actionfp.format(*template(tenant)), 'r') as inp:

                        for line in inp:
                            action = json.loads(line, encoding='UTF-8')
                            actions.append(action)

                json.dump(dict(type="metadata", metadata=metadata), fp)
                fp.write('\n')

                for session in sessions:
                    data = dict(type="Session", data=session)
                    json.dump(data, fp)
                    fp.write('\n')

                for agent in agents:
                    data = dict(type="Agent", data=agent)
                    json.dump(data, fp)
                    fp.write('\n')

                for user in users:
                    data = dict(type="User", data=user)
                    json.dump(data, fp)
                    fp.write('\n')

                for item in items:
                    data = dict(type="Item", data=item)
                    json.dump(data, fp)
                    fp.write('\n')

                for action in actions:
                    data = dict(type="Action", data=action)
                    json.dump(data, fp)
                    fp.write('\n')

            return upload(tenant, filepath=filename)

        for logfile in logfiles:

            Logger.info(
                'Processing log file {0}'.format(
                    logfile.log
                )
            )

            try:
                payloads = log.process_log(logfile.filepath, errors=errors)

                for payload in payloads:

                    try:
                        session, agent, user, items, actions = pl.parse_entities_from_data(payload)
                    except exceptions.BadSchemaError:
                        pass
                    else:
                        assert isinstance(session, tapirus.entities.Session)
                        assert isinstance(agent, tapirus.entities.Agent)
                        assert isinstance(user, tapirus.entities.User)
                        assert isinstance(items, set)
                        for item in items:
                            assert isinstance(item, tapirus.entities.Item)
                        assert isinstance(actions, list)
                        for action in actions:
                            assert isinstance(action, tapirus.entities.Action)

                        tenant = session.tenant
                        tenants.append(tenant)

                        # TODO: How can I/O be reduced here?
                        with open(sessionfp.format(*template(tenant)), 'a') as fp:
                            json.dump(session.properties, fp, cls=io.DateTimeEncoder)
                            fp.write('\n')

                        with open(agentfp.format(*template(tenant)), 'a') as fp:
                            json.dump(agent.properties, fp, cls=io.DateTimeEncoder)
                            fp.write('\n')

                        with open(userfp.format(*template(tenant)), 'a') as fp:
                            json.dump(user.properties, fp, cls=io.DateTimeEncoder)
                            fp.write('\n')

                        with open(itemfp.format(*template(tenant)), 'a') as fp:
                            for item in items:
                                json.dump(item.properties, fp, cls=io.DateTimeEncoder)
                                fp.write('\n')

                        with open(actionfp.format(*template(tenant)), 'a') as fp:
                            for action in actions:
                                json.dump(action.properties, fp, cls=io.DateTimeEncoder)
                                fp.write('\n')

                # process errors (Send them to a worker)
                from tapirus.domain import LogErrorDomain
                for err in errors:
                    LogErrorDomain.process_log_error(err)

                del errors[:]

            except EOFError:
                pass
            except OSError:
                pass

        tenants = list(set(tenants))

        with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
            for tenant, result in zip(tenants, executor.map(pack, tenants)):
                Logger.info(
                    'Uploaded record for tenant {0}, code: {1}'.format(
                        tenant, result
                    )
                )

        for logfile in logfiles:
            assert isinstance(logfile, LogFile)
            os.remove(logfile.filepath)

            logfile.filepath = None
            _ = LogFileDAO.update(logfile)

        Logger.info('Updating record {0} status to {1}'.format(
            str(record.timestamp), record)
        )

        record.status = constants.STATUS_PROCESSED
        _ = RecordDAO.update(record)

        for tenant in tenants:

            for file in (sessionfp, agentfp, userfp, itemfp, actionfp):

                filepath = file.format(*template(tenant))

                if os.path.exists(filepath):
                    Logger.info('Removing file {0}'.format(filepath))
                    os.remove(filepath)

            filename = os.path.join(
                tempfile.gettempdir(),
                '.'.join([prefix.format(*template(tenant)), 'hdfs'])
            )

            Logger.info('Removing file {0}'.format(filename))
            os.remove(filename)


if __name__ == '__main__':
    luigi.run()
