import os
import os.path
import datetime

from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Date, DateTime, String, Integer, BigInteger, and_
from sqlalchemy.orm.exc import MultipleResultsFound
from sqlalchemy import create_engine

from tapirus.entities import Record
from tapirus.utils import config


_Base = declarative_base()


def _start_session():

    return _session()


def _session():

    db = config.get("sqlite")

    dbfile = os.path.join(os.path.dirname(os.path.realpath(__file__)), "../../{0}".format(db["filename"]))

    _Engine = create_engine('sqlite:///{0}'.format(dbfile), echo=False)

    _Base.metadata.create_all(_Engine)

    _Session = sessionmaker(bind=_Engine)

    return _Session()


class _RecordORM(_Base):
    __tablename__ = "records"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    date = Column(Date, index=True, nullable=False)
    hour = Column(Integer, index=True, nullable=False)
    last_updated = Column(DateTime, default=datetime.datetime.utcnow(), nullable=False)
    status = Column(String, nullable=False)
    uri = Column(String, nullable=True)


class RecordDAO(object):

    STATUS_OPTIONS = {"PENDING", "BUILDING", "PROCESSED"}

    @classmethod
    def create(cls, record):

        assert isinstance(record, Record)

        session = _start_session()

        try:
            new_record_orm = _RecordORM(id=record.id, date=record.date, hour=record.hour, last_updated=record.last_updated,
                                  status=record.status, uri=record.uri)

            session.add(new_record_orm)
            session.commit()

            return Record(new_record_orm.id, new_record_orm.date, new_record_orm.hour, new_record_orm.last_updated,
                          new_record_orm.status, new_record_orm.uri)

        finally:
            session.close()

    @classmethod
    def read(cls, date, hour):

        session = _start_session()

        try:
            instance = session.query(_RecordORM).filter(
                and_(
                    _RecordORM.date == date,
                    _RecordORM.hour == hour
                )
            ).one()

        except MultipleResultsFound:
            raise
        else:

            return Record(instance.id, instance.date, instance.hour, instance.last_updated,
                          instance.status, instance.uri)
        finally:
            session.close()

    @classmethod
    def get_records(cls, start_date, start_hour, end_date, end_hour):

        session = _start_session()

        records = session.query(_RecordORM).filter(
            and_(_RecordORM.date.between(start_date, end_date),
                 _RecordORM.hour.between(start_hour, end_hour)
                 )
        )

        return [Record(id=x.id, date=x.date, hour=x.hour, last_updated=x.last_updated,
                       status=x.status, uri=x.uri) for x in records]

    @classmethod
    def list(cls, skip, limit):

        session = _start_session()

        try:
            records = session.query(_RecordORM).limit(limit).offset(skip)

            return [Record(id=x.id, date=x.date, hour=x.hour, last_updated=x.last_updated,
                           status=x.status, uri=x.uri) for x in records]

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

            return session.query(_RecordORM).filter_by(id=id).count() == 0
        finally:
            session.close()
