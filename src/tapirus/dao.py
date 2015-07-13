import datetime

from sqlalchemy import Column, ForeignKey, DateTime, String, Integer
from sqlalchemy import desc
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm.exc import MultipleResultsFound, NoResultFound
from sqlalchemy.ext.declarative import declarative_base
import sqlalchemy.exc
import sqlalchemy
from tapirus.entities import Record, LogFile, TenantRecord
from tapirus.utils import config

_Base = declarative_base()


def _start_session():

    return _session()


def _session():

    db = config.get('datastore')

    _Engine = create_engine(
        '{store}+{driver}://{username}:{password}@{host}/{database}'.format(
            store=db['store'],
            driver=db['driver'],
            username=db['username'],
            password=db['password'],
            host=db['host'],
            database=db['database']
        ),
        echo=False
    )

    try:
        _Base.metadata.create_all(_Engine)
    except sqlalchemy.exc.InternalError:
        raise
    else:
        _Session = sessionmaker(bind=_Engine)

        return _Session()


class _RecordORM(_Base):
    """
    Data Record
    """

    __tablename__ = 'records'

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    timestamp = Column(DateTime, unique=True, nullable=False)
    last_updated = Column(DateTime, default=datetime.datetime.utcnow(), nullable=False)
    status = Column(String(20), nullable=False)


class _TenantRecordORM(_Base):
    """
    Generated tenant record
    """
    __tablename__ = 'tenant_records'

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    tenant = Column(String(256), index=True)
    timestamp = Column(DateTime, nullable=False)
    last_updated = Column(DateTime, default=datetime.datetime.utcnow(), nullable=False)
    uri = Column(String(512), nullable=True)


class _LogFileORM(_Base):
    """
    Log files downloaded from S3
    """
    __tablename__ = "logfiles"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    record = Column(Integer, ForeignKey("records.id"), nullable=False)
    log = Column(String(256), unique=True)
    filepath = Column(String(256), nullable=True)


class RecordDAO(object):

    STATUS_OPTIONS = {"PENDING", "DOWNLOADED", "BUILDING", "PROCESSED"}

    @classmethod
    def create(cls, record):

        assert isinstance(record, Record)

        session = _start_session()

        try:

            new_record_orm = _RecordORM(id=record.id, timestamp=record.timestamp,
                                        last_updated=record.last_updated, status=record.status)

            session.add(new_record_orm)
            session.commit()

            return Record(id=new_record_orm.id, timestamp=new_record_orm.timestamp,
                          last_updated=new_record_orm.last_updated,
                          status=new_record_orm.status)

        finally:
            session.close()

    @classmethod
    def read(cls, timestamp):

        session = _start_session()

        try:
            instance = session.query(_RecordORM).filter(
                _RecordORM.timestamp == timestamp
            ).one()

        except MultipleResultsFound:
            raise
        except NoResultFound:
            raise
        else:

            return Record(id=instance.id, timestamp=instance.timestamp,
                          last_updated=instance.last_updated,
                          status=instance.status)
        finally:
            session.close()

    @classmethod
    def get_records(cls, start_timestamp, end_timestamp):

        session = _start_session()

        records = session.query(_RecordORM).filter(
            _RecordORM.timestamp.between(start_timestamp, end_timestamp)
        )

        for record in records:
            yield Record(id=record.id, timestamp=record.timestamp, last_updated=record.last_updated,
                         status=record.status)

    @classmethod
    def list(cls, skip, limit, reverse=False):

        session = _start_session()

        try:

            if reverse:
                records = session.query(_RecordORM).order_by(
                    _RecordORM.timestamp
                ).limit(limit).offset(skip)
            else:
                records = session.query(_RecordORM).order_by(
                    desc(_RecordORM.timestamp)
                ).limit(limit).offset(skip)

            for record in records:
                yield Record(id=record.id, timestamp=record.timestamp, last_updated=record.last_updated,
                             status=record.status)

        finally:
            session.close()

    @classmethod
    def count(cls):

        session = _start_session()

        try:
            count = session.query(_RecordORM).count()

            return count

        finally:
            session.close()

    @classmethod
    def delete(cls, id):

        session = _start_session()

        try:
            persistent_instance = session.query(_RecordORM).filter(_RecordORM.id == id).one()
        except MultipleResultsFound:
            raise
        else:
            session.delete(persistent_instance)
            session.commit()

            return session.query(_RecordORM).filter(_RecordORM.id == id).count() == 0
        finally:
            session.close()

    @classmethod
    def exists(cls, timestamp):

        session = _start_session()

        try:
            _ = session.query(_RecordORM).filter(
                _RecordORM.timestamp == timestamp
            ).one()

        except MultipleResultsFound:
            raise
        except NoResultFound:
            return False
        else:

            return True
        finally:
            session.close()

    @classmethod
    def update(cls, record):

        session = _start_session()

        try:

            transient_instance = _RecordORM(**record.__dict__)
            session.merge(transient_instance)
            session.commit()

            return Record(id=transient_instance.id, timestamp=transient_instance.timestamp,
                          last_updated=transient_instance.last_updated, status=transient_instance.status)
        finally:
            session.close()


