#!/bin/env python3

import unittest
from unittest import TestLoader, TextTestRunner, TestSuite
import subprocess
import os

# from database.database import DataBase
# from database.royaltyworksheet import RoyaltyWorksheet
from src.calc.calcroyalties import ProcessRoyalties
# from database.calcroyalties_test import TestSaskRoyaltyCalc
# from database.sqlite_load_excel import Loader
from src.tool.sqlite_load_excel import load_all_from_scratch
# from database.sqlite_appserver import AppServer
from src.database.database_create import DatabaseCreate
from tests.database.sqlite_utilities_test import DatabaseUtilities
#from database.Adrienne import calc_royalties
#from database.Adrienne_test import test_calcSaskOilProvCrownRoyaltyRate

import config
#
# Using this technique I do not know how to run just one of the methods in the class. If you can 
# figure it out please send me a note.... Thanks Larry.
#

def run_royalties_and_worksheet():
    pr = ProcessRoyalties()
    pr.process_all()
    # pr.process_one('SK WI 111112905627W300', 201601, 'Oil')

#    pr.process(config.get_file_dir() + 'database.xlsx')
#     pr.process('d:/$temp/sample.xlsx')
    print('os name is:',os.name)
    if os.name != "posix":
        subprocess.call(['notepad.exe', config.get_temp_dir() + 'log.txt'])
        subprocess.call(['notepad.exe', config.get_temp_dir() + 'Royalty Worksheet.txt'])

def runTestModule():
    unittest.main(module='database.calcroyalties_test')
#    unittest.main(module='database.sqlite_load_excel_test')

def load_tests(loader, tests, pattern):
    suite = TestSuite()
    for all_test_suite in unittest.defaultTestLoader.discover('.', pattern='*_test.py'):
        for test_suite in all_test_suite:
            suite.addTests(test_suite)
    return suite

def drop_create_tables():
    dbu = DatabaseUtilities()
    dbu.delete_all_tables()
    create_tables()

def create_tables():
    db_create = DatabaseCreate()
    db_create.create_all()

def load_sample_data():
    dbu = DatabaseUtilities()
    drop_create_tables()
    dbu.create_some_test_wells()
    dbu.create_some_test_leases()

print('-- Runing Batch')
if __name__ == "__main__":
    drop_create_tables()
    load_all_from_scratch()
#     load_sample_data()

#     browser_app()
#    create_tables()
    run_royalties_and_worksheet()
#    unittest.main()
#     runTestModule()
    print("Goodbye world!")

    

# if __name__ == "__main__":
#     """This runs all the tests in the module"""
#    import sys;sys.argv = ['', 'Test.testName']
#    unittest.main() # This works for testing the current file
#     unittest.main(module='batch') # works
#     unittest.main(module='database.testhelper_test')
#      unittest.main(module='database.calcroyalties_test')
#     tst = TestSaskRoyaltyCalc()
#     tst.test_calcSaskOilProvCrownRoyaltyRate()

