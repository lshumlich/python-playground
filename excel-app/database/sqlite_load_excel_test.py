#!/bin/env python3

import os
import unittest

import config
import database.sqlite_load_excel
import database.sqlite_show


class TestLoader(unittest.TestCase):

    TEST_DATABASE = config.get_temp_dir() + 'test_database.db'
    TEST_SPREADSHEET = config.get_file_dir() + 'test_database.xlsx'

    def test_run(self):
        #Testing loading an Excel spreadsheet into an sqlite3 database.
#         print ("Creating temporary database %s" % self.TEST_DATABASE)
        loader = database.sqlite_load_excel.Loader()
        loader.delete_database(self.TEST_DATABASE)
        loader.connect(self.TEST_DATABASE)
        loader.open_excel(self.TEST_SPREADSHEET)
        shower = database.sqlite_show.Shower()
        shower.connect(self.TEST_DATABASE)

        #Test that the worksheet has x number of tabs
        self.assertEqual(len(loader.wb.get_sheet_names()), 2)

        #Test that each tab has x number of columns
        self.assertEqual(len(loader.wb['Well'].columns), 11)
        self.assertEqual(len(loader.wb['Royalty Master'].columns), 10)

        #Test that each tab has x number of rows
        self.assertEqual(len(loader.wb['Well'].rows), 9)
        self.assertEqual(len(loader.wb['Royalty Master'].rows), 11)

        #Test that we have an empty database
        self.assertEqual(len(shower.show_tables()), 0)

        #Test that we have x number of tables
        loader.load_all_sheets()
        self.assertEqual(len(shower.show_tables()), 2)

        #test that each table has x number of columns
        self.assertEqual(len(shower.show_table('Well')), 8)
        self.assertEqual(len(shower.show_table('RoyaltyMaster')), 10)

        #test that each table has x number of row
        self.assertEqual(len(shower.show_columns('Well')), 11)
        self.assertEqual(len(shower.show_columns('RoyaltyMaster')), 10)

        #test column type
        self.assertEqual(shower.column_type('Well', 'WellId'), 'int')
        #!!!really odd: removing the following print will make deleteTable fail
        print(shower.show_tables())
        loader.commit()
        loader.delete_table('Well')
        self.assertNotIn('Well', shower.show_tables()) 

        #clean up
        loader.close()
        shower.close()
        # loader.delete_database(self.TEST_DATABASE)        
        self.assertFalse(os.path.exists(self.TEST_DATABASE))

"""
        self.assertIn('Well', shower.showTables())
        self.assertIn('RoyaltyMaster', shower.showTables())

        self.assertIn('RoyaltyClassification', shower.showColumns('Well'))
        self.assertIn('TruckingDeducted', shower.showColumns('RoyaltyMaster'))

        table = shower.showTable('Well')
        print(table)
        self.assertIn('SKWI112062705025W300', table[1])
"""

if __name__ == '__main__':
    unittest.main()
