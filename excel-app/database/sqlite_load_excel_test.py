#!/bin/env python3

import os
import unittest
import openpyxl
import database.sqlite_load_excel
import database.sqlite_show


class TestLoader(unittest.TestCase):

    TEST_DATABASE = 'test_database.db'
    TEST_SPREADSHEET = 'test_database.xlsx'

    def test_run(self):
    	#Testing loading an Excel spreadsheet into an sqlite3 database.
        print ("Creating temporary database %s" % self.TEST_DATABASE)
        loader = database.sqlite_load_excel.Loader()
        loader.delete_database(self.TEST_DATABASE)
        loader.connect(self.TEST_DATABASE)
        loader.openExcel(self.TEST_SPREADSHEET)
        shower = database.sqlite_show.Shower()
        shower.connect(self.TEST_DATABASE)

        #Test that the worksheet has x number of tabs
        self.assertEqual(len(loader.wb.get_sheet_names()), 2)

        #Test that each tab has x number of columns
        self.assertEqual(len(loader.wb['Well'].columns), 9)
        self.assertEqual(len(loader.wb['Royalty Master'].columns), 10)

        #Test that each tab has x number of rows
        self.assertEqual(len(loader.wb['Well'].rows), 9)
        self.assertEqual(len(loader.wb['Royalty Master'].rows), 11)

        #Test that we have an empty database
        self.assertEqual(len(shower.showTables()), 0)

        #Test that we have x number of tables
        loader.loadAllSheets()
        self.assertEqual(len(shower.showTables()), 2)

        #test that each table has x number of columns
        self.assertEqual(len(shower.showTable('Well')), 8)
        self.assertEqual(len(shower.showTable('RoyaltyMaster')), 10)

        #test that each table has x number of row
        self.assertEqual(len(shower.showColumns('Well')), 9)
        self.assertEqual(len(shower.showColumns('RoyaltyMaster')), 10)

        #test column type
        self.assertEqual(shower.columnType('Well', 'WellId'), 'int')
        #!!!really odd: removing the following print will make deleteTable fail
        print(shower.showTables())
        loader.deleteTable('Well')
        self.assertNotIn('Well', shower.showTables()) 

        #clean up
        loader.close()
        shower.close()
        loader.delete_database(self.TEST_DATABASE)        
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
