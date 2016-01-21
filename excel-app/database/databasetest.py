
import unittest

from apperror import AppError
from database.database import DataBase

class DataBaseTest(unittest.TestCase):
#    Major Hack must be fixed.    
    def test_getMonthlyDataByWellProdMonthProduct(self):
        db = DataBase('database.xlsx')
        md = db.getMonthlyDataByWellProdMonthProduct(6,201501,'Oil')
        self.assertRaises(AppError,db.getMonthlyDataByWellProdMonthProduct,99999,201512,'Oil')
        print(md)
