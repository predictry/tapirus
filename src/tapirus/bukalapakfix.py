import tapirus.constants
import tapirus.entities
import tapirus.repo.models

"""
Workflow
"""
import os
import os.path
import tempfile
import datetime
import csv
import json
import gzip

from tapirus import constants
from tapirus.core import aws
from tapirus.processor import log
from tapirus.utils import config
from tapirus.utils.logger import Logger
from tapirus.utils import text
from tapirus.utils import io
from tapirus.constants import *
from tapirus.core import errors as exceptions

import luigi
import luigi.file

if os.name == 'posix':
    tempfile.tempdir = '/tmp'
else:
    tempfile.tempdir = 'out'

TASK = 'bukalapakfix'


class DownloadRecordLogsTask(luigi.Task):
    date = luigi.DateParameter()
    hour = luigi.IntParameter()

    def output(self):
        filename = '{0}_{1}_{2}_'.format(
            self.__class__.__name__,
            str(self.date),
            self.hour
        )

        filepath = os.path.join(tempfile.gettempdir(), 'tasks', TASK, 'status', filename)

        return luigi.LocalTarget(filepath)

    def run(self):

        # timestamp = datetime.datetime(
        #     year=self.date.year,
        #     month=self.date.month,
        #     day=self.date.day,
        #     hour=self.hour
        # )

        s3 = config.get('s3')
        bucket = s3['bucket']
        prefix = s3['prefix']

        pattern = ''.join([prefix, str(self.date), '-', '{:02d}'.format(self.hour)])

        keys = aws.S3.list_bucket_keys(bucket, pattern)
        files = []

        for key in keys:

            s3_key = '/'.join([bucket, key])
            filename = key.split('/')[-1]
            filepath = os.path.join(tempfile.gettempdir(), 'tasks', TASK, 'logs', filename)

            if not os.path.exists(os.path.dirname(filepath)):
                Logger.debug('Creating directory {0}'.format(os.path.dirname(filepath)))

                os.makedirs(os.path.dirname(filepath))

            files.append(filepath)

            Logger.info('Downloading {0} from bucket {1}'.format(key, bucket))

            aws.S3.download_file(s3_key, filepath)

        with self.output().open('w') as fp:

            writer = csv.writer(fp, quoting=csv.QUOTE_ALL)

            for filepath in files:
                writer.writerow([filepath])


