import datetime
import sys
import subprocess
import os.path
import urllib.parse

from redis import Redis
from rq.decorators import job
import requests
import requests.auth
from tapirus.workflows import harvest
from tapirus.utils.logger import Logger
from tapirus.core import errors
from tapirus.utils import config
from tapirus.repo.models import Error

_redis_conn = Redis()


@job('low', connection=_redis_conn, timeout=10)
def send_error_to_operator(error):
    assert isinstance(error, Error)

    cfg = config.get('log-error')

    auth = requests.auth.HTTPBasicAuth(cfg['username'], cfg['password'])
    url = '{protocol}://{host}:{port}/{endpoint}/{channel}?{params}'.format(
        protocol=cfg['protocol'],
        host=cfg['host'],
        port=cfg['port'],
        endpoint=cfg['endpoint'],
        channel=cfg['channel'],
        params=urllib.parse.urlencode({'type': cfg['type']})
    )

    s = requests.session()
    s.auth = auth

    response = s.post(url=url, json=error.properties)

    if response.status_code != 200:
        Logger.error(
            'There was problem sending "log error" to the Operator: returned status {0}'.format(
                response.status_code
            )
        )


@job('medium', connection=_redis_conn, timeout=int(config.get('harvester', 'timeout')))
def run_workflow_for_record(timestamp):
    assert isinstance(timestamp, datetime.datetime)

    filepath = os.path.abspath(harvest.__file__)
    classname = harvest.ProcessRecordTask.__name__

    Logger.info([sys.executable, filepath, classname,
                 "--date", str(timestamp.date()),
                 "--hour", str(timestamp.hour)])

    p = subprocess.Popen([sys.executable, filepath, classname,
                          "--date", str(timestamp.date()),
                          "--hour", str(timestamp.hour)])

    stdout, stderr = p.communicate()

    if stderr:

        Logger.error(stderr)

        message = '{0} ({1}, {2}) failed'.format(
            classname, str(timestamp.date()), timestamp.hour
        )

        raise errors.ProcessFailureError(
            message
        )

    else:

        Logger.info(stdout)

        if p.returncode == 0:
            return True
        else:

            message = '{0} ({1}, {2}) failed'.format(
                classname, str(timestamp.date()), timestamp.hour
            )

            raise errors.ProcessFailureError(
                message
            )
