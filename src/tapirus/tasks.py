import datetime
import sys
import subprocess
import os.path

from redis import Redis
from rq.decorators import job

from tapirus.services import harvest
from tapirus.utils.logger import Logger

_redis_conn = Redis()


@job('medium', connection=_redis_conn, timeout=60*20)
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

    return p.wait()