class TenantRecordDAO(object):

    @classmethod
    def create(cls, tenant_record):

        assert isinstance(tenant_record, TenantRecord)

        session = _start_session()

        try:

            new_tenant_record_orm = _TenantRecordORM(id=tenant_record.id, tenant=tenant_record.tenant,
                                                     timestamp=tenant_record.timestamp,
                                                     last_updated=tenant_record.last_updated,
                                                     uri=tenant_record.uri)

            session.add(new_tenant_record_orm)
            session.commit()

            return TenantRecord(id=new_tenant_record_orm.id, tenant=new_tenant_record_orm.tenant,
                                timestamp=new_tenant_record_orm.timestamp,
                                last_updated=new_tenant_record_orm.last_updated,
                                uri=new_tenant_record_orm.uri)

        finally:
            session.close()

    @classmethod
    def read(cls, tenant, timestamp):

        session = _start_session()

        try:
            instance = session.query(_TenantRecordORM).filter(
                sqlalchemy.and_(
                    _TenantRecordORM.tenant == tenant,
                    _TenantRecordORM.timestamp == timestamp
                )
            ).one()

        except MultipleResultsFound:
            raise
        except NoResultFound:
            raise
        else:

            return TenantRecord(id=instance.id, tenant=instance.tenant, timestamp=instance.timestamp,
                                last_updated=instance.last_updated,
                                uri=instance.uri)
        finally:
            session.close()

    @classmethod
    def find(cls, timestamp, tenant=None):

        session = _start_session()

        try:

            if tenant:
                try:
                    instance = session.query(_TenantRecordORM).filter(
                        sqlalchemy.and_(
                            _TenantRecordORM.tenant == tenant,
                            _TenantRecordORM.timestamp == timestamp
                        )
                    ).one()

                except MultipleResultsFound:
                    raise
                except NoResultFound:
                    pass
                else:

                    yield TenantRecord(id=instance.id, tenant=instance.tenant, timestamp=instance.timestamp,
                                       last_updated=instance.last_updated,
                                       uri=instance.uri)
            else:

                try:
                    instances = session.query(_TenantRecordORM).filter(
                        _TenantRecordORM.timestamp == timestamp
                    ).all()
                except NoResultFound:
                    pass
                else:

                    for instance in instances:
                        yield TenantRecord(id=instance.id, tenant=instance.tenant, timestamp=instance.timestamp,
                                           last_updated=instance.last_updated,
                                           uri=instance.uri)
        finally:
            session.close()


    @classmethod
    def get_records(cls, tenant, start_timestamp, end_timestamp):

        session = _start_session()

        tenant_records = session.query(_TenantRecordORM).filter(
            sqlalchemy.and_(
                _TenantRecordORM.tenant == tenant,
                _TenantRecordORM.timestamp.between(start_timestamp, end_timestamp)
            )
        )

        for tenant_record in tenant_records:
            yield TenantRecord(id=tenant_record.id, tenant=tenant_record.tenant,
                               timestamp=tenant_record.timestamp, last_updated=tenant_record.last_updated,
                               uri=tenant_record.uri)

    @classmethod
    def list(cls, tenant, skip, limit, reverse=False):

        session = _start_session()

        try:

            if reverse:
                tenant_records = session.query(_TenantRecordORM).filter(
                    _TenantRecordORM.tenant == tenant).order_by(
                    _TenantRecordORM.timestamp
                ).limit(limit).offset(skip)
            else:
                tenant_records = session.query(_TenantRecordORM).filter(
                    _TenantRecordORM.tenant == tenant).order_by(
                    desc(_RecordORM.timestamp)
                ).limit(limit).offset(skip)

            for tenant_record in tenant_records:
                yield TenantRecord(id=tenant_record.id, tenant=tenant_record.tenant,
                                   timestamp=tenant_record.timestamp, last_updated=tenant_record.last_updated,
                                   uri=tenant_record.uri)

        finally:
            session.close()

    @classmethod
    def count(cls):

        session = _start_session()

        try:
            count = session.query(_TenantRecordORM).count()

            return count

        finally:
            session.close()

    @classmethod
    def delete(cls, id):

        session = _start_session()

        try:
            persistent_instance = session.query(_TenantRecordORM).filter(_TenantRecordORM.id == id).one()
        except MultipleResultsFound:
            raise
        else:
            session.delete(persistent_instance)
            session.commit()

            return session.query(_TenantRecordORM).filter(_TenantRecordORM.id == id).count() == 0
        finally:
            session.close()

    @classmethod
    def exists(cls, tenant, timestamp):

        session = _start_session()

        try:
            _ = session.query(_TenantRecordORM).filter(
                sqlalchemy.and_(
                    _TenantRecordORM.timestamp == timestamp,
                    _TenantRecordORM.tenant == tenant
                )
            ).one()

        except MultipleResultsFound:
            raise
        except NoResultFound:
            return False
        else:

            return True
        finally:
            session.close()

    @classmethod
    def update(cls, tenant_record):

        session = _start_session()

        try:

            transient_instance = _TenantRecordORM(**tenant_record.__dict__)
            session.merge(transient_instance)
            session.commit()

            return TenantRecord(id=transient_instance.id, tenant=transient_instance.tenant,
                                timestamp=transient_instance.timestamp,
                                last_updated=transient_instance.last_updated, uri=transient_instance.uri)
        finally:
            session.close()


