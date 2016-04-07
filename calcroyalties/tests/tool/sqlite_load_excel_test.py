#!/bin/env python3

import unittest

import config
from tests.database.sqlite_database_test import DatabaseUtilities
from src.tool.sqlite_load_excel import Loader


class TestLoader(unittest.TestCase):

    TEST_SPREADSHEET = config.get_file_dir() + 'test_database.xlsx'

    def test_run(self):

        self.assertEqual(config.get_environment(), 'unittest')  # Distructive Tests must run in unittest enviornment

        dbu = DatabaseUtilities()
        # dbc = DatabaseCreate()
        loader = Loader()
        dbu.delete_all_tables()
        dbi = config.get_database_instance()
        db = config.get_database()

        loader.open_excel(self.TEST_SPREADSHEET)

        # Test that the worksheet has x number of tabs
        self.assertEqual(len(loader.wb.get_sheet_names()), 2)

        # Test that each tab has x number of columns
        self.assertEqual(len(loader.wb['Well'].columns), 12)
        self.assertEqual(len(loader.wb['Royalty Master'].columns), 11)

        # Test that each tab has x number of rows
        self.assertEqual(len(loader.wb['Well'].rows), 9)
        self.assertEqual(len(loader.wb['Royalty Master'].rows), 11)

        loader.load_all_sheets()

        # Test that we have x number of tables
        self.assertEqual(len(dbi.get_table_names()), 2)

        # check the rows and columns for well
        rows = db.select('Well')
        self.assertEqual(len(rows), 8)
        self.assertEqual(len(dbi.get_column_names()), 12)

        # check the rows and columns for royalty master
        rows = db.select('RoyaltyMaster')
        self.assertEqual(len(rows), 10)
        self.assertEqual(len(dbi.get_column_names()), 11)

if __name__ == '__main__':
    unittest.main()
