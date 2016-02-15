#!/bin/env python3
"""
Test all the weird and wonderful configuration parameters
"""


import unittest
import os

import config
from config import DatabaseInstance
from database.apperror import AppError


class Test(unittest.TestCase):
    
    def test_where_am_i(self):
        config.where_am_i() # Simple test it should just print to the console...
        
    def test_get_file_dir(self):
        self.assertTrue(os.path.isdir(config.get_file_dir()),'File directory must exist: ' + config.get_file_dir())
        
    def test_get_temp_dir(self):
        self.assertTrue(os.path.isdir(config.get_temp_dir()),'File directory must exist: ' + config.get_temp_dir())
        
    # Note*** This test could cause a problem if it's not the first one to run.
    def test_only_one_instance_of_database_instance(self):
        DatabaseInstance('dummy.db');
        self.assertRaises(AppError, DatabaseInstance, 'dummy.db')
    
    def test_get_Database_gives_same_instance(self):
        db1 = config.get_database()
        db2 = config.get_database()
        self.assertEqual(db1, db2, 'Only one instance of database is allowed.')
        
    def test_set_database_must_be_called_before_get_database(self):
        config.get_database()
        self.assertRaises(AppError, config.set_database_name, 'my_db.db')
        
    def test_get_database_name(self):
        config.get_database_name()
        
    def test_get_database_instance(self):
        config.get_database_instance()
        
    def test_get_database(self):
        config.get_database()
        
    def test_set_database_name(self):
        config.set_database_name("whatever.db")
        