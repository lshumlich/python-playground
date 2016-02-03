#!/bin/env python3

import unittest
from datetime import date
from datetime import datetime
from database.database import AppError, DataStructure


from database.testhelper import TestHelper
from database.calcroyalties import ProcessRoyalties
#from DataBase import DataBase,AppError,DataStructure,TestDataBase

class DataObj(object):
    None

class TestSaskRoyaltyCalc(unittest.TestCase):

#     def xtest_determineRoyaltyPrice (self):
#         
#         pr = ProcessRoyalties()
#         monthly = TestHelper.getMonthlyDataClone()
#         monthly.WellHeadPrice = 10
#         monthly.TransRate = 3
#         monthly.ProcessingRate = 1
#         self.assertEqual(pr.determineRoyaltyprice(None,monthly), monthly.WellHeadPrice)
#         self.assertEqual(pr.determineRoyaltyprice('asdf',monthly), monthly.WellHeadPrice)
#         self.assertEqual(pr.determineRoyaltyprice('ActSales',monthly), 14)
# 
#         return

    def test_calcSaskOilRegulationSubsection2(self):
        """ subsection (2) """
        pr = ProcessRoyalties()
        self.assertEqual(pr.calcSaskOilRegulationSubsection2(70),7)
        self.assertEqual(pr.calcSaskOilRegulationSubsection2(90),10)
        self.assertEqual(pr.calcSaskOilRegulationSubsection2(200),(24+.26*(200-160)))
        self.assertEqual(pr.calcSaskOilRegulationSubsection2(2000),(24+.26*(2000-160)))
        return
    
    def test_calcSaskOilRegulationSubsection3(self):
        """ subsection (3) """
        pr = ProcessRoyalties()
        self.assertEqual(pr.calcSaskOilRegulationSubsection3(70),7)
        self.assertEqual(pr.calcSaskOilRegulationSubsection3(90),10)
        self.assertEqual(pr.calcSaskOilRegulationSubsection3(200),(24+.26*(200-160)))
        self.assertEqual(pr.calcSaskOilRegulationSubsection3(2000),(189+.4*(2000-795)))
        return
    
    
    def test_determineCommencementPeriod(self):
        pr = ProcessRoyalties()
        self.assertEqual(pr.determineCommencementPeriod(201501, date(2014,12,1)),.08)
        self.assertEqual(pr.determineCommencementPeriod(201501, date(2014,12,31)),0)
        self.assertEqual(pr.determineCommencementPeriod(201501, date(2014,1,1)),1)
        self.assertEqual(pr.determineCommencementPeriod(201501, date(2010,11,30)),4.09)
        self.assertEqual(pr.determineCommencementPeriod(201501, date(2010,1,1)),5)
        self.assertEqual(pr.determineCommencementPeriod(201501, date(2010,1,31)),4.92)
        self.assertEqual(pr.determineCommencementPeriod(201501, date(2010,1,1)),5.0)
        self.assertRaises(AppError,pr.determineCommencementPeriod,None,None)
        self.assertEqual(pr.determineCommencementPeriod(201501, datetime(2003,1,1)),12.01)
        return
    

