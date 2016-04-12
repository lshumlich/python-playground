#!/bin/env python3

import unittest
from datetime import datetime

import config
from src.database.data_structure import DataStructure
from src.database.database_create import DatabaseCreate
from src.util.apperror import AppError
from tests.database.sqlite_utilities_test import DatabaseUtilities


class SqliteDatabaseTest(unittest.TestCase):

    def setUp(self):
        self.assertEqual(config.get_environment(),'unittest') # Distructive Tests must run in unittest enviornment
        self.dbi = config.get_database_instance()
        self.db = config.get_database()
        self.dbu = DatabaseUtilities()
        self.db_create = DatabaseCreate()
        
        self.dbu.delete_all_tables()
        
    def test_to_db_value(self):
        self.assertEqual('123', self.db.to_db_value(123))
        self.assertEqual('"asdf"', self.db.to_db_value("asdf"))
        self.assertEqual('123.45', self.db.to_db_value(123.45))
        self.assertEqual('1', self.db.to_db_value(True))
        self.assertEqual('0', self.db.to_db_value(False))
        self.assertEqual('null', self.db.to_db_value(None))
        
    def test_get_data_structure(self):
        ds = self.db.get_data_structure('WhatEver')
        self.assertEqual('WhatEver',ds._table_name)

    def test_select(self):
        self.dbu.create_some_test_wells()
        self.dbu.create_some_test_leases()
        
        self.assertIsNotNone(self.db.select('Well', RoyaltyClassification='New Oil'))
        self.assertEqual(len(self.db.select('Well', Prov='SK', Classification='Other')), 2)
        self.assertEqual(len(self.db.select('Well')), 4)
        self.assertRaises(AppError, self.db.select, 'WrongTable')
        self.assertRaises(AppError, self.db.select, 'WrongTable',WrongAttr='WhoCares')
        self.assertRaises(AppError, self.db.select, 'Well', Foo='bar')
        self.assertEqual(len(self.db.select('Lease')), 3)
        self.assertEqual(len(self.db.select('Lease', Prov='SK')), 3)
        self.assertEqual(len(self.db.select('Well', ID=1000)),0)


        #WRITE TEST FOR SELECT1
        
    def test_update(self):
        self.dbu.create_some_test_wells()

        # change all types of attributes, read another record and then read the record again to make sure the changes were made.
        well = self.db.select('Well', ID=2)
        well[0].UWI = 'Changed'
        well[0].LeaseID = 100
        well[0].CommencementDate = '2016-02-01 00:00:00'
        well[0].WellType = None
        self.db.update(well[0])
        well = self.db.select('Well', ID=1)
        self.assertEqual(well[0].ID, 1)
        self.assertEqual(well[0].UWI, 'SKWI111062705025W300')
        well = self.db.select('Well', ID=2)
        self.assertEqual(well[0].ID, 2)
        self.assertEqual(well[0].UWI, 'Changed')
        self.assertEqual(well[0].LeaseID, 100)
        self.assertEqual(well[0].CommencementDate, datetime(2016,2,1,0,0))
        self.assertEqual(well[0].WellType, None)

        ds = DataStructure()
        self.assertRaises(AttributeError, self.db.update, ds)
        
        ds._table_name = 'Well'
        self.assertRaises(AttributeError, self.db.update, ds)
        ds.ID = 100
        self.assertRaises(AppError, self.db.update, ds)

    def test_insert(self):
        self.db_create.Well()
        
        well = DataStructure()
        well.UWI = 'UWI for this well'
        # Should raise this error since we need to get the structure from the database
        self.assertRaises(TypeError, self.db.insert)

        well = self.db.get_data_structure('Well')
        well.UWI = 'UWI for this well'
        self.db.insert(well)
        self.assertEqual(well.ID, 1)
        
        well = self.db.get_data_structure('Well')
        well.UWI = 'Different UWI for this well'
        self.db.insert(well)
        self.assertEqual(well.ID, 2)
        
        well = self.db.select('Well', ID=1)
        self.assertEqual(well[0].ID, 1)
        self.assertEqual(well[0].UWI, 'UWI for this well')
        
        well = self.db.get_data_structure('Well')
        well.UWI = 'Next Well UWI'
        well.ID = 10
        self.db.insert(well)
        
        well = self.db.select('Well', ID=1)
        self.assertEqual(well[0].ID, 1)
        self.assertEqual(well[0].UWI, 'UWI for this well')
        
        well = self.db.select('Well', ID=10)
        self.assertEqual(well[0].ID, 10)
        self.assertEqual(well[0].UWI, 'Next Well UWI')

        well = self.db.get_data_structure('Well')
        well.UWI = 'Just One More'
        self.db.insert(well)
        self.assertEqual(well.ID, 11)
        

        well = self.db.get_data_structure('Well')
        well.BadAttr = 'Just another value'
        self.assertRaises(AppError, self.db.insert,well)
        
        # if the ID is None,Blank,or zero we shold still be able to insert a record
        well = self.db.get_data_structure('Well')
        well.ID = None
        well.UWI = 'Just One More'
        self.db.insert(well)
        self.assertEqual(well.ID, 12)
        well.ID = 0
        self.db.insert(well)
        self.assertEqual(well.ID, 13)
        well.ID = ''
        self.db.insert(well)
        self.assertEqual(well.ID, 14)
        
        
    def test_delete(self):
        self.dbu.create_some_test_wells()

        self.assertEqual(4,len(self.db.select('Well')))
                         
        self.db.delete('Well', 2)
        self.assertEqual(3,len(self.db.select('Well')))
        self.assertEqual(0, len(self.db.select('Well', ID=2)))
        
    def test_date_format(self):
        self.dbu.create_some_test_wells()
        
        well = self.db.select('Well', ID=1)
        self.assertTrue(isinstance(well[0].CommencementDate,datetime))
#         print('CommencementDate:' , well[0].CommencementDate, type(well[0].CommencementDate))
