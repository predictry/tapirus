__author__ = 'guilherme'

from tapirus.model import store

import unittest
import uuid


class TestAgent(unittest.TestCase):

    agent = dict(
        id=str(uuid.uuid4()),
        domain="my.store.com",
        uuid=str(uuid.uuid4())
    )

    def test_01_should_instantiate_agent(self):

        print("Testing Instantiation of model `{0}`".format("Agent"))

        agent = store.Agent(self.agent["id"], self.agent["domain"], self.agent["uuid"])

        assert agent is not None
        assert agent.id == self.agent["id"]
        assert agent.domain == self.agent["domain"]
        assert agent.uuid == self.agent["uuid"]


if __name__ == "__main__":
    unittest.main()
