import unittest

from tapirus.utils.io import validate_hour, validate_date


class ValidationTestCases(unittest.TestCase):

    def test_should_validate_dates(self):

        dates = [
            "2015-04-03",
            "1993-02-27",
            "0023-10-2"
        ]

        for d in dates:

            self.assertTrue(validate_date(d))

    def test_should_fail_date_validation(self):

        dates = [
            "999-04-03",
            "1993-02-44",
            "2015-13-03"
        ]

        for d in dates:

            self.assertFalse(validate_date(d))

    def test_should_validate_hours(self):

        hours = [
            "01",
            "13",
            "00",
            "2"
        ]

        for h in hours:

            self.assertTrue(validate_hour(h))

    def test_should_fail_hour_validation(self):

        hours = [
            "24",
            "25"
        ]

        for h in hours:

            self.assertFalse(validate_hour(h))


if __name__ == "__main__":

    unittest.main()


