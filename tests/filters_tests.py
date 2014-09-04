__author__ = 'guilherme'

import json
import time
import unittest
from predictry.engine.graph.query.generator.services import recommendation as rec

now = long(time.time().real)


'''
Test data
#create data

CREATE (:house:test {id: 1, rooms: 2, beach: false, region:["Belarus", "Virginia", "Pt. Elizabeth"]})
CREATE (:house:test {id: 2, rooms: 3, beach: true, region:["Belarus", "Virginia"]})
CREATE (:house:test {id: 3, rooms: 4, beach: true, region:["Belarus"]})

#delete data
MATCH (n:house:test) DELETE n

'''

class FilterTestCase(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_1_single_single(self):
        n_rooms = 2
        beach = "false"
        ref = "x"

        q = "rooms$e$%d$num|beach$e$%s$bool" % (n_rooms, beach)

        filters = rec.parse_filters(q)

        print rec.translate_filters(filters, ref)

    def test_2_single_list(self):
        location = "Belarus"
        ref = "x"

        q = "region$cti$%s$str" % location

        filters = rec.parse_filters(q)

        print rec.translate_filters(filters, ref)

    def test_3_list_list(self):
        location = "Belarus"
        ref = "x"

        q = "regions$cti$%s$str$ls" % location

        filters = rec.parse_filters(q)

        print rec.translate_filters(filters, ref)

    def test_4_all_at_once(self):
        n_rooms = 2
        location = "Belarus"
        locations = "Belarus, Pt.Elizabeth"
        ref = "x"

        q = "rooms$e$%d$num|region$cti$%s$str|regions$cti$%s$str$ls" % (n_rooms, location, locations)

        filters = rec.parse_filters(q)

        print rec.translate_filters(filters, ref)


if __name__ == '__main__':
    unittest.main()