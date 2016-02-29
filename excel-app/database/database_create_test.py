#!/bin/env python3

import unittest

import config
from database.database_create import DatabaseCreate
from database.sqlite_utilities_test import DatabaseUtilities

class Test(unittest.TestCase):

    def setUp(self):
        self.assertEqual(config.get_environment(),'unittest') # Distructive Tests must run in unittest enviornment

    def test_all(self):
        dbu = DatabaseUtilities()
        dbc = DatabaseCreate()
        
        dbu.delete_all_tables()
        dbc.create_all()
