#!/bin/env python3

import unittest

import config
from database.sqlite_show import Shower
from database.sqlite_database_test import DatabaseUtilities
from database.sqlite_load_excel import Loader


class TestLoader(unittest.TestCase):

    TEST_SPREADSHEET = config.get_file_dir() + 'test_database.xlsx'

    def test_run(self):
        #Testing loading an Excel spreadsheet into an sqlite3 database.
#         print ("Creating temporary database %s" % self.TEST_DATABASE)

        self.assertEqual(config.get_environment(),'unittest') # Distructive Tests must run in unittest enviornment

        dbu = DatabaseUtilities()
        loader = Loader()
        dbu.delete_all_tables()
        dbi = config.get_database_instance()
        
        loader.connect()
        loader.open_excel(self.TEST_SPREADSHEET)
        shower = Shower()
        shower.connect()

        #Test that the worksheet has x number of tabs
        self.assertEqual(len(loader.wb.get_sheet_names()), 2)

        #Test that each tab has x number of columns
        self.assertEqual(len(loader.wb['Well'].columns), 11)
        self.assertEqual(len(loader.wb['Royalty Master'].columns), 10)

        #Test that each tab has x number of rows
        self.assertEqual(len(loader.wb['Well'].rows), 9)
        self.assertEqual(len(loader.wb['Royalty Master'].rows), 11)

        print(dbi.get_table_names())
        self.assertEqual(len(dbi.get_table_names()), 0)

        #Test that we have x number of tables
        loader.load_all_sheets()
        self.assertEqual(len(dbi.get_table_names()), 2)

        #test that each table has x number of columns
        self.assertEqual(len(shower.show_table('Well')), 8)
        self.assertEqual(len(shower.show_table('RoyaltyMaster')), 10)

        #test that each table has x number of row
        self.assertEqual(len(shower.show_columns('Well')), 11)
        self.assertEqual(len(shower.show_columns('RoyaltyMaster')), 10)

        #test column type
        self.assertEqual(shower.column_type('Well', 'WellId'), 'int')
        loader.commit()
        dbu.delete_table('well')
        self.assertNotIn('Well', dbi.get_table_names())

if __name__ == '__main__':
    unittest.main()