class LogFileDAO(object):

    @classmethod
    def create(cls, logfile):

        assert isinstance(logfile, LogFile)

        session = _start_session()

        try:
            new_logfile_orm = _LogFileORM(id=logfile.id, record=logfile.record,
                                          log=logfile.log, filepath=logfile.filepath)

            session.add(new_logfile_orm)
            session.commit()

            return LogFile(id=new_logfile_orm.id, record=new_logfile_orm.record,
                           log=new_logfile_orm.log, filepath=new_logfile_orm.filepath)

        finally:
            session.close()

    @classmethod
    def read(cls, id):

        session = _start_session()

        try:
            instance = session.query(_LogFileORM).filter(_LogFileORM.id == id).one()

        except MultipleResultsFound:
            raise
        except NoResultFound:
            raise
        else:

            return LogFile(id=instance.id, record=instance.record,
                           log=instance.log, filepath=instance.filepath)
        finally:
            session.close()

    @classmethod
    def get_logfiles(cls, record_id):

        session = _start_session()

        try:

            logfiles = session.query(_LogFileORM).filter(
                _LogFileORM.record == record_id
            ).all()

            for logfile in logfiles:

                yield LogFile(id=logfile.id, record=logfile.record,
                              log=logfile.log, filepath=logfile.filepath)

        finally:
            session.close()

    @classmethod
    def list(cls, skip, limit):

        session = _start_session()

        try:
            logfiles = session.query(_LogFileORM).limit(limit).offset(skip)

            return [LogFile(id=x.id, record=x.record,
                            log=x.log, filepath=x.filepath) for x in logfiles]

        finally:
            session.close()

    @classmethod
    def update(cls, logfile):

        session = _start_session()

        try:

            transient_instance = _LogFileORM(**logfile.__dict__)
            session.merge(transient_instance)
            session.commit()

            return LogFile(id=transient_instance.id, record=transient_instance.record,
                           log=transient_instance.log, filepath=transient_instance.filepath)
        finally:
            session.close()

    @classmethod
    def count(cls):

        session = _start_session()

        try:
            count = session.query(_LogFileORM).count()

            return count

        finally:
            session.close()

    @classmethod
    def delete(cls, id):

        session = _start_session()

        try:
            persistent_instance = session.query(_LogFileORM).filter(_LogFileORM.id == id).one()
        except MultipleResultsFound:
            raise
        else:
            session.delete(persistent_instance)
            session.commit()

            return session.query(_LogFileORM).filter(_LogFileORM.id == id).count() == 0
        finally:
            session.close()