#    
    # Adrienne - write this tests
    # 110% if you can understand what all these lines of code are trying to do....
    
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

        th.loadObjectCSVStyle(econOilData, econStringData)
              
        pr = ProcessRoyalties()

        self.assertEqual(pr.calcSaskOilProvCrownRoyaltyRate(royaltyCalc,econOilData,'Fourth Tier Oil', 'Heavy', 24, 0), 0)
        self.assertEqual(pr.calcSaskOilProvCrownRoyaltyRate(royaltyCalc,econOilData,'Fourth Tier Oil', 'Heavy', 100, 0), 6.31)
        self.assertEqual(pr.calcSaskOilProvCrownRoyaltyRate(royaltyCalc,econOilData,'Fourth Tier Oil', 'Southwest', 100, 0), 7.84)
        self.assertEqual(pr.calcSaskOilProvCrownRoyaltyRate(royaltyCalc,econOilData,'Fourth Tier Oil', 'Other', 130, 0), 12.697)
        self.assertEqual(pr.calcSaskOilProvCrownRoyaltyRate(royaltyCalc,econOilData,'Fourth Tier Oil', 'Other', 0, 0), 0)
        self.assertRaises(AppError, pr.calcSaskOilProvCrownRoyaltyRate, royaltyCalc, econOilData, 'Fourth Tier Oil', 'BadString', 120, 0)

        self.assertEqual(pr.calcSaskOilProvCrownRoyaltyRate(royaltyCalc,econOilData,'Third Tier Oil', 'Heavy', 100, 0.75), 14.99)
        self.assertAlmostEqual(pr.calcSaskOilProvCrownRoyaltyRate(royaltyCalc,econOilData,'New Oil', 'Heavy', 100, 0.75), 19.620000)
        self.assertEqual(pr.calcSaskOilProvCrownRoyaltyRate(royaltyCalc,econOilData,'New Oil', 'Heavy', 0, 0), 0)
        self.assertRaises(AppError, pr.calcSaskOilProvCrownRoyaltyRate, royaltyCalc, econOilData, 'Bad String', 'Heavy', 120, 0)

        self.assertEqual(pr.calcSaskOilProvCrownRoyaltyRate(royaltyCalc,econOilData,'Third Tier Oil', 'Southwest', 120, 0), 25.495000)
        self.assertEqual(pr.calcSaskOilProvCrownRoyaltyRate(royaltyCalc,econOilData,'New Oil', 'Southwest', 130, 0.75), 30.943846)
        self.assertEqual(pr.calcSaskOilProvCrownRoyaltyRate(royaltyCalc,econOilData,'New Oil', 'Southwest', 0, 0), 0)
        self.assertRaises(AppError, pr.calcSaskOilProvCrownRoyaltyRate, royaltyCalc, econOilData, 'Bad String', 'Southwest', 120, 0)

        self.assertEqual(pr.calcSaskOilProvCrownRoyaltyRate(royaltyCalc,econOilData,'Third Tier Oil', 'Other', 120, 2.25), 26.888333)
        self.assertEqual(pr.calcSaskOilProvCrownRoyaltyRate(royaltyCalc,econOilData,'New Oil', 'Other', 110, 0), 32.235455)
        self.assertEqual(pr.calcSaskOilProvCrownRoyaltyRate(royaltyCalc,econOilData,'Old Oil', 'Other', 100, 0.75), 39.720000)
        self.assertEqual(pr.calcSaskOilProvCrownRoyaltyRate(royaltyCalc,econOilData,'Old Oil', 'Other', 0, 0), 0)
        self.assertRaises(AppError, pr.calcSaskOilProvCrownRoyaltyRate, royaltyCalc, econOilData, 'Bad String', 'Other', 120, 0)

        self.assertRaises(AppError, pr.calcSaskOilProvCrownRoyaltyRate, royaltyCalc, econOilData, 'Old Oil', 'Heavy', 120, 0)
        self.assertRaises(AppError, pr.calcSaskOilProvCrownRoyaltyRate, royaltyCalc, econOilData, 'Old Oil', 'Southwest', 120, 0)

        return


    """
    def test_calcSaskOilProvCrownRoyaltyVolumeValue(self):
        royStringData = \

ProvCrownUsedRoyaltyRate, CrownMultiplier, IndianInterest, MinRoyalty, RoyaltyPrice
6.31, 1, 1, 3.21,

        royOilData = DataStructure()
        th = TestHelper()
        royaltyCalc = DataStructure()

        th.loadObjectCSVStyle(royOilData, royStringData)
        print('ProvCrownUsedRoyaltyRate:',royOilData.ProvCrownUsedRoyaltyRate)
        print('CrownMultiplier:',royOilData.CrownMultiplier)
        print(vars(royOilData))
        print(vars(royOilData).values())

        pr = ProcessRoyalties()


    def test_calcSaskOilProvCrownRoyaltyVolumeValue(self):
        self.assertEqual(calcSaskOilProvCrownRoyaltyVolumeValue(royaltyCalc,100,1,20, 1), 100)

        return
    """
if __name__ == '__main__':
    unittest.main()