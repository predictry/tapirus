import datetime
import sys
import subprocess
import os.path
import urllib.parse
import json

from redis import Redis
from rq.decorators import job
import requests
import requests.auth
from tapirus.workflows import harvest
from tapirus.utils.logger import Logger
from tapirus.core import errors
from tapirus.utils import config
from tapirus.repo.models import Error
from tapirus.parser.v1 import pl
from tapirus.utils import io

_redis_conn = Redis()


@job('low', connection=_redis_conn, timeout=60)
def send_error_to_operator(error):
    assert isinstance(error, Error)

    go = config.get('log-error', 'enabled', type=bool)

    if go is False:

        Logger.info(
            'Error processing is disabled. Skipping error.'
        )

        return

    faults = pl.detect_schema_errors(
        error
    )

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

    for fault in faults:

        err = {
            'code': error.code,
            'data': fault,
            'timestamp': error.timestamp,
            'payload': error.data
        }

        response = s.post(url=url, data=json.dumps(err, cls=io.DateTimeEncoder),
                          headers={'Content-Type': 'text/plain'})

        if response.status_code == 200:

            Logger.info(
                'Successfully sent "log error" to Operator, [{0}, {1}]'.format(
                    str(error.code), str(error.timestamp)
                )
            )

        else:

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
