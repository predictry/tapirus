__author__ = 'guilherme'

from tapirus.model import store

import unittest
import uuid


class TestItem(unittest.TestCase):

    item = dict(
        id=str(uuid.uuid4()),
        domain="my.store.com",
        uuid=str(uuid.uuid4())
    )

    def test_01_should_instantiate_item(self):

        print("Testing Instantiation of model `{0}`".format("Item"))

        item = store.Item(self.item["id"], self.item["domain"], self.item["uuid"])

        assert item is not None
        assert item.id == self.item["id"]
        assert item.domain == self.item["domain"]
        assert item.uuid == self.item["uuid"]


if __name__ == "__main__":
    unittest.main()
