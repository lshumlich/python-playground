
import unittest
import subprocess

from database.apperror import AppError
from database.database import DataBase
from database.royaltyworksheet import RoyaltyWorksheet

class DataBaseTest(unittest.TestCase):
#    Major Hack must be fixed.    
    def test_getMonthlyDataByWellProdMonthProduct(self):
        rw = RoyaltyWorksheet()
        rw.printWithWellProdDate(6,201501,'Oil')
        subprocess.call(['notepad.exe', 'Royalty Worksheet.txt'])
        subprocess.call(['notepad.exe', 'log.txt'])

        
    def xtest_whatever1(self):
        print ('in test_whatever1')

        
    def xtest_whatever2(self):
        print ('in test_whatever2')

        
    def xtest_whatever3(self):
        print ('in test_whatever3')
