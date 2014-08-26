__author__ = 'guilherme'

import json
import time
import unittest
from predictry import server

now = long(time.time().real)


class ItemTestCase(unittest.TestCase):

    def setUp(self):
        assert type(now) is long
        server.app.config['TESTING'] = True
        self.app = server.app.test_client()
        self.appid = "pongo"
        self.domain = "verve"
        self.item = dict(id=123456, name="TestItem",
                         brand="TestBrand", model="TestModel", tags=["Test", "Item"],
                         description="This is a test item", price=1.0, category="TestItem",
                         date_added=now, subcategory="SubCategory", start_date=now, end_date=now+60480000,
                         item_url="http://localhostL7474/", image_url="images.google.com",
                         locations=["Singapore", "Indonesia"])

    def tearDown(self):
        pass

    def test_1_create_item(self):

        print "CREATE ITEM"

        url = "/predictry/api/v1/items/?appid=%s&domain=%s" % (self.appid, self.domain)

        data = json.dumps(self.item, ensure_ascii=False)
        resp = self.app.post(url, data=data, content_type='application/json')

        content = json.loads(resp.data)

        print content
        assert 'status' in content
        assert content['status'] == resp.status_code
        assert resp.status_code == 200

        item = content['data']['items'][0]

        for k in self.item:
            #if type(item[k]) is list:
            #    text = ','.join(item[k])
            #    assert self.item[k] == text
            #else:
            assert self.item[k] == item[k]

    def test_2_get_item(self):

        print "RETRIEVE ITEM"

        url = "/predictry/api/v1/items/%s/?appid=%s&domain=%s" % (self.item['id'], self.appid, self.domain)

        resp = self.app.get(url)

        content = json.loads(resp.data)

        print content
        assert 'data' in content
        assert 'status' in content
        assert content['status'] == resp.status_code

        item = content['data']['items'][0]

        for k in item:
            #if type(item[k]) is list:
            #    text = ','.join(item[k])
            #    assert self.item[k] == text
            #else:
            assert self.item[k] == item[k]

    def test_3_update_item(self):

        print "UPDATE ITEM"

        url = "/predictry/api/v1/items/%s/?appid=%s&domain=%s" % (self.item['id'], self.appid, self.domain)

        payload = dict(category="UpdatedTestItem", image_url="images.yahoo.com", tags=["Updated", "Test", "Item"],
                       subcategory="UpdatedSubcategory", end_date=now+60480000*2, locations=["Vermont", "Singapore"])
        data = json.dumps(payload, ensure_ascii=False)
        resp = self.app.put(url, data=data, content_type='application/json')

        content = json.loads(resp.data)
        item = content['data']['items'][0]

        print content
        for k in payload:
            #if type(item[k]) is list:
            #    text = ','.join(item[k])
            #    assert payload[k] == text
            #else:
            assert payload[k] == item[k]
        assert 'status' in content
        assert content['status'] == resp.status_code
        assert resp.status_code == 200

    def test_4_delete_item(self):

        print "DELETE ITEM"

        url = "/predictry/api/v1/items/%s/?appid=%s&domain=%s" % (self.item['id'], self.appid, self.domain)

        resp = self.app.delete(url)

        content = json.loads(resp.data)

        print content
        assert 'status' in content
        assert content['status'] == resp.status_code
        assert resp.status_code == 200
        for k in content['data']['items'][0]:
            assert content['data']['items'][0][k] == self.item[k]


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
            #if type(user[k]) is list:
            #    text = ','.join(user[k])
            #    assert self.user[k] == text
            #else:
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
            #if type(user[k]) is list:
            #    text = ','.join(user[k])
            #    assert self.user[k] == text
            #else:
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
            #if type(user[k]) is list:
            #    text = ','.join(user[k])
            #    assert payload[k] == text
            #else:
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

