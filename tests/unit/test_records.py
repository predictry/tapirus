import unittest
import datetime

from tapirus.entities import Record
from tapirus.dao import RecordDAO


class RecordDAOTestCases(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        # def setUp(self):

        start = datetime.datetime(year=2012, month=1, day=1, hour=0)

        for i in range(1, 24):

            timestamp = start + datetime.timedelta(hours=1)

            record = Record(None, timestamp=timestamp, last_updated=None,
                            status="PENDING", uri=None)

            RecordDAO.create(record)

    @classmethod
    def tearDownClass(cls):
        # def tearDown(self):

        while RecordDAO.count() > 0:

            records = RecordDAO.list(0, 100)

            for record in records:
                RecordDAO.delete(record.id)

    def test_should_read_records_in_interval(self):

        start = datetime.datetime(year=2012, month=1, day=1, hour=0)
        end = start + datetime.timedelta(hours=12)

        records = RecordDAO.get_records(start_timestamp=start, end_timestamp=end)

        self.assertEqual(len([x for x in records]), 12)

    def test_should_read_record_for_specific_date_hour(self):

        timestamp = datetime.datetime(year=2012, month=1, day=1, hour=7)

        record = RecordDAO.read(timestamp=timestamp)

        self.assertIsInstance(record, Record)
        self.assertEqual(record.timestamp.date(), timestamp.date())
        self.assertEqual(record.timestamp.hour, timestamp.hour)
        self.assertEqual(record.status, "PENDING")
