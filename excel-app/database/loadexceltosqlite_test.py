#!/bin/env python3
"""
Testing loading an Excel spreadsheet into an sqlite3 database.

Test that the worksheet has x number of tabs
Test that each tab has x number of columns
Test that each tab has x number of rows

test that we have an empty database
load database

test that we have x number of tables
test that each table has x number of columns
test that each table has x number of row

cleanup
test that the database is empty


"""

import unittest
import os
import database.loadexceltosqlite


class TestLoader(unittest.TestCase):

    TEST_DATABASE = 'test_database.db'
    TEST_SPREADSHEET = 'test_database.xlsx'

    def setUp(self):
        print ("Creating temporary database %s" % self.TEST_DATABASE)
        self.loader = database.loadexceltosqlite.Loader()
        self.loader.connect(self.TEST_DATABASE)
        self.loader.openExcel(self.TEST_SPREADSHEET)
        self.loader.loadAllSheets()
        self.shower = database.loadexceltosqlite.Shower()
        self.shower.connect(self.TEST_DATABASE)

    def test_show_tables(self):
        self.assertIn('Well', self.shower.showTables())
        self.assertIn('RoyaltyMaster', self.shower.showTables())

    def test_drop_table(self):
        self.loader.deleteTable('Well')
        self.assertNotIn('Well', self.shower.showTables())

    def test_show_columns(self):
        self.assertIn('RoyaltyClassification', self.shower.showColumns('Well'))
        self.assertIn('TruckingDeducted',
                self.shower.showColumns('RoyaltyMaster'))

    def test_show_table(self):
        # Had to fix showTable() to make it work. It used to return an
        # sqliteCursor object, now it returns a list of rows, much like
        # showTables()
        table = self.shower.showTable('Well')
        print(table)
        self.assertIn('SKWI112062705025W300', table[1])


#    Doesn't work because createTable expects 'row' objects returned by
#    openpyxl, not strings :( Nice try, though
#    def test_create_table(self):
#        test_header_row = ['Full Name', 'Age', 'Date']
#        test_row_1 = ['John Doe', 30, '2015-01-01']
#        test_row_2 = ['Jane Doe', 50, '1969-10-10']
#        self.loader.createTable('Test Table', test_header_row, test_row_1)
    
    def tearDown(self):
        self.shower.close()
        print ("Testing done, removing %s" % self.TEST_DATABASE)
        os.remove(self.TEST_DATABASE)

if __name__ == '__main__':
    print ("Here be tests:")
    unittest.main()