class ErrorDAO(object):

    @classmethod
    def create(cls, error):

        # assert isinstance(error, Error)
        #
        # session = _start_session()
        #
        # try:
        #     new_error_orm = _ErrorORM(id=error.id, code=error.code, data=error.data, timestamp=error.timestamp)
        #
        #     session.add(new_error_orm)
        #     session.commit()
        #
        #     return Error(id=new_error_orm.id, code=new_error_orm.code, data=new_error_orm.data,
        #                  timestamp=new_error_orm.timestamp)
        #
        # finally:
        #     session.close()

        raise NotImplementedError

    @classmethod
    def read(cls, id):

        # session = _start_session()
        #
        # try:
        #     instance = session.query(_ErrorORM).filter(_ErrorORM.id == id).one()
        #
        # except MultipleResultsFound:
        #     raise
        # except NoResultFound:
        #     raise
        # else:
        #
        #     return Error(id=instance.id, code=instance.code, data=instance.data,
        #                  timestamp=instance.timestamp)
        # finally:
        #     session.close()

        raise NotImplementedError

    # TODO: find errors with tenant in them, top 10, desc order
    @classmethod
    def find(cls, limit, skip, tenant):

        # session = _start_session()
        #
        # try:
        #
        #     errors = session.query(_ErrorORM).filter(
        #         _ErrorORM.data.ilike(''.join(['%', tenant, '%']))
        #     ).order_by(
        #         desc(_ErrorORM.timestamp)
        #     ).limit(limit).offset(skip)
        #
        #     for error in errors:
        #
        #         yield Error(id=error.id, code=error.code, data=error.data, timestamp=error.timestamp)
        #
        # finally:
        #     session.close()

        raise NotImplementedError

    @classmethod
    def list(cls, skip, limit):

        # session = _start_session()
        #
        # try:
        #     errors = session.query(_ErrorORM).limit(limit).offset(skip)
        #
        #     return [Error(id=error.id, code=error.code, data=error.data, timestamp=error.timestamp) for error in errors]
        #
        # finally:
        #     session.close()
        raise NotImplementedError

    @classmethod
    def update(cls, error):

        # session = _start_session()
        #
        # try:
        #
        #     transient_instance = _ErrorORM(**error.__dict__)
        #     session.merge(transient_instance)
        #     session.commit()
        #
        #     return Error(id=transient_instance.id, code=transient_instance.code, data=transient_instance.data,
        #                  timestamp=transient_instance.timestamp)
        # finally:
        #     session.close()
        raise NotImplementedError

    @classmethod
    def count(cls):

        # session = _start_session()
        #
        # try:
        #     count = session.query(_ErrorORM).count()
        #
        #     return count
        #
        # finally:
        #     session.close()

        raise NotImplementedError

    @classmethod
    def delete(cls, id):

        # session = _start_session()
        #
        # try:
        #     persistent_instance = session.query(_ErrorORM).filter(_ErrorORM.id == id).one()
        # except MultipleResultsFound:
        #     raise
        # else:
        #     session.delete(persistent_instance)
        #     session.commit()
        #
        #     return session.query(_ErrorORM).filter(_ErrorORM.id == id).count() == 0
        # finally:
        #     session.close()
        raise NotImplementedError