#class ActionTestCase(unittest.TestCase):
class ActionTestCase():

    def setUp(self):
        assert type(now) is long
        server.app.config['TESTING'] = True
        self.app = server.app.test_client()
        self.appid = "pongo"
        self.domain = "verve"
        self.action = dict(domain=self.domain, id=123456, type="view", timestamp=long(1800),
                           ip_address="192.168.24.0", session_id="xYz47Q",
                           guid="someGUID", agent="Mozilla") #quantum for rated
        self.item = dict(domain=self.domain, id=123456, name="TestItem", brand="TestBrand", model="TestModel",
             tags="Test,Item", description="This is a test item",
             price=1.0, category="TestItem", date_added=now,
             item_url="http://localhostL7474/",
             image_url="images.google.com")
        self.user = dict(domain=self.domain, id=123456, email="user@mail.domain.com")


    def tearDown(self):
        pass

    def test_1_create_action(self):

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
            if type(user[k]) is list:
                text = ','.join(user[k])
                assert self.user[k] == text
            else:
                assert self.user[k] == user[k]

        print "CREATE ITEM"

        url = "/predictry/api/v1/items/?appid=%s&domain=%s" % (self.appid, self.domain)

        data = json.dumps(self.item, ensure_ascii=False)
        resp = self.app.post(url, data=data, content_type='application/json')

        content = json.loads(resp.data)

        print content
        assert 'status' in content
        assert content['status'] == resp.status_code
        assert resp.status_code == 200

        item = content['data']['items'][0]

        for k in self.item:
            if type(item[k]) is list:
                text = ','.join(item[k])
                assert self.item[k] == text
            else:
                assert self.item[k] == item[k]

        print "CREATE ACTION"

        url = "/predictry/api/v1/actions/?appid=%s&domain=%s" % (self.appid, self.domain)


        data = json.dumps(dict(self.action.items() + dict(user_id=123456, item_id=123456).items()),
                          ensure_ascii=False)
        resp = self.app.post(url, data=data, content_type='application/json')

        content = json.loads(resp.data)

        print content
        assert 'status' in content
        assert content['status'] == resp.status_code
        assert resp.status_code == 200

        action = content['data']['actions'][0]

        for k in self.action:
            if type(action[k]) is list:
                text = ','.join(action[k])
                assert self.action[k] == text
            else:
                assert self.action[k] == action[k]

    def test_2_get_action(self):

        print "RETRIEVE ACTION"

        url = "/predictry/api/v1/actions/%s/?appid=%s&domain=%s" % (self.action['id'], self.appid, self.domain)

        resp = self.app.get(url)

        content = json.loads(resp.data)

        print content
        assert 'data' in content
        assert 'status' in content
        assert content['status'] == resp.status_code

        action = content['data']['actions'][0]

        for k in self.action:
            if type(action[k]) is list:
                text = ','.join(action[k])
                assert self.action[k] == text
            else:
                assert self.action[k] == action[k]

    def test_3_update_action(self):

        print "UPDATE ACTION"

        url = "/predictry/api/v1/actions/%s/?appid=%s&domain=%s" % (self.action['id'], self.appid, self.domain)

        payload = dict(timestamp=2400, agent="Safari")
        data = json.dumps(payload, ensure_ascii=False)
        resp = self.app.put(url, data=data, content_type='application/json')

        content = json.loads(resp.data)
        action = content['data']['actions'][0]

        print content
        for k in payload:
            if type(action[k]) is list:
                text = ','.join(action[k])
                assert payload[k] == text
            else:
                assert payload[k] == action[k]

    def test_4_delete_action(self):

        print "DELETE ACTION"

        url = "/predictry/api/v1/actions/%s/?appid=%s&domain=%s" % (self.action['id'], self.appid, self.domain)

        resp = self.app.delete(url)

        content = json.loads(resp.data)

        print content
        assert 'status' in content
        assert content['status'] == resp.status_code
        assert resp.status_code == 200
        for k in content['data']['actions'][0]:
            assert content['data']['actions'][0][k] == self.action[k]

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

        print "DELETE ITEM"

        url = "/predictry/api/v1/items/%s/?appid=%s&domain=%s" % (self.item['id'], self.appid, self.domain)

        resp = self.app.delete(url)

        content = json.loads(resp.data)

        print content
        assert 'status' in content
        assert content['status'] == resp.status_code
        assert resp.status_code == 200
        for k in content['data']['items'][0]:
            assert content['data']['items'][0][k] == self.item[k]


if __name__ == '__main__':
    unittest.main()

#from predictry.engine.graph.query.executor.executor import QueryExecutor

#qexec = QueryExecutor()

#qgen = ActionQueryGenerator()

#q, param = qgen.create(args=dict(domain="verve", appid="pongo"),
#                  data=dict(id=1, item_id=1, session_id=1, browser_id=1,
#                            type="view", timestamp=123456))

#r, err = qexec.run(q, param, commit=True)

#print r, err

#q, param = qgen.read(args=dict(domain="verve", appid="pongo", id=1))

#r, err = qexec.run(q, param, commit=False)
#print r, err

#q, param = qgen.update(args=dict(domain="verve", appid="pongo", id=1), data=dict(timestamp=654321, fuzz="buzz"))

#r, err = qexec.run(q, param, commit=True)
#print r, err

#q, param = qgen.delete(args=dict(domain="verve", appid="pongo", id=1))

#r, err = qexec.run(q, param, commit=True)
#print r, err