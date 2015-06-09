import os
import os.path

from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, String, ForeignKey
from sqlalchemy.orm.exc import MultipleResultsFound
from sqlalchemy import create_engine

from tapirus.utils import config


_Base = declarative_base()


def _start_session():

    return _session()


def _session():

    db = config.get("sqlite")

    dbfile = os.path.join(os.path.dirname(os.path.realpath(__file__)), "../../{0}".format(db["filename"]))

    _Engine = create_engine('sqlite:///{0}'.format(dbfile), echo=False)

    _Session = sessionmaker(bind=_Engine)

    return _Session()


class RecordDAO(object):

    @classmethod
    def get_records(cls, start_date, start_hour, end_date, end_hour):

        return []
