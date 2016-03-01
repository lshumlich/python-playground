#!/bin/env python3

import unittest

#TODO This test must be redone to not depend on a specific database

from database.sqlite_appserver import AppServer
from database.data_structure import DataStructure
from database.sqlite_utilities_test import DatabaseUtilities

class FlaskTest(unittest.TestCase):

    def setUp(self):
        self.myapp = AppServer.app.test_client()

    def test_to_json(self):
        # create a dummy request structure
        request = DataStructure()
        # This is exactly what the data from the browser looks like:
        request.data = b'{"tableName":"BAInfo","attrName":" StartDate ","attrValue":"","linkName":"undefined","baseTab":false,"showAttrs":""}'
        dictionaryStructure = AppServer.json_decode(request)
        self.assertEqual("BAInfo", dictionaryStructure['tableName'])

    def test_linkjson(self):
        resp = self.myapp.post('/data/link.json',data='{"fld1":"val1"}')
        self.assertEqual(resp.status_code, 200)
        
    def test_get_link_data(self):
        resp = self.myapp.post('/data/getLinkData.json',data='{"TabName":"Well","AttrName":"UWI"}')
        print('status:',resp.status)
        print('status code:',resp.status_code)
        print(resp)
        print(resp.data)      

#     @app.route("/data/getLinkData.json",methods=['POST']) 

