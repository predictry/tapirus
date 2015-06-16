import os
import os.path
import datetime

from sqlalchemy import Column, ForeignKey, DateTime, String, Integer
from sqlalchemy import desc
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm.exc import MultipleResultsFound, NoResultFound
from sqlalchemy.ext.declarative import declarative_base


from tapirus.entities import Record, LogFile
from tapirus.utils import config


_Base = declarative_base()


def _start_session():

    return _session()


def _session():

    db = config.get("sqlite")

    dbfile = os.path.join(os.path.dirname(os.path.realpath(__file__)), "../../{0}".format(db["filename"]))

    # TODO: ?
    _Engine = create_engine('sqlite:///{0}'.format(dbfile),
                            connect_args={'check_same_thread': False},
                            echo=False)

    _Base.metadata.create_all(_Engine)

    _Session = sessionmaker(bind=_Engine)

    return _Session()


class _RecordORM(_Base):
    __tablename__ = "records"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    timestamp = Column(DateTime, unique=True, nullable=False)
    last_updated = Column(DateTime, default=datetime.datetime.utcnow(), nullable=False)
    status = Column(String, nullable=False)
    uri = Column(String, nullable=True)


class _LogFileORM(_Base):
    __tablename__ = "logfiles"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    record = Column(Integer, ForeignKey("records.id"), nullable=False)
    log = Column(String, unique=True)
    filepath = Column(String, nullable=True)


class RecordDAO(object):

    STATUS_OPTIONS = {"PENDING", "DOWNLOADED", "BUILDING", "PROCESSED"}

    @classmethod
    def create(cls, record):

        assert isinstance(record, Record)

        session = _start_session()

        try:

            new_record_orm = _RecordORM(id=record.id, timestamp=record.timestamp,
                                        last_updated=record.last_updated, status=record.status, uri=record.uri)

            session.add(new_record_orm)
            session.commit()

            return Record(id=new_record_orm.id, timestamp=new_record_orm.timestamp,
                          last_updated=new_record_orm.last_updated,
                          status=new_record_orm.status, uri=new_record_orm.uri)

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
                          status=instance.status, uri=instance.uri)
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
                         status=record.status, uri=record.uri)

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
                             status=record.status, uri=record.uri)

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
                          last_updated=transient_instance.last_updated, status=transient_instance.status,
                          uri=transient_instance.uri)
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
