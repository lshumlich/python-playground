#!/bin/env python3

import unittest

#TODO This test must be redone to not depend on a specific database

from database.sqlite_appserver import AppServer
from database.data_structure import DataStructure

class FlaskTest(unittest.TestCase):

    def setUp(self):
        self.myapp = AppServer.app.test_client()

    def test_to_json(self):
        # create a dummy request structure
        request = DataStructure()
        # This is exactly what the data from the browser looks like:
        request.data = b'{"tableName":"BAInfo","attrName":" StartDate ","attrValue":"","linkName":"undefined","baseTab":false,"showAttrs":""}'
        dictionaryStructure = AppServer.to_json(request)
        self.assertEqual("BAInfo", dictionaryStructure['tableName'])

    def test_linkjson(self):
        resp = self.myapp.post('/data/link.json',data='{"fld1":"val1"}')
        print(resp)      

