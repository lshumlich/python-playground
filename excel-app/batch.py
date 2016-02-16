#!/bin/env python3

import unittest
import subprocess
import os

from database.database import DataBase
from database.royaltyworksheet import RoyaltyWorksheet
from database.calcroyalties import ProcessRoyalties
from database.calcroyalties_test import TestSaskRoyaltyCalc
from database.sqlite_load_excel import Loader
from database.sqlite_appserver import AppServer
import config
#
# Using this technique I do not know how to run just one of the methods in the class. If you can 
# figure it out please send me a note.... Thanks Larry.
#

def runRoyaltiesAndWorksheet():
    pr = ProcessRoyalties()
    pr.process(config.get_file_dir() + 'database.xlsx')
    pr.process('d:/$temp/sample.xlsx')
    print('os name is:',os.name)
    if os.name != "posix":
        subprocess.call(['notepad.exe', config.get_file_dir() + 'log.txt'])
        subprocess.call(['notepad.exe', config.get_file_dir() + 'Royalty Worksheet.txt'])

def runTestModule():
#     unittest.main(module='database.calcroyalties_test')
    unittest.main(module='database.sqlite_load_excel_test')

def sqliteLoadExcel():
    database = config.get_temp_dir() + 'browser.db'
    excelSheet = r'd:\$temp\Onion Lake SK wells.xlsx'
#     loader = database.sqlite_load_excel.Loader()
    loader = Loader()
    loader.connect(database)
    loader.open_excel(excelSheet)
    loader.load_all_sheets()
    loader.close()
    
def browser_app():
    AppServer.run(config.get_temp_dir() + 'browser.db')

print('-- Runing Batch')
if __name__ == "__main__":
#     sqliteLoadExcel()
    browser_app()

    
# runRoyaltiesAndWorksheet()
# runTestModule()

# if __name__ == "__main__":
#     """This runs all the tests in the module"""
#    import sys;sys.argv = ['', 'Test.testName']
#    unittest.main() # This works for testing the current file
#     unittest.main(module='batch') # works
#     unittest.main(module='database.testhelper_test')
#      unittest.main(module='database.calcroyalties_test')
#     tst = TestSaskRoyaltyCalc()
#     tst.test_calcSaskOilProvCrownRoyaltyRate()



#     Major Hack must be fixed.    
""" Ignore all this commented out code for now
class DataBaseTest(unittest.TestCase):

    def xtest_getMonthlyDataByWellProdMonthProduct(self):
        rw = RoyaltyWorksheet()
        rw.printWithWellProdDate(6,201501,'Oil')
        subprocess.call(['notepad.exe', 'Royalty Worksheet.txt'])
        subprocess.call(['notepad.exe', 'log.txt'])

        
    def xtest_runRoyaltiesAndWorksheet(self):
        pr = ProcessRoyalties()
        pr.process('database.xlsx')
        print('os name is:',os.name)
        if os.name != "posix":
            subprocess.call(['notepad.exe', 'Royalty Worksheet.txt'])
            subprocess.call(['notepad.exe', 'log.txt'])

        
    def test_whatever2(self):
        print ('in test_whatever2')

        
    def test_whatever3(self):
        print ('in test_whatever3')
        
def suite(): # Need to play with this more.
    suite = unittest.TestSuite()
    suite.addTest (DataBaseTest('test_whatever2'))
    return suite
if __name__ == '__main__':
    print('batch - running from main')
    runner = unittest.TextTestRunner()
    test_suite = suite()
    runner.run (test_suite)
"""
    
