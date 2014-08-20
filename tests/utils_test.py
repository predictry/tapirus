__author__ = 'guilherme'

from predictry.utils.helpers import text
import unittest


class UtilsTest(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_text_decoding(self):

        payload = dict(
            people = dict(
                name="Ada",
                profession=["professor", "mathematician", "programmer"]
            ),
            places=["Budapest", "New Dehli", "Mumbai", None],
            time = ("h", "m", "s")
        )

        translated = text.encode(payload)

        assert translated == payload
        print translated


if __name__ == '__main__':
    unittest.main()