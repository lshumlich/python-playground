#!/bin/env python3
"""
Test all the weird and wonderful configuration parameters
"""


import unittest
import os

import config


class Test(unittest.TestCase):
    
    def test_where_am_i(self):
        config.where_am_i() # Simple test it should just print to the console...
        
    def test_get_file_dir(self):
        self.assertTrue(os.path.isdir(config.get_file_dir()),'File directory must exist: ' + config.get_file_dir())
        
    def test_get_temp_dir(self):
        self.assertTrue(os.path.isdir(config.get_temp_dir()),'File directory must exist: ' + config.get_temp_dir())
        
    def test_get_database_instance_gives_same_instance(self):
        dbi1 = config.get_database_instance()
        dbi2 = config.get_database_instance()
        self.assertEqual(dbi1, dbi2, 'All instances must be the same.')
        
    def test_get_database_instance_with_a_name_gives_new_instance(self):
        dbi1 = config.get_database_instance()
        dbi2 = config.get_database_instance('mydb.db')
        self.assertNotEqual(dbi1, dbi2, 'These instances should not be the same.')
        dbi3 = config.get_database_instance()
        self.assertEqual(dbi2, dbi3, 'These should be the same.')
