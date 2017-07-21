#!/bin/env python3
"""
Test all the weird and wonderful configuration parameters
"""

import unittest
import os, os.path

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
        
    def test_debug_sql(self):
        None
        # print('debug_sql:',config.debug_sql())

    def test_set_methods(self):
        """ this tests all of the set methods since they need to work together """
        save_config_file = config.ConfigObject.CONFIG_FILE 
        
        # Test the default with no file is 'unittest'
        config.reset()
        config.ConfigObject.CONFIG_FILE = 'badfile.xxx'
        self.assertEqual(config.get_environment(), 'unittest')
        
        config.ConfigObject.CONFIG_FILE = save_config_file
        
        # test that if we the database name we have an unknown environmentwe
        config.reset()
        config.set_database_name(':memory:')
        self.assertEqual(config.get_environment(), '????')
        
        # test that if we the database name we have an unknown environment
        config.reset()
        config.set_enviornment('test')
        self.assertTrue(config.get_database_name())
        
        # test that we have an instance and database
        config.reset()
        self.assertTrue(config.get_environment()) # All these values must be set... Can't test to what though
        self.assertTrue(config.get_database_name())
        self.assertTrue(config.get_database_instance())
        self.assertTrue(config.get_database())

        # test that the default pdf location is the temp directory
        config.reset()
        self.assertTrue(config.get_pdf_location())
        self.assertEqual(config.get_pdf_location(),config.get_temp_dir())

        
        # Test that the config file works. This is commented out because it can not resonably be tested
#         config.reset()
#         self.assertEqual(config.get_environment(),"test") # All these values must be set... Can't test to what though
        


