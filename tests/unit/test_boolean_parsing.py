import unittest
import datetime

from tapirus.utils import text


class TestBooleanParsing(unittest.TestCase):

    def test_should_parse_true(self):

        values = ['True', 'TRUE', 'true', '1', True, 1]

        for value in values:
            self.assertTrue(text.boolean(value))

    def test_should_parse_false(self):

        values = ['False', 'FALSE', 'false', '0', False, 0]

        for value in values:
            self.assertFalse(text.boolean(value))

    def test_should_parse_non_boolean(self):

        values = ['yes', 'y', 'maybe', datetime.datetime.utcnow(),  0.0, 0.0001]

        for value in values:
            self.assertIsNone(text.boolean(value))
