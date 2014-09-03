__author__ = 'guilherme'

import json
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

        print "RECOMMENDATION: Other items viewed (oiv)"

        url = "/predictry/api/v1/recommend/?appid=%s&domain=%s&type=%s&item_id=%s&fields=%s&q=%s" \
              % (self.appid, self.domain, "oiv", str(5124), "price", "price$gt$10$num")

        resp = self.app.get(url)

        content = json.loads(resp.data)

        print content
        assert 'status' in content
        assert content['status'] == resp.status_code
        assert resp.status_code == 200

        #item = content['data']['items'][0]
        #for k in ["id", "matches"]:
        #    assert item[k]

    def test_2_oivt(self):

        print "RECOMMENDATION: Other items viewed together (oivt)"

        url = "/predictry/api/v1/recommend/?appid=%s&domain=%s&type=%s&item_id=%s&fields=%s&q=%s" \
              % (self.appid, self.domain, "oivt", str(5124), "price", "price$lt$10$num")

        resp = self.app.get(url)

        content = json.loads(resp.data)

        print content
        assert 'status' in content
        assert content['status'] == resp.status_code
        assert resp.status_code == 200

        #item = content['data']['items'][0]
        #for k in ["id", "matches"]:
        #    assert item[k]

    def test_3_rts(self):

        print "RECOMMENDATION: Recent Top Sellers (trp)"

        url = "/predictry/api/v1/recommend/?appid=%s&domain=%s&type=%s&fields=%s&q=%s" \
              % (self.appid, self.domain, "trp", "price", "price$lt$10$num")

        resp = self.app.get(url)

        content = json.loads(resp.data)

        print content
        assert 'status' in content
        assert content['status'] == resp.status_code
        assert resp.status_code == 200
