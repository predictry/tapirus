__author__ = 'guilherme'

import json
import unittest
from predictry import server


class RecommendationTestCase(unittest.TestCase):

    def setUp(self):
        server.app.config['TESTING'] = True
        self.app = server.app.test_client()
        self.appid = "pongo"
        self.domain = "verve"

    def tearDown(self):
        pass

    def test_1_oiv(self):

        print "RECOMMENDATION: Other items viewed (oiv)"

        url = "/predictry/api/v1/recommend/?appid=%s&domain=%s" \
              % (self.appid, self.domain)

        data = json.dumps(dict(item_id=6, type="oiv", fields="brand,model"),
                          ensure_ascii=False)

        resp = self.app.post(url, data=data, content_type='application/json')

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

        url = "/predictry/api/v1/recommend/?appid=%s&domain=%s" \
              % (self.appid, self.domain)

        data = json.dumps(dict(item_id=6, type="oivt", fields="brand,model,size"),
                          ensure_ascii=False)

        resp = self.app.post(url, data=data, content_type='application/json')

        content = json.loads(resp.data)

        print content
        assert 'status' in content
        assert content['status'] == resp.status_code
        assert resp.status_code == 200

        #item = content['data']['items'][0]
        #for k in ["id", "matches"]:
        #    assert item[k]

    def test_3_rts(self):

        print "RECOMMENDATION: Recent Top Sellers (rts)"

        url = "/predictry/api/v1/recommend/?appid=%s&domain=%s" \
              % (self.appid, self.domain)

        data = json.dumps(dict(type="rts", fields="brand,model,size"),
                          ensure_ascii=False)

        resp = self.app.post(url, data=data, content_type='application/json')

        content = json.loads(resp.data)

        print content
        assert 'status' in content
        assert content['status'] == resp.status_code
        assert resp.status_code == 200
