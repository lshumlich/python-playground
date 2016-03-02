#!/bin/env python3

import unittest

import config
from database.apperror import AppError
from database.sqlite_utilities_test import DatabaseUtilities
from database.data_structure import DataStructure
from database.database_create import DatabaseCreate


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
        self.assertEqual(len(self.db.select('Lease')), 4)
        self.assertEqual(len(self.db.select('Lease', Prov='SK')), 3)
        self.assertIsNone(self.db.select('Well', ID=1000))
        
    def test_update(self):
        self.dbu.create_some_test_wells()

        # change all types of attributes, read another record and then read the record again to make sure the changes were made.
        well = self.db.select('Well', ID=2)
        well.UWI = 'Changed'
        well.LeaseID = 100
        well.CommencementDate = '2016-02-01 00:00:00'
        self.db.update(well)
        well = self.db.select('Well', ID=1)
        self.assertEqual(well.ID, 1)
        self.assertEqual(well.UWI, 'SKWI111062705025W300')
        well = self.db.select('Well', ID=2)
        self.assertEqual(well.ID, 2)
        self.assertEqual(well.UWI, 'Changed')
        self.assertEqual(well.LeaseID, 100)
        self.assertEqual(well.CommencementDate, '2016-02-01 00:00:00')

        ds = DataStructure()
        self.assertRaises(AttributeError, self.db.update, ds)
        
        ds._table_name = 'Well'
        self.assertRaises(AttributeError, self.db.update, ds)
        ds.ID = 100
        self.assertRaises(AppError, self.db.update, ds)

    def test_insert(self):
        self.db_create.well()
        
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
        self.assertEqual(well.ID, 1)
        self.assertEqual(well.UWI, 'UWI for this well')
        
        well = self.db.get_data_structure('Well')
        well.UWI = 'Next Well UWI'
        well.ID = 10
        self.db.insert(well)
        
        well = self.db.select('Well', ID=1)
        self.assertEqual(well.ID, 1)
        self.assertEqual(well.UWI, 'UWI for this well')
        
        well = self.db.select('Well', ID=10)
        self.assertEqual(well.ID, 10)
        self.assertEqual(well.UWI, 'Next Well UWI')

        well = self.db.get_data_structure('Well')
        well.UWI = 'Just One More'
        self.db.insert(well)
        self.assertEqual(well.ID, 11)
        

        well = self.db.get_data_structure('Well')
        well.BadAttr = 'Just another value'
        self.assertRaises(AppError, self.db.insert,well)
        
    def test_delete(self):
#         statement = """
#             CREATE TABLE Well ('ID' int, 'UWI' text, 'Prov' text, 'WellType' text, 'LeaseType' text, 'LeaseID' int, 'RoyaltyClassification' text, 'Classification' text, 'SRC' int, 'IndianInterest' float, 'CommencementDate' date, 'ReferencePrice' int);
#             INSERT INTO Well VALUES(1,'SKWI111062705025W300','SK','Oil','OL',1,'New Oil','Heavy',0,0.25,'2014-12-01 00:00:00',1);
#             INSERT INTO Well VALUES(2,'SKWI112062705025W300','SK','Oil','OL',2,'Third Tier Oil','Southwest',0,0.95,'2014-12-01 00:00:00',1);
#             INSERT INTO Well VALUES(3,'SKWI113062705025W300','SK','Oil','OL',3,'Fourth Tier Oil','Other',0,1.0,NULL,NULL);
#         """
#         
#         self.dbu.execute_statement(statement)
        self.dbu.create_some_test_wells()

        self.assertEqual(4,len(self.db.select('Well')))
                         
        self.db.delete('Well', 2)
        self.assertEqual(3,len(self.db.select('Well')))
        self.assertIsNone(self.db.select('Well', ID=2))
        
        