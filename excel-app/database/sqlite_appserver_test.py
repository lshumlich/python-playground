#!/bin/env python3

import unittest
import json

#TODO This test must be redone to not depend on a specific database

import config
from database.sqlite_appserver import AppServer
from database.data_structure import DataStructure
from database.database_create import DatabaseCreate
from database.utils import Utils

from database.sqlite_utilities_test import DatabaseUtilities


class FlaskTest(unittest.TestCase):

    def setUp(self):
        self.assertEqual(config.get_environment(),'unittest') # Distructive Tests must run in unittest enviornment
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
        #setup stuff
        db = config.get_database()
        dbu = DatabaseUtilities()
        db_create = DatabaseCreate()
        utils = Utils()

        dbu.delete_all_tables()

        db_create.linktab()
        linktab = db.get_data_structure('LinkTab')
        linktab.TabName = 'Well'
        linktab.AttrName = 'ID'
        json_to_browser = json.dumps(utils.obj_to_dict(linktab))
        print('json_to_browser', json_to_browser)

        # Data should not be found but there should not be an error
        resp = self.myapp.post('/data/getLinkData.json',data=json_to_browser)
        data = AppServer.json_decode(resp)
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(data["LinkName"],'')
        
        linktab.LinkName = 'Well'
        linktab.BaseTab = 0
        linktab.ShowAttrs = 'ID,UWI'
        db.insert(linktab)
        
        # Data should be found 
        resp = self.myapp.post('/data/getLinkData.json',data=json_to_browser)
        data = AppServer.json_decode(resp)
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(data["LinkName"],'Well')
        self.assertEqual(data["ShowAttrs"],'ID,UWI')
        

        
        
        print('status:',resp.status)
        print('status code:',resp.status_code)
        print(resp)
        print(resp.data)      

#     @app.route("/data/getLinkData.json",methods=['POST']) 

