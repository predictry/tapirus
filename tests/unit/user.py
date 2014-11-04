__author__ = 'guilherme'

import json
import time
import unittest
from predictry import server

now = long(time.time().real)


class UserTestCase(unittest.TestCase):

    def setUp(self):
        assert type(now) is long
        server.app.config['TESTING'] = True
        self.app = server.app.test_client()
        self.appid = "pongo"
        self.domain = "verve"
        self.user = dict(id=123456,
                         email="user@mail.domain.com", schools=["School A", "School B"])

    def tearDown(self):
        pass

    def test_1_create_user(self):

        print "CREATE USER"

        url = "/predictry/api/v1/users/?appid=%s&domain=%s" % (self.appid, self.domain)

        data = json.dumps(self.user, ensure_ascii=False)
        resp = self.app.post(url, data=data, content_type='application/json')

        content = json.loads(resp.data)

        print content
        assert 'status' in content
        assert content['status'] == resp.status_code
        assert resp.status_code == 200

        user = content['data']['users'][0]

        for k in self.user:
            assert self.user[k] == user[k]

    def test_2_get_user(self):

        print "RETRIEVE USER"

        url = "/predictry/api/v1/users/%s/?appid=%s&domain=%s&fields=id,domain,email,schools" \
              % (self.user['id'], self.appid, self.domain)

        resp = self.app.get(url)

        content = json.loads(resp.data)

        print content
        assert 'data' in content
        assert 'status' in content
        assert content['status'] == resp.status_code

        user = content['data']['users'][0]

        print user

        for k in self.user:
            assert self.user[k] == user[k]

    def test_3_update_user(self):

        print "UPDATE USER"

        url = "/predictry/api/v1/users/%s/?appid=%s&domain=%s" % (self.user['id'], self.appid, self.domain)

        payload = dict(email="updated@mail.domain.com", schools=["School C", "School D"])
        data = json.dumps(payload, ensure_ascii=False)
        resp = self.app.put(url, data=data, content_type='application/json')

        content = json.loads(resp.data)
        user = content['data']['users'][0]

        print content
        for k in payload:
            assert payload[k] == user[k]

    def test_4_delete_user(self):

        print "DELETE USER"

        url = "/predictry/api/v1/users/%s/?appid=%s&domain=%s" % (self.user['id'], self.appid, self.domain)

        resp = self.app.delete(url)

        content = json.loads(resp.data)

        print content
        assert 'status' in content
        assert content['status'] == resp.status_code
        assert resp.status_code == 200
        for k in content['data']['users'][0]:
            assert content['data']['users'][0][k] == self.user[k]


if __name__ == "__main__":
    unittest.main()
