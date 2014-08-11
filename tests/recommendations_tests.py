__author__ = 'guilherme'

import json
import time
import unittest
from predictry import server

class RecommendationTestCase(unittest.TestCase):

    def setUp(self):
        server.app.config['TESTING'] = True
        self.app = server.app.test_client()
        self.appid = "pongo"
        self.domain = "redmart"

    def tearDown(self):
        pass

    def test_1_oiv(self):

        print "RECOMMENDATION: OIV"

        url = "/predictry/api/v1/recommend/"

        data = json.dumps(dict(itemId=9095, type="oiv", appid=self.appid,
                               domain=self.domain, fields="price,description",
                               priceFloor=10), ensure_ascii=False)
        resp = self.app.post(url, data=data, content_type='application/json')

        content = json.loads(resp.data)

        print content
        assert 'status' in content
        assert content['status'] == resp.status_code
        assert resp.status_code == 200

        #item = content['data']['items'][0]
        #for k in self.item:
        #    if type(item[k]) is list:
        #        text = ','.join(item[k])
        #        assert self.item[k] == text
        #    else:
        #        assert self.item[k] == item[k]


    def test_2_oip(self):

        print "RECOMMENDATION: OIP"

        url = "/predictry/api/v1/recommend/"

        data = json.dumps(dict(itemId=9095, type="oip", appid=self.appid,
                               domain=self.domain, fields="price,description"),
                          ensure_ascii=False)
        resp = self.app.post(url, data=data, content_type='application/json')

        content = json.loads(resp.data)

        print content
        assert 'status' in content
        assert content['status'] == resp.status_code
        assert resp.status_code == 200

    def test_3_oivt(self):

        print "RECOMMENDATION: OIVT"

        url = "/predictry/api/v1/recommend/"

        data = json.dumps(dict(itemId=9095, type="oivt", appid=self.appid,
                               domain=self.domain, fields="price,description"),
                          ensure_ascii=False)
        resp = self.app.post(url, data=data, content_type='application/json')

        content = json.loads(resp.data)

        print content
        assert 'status' in content
        assert content['status'] == resp.status_code
        assert resp.status_code == 200

    def test_4_oipt(self):

        print "RECOMMENDATION: OIPT"

        url = "/predictry/api/v1/recommend/"

        data = json.dumps(dict(itemId=9095, type="oipt", appid=self.appid,
                               domain=self.domain, fields="price,description"),
                          ensure_ascii=False)
        resp = self.app.post(url, data=data, content_type='application/json')

        content = json.loads(resp.data)

        print content
        assert 'status' in content
        assert content['status'] == resp.status_code
        assert resp.status_code == 200