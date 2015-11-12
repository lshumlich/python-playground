#!/bin/env python3

import unittest
from datetime import date
from datetime import datetime
from apperror import AppError


from TestHelper import TestHelper
from CalcRoyalties import ProcessRoyalties
#from DataBase import DataBase,AppError,DataStructure,TestDataBase

class TestSaskRoyaltyCalc(unittest.TestCase):

    def test_determineRoyaltyPrice (self):
        
        pr = ProcessRoyalties()
        monthly = TestHelper.getMonthlyDataClone()
        monthly.WellHeadPrice = 10
        monthly.TransRate = 3
        monthly.ProcessingRate = 1
        self.assertEqual(pr.determineRoyaltyprice(None,monthly), monthly.WellHeadPrice)
        self.assertEqual(pr.determineRoyaltyprice('asdf',monthly), monthly.WellHeadPrice)
        self.assertEqual(pr.determineRoyaltyprice('ActSales',monthly), 14)

        return
    
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
    