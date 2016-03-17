import unittest
from datetime import date
from datetime import datetime
from database.database import AppError, DataStructure
from database.data_structure import DataStructure


from database.testhelper import TestHelper
from database.Adrienne import calc_royalties
def test_calcSaskOilProvCrownRoyaltyRate(self):
    econStringData = \
"""
CharMonth,ProdMonth,HOP,SOP,NOP,H4T_C,H4T_D,H4T_K,H4T_X,H3T_K,H3T_X,HNEW_K,HNEW_X,SW4T_C,SW4T_D,SW4T_K,SW4T_X,SW3T_K,SW3T_X,SWNEW_K,SWNEW_X,O4T_C,O4T_D,O4T_K,O4T_X,O3T_K,O3T_X,ONEW_K,ONEW_X,OOLD_K,OOLD_X
Sept.,201509,162,210,276,0.0841,2.1,20.81,1561,20.46,472,26.48,611,0.1045,2.61,25.85,1939,31.57,729,38.54,890,0.1209,3.02,29.91,2243,36.08,833,40.79,941,52.61,1214
"""
        # All this work so we don't need to read from the database. It's a way better test.
    econOilData = DataStructure()
    th = TestHelper()
    royaltyCalc = DataStructure()

    th.load_object_csv_style(econOilData, econStringData)

    cr = calc_royalties()

    self.assertEqual(cr.calcSaskOilProvCrownRoyaltyRate(royaltyCalc,econOilData,'Fourth Tier Oil', 'Heavy', 24, 0), 0)
    self.assertEqual(cr.calcSaskOilProvCrownRoyaltyRate(royaltyCalc,econOilData,'Fourth Tier Oil', 'Heavy', 100, 0), 6.31)
    self.assertEqual(cr.calcSaskOilProvCrownRoyaltyRate(royaltyCalc,econOilData,'Fourth Tier Oil', 'Southwest', 100, 0), 7.84)
    self.assertEqual(cr.calcSaskOilProvCrownRoyaltyRate(royaltyCalc,econOilData,'Fourth Tier Oil', 'Other', 130, 0), 12.697)
    self.assertEqual(cr.calcSaskOilProvCrownRoyaltyRate(royaltyCalc,econOilData,'Fourth Tier Oil', 'Heavy', 140, 0), 9.66)
    self.assertEqual(cr.calcSaskOilProvCrownRoyaltyRate(royaltyCalc,econOilData,'Fourth Tier Oil', 'Southwest', 136.3, 0), 11.624028)
    self.assertEqual(cr.calcSaskOilProvCrownRoyaltyRate(royaltyCalc,econOilData,'Fourth Tier Oil', 'Other', 150, 0), 14.956667)
    self.assertEqual(cr.calcSaskOilProvCrownRoyaltyRate(royaltyCalc,econOilData,'Fourth Tier Oil', 'Other', 0, 0), 0)
    self.assertRaises(AppError, cr.calcSaskOilProvCrownRoyaltyRate, royaltyCalc, econOilData, 'Fourth Tier Oil', 'BadString', 120, 0)
    self.assertRaises(AppError, cr.calcSaskOilProvCrownRoyaltyRate, royaltyCalc, econOilData, 'Fourth Tier Oil', 'BadString', 140, 0)
    self.assertRaises(AppError, cr.calcSaskOilProvCrownRoyaltyRate, royaltyCalc, econOilData, 'Bad String', 'Heavy', 120, 0)
    self.assertRaises(AppError, cr.calcSaskOilProvCrownRoyaltyRate, royaltyCalc, econOilData, 'Bad String', 'Southwest', 120, 0)
    self.assertRaises(AppError, cr.calcSaskOilProvCrownRoyaltyRate, royaltyCalc, econOilData, 'Bad String', 'Other', 120, 0)

    self.assertEqual(cr.calcSaskOilProvCrownRoyaltyRate(royaltyCalc,econOilData,'Third Tier Oil', 'Heavy', 100, 0.75), 14.99)
    self.assertAlmostEqual(cr.calcSaskOilProvCrownRoyaltyRate(royaltyCalc,econOilData,'New Oil', 'Heavy', 100, 0.75), 19.620000)
    self.assertEqual(cr.calcSaskOilProvCrownRoyaltyRate(royaltyCalc,econOilData,'New Oil', 'Heavy', 0, 0), 0)
    self.assertRaises(AppError, cr.calcSaskOilProvCrownRoyaltyRate, royaltyCalc, econOilData, 'Third Tier Oil', 'Bad String', 120, 0)

    self.assertEqual(cr.calcSaskOilProvCrownRoyaltyRate(royaltyCalc,econOilData,'Third Tier Oil', 'Southwest', 120, 0), 25.495000)
    self.assertEqual(cr.calcSaskOilProvCrownRoyaltyRate(royaltyCalc,econOilData,'New Oil', 'Southwest', 130, 0.75), 30.943846)
    self.assertEqual(cr.calcSaskOilProvCrownRoyaltyRate(royaltyCalc,econOilData,'New Oil', 'Southwest', 0, 0), 0)
    self.assertRaises(AppError, cr.calcSaskOilProvCrownRoyaltyRate, royaltyCalc, econOilData, 'New Oil', 'Bad String', 120, 0)

    self.assertEqual(cr.calcSaskOilProvCrownRoyaltyRate(royaltyCalc,econOilData,'Third Tier Oil', 'Other', 120, 2.25), 26.888333)
    self.assertEqual(cr.calcSaskOilProvCrownRoyaltyRate(royaltyCalc,econOilData,'New Oil', 'Other', 110, 0), 32.235455)
    self.assertEqual(cr.calcSaskOilProvCrownRoyaltyRate(royaltyCalc,econOilData,'Old Oil', 'Other', 100, 0.75), 39.720000)
    self.assertEqual(cr.calcSaskOilProvCrownRoyaltyRate(royaltyCalc,econOilData,'Old Oil', 'Other', 0, 0), 0)
    self.assertRaises(AppError, cr.calcSaskOilProvCrownRoyaltyRate, royaltyCalc, econOilData, 'Old Oil', 'Bad String', 120, 0)

    self.assertRaises(AppError, cr.calcSaskOilProvCrownRoyaltyRate, royaltyCalc, econOilData, 'Old Oil', 'Heavy', 120, 0)
    self.assertRaises(AppError, cr.calcSaskOilProvCrownRoyaltyRate, royaltyCalc, econOilData, 'Old Oil', 'Southwest', 120, 0)

    return