class ProcessRecordTask(luigi.Task):
    date = luigi.DateParameter()
    hour = luigi.IntParameter()

    def requires(self):

        return DownloadRecordLogsTask(date=self.date, hour=self.hour)

    def output(self):

        filename = '{0}_{1}_{2}.csv'.format(
            self.__class__.__name__,
            str(self.date),
            self.hour
        )

        filepath = os.path.join(tempfile.gettempdir(), 'tasks', TASK, 'status', filename)

        return luigi.LocalTarget(filepath)

    def run(self):

        def upload(tenant, timestamp, filepath):

            s3 = config.get('s3')
            bucket = s3['bucket']
            folder = 'recovered'

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
                pass
            else:

                Logger.error('Error uploading file to S3: \n{0}'.format(status))

        timestamp = datetime.datetime(
            year=self.date.year,
            month=self.date.month,
            day=self.date.day,
            hour=self.hour
        )

        filepaths = []

        with self.input().open('r') as fp:

            reader = csv.reader(fp)

            for row in reader:
                filepaths.append(row[0])

        errors = []

        prefix = '{0}-{1}-{2}'

        sessionfp = os.path.join(tempfile.gettempdir(), 'tasks', TASK, 'tmp', '-'.join([prefix, 'session']))
        agentfp = os.path.join(tempfile.gettempdir(), 'tasks', TASK, 'tmp', '-'.join([prefix, 'agent']))
        userfp = os.path.join(tempfile.gettempdir(), 'tasks', TASK, 'tmp', '-'.join([prefix, 'user']))
        itemfp = os.path.join(tempfile.gettempdir(), 'tasks', TASK, 'tmp', '-'.join([prefix, 'item']))
        actionfp = os.path.join(tempfile.gettempdir(), 'tasks', TASK, 'tmp', '-'.join([prefix, 'action']))

        if os.path.exists(os.path.dirname(os.path.join(tempfile.gettempdir(), 'tasks', TASK, 'tmp'))) is False:
            os.makedirs(os.path.dirname(os.path.join(tempfile.gettempdir(), 'tasks', TASK, 'tmp')))

        tenants = []

        for filepath in filepaths:

            Logger.info(
                'Processing log file {0}'.format(
                    filepath
                )
            )

            try:
                payloads = log.process_log(filepath, errors=errors)

                # TODO: doesn't contain anything until generator runs. remove
                for _ in payloads:
                    pass

                for err in errors:

                    code, data, tmpstp = err

                    # successfully parsed json
                    if type(data) is not str and code == tapirus.constants.ERROR_INVALIDSCHEMA_DD:

                        # validate scheme
                        # if it's what we're looking for, transform it, and put it in a file
                        data['datetime'] = tmpstp
                        try:
                            session, agent, user, items, actions = parse_entities_from_data(data)
                        except exceptions.BadSchemaError:
                            pass
                        else:

                            tenant = session.tenant

                            if tenant != 'bukalapak':
                                continue

                            tenants.append(tenant)

                            with open(sessionfp.format(str(self.date), self.hour, tenant), 'a') as fp:
                                json.dump(session.properties, fp, cls=io.DateTimeEncoder)
                                fp.write('\n')

                            with open(agentfp.format(str(self.date), self.hour, tenant), 'a') as fp:
                                json.dump(agent.properties, fp, cls=io.DateTimeEncoder)
                                fp.write('\n')

                            with open(userfp.format(str(self.date), self.hour, tenant), 'a') as fp:
                                json.dump(user.properties, fp, cls=io.DateTimeEncoder)
                                fp.write('\n')

                            with open(itemfp.format(str(self.date), self.hour, tenant), 'a') as fp:
                                for item in items:
                                    json.dump(item.properties, fp, cls=io.DateTimeEncoder)
                                    fp.write('\n')

                            with open(actionfp.format(str(self.date), self.hour, tenant), 'a') as fp:
                                for action in actions:
                                    json.dump(action.properties, fp, cls=io.DateTimeEncoder)
                                    fp.write('\n')

                del errors[:]

            except EOFError:
                pass
            except OSError:
                pass

        sessions = []
        agents = []
        users = []
        items = []
        actions = []
        tenants = list(set(tenants))

        for tenant in tenants:

            filename = os.path.join(
                tempfile.gettempdir(),
                'tasks',
                TASK,
                'tmp',
                '.'.join([prefix.format(str(self.date), self.hour, tenant), 'hdfs'])
            )

            Logger.info(
                'Creating record file {0} for tenant {1}'.format(
                    filename, tenant
                )
            )

            if os.path.exists(filename):
                Logger.info('Deleting file {0}'.format(filename))
                os.remove(filename)

            if os.path.exists(os.path.dirname(filename)) is False:
                os.makedirs(os.path.dirname(filename))

            with open(filename, 'w') as fp:

                metadata = {
                    'date': str(timestamp.date()),
                    'hour': timestamp.hour,
                    'processed': str(datetime.datetime.now())
                }

                if os.path.exists(sessionfp.format(str(self.date), self.hour, tenant)):
                    with open(sessionfp.format(str(self.date), self.hour, tenant), 'r') as inp:

                        for line in inp:
                            session = json.loads(line, encoding='UTF-8')

                            sessions.append(session)

                if os.path.exists(agentfp.format(str(self.date), self.hour, tenant)):
                    with open(agentfp.format(str(self.date), self.hour, tenant), 'r') as inp:

                        for line in inp:
                            agent = json.loads(line, encoding='UTF-8')
                            agents.append(agent)

                if os.path.exists(userfp.format(str(self.date), self.hour, tenant)):
                    with open(userfp.format(str(self.date), self.hour, tenant), 'r') as inp:

                        for line in inp:
                            user = json.loads(line, encoding='UTF-8')
                            users.append(user)

                if os.path.exists(itemfp.format(str(self.date), self.hour, tenant)):
                    with open(itemfp.format(str(self.date), self.hour, tenant), 'r') as inp:

                        for line in inp:
                            item = json.loads(line, encoding='UTF-8')
                            items.append(item)

                if os.path.exists(actionfp.format(str(self.date), self.hour, tenant)):
                    with open(actionfp.format(str(self.date), self.hour, tenant), 'r') as inp:

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

            upload(tenant, timestamp=timestamp, filepath=filename)

        # TODO: delete logs
        for filepath in filepaths:
            os.remove(filepath)

        for tenant in tenants:

            for file in (sessionfp, agentfp, userfp, itemfp, actionfp):

                filepath = file.format(str(self.date), self.hour, tenant)

                if os.path.exists(filepath):
                    Logger.info('Removing file {0}'.format(filepath))
                    os.remove(filepath)

            filename = os.path.join(
                tempfile.gettempdir(),
                'tasks',
                TASK,
                'tmp',
                '.'.join([prefix.format(str(self.date), self.hour, tenant), 'hdfs'])
            )

            Logger.info('Removing file {0}'.format(filename))
            os.remove(filename)

        with self.output().open('w') as fp:

            writer = csv.writer(fp, quoting=csv.QUOTE_ALL)

            for tenant in tenants:
                writer.writerow([tenant])


def _is_valid_data(value):
    chars = ("[", "]", ".")

    if any([c in value for c in chars]):
        return False

    return True


def is_valid_schema(data):
    """
    :param data:
    :return:
    """

    if SCHEMA_KEY_SESSION_ID not in data:
        return False
    if type(data[SCHEMA_KEY_SESSION_ID]) is not str:
        return False
    if len(data[SCHEMA_KEY_SESSION_ID]) < 1:
        return False
    if not _is_valid_data(data[SCHEMA_KEY_SESSION_ID]):
        return False

    if SCHEMA_KEY_TENANT_ID not in data:
        return False
    if type(data[SCHEMA_KEY_TENANT_ID]) is not str:
        return False
    if len(data[SCHEMA_KEY_TENANT_ID]) < 1:
        return False
    if not _is_valid_data(data[SCHEMA_KEY_TENANT_ID]):
        return False

    if SCHEMA_KEY_ACTION not in data:
        return False

    if SCHEMA_KEY_NAME not in data[SCHEMA_KEY_ACTION]:
        return False
    if type(data[SCHEMA_KEY_ACTION][SCHEMA_KEY_NAME]) is not str:
        return False
    if len(data[SCHEMA_KEY_ACTION][SCHEMA_KEY_NAME]) < 1:
        return False
    if not _is_valid_data(data[SCHEMA_KEY_ACTION][SCHEMA_KEY_NAME]):
        return False

    if SCHEMA_KEY_USER in data:

        if SCHEMA_KEY_USER_ID not in data[SCHEMA_KEY_USER]:
            return False
        if type(data[SCHEMA_KEY_USER][SCHEMA_KEY_USER_ID]) is not str:
            return False
        if len(data[SCHEMA_KEY_USER][SCHEMA_KEY_USER_ID]) < 1:
            return False
        if not _is_valid_data(data[SCHEMA_KEY_USER][SCHEMA_KEY_USER_ID]):
            return False

    if SCHEMA_KEY_RECOMMENDATION in data[SCHEMA_KEY_ACTION]:
        if type(data[SCHEMA_KEY_ACTION][SCHEMA_KEY_RECOMMENDATION]) is not str:
            return False

        if text.boolean(data[SCHEMA_KEY_ACTION][SCHEMA_KEY_RECOMMENDATION]) is None:
            return False

    if SCHEMA_KEY_RECOMMENDATION_ORI in data[SCHEMA_KEY_ACTION]:
        if type(data[SCHEMA_KEY_ACTION][SCHEMA_KEY_RECOMMENDATION_ORI]) is not dict:
            return False

        # other rec parameters must be a flat dictionary/map (no nested dictionaries)
        for k in data[SCHEMA_KEY_ACTION][SCHEMA_KEY_RECOMMENDATION_ORI]:

            if _is_valid_data(data[SCHEMA_KEY_ACTION][SCHEMA_KEY_RECOMMENDATION_ORI][k]) is False:
                return False

    if data[SCHEMA_KEY_ACTION][SCHEMA_KEY_NAME].lower() == REL_ACTION_TYPE_BUY.lower():

        if SCHEMA_KEY_ITEMS not in data:
            return False

        if type(data[SCHEMA_KEY_ITEMS]) is not list:
            return False

        package = data[SCHEMA_KEY_ITEMS][0]

        if type(package) is not dict:
            return False
        if "" not in package:
            return False

        for item in package[""]:

            if SCHEMA_KEY_ITEM_ID not in item:
                return False
            if type(item[SCHEMA_KEY_ITEM_ID]) is not str:
                return False
            if len(item[SCHEMA_KEY_ITEM_ID]) < 1:
                return False
            if not _is_valid_data(item[SCHEMA_KEY_ITEM_ID]):
                return False

            if SCHEMA_KEY_QUANTITY not in item:
                return False

            if SCHEMA_KEY_SUBTOTAL not in item:
                return False

    return True


def parse_entities_from_data(data):
    dt = data["datetime"]
    tenant = data[SCHEMA_KEY_TENANT_ID]

    if is_valid_schema(data) is False:
        print('bad schema', data)
        raise exceptions.BadSchemaError('Bad Schema')

    # session = None
    agent = None
    # user = None
    items = set()
    actions = []

    # Session
    session = tapirus.entities.Session(id=data[SCHEMA_KEY_SESSION_ID], tenant=tenant, timestamp=dt, fields={})

    # User
    if SCHEMA_KEY_USER in data:
        user = tapirus.entities.User(id=data[SCHEMA_KEY_USER][SCHEMA_KEY_USER_ID], tenant=tenant, timestamp=dt,
                                     fields={})
    else:
        user = tapirus.entities.User(id=data[SCHEMA_KEY_SESSION_ID], tenant=tenant, timestamp=dt, fields={})

    # Agent
    if SCHEMA_KEY_AGENT_ID in data:
        agent = tapirus.entities.Agent(id=data[SCHEMA_KEY_AGENT_ID], tenant=tenant, timestamp=dt, fields={})

    if data[SCHEMA_KEY_ACTION][SCHEMA_KEY_NAME].upper() == REL_ACTION_TYPE_BUY:

        if SCHEMA_KEY_RECOMMENDATION in data[SCHEMA_KEY_ACTION]:
            recommended = text.boolean(data[SCHEMA_KEY_ACTION][SCHEMA_KEY_RECOMMENDATION])
        else:
            recommended = False

        if SCHEMA_KEY_RECOMMENDATION_ORI in data[SCHEMA_KEY_ACTION]:
            parameters = data[SCHEMA_KEY_ACTION][SCHEMA_KEY_RECOMMENDATION_ORI]
        else:
            parameters = {}

        recommendation = dict(recommended=recommended, parameters=parameters)

        package = data[SCHEMA_KEY_ITEMS][0][""]

        for item_data in package:
            item = tapirus.entities.Item(id=item_data[SCHEMA_KEY_ITEM_ID], tenant=tenant, timestamp=dt, fields={})

            items.add(item)

            action = tapirus.entities.Action(name=REL_ACTION_TYPE_BUY, tenant=tenant, user=user.id,
                                             agent=agent.id, session=session.id, item=item.id, timestamp=dt,
                                             fields={"quantity": item_data[SCHEMA_KEY_QUANTITY],
                                                     "sub_total": item_data[SCHEMA_KEY_SUBTOTAL]},
                                             recommendation=recommendation)

            actions.append(action)

    return session, agent, user, items, actions


if __name__ == '__main__':
    luigi.run()
