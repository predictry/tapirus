import datetime

from tapirus import dao
from tapirus import entities
from tapirus.utils import config
from tapirus import constants
from tapirus import tasks


class RecordUseCases(object):

    @staticmethod
    def update_record_status(timestamp):

        if not dao.RecordDAO.exists(timestamp=timestamp):
            record = entities.Record(id=None, timestamp=timestamp, last_updated=None,
                                     status=constants.STATUS_PENDING,
                                     uri=None)

            new_record = dao.RecordDAO.create(record)

            tasks.run_workflow_for_record.delay(timestamp)

            return new_record

        else:

            record = dao.RecordDAO.read(timestamp=timestamp)

            if record.status == constants.STATUS_NOT_FOUND:

                pass

            elif record.status in (constants.STATUS_PENDING, constants.STATUS_DOWNLOADED, constants.STATUS_BUILDING):

                threshold = int(config.get('harvester', 'threshold'))

                delta = datetime.datetime.utcnow() - record.last_updated

                if delta.total_seconds() > threshold:

                    tasks.run_workflow_for_record.delay(timestamp)

            return record
