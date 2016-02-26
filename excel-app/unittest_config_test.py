#!/bin/env python3
"""
Test all the weird and wonderful configuration parameters
"""


import unittest

import unittest_config


class UnittestConfigTest(unittest.TestCase):
    
    def test_get_database_instance_gives_same_instance(self):
        dbi1 = unittest_config.get_database_instance()
        dbi2 = unittest_config.get_database_instance()
        self.assertEqual(dbi1, dbi2, 'All instances must be the same.')
        
    def test_get_database_instance_with_a_name_gives_new_instance(self):
        dbi1 = unittest_config.get_database_instance()
        dbi2 = unittest_config.get_database_instance('mydb.db')
        self.assertNotEqual(dbi1, dbi2, 'These instances should not be the same.')
        dbi3 = unittest_config.get_database_instance()
        self.assertEqual(dbi2, dbi3, 'These should be the same.')
        
    def test_database_reset(self):
        dbi1 = unittest_config.get_database_instance()
        unittest_config.database_reset()
        dbi2 = unittest_config.get_database_instance()
        self.assertNotEqual(dbi1, dbi2, 'These instances should not be the same.')
        
