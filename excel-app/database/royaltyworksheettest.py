
import unittest

from royaltyworksheet import RoyaltyWorksheet

class RoyaltyWorksheetTest(unittest.TestCase):
    
    def test_PrintWithWellProdDate(self):
        ws = RoyaltyWorksheet()
        md = ws.printWithWellProdDate(6,201501,'Oil')

    