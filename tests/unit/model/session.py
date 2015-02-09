__author__ = 'guilherme'

from tapirus.model import store

import unittest
import uuid


class TestSession(unittest.TestCase):

    session = dict(
        id=str(uuid.uuid4()),
        domain="my.store.com",
        uuid=str(uuid.uuid4())
    )

    def test_01_should_instantiate_session(self):

        print("Testing Instantiation of model `{0}`".format("Session"))

        session = store.Session(self.session["id"], self.session["domain"], self.session["uuid"])

        assert session is not None
        assert session.id == self.session["id"]
        assert session.domain == self.session["domain"]
        assert session.uuid == self.session["uuid"]


if __name__ == "__main__":
    unittest.main()