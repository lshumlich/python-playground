
import unittest

"""
Testing

Well ---

clear table
load known record using insert
check rows are there
get by id and check
get by any selection like prov check that you got the records
do an update then a read and make sure it got updated
check that audit has been create
  add
  update
  delete

"""

from database.apperror import AppError
from database.database import DataBase
import config

class DataBaseTest(unittest.TestCase):
#    Major Hack must be fixed.    
    def test_getMonthlyDataByWellProdMonthProduct(self):
        db = DataBase(config.get_file_dir() + 'database new.xlsx')
        md = db.getMonthlyDataByWellProdMonthProduct(6,201501,'Oil')
        self.assertRaises(AppError,db.getMonthlyDataByWellProdMonthProduct,99999,201512,'Oil')
