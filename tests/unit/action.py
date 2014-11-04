__author__ = 'guilherme'

import unittest
import time
import datetime
from predictry.engine.graph.query.generator.resources.action import ActionQueryGenerator


class ActionUnitTest(unittest.TestCase):


    payloads = [
        {
            "item_id": 12,
            "session_id": 34,
            "browser_id": 56,
            "timestamp": time.mktime(datetime.datetime.utcnow().timetuple()),
            "type": "view"
        }
    ]

    args = {
        "domain": "house"
    }

    def test_1_should_create_query_to_create_an_action(self):

        qgen = ActionQueryGenerator()

        print qgen.create(self.args, self.payloads[0])


if __name__ == "__main__":
    unittest.main()