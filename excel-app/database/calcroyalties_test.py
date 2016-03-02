#!/bin/env python3

import unittest
from datetime import date
from datetime import datetime
from database.database import AppError, DataStructure
from database.data_structure import DataStructure


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
        self.assertEqual(pr.calcSaskOilProvCrownRoyaltyRate(royaltyCalc,econOilData,'Fourth Tier Oil', 'Heavy', 140, 0), 9.66)
        self.assertEqual(pr.calcSaskOilProvCrownRoyaltyRate(royaltyCalc,econOilData,'Fourth Tier Oil', 'Southwest', 136.3, 0), 11.624028)
        self.assertEqual(pr.calcSaskOilProvCrownRoyaltyRate(royaltyCalc,econOilData,'Fourth Tier Oil', 'Other', 150, 0), 14.956667)
        self.assertEqual(pr.calcSaskOilProvCrownRoyaltyRate(royaltyCalc,econOilData,'Fourth Tier Oil', 'Other', 0, 0), 0)
        self.assertRaises(AppError, pr.calcSaskOilProvCrownRoyaltyRate, royaltyCalc, econOilData, 'Fourth Tier Oil', 'BadString', 120, 0)
        self.assertRaises(AppError, pr.calcSaskOilProvCrownRoyaltyRate, royaltyCalc, econOilData, 'Fourth Tier Oil', 'BadString', 140, 0)
        self.assertRaises(AppError, pr.calcSaskOilProvCrownRoyaltyRate, royaltyCalc, econOilData, 'Bad String', 'Heavy', 120, 0)
        self.assertRaises(AppError, pr.calcSaskOilProvCrownRoyaltyRate, royaltyCalc, econOilData, 'Bad String', 'Southwest', 120, 0)
        self.assertRaises(AppError, pr.calcSaskOilProvCrownRoyaltyRate, royaltyCalc, econOilData, 'Bad String', 'Other', 120, 0)

        self.assertEqual(pr.calcSaskOilProvCrownRoyaltyRate(royaltyCalc,econOilData,'Third Tier Oil', 'Heavy', 100, 0.75), 14.99)
        self.assertAlmostEqual(pr.calcSaskOilProvCrownRoyaltyRate(royaltyCalc,econOilData,'New Oil', 'Heavy', 100, 0.75), 19.620000)
        self.assertEqual(pr.calcSaskOilProvCrownRoyaltyRate(royaltyCalc,econOilData,'New Oil', 'Heavy', 0, 0), 0)
        self.assertRaises(AppError, pr.calcSaskOilProvCrownRoyaltyRate, royaltyCalc, econOilData, 'Third Tier Oil', 'Bad String', 120, 0)

        self.assertEqual(pr.calcSaskOilProvCrownRoyaltyRate(royaltyCalc,econOilData,'Third Tier Oil', 'Southwest', 120, 0), 25.495000)
        self.assertEqual(pr.calcSaskOilProvCrownRoyaltyRate(royaltyCalc,econOilData,'New Oil', 'Southwest', 130, 0.75), 30.943846)
        self.assertEqual(pr.calcSaskOilProvCrownRoyaltyRate(royaltyCalc,econOilData,'New Oil', 'Southwest', 0, 0), 0)
        self.assertRaises(AppError, pr.calcSaskOilProvCrownRoyaltyRate, royaltyCalc, econOilData, 'New Oil', 'Bad String', 120, 0)

        self.assertEqual(pr.calcSaskOilProvCrownRoyaltyRate(royaltyCalc,econOilData,'Third Tier Oil', 'Other', 120, 2.25), 26.888333)
        self.assertEqual(pr.calcSaskOilProvCrownRoyaltyRate(royaltyCalc,econOilData,'New Oil', 'Other', 110, 0), 32.235455)
        self.assertEqual(pr.calcSaskOilProvCrownRoyaltyRate(royaltyCalc,econOilData,'Old Oil', 'Other', 100, 0.75), 39.720000)
        self.assertEqual(pr.calcSaskOilProvCrownRoyaltyRate(royaltyCalc,econOilData,'Old Oil', 'Other', 0, 0), 0)
        self.assertRaises(AppError, pr.calcSaskOilProvCrownRoyaltyRate, royaltyCalc, econOilData, 'Old Oil', 'Bad String', 120, 0)

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
"""

    def test_calcSaskOilProvCrownRoyaltyVolumeValue(self):
        pr = ProcessRoyalties()
        self.assertEqual(pr.calcSaskOilProvCrownRoyaltyVolumeValue(2, 100, 1, 20, 1,100), (20.0, 2000.0))
        self.assertEqual(pr.calcSaskOilProvCrownRoyaltyVolumeValue(-1, 100 ,1 ,20, 1, 100), (20.0, 2000.0))
        self.assertEqual(pr.calcSaskOilProvCrownRoyaltyVolumeValue(2, 100 ,1, 5, 1,100), (5, 500.0))
        self.assertEqual(pr.calcSaskOilProvCrownRoyaltyVolumeValue(2, 100 ,1, None, 1,100), (2.0, 200.0))
        self.assertEqual(pr.calcSaskOilProvCrownRoyaltyVolumeValue(10, 120 ,1, 2, 1,120), (12, 1440.0))

        return



    def test_calcSaskOilIOGR1995(self):
        m = DataStructure()
        m.WellHeadPrice = 221.123456
        m.TransRate = 2.123455
        m.ProcessingRate = 0.123455
        m.ProdVol = 70
        m.ProdMonth = 201501

        calc = DataStructure()

        pr = ProcessRoyalties()
        #all tests for SaskWellHead
        pr.calcSaskOilIOGR1995(datetime(2015,1,1), "SaskWellHead", 1.2, 0.25, m, calc)
        self.assertEqual(calc.IOGR1995RoyaltyValue,464.36)
        self.assertEqual(calc.CommencementPeriod,0)
        self.assertEqual(calc.IOGR1995RoyaltyVolume,7)
        self.assertEqual(calc.RoyaltyPrice,221.123456)

        m.ProdVol = 100
        pr.calcSaskOilIOGR1995(datetime(2015,4,2), "SaskWellHead", 0.25, 3, m, calc)
        self.assertEqual(calc.IOGR1995RoyaltyValue,1990.11)
        m.ProdVol = 170
        pr.calcSaskOilIOGR1995(datetime(2015,5,1), "SaskWellHead", 1, 1, m,calc)
        self.assertEqual(calc.IOGR1995RoyaltyValue, 5881.88)
        m.ProdVol = 79.9
        pr.calcSaskOilIOGR1995(datetime(2010,1,1), "SaskWellHead", 3, 2, m, calc)
        self.assertEqual(calc.IOGR1995RoyaltyValue,10600.66)
        m.ProdVol = 150
        pr.calcSaskOilIOGR1995(datetime(2009,7,3), "SaskWellHead", 2, 4, m, calc)
        self.assertEqual(calc.IOGR1995RoyaltyValue, 38917.73)
        m.ProdVol = 500
        pr.calcSaskOilIOGR1995(datetime(2007,8,2), "SaskWellHead", 1, 5, m, calc)
        self.assertEqual(calc.IOGR1995RoyaltyValue, 124271.38)
        m.ProdVol = 800
        pr.calcSaskOilIOGR1995(datetime(2008,9,9), "SaskWellHead", 5, 0.1, m, calc)

        self.assertEqual(calc.IOGR1995RoyaltyValue, 21117.29)

    def test_determineCommencementPeriod(self):
        pr = ProcessRoyalties()
        self.assertEqual(pr.determineCommencementPeriod(201501, datetime(2015,1,1)), 0)
        self.assertEqual(pr.determineCommencementPeriod(201501, datetime(2014,12,1)), 0.08)
        self.assertEqual(pr.determineCommencementPeriod(201501, datetime(2014,11,15)), 0.13)
        self.assertEqual(pr.determineCommencementPeriod(201501, datetime(2014,1,1)), 1)
        self.assertEqual(pr.determineCommencementPeriod(201501, datetime(2014,1,1)), 1)
        self.assertEqual(pr.determineCommencementPeriod(201501, datetime(2010,1,1)), 5)
        self.assertEqual(pr.determineCommencementPeriod(201501, datetime(2009,12,1)), 5.09)
        self.assertRaises(AppError,pr.determineCommencementPeriod, 201501, None)
        #write tests for ActSales



    def test_calcSaskOilRegulationSubsection2(self):
        pr = ProcessRoyalties()
        self.assertEqual(pr.calcSaskOilRegulationSubsection2(70), 7)
        self.assertEqual(pr.calcSaskOilRegulationSubsection2(100), 12)
        self.assertEqual(pr.calcSaskOilRegulationSubsection2(170), 26.6)



    def test_calcSaskOilRegulationSubsection3(self):
        pr = ProcessRoyalties()
        self.assertAlmostEqual(pr.calcSaskOilRegulationSubsection3(79.9), 7.99)
        self.assertEqual(pr.calcSaskOilRegulationSubsection3(150), 22)
        self.assertEqual(pr.calcSaskOilRegulationSubsection3(500), 112.4)
        self.assertEqual(pr.calcSaskOilRegulationSubsection3(800), 191)

    def test_determineRoyaltyPrice(self):
        m = DataStructure()
        m.WellHeadPrice = 221.123456
        m.TransRate = 2.123455
        m.ProcessingRate = 0.123455

        pr = ProcessRoyalties()
        self.assertAlmostEqual(pr.determineRoyaltyPrice('ActSales', m),223.370366)

        m.WellHeadPrice = 225
        m.TransRate = 3
        m.ProcessingRate = 1

        self.assertAlmostEqual(pr.determineRoyaltyPrice('ActSales', m),229)


    def test_calcGorrPercent(self):
        pr = ProcessRoyalties()

        gorr = "bad string,0,2"
        self.assertRaises(AppError, pr.calcGorrPercent, 400, 10, gorr)
        self.assertRaises(AppError, pr.calcGorrPercent, None, 10, gorr)

        gorr = None,"0,2"
        self.assertRaises(AttributeError, pr.calcGorrPercent, 400, 10, gorr)

        gorr = "dprod,250,2,300,3,400,4,500,5,0,6"
        self.assertEqual(pr.calcGorrPercent(600, 10, gorr), (2.0, 'dprod = 60.000000 = 600 / 10 is greater than 0.0 and less than or equal to 250.0 for an RR of 2.0%'))
        self.assertEqual(pr.calcGorrPercent(1008, 4, gorr), (3.0, 'dprod = 252.000000 = 1008 / 4 is greater than 250.0 and less than or equal to 300.0 for an RR of 3.0%'))
        self.assertEqual(pr.calcGorrPercent(400, 1, gorr), (4.0, 'dprod = 400.000000 = 400 / 1 is greater than 300.0 and less than or equal to 400.0 for an RR of 4.0%'))
        self.assertEqual(pr.calcGorrPercent(990, 2, gorr), (5.0, 'dprod = 495.000000 = 990 / 2 is greater than 400.0 and less than or equal to 500.0 for an RR of 5.0%'))
        self.assertEqual(pr.calcGorrPercent(10000, 17, gorr), (6.0,'dprod = 588.235294 = 10000 / 17 is greater than 500.0 for an RR of 6.0%'))

        self.assertRaises(TypeError, pr.calcGorrPercent, None, 10, gorr)

        gorr = "mprod,250,2,300,3,400,4,500,5,0,6"
        self.assertEqual(pr.calcGorrPercent(200, 10, gorr), (2.0, 'mprod = 200 is greater than 0.0 and less than or equal to 250.0 for an RR of 2.0%'))
        self.assertEqual(pr.calcGorrPercent(300, 4, gorr), (3.0, 'mprod = 300 is greater than 250.0 and less than or equal to 300.0 for an RR of 3.0%'))
        self.assertEqual(pr.calcGorrPercent(350.6, 1, gorr), (4.0, 'mprod = 350.6 is greater than 300.0 and less than or equal to 400.0 for an RR of 4.0%'))
        self.assertEqual(pr.calcGorrPercent(410, 2, gorr), (5.0, 'mprod = 410 is greater than 400.0 and less than or equal to 500.0 for an RR of 5.0%'))
        self.assertEqual(pr.calcGorrPercent(10000, 17, gorr), (6.0,'mprod = 10000 is greater than 500.0 for an RR of 6.0%'))

        gorr = "fixed,0,2"
        self.assertEqual(pr.calcGorrPercent(200, 10, gorr), (2.0, 'fixed for an RR of 2.0%'))
        self.assertEqual(pr.calcGorrPercent(10000, 4, gorr), (2.0, 'fixed for an RR of 2.0%'))
        #In future make this raise an error:
        self.assertEqual(pr.calcGorrPercent(None, 10, gorr), (2.0, 'fixed for an RR of 2.0%'))

    def test_calcSupplementaryRoyaltiesIOGR1995(self):
        reference_price = {'Pigeon Lake Indian': 24.04, 'Reserve no.138A': 25.37, 'Sawridge Indian': 25.13, 'Stony Plain Indian': 24.64}
        pr = ProcessRoyalties()
        self.assertEqual(pr.calcSupplementaryRoyaltiesIOGR1995(3.5, 228, 80, 60, reference_price['Pigeon Lake Indian']),2039.6)
        self.assertEqual(pr.calcSupplementaryRoyaltiesIOGR1995(5, 200, 90, 40, reference_price['Reserve no.138A']),4365.75)
        self.assertEqual(pr.calcSupplementaryRoyaltiesIOGR1995(4, 221.123456, 100, 50, reference_price['Sawridge Indian']),4899.84)
        self.assertEqual(pr.calcSupplementaryRoyaltiesIOGR1995(.2, 180, 80, 35, reference_price['Stony Plain Indian']),3495.6)

        self.assertEqual(pr.calcSupplementaryRoyaltiesIOGR1995(6, 228, 80, 60, reference_price['Pigeon Lake Indian']),2996.5)
        self.assertEqual(pr.calcSupplementaryRoyaltiesIOGR1995(5.5, 200, 90, 40, reference_price['Reserve no.138A']),6391.38)
        self.assertEqual(pr.calcSupplementaryRoyaltiesIOGR1995(8, 221.123456, 100, 50, reference_price['Sawridge Indian']),7192.5)
        self.assertEqual(pr.calcSupplementaryRoyaltiesIOGR1995(15, 180, 80, 35, reference_price['Stony Plain Indian']),5101.88)


if __name__ == '__main__':
    unittest.main()
