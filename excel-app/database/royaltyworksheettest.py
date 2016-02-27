
import unittest

from database.royaltyworksheet import RoyaltyWorksheet

class RoyaltyWorksheetTest(unittest.TestCase):
    
    def test_PrintWithWellProdDate(self):
        ws = RoyaltyWorksheet()
        ws.printWithWellProdDate(6,201501,'Oil')

    