__author__ = 'guilherme'

from tapirus.model import store

import unittest
import uuid


class TestUser(unittest.TestCase):

    user = dict(
        id=str(uuid.uuid4()),
        domain="my.store.com",
        uuid=str(uuid.uuid4())
    )

    def test_01_should_instantiate_user(self):

        print("Testing Instantiation of model `{0}`".format("User"))

        user = store.User(self.user["id"], self.user["domain"], self.user["uuid"])

        assert user is not None
        assert user.id == self.user["id"]
        assert user.domain == self.user["domain"]
        assert user.uuid == self.user["uuid"]


if __name__ == "__main__":
    unittest.main()
