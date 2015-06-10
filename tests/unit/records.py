import unittest
import datetime

from tapirus.entities import Record
from tapirus.dao import RecordDAO


class RecordDAOTestCases(unittest.TestCase):

    def setUp(self):

        start = datetime.datetime(year=2012, month=1, day=1, hour=0)

        for i in range(1, 24*30):

            date = start + datetime.timedelta(hours=i)

            record = Record(None, date=date.date(), hour=date.hour, last_updated=None,
                            status="PENDING", uri=None)

            RecordDAO.create(record)

    def tearDown(self):

        while RecordDAO.count() > 0:

            records = RecordDAO.list(0, 100)

            for record in records:
                RecordDAO.delete(record.id)

    def test_should_read_records_in_interval(self):

        start = datetime.datetime(year=2012, month=1, day=1, hour=0)
        end = start + datetime.timedelta(hours=12)

        records = RecordDAO.get_records(start.date(), start.hour, end.date(), end.hour)

        self.assertEqual(len(records), 12)

    def test_should_read_record_for_specific_date_hour(self):

        date = datetime.datetime(year=2012, month=1, day=14, hour=7)

        record = RecordDAO.read(date.date(), date.hour)

        self.assertIsInstance(record, Record)
        self.assertEqual(record.date, date.date())
        self.assertEqual(record.hour, date.hour)
        self.assertEqual(record.status, "PENDING")
