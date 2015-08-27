import datetime

from tapirus.repo import dao
from tapirus.repo import models
from tapirus.utils import config
from tapirus import constants
from tapirus import tasks


class RecordDomain(object):

    @staticmethod
    def update_record_status(timestamp):

        if not dao.RecordDAO.exists(timestamp=timestamp):
            record = models.Record(id=None, timestamp=timestamp, last_updated=None,
                                   status=constants.STATUS_PENDING)

            new_record = dao.RecordDAO.create(record)

            tasks.run_workflow_for_record.delay(timestamp)

            return new_record

        else:

            record = dao.RecordDAO.read(timestamp=timestamp)

            if record.status == constants.STATUS_NOT_FOUND:

                # try again. it might too early, or record may have been made available
                tasks.run_workflow_for_record.delay(timestamp)

            elif record.status in (constants.STATUS_PENDING, constants.STATUS_DOWNLOADED,
                                   constants.STATUS_BUILDING):

                threshold = int(config.get('harvester', 'threshold'))

                delta = datetime.datetime.utcnow() - record.last_updated

                if delta.total_seconds() > threshold:
                    tasks.run_workflow_for_record.delay(timestamp)

            return record

    @staticmethod
    def get_tenant_records(timestamp, tenant=None):

        if dao.RecordDAO.exists(timestamp=timestamp) is False:
            return []
        else:

            tenant_records = dao.TenantRecordDAO.find(timestamp=timestamp, tenant=tenant)

            return [x for x in tenant_records]


class LogErrorDomain(object):

    @staticmethod
    def process_log_error(error):
        tasks.send_error_to_operator.delay(error)
