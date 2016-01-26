
import unittest
import subprocess
import os

from database.apperror import AppError
from database.database import DataBase
from database.royaltyworksheet import RoyaltyWorksheet
from database.calcroyalties import ProcessRoyalties

class DataBaseTest(unittest.TestCase):
#     Major Hack must be fixed.    
    def xtest_getMonthlyDataByWellProdMonthProduct(self):
        rw = RoyaltyWorksheet()
        rw.printWithWellProdDate(6,201501,'Oil')
        subprocess.call(['notepad.exe', 'Royalty Worksheet.txt'])
        subprocess.call(['notepad.exe', 'log.txt'])

        
    def test_runRoyaltiesAndWorksheet(self):
        pr = ProcessRoyalties()
        pr.process('database.xlsx')
        print('os name is:',os.name)
        if os.name != "posix":
            subprocess.call(['notepad.exe', 'Royalty Worksheet.txt'])
            subprocess.call(['notepad.exe', 'log.txt'])

        
    def xtest_whatever2(self):
        print ('in test_whatever2')

        
    def xtest_whatever3(self):
        print ('in test_whatever3')

