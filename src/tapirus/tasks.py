import datetime
import sys
import subprocess
import os.path

from redis import Redis
from rq.decorators import job
from tapirus.workflows import harvest
from tapirus.utils.logger import Logger
from tapirus.core import errors
from tapirus.utils import config

_redis_conn = Redis()


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
