#!/bin/env python3

import unittest
import json

#TODO This test must be redone to not depend on a specific database

import config
# from database.sqlite_appserver import AppServer
# from database.data_structure import DataStructure
from database.database_create import DatabaseCreate
from database.utils import Utils
from app import app

from database.sqlite_utilities_test import DatabaseUtilities


class FlaskTest(unittest.TestCase):

    def setUp(self):
        self.assertEqual(config.get_environment(),'unittest') # Distructive Tests must run in unittest enviornment
        self.myapp = app.test_client()

#         self.myapp = AppServer.app.test_client()

    def test_link_update(self):
        db = config.get_database()
        dbu = DatabaseUtilities()
        db_create = DatabaseCreate()
        utils = Utils()

        dbu.delete_all_tables()
        db_create.linktab()

        # Test Insert
        data = dict()
        data["ID"] = '0'
        data["TabName"] = 'Lease'
        data["AttrName"] = 'ID'
        data["LinkName"] = 'Lease'
        json_to_browser = json.dumps(data)
        resp = self.myapp.post('/data/updateLinkRow.json',data=json_to_browser)
        self.assertEqual(resp.status_code, 200)
        data = utils.json_decode(resp)
        self.assertEqual(data["StatusCode"],0)
        
        result = db.select('LinkTab', TabName='Lease', AttrName='ID')
        self.assertEqual(len(result), 1)
        
        # Test Update
        data = utils.obj_to_dict(result[0])
        data['LinkName'] = 'Changed' 

        json_to_browser = json.dumps(data)
        resp = self.myapp.post('/data/updateLinkRow.json',data=json_to_browser)
        self.assertEqual(resp.status_code, 200)
        data = utils.json_decode(resp)
        self.assertEqual(data["StatusCode"],0)
        
        result = db.select('LinkTab', TabName='Lease', AttrName='ID')
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].LinkName,'Changed')
        
    def test_get_link_row(self):
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
        resp = self.myapp.post('/data/getLinkRow.json',data=json_to_browser)
        self.assertEqual(resp.status_code, 200)
        data = utils.json_decode(resp)
        self.assertEqual(data["LinkName"],'')
        
        linktab.LinkName = 'Well'
        linktab.BaseTab = 0
        linktab.ShowAttrs = 'ID,UWI'
        db.insert(linktab)
        
        # Data should be found 
        resp = self.myapp.post('/data/getLinkRow.json',data=json_to_browser)
        data = utils.json_decode(resp)
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(data["LinkName"],'Well')
        self.assertEqual(data["ShowAttrs"],'ID,UWI')
        
        print('status:',resp.status)
        print('status code:',resp.status_code)
        print(resp)
        print(resp.data)      
        
    def test_get_link_data(self):
        #setup stuff
        utils = Utils()
        db = config.get_database()
        dbu = DatabaseUtilities()
        db_create = DatabaseCreate()

        dbu.delete_all_tables()
        db_create.linktab()
        dbu.create_some_test_well_royalty_masters()
        dbu.create_some_test_leases()
        
        linktab = db.get_data_structure('LinkTab')
        linktab.TabName = 'Lease'
        linktab.AttrName = 'ID'
        linktab.LinkName = 'Lease'
        linktab.BaseTab = 1
        linktab.ShowAttrs = 'ID,Lessor'
        db.insert(linktab)
        
        linktab = db.get_data_structure('LinkTab')
        linktab.TabName = 'Well'
        linktab.AttrName = 'LeaseID'
        linktab.LinkName = 'Lease'
        linktab.BaseTab = 0
        linktab.ShowAttrs = ''
        db.insert(linktab)

        data = dict()
        data["TabName"] = 'Well'
        data["AttrName"] = 'LeaseID'
        data["AttrValue"] = 2
        
        json_from_browser = json.dumps(data)
        print('json_from_browser', json_from_browser)

        # Data should be found
        resp = self.myapp.post('/data/getLinkData.json',data=json_from_browser)
        print("resp:",resp)
        self.assertEqual(resp.status_code, 200)
        data = utils.json_decode(resp)
        
        print('data',data)
        rows = data['BaseData']
        self.assertEqual(len(rows),2)
        self.assertEqual(rows[0][0],'ID')
        self.assertEqual(rows[0][1],'Lessor')
        self.assertEqual(rows[1][0],2)
        self.assertEqual(rows[1][1],2346)
        
        rows = data['Links']
        self.assertEqual(len(rows),2)
        self.assertEqual(rows[0][0],'Lease')
        self.assertEqual(rows[0][1],'ID')
        self.assertEqual(rows[1][0],'Well')
        self.assertEqual(rows[1][1],'LeaseID')
        
