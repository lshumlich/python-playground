#!/bin/env python3

import unittest
from datetime import date
from datetime import datetime

import config
from src.calc.calcroyalties import ProcessRoyalties
from src.database.data_structure import DataStructure
from src.util.apperror import AppError
from src.util.app_logger import AppLogger

from tests.database.testhelper import TestHelper
from tests.database.sqlite_utilities_test import DatabaseUtilities


# class DataObj(object):
#     None
#

class TestSaskRoyaltyCalc(unittest.TestCase):

    def setUp(self):
        # Destructive Tests must run in unittest environment
        self.assertEqual('unittest', config.get_environment())


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

    def test_determine_commencement_period(self):
        pr = ProcessRoyalties()
        self.assertEqual(pr.determine_commencement_period(201501, date(2014, 12, 1)), .08)
        self.assertEqual(pr.determine_commencement_period(201501, date(2014, 12, 31)), 0)
        self.assertEqual(pr.determine_commencement_period(201501, date(2014, 1, 1)), 1)
        self.assertEqual(pr.determine_commencement_period(201501, date(2010, 11, 30)), 4.09)
        self.assertEqual(pr.determine_commencement_period(201501, date(2010, 1, 1)), 5)
        self.assertEqual(pr.determine_commencement_period(201501, date(2010, 1, 31)), 4.92)
        self.assertEqual(pr.determine_commencement_period(201501, date(2010, 1, 1)), 5.0)
        self.assertEqual(pr.determine_commencement_period(None, None), 5)
        self.assertEqual(pr.determine_commencement_period(201501, datetime(2003, 1, 1)), 12.01)
        return
    
    def test_calcSaskGasBaseRoyaltyCalcRate(self):
        econ_string_data =  \
            """
CharMonth,ProdMonth,G4T_C,G4T_D,G4T_K,G4T_X,G3T_C,G3T_K,G3T_X,GNEW_C,GNEW_K,GNEW_X,GOLD_C,GOLD_K,GOLD_X
Sept.,201509,0.1185,2.96,24.39,1578,0.1434,33.10,1910,0.1593,36.77,2121,0.2062,47.59,2745
"""
        th = TestHelper()
        econ_gas_data = DataStructure()
        th.load_object_csv_style(econ_gas_data, econ_string_data)
        pr = ProcessRoyalties()
        royalty_calc = DataStructure()

        self.assertEqual(pr.calc_sask_gas_prov_crown_royalty_rate(royalty_calc, econ_gas_data,
                                                                  'Fourth Tier', 0, 0, 'Gas'), 0)
        self.assertEqual(pr.calc_sask_gas_prov_crown_royalty_rate(royalty_calc, econ_gas_data,
                                                                  'Fourth Tier', 30, 0, 'Gas'), 0.00595)
        self.assertEqual(pr.calc_sask_gas_prov_crown_royalty_rate(royalty_calc, econ_gas_data,
                                                                  'Fourth Tier', 200, 0, 'Gas'), 0.165)

        self.assertEqual(pr.calc_sask_gas_prov_crown_royalty_rate(royalty_calc, econ_gas_data,
                                                                  'Fourth Tier', 0, 0, 'Oil'), 0)
        self.assertEqual(pr.calc_sask_gas_prov_crown_royalty_rate(royalty_calc, econ_gas_data,
                                                                  'Fourth Tier', 220, 0, 'Oil'), 0.172173)

        self.assertEqual(pr.calc_sask_gas_prov_crown_royalty_rate(royalty_calc, econ_gas_data,
                                                                  'Third Tier', 100, 0.75, None), 0.1359)
        self.assertEqual(pr.calc_sask_gas_prov_crown_royalty_rate(royalty_calc, econ_gas_data,
                                                                  'Third Tier', 200, 1, None), 0.2255)

        self.assertEqual(pr.calc_sask_gas_prov_crown_royalty_rate(royalty_calc, econ_gas_data,
                                                                  'New', 50, 2.25, None), 0.05715)
        self.assertEqual(pr.calc_sask_gas_prov_crown_royalty_rate(royalty_calc, econ_gas_data,
                                                                  'New', 130, 0.75, None), 0.197046)

        self.assertEqual(pr.calc_sask_gas_prov_crown_royalty_rate(royalty_calc, econ_gas_data,
                                                                  'Old', 20, 1, None), 0.03124)
        self.assertEqual(pr.calc_sask_gas_prov_crown_royalty_rate(royalty_calc, econ_gas_data,
                                                                  'Old', 150, 0.5, None), 0.2879)

        self.assertRaises(AppError, pr.calc_sask_gas_prov_crown_royalty_rate, royalty_calc,
                          econ_gas_data, 'Fourth Tier', 20, 1, 'Bad String')
        self.assertRaises(AppError, pr.calc_sask_gas_prov_crown_royalty_rate, royalty_calc,
                          econ_gas_data, 'Bad String', 20, 1, 'Gas')

    def test_calc_sask_gas_prov_crown_royalty_volume_value(self):
        pr = ProcessRoyalties()
        m = DataStructure()
        # m.ProdVol = 100

        lease_rm = DataStructure()
        lease_rm.MinRoyaltyRate = 0.0
        lease_rm.MinRoyaltyDollar = 0.0
        lease_rm.CrownMultiplier = 1
        lease_rm.ValuationMethod = 'ActSales'
        lease_rm.CrownModifier = None

        calc = DataStructure()
        calc.BaseRoyaltyRate = .25
        calc.BaseRoyaltyCalcRate = .25
        calc.RoyaltyPrice = 223.370366
        calc.BaseRoyaltyVolume = 0.0
        calc.BaseRoyaltyValue = 0.0
        m.TransRate = 2.123455
        m.ProcessingRate = 0.123455

        calc.RoyaltyBasedOnVol = 100
        calc.PEFNInterest = 1.0
        calc.RTPInterest = 1.0
        pr.calc_sask_gas_prov_crown_royalty_volume_value(m, lease_rm, calc)
        self.assertEqual(calc.BaseRoyaltyVolume, 0.0)
        self.assertEqual(calc.BaseRoyaltyValue, 5584.26)

        calc.BaseRoyaltyCalcRate = -.01
        calc.BaseRoyaltyRate = -.01
        lease_rm.MinRoyaltyRate = None
        pr.calc_sask_gas_prov_crown_royalty_volume_value(m, lease_rm, calc)
        self.assertEqual(calc.BaseRoyaltyRate, 0)

        calc.BaseRoyaltyCalcRate = -.01
        calc.BaseRoyaltyRate = -.01
        lease_rm.MinRoyaltyRate = .02
        pr.calc_sask_gas_prov_crown_royalty_volume_value(m, lease_rm, calc)
        self.assertEqual(calc.BaseRoyaltyRate, .02)
        self.assertEqual(calc.BaseRoyaltyValue, 446.74)

        lease_rm.MinRoyaltyDollar = 500.0
        pr.calc_sask_gas_prov_crown_royalty_volume_value(m, lease_rm, calc)
        self.assertEqual(calc.BaseRoyaltyValue, 500.0)

        lease_rm.MinRoyaltyDollar = None
        lease_rm.MinRoyaltyRate = None
        calc.BaseRoyaltyCalcRate = .35
        lease_rm.CrownModifier = .02
        calc.BaseRoyaltyRate = None
        pr.calc_sask_gas_prov_crown_royalty_volume_value(m, lease_rm, calc)
        self.assertEqual(calc.BaseRoyaltyRate, .37)

        # Reset to normal again
        lease_rm.CrownModifier = .0
        calc.BaseRoyaltyCalcRate = .25
        calc.RoyaltyPrice = 223.370366
        calc.BaseRoyaltyVolume = 0.0
        calc.BaseRoyaltyValue = 0.0
        pr.calc_sask_gas_prov_crown_royalty_volume_value(m, lease_rm, calc)
        self.assertEqual(calc.BaseRoyaltyVolume, 0.0)
        self.assertEqual(calc.BaseRoyaltyValue, 5584.26)

        # m.ProdVol = 100
        calc.RoyaltyBasedOnVol = 100
        calc.RTPInterest = .50
        pr.calc_sask_gas_prov_crown_royalty_volume_value(m, lease_rm, calc)
        self.assertEqual(calc.BaseRoyaltyVolume, 0.0)
        self.assertEqual(calc.BaseRoyaltyValue, 2792.13)

        # m.ProdVol = 100
        calc.RoyaltyBasedOnVol = 100
        calc.PEFNInterest =.5
        calc.RTPInterest = .5
        pr.calc_sask_gas_prov_crown_royalty_volume_value(m, lease_rm, calc)
        self.assertEqual(calc.BaseRoyaltyVolume, 0.0)
        self.assertEqual(calc.BaseRoyaltyValue, 1396.06)

    def test_calcSaskOilBaseRoyaltyCalcRate(self):
        econ_string_data = \
            """
CharMonth,ProdMonth,HOP,SOP,NOP,H4T_C,H4T_D,H4T_K,H4T_X,H3T_K,H3T_X,HNEW_K,HNEW_X,SW4T_C,SW4T_D,SW4T_K,SW4T_X,SW3T_K,SW3T_X,SWNEW_K,SWNEW_X,O4T_C,O4T_D,O4T_K,O4T_X,O3T_K,O3T_X,ONEW_K,ONEW_X,OOLD_K,OOLD_X
Sept.,201509,162,210,276,0.0841,2.1,20.81,1561,20.46,472,26.48,611,0.1045,2.61,25.85,1939,31.57,729,38.54,890,0.1209,3.02,29.91,2243,36.08,833,40.79,941,52.61,1214
"""
        # All this work so we don't need to read from the database. It's a way better test.
        econ_oil_data = DataStructure()
        th = TestHelper()
        royalty_calc = DataStructure()

        th.load_object_csv_style(econ_oil_data, econ_string_data)
              
        pr = ProcessRoyalties()

        self.assertEqual(pr.calc_sask_oil_prov_crown_royalty_rate(royalty_calc, econ_oil_data,
                                                                  'Fourth Tier', 'Heavy', 24, 0), 0)
        self.assertEqual(pr.calc_sask_oil_prov_crown_royalty_rate(royalty_calc, econ_oil_data,
                                                                  'Fourth Tier', 'Heavy', 100, 0), .0631)
        self.assertEqual(pr.calc_sask_oil_prov_crown_royalty_rate(royalty_calc, econ_oil_data,
                                                                  'Fourth Tier', 'Southwest', 100, 0), .0784)
        self.assertEqual(pr.calc_sask_oil_prov_crown_royalty_rate(royalty_calc, econ_oil_data,
                                                                  'Fourth Tier', 'Other', 130, 0), .12697)
        self.assertEqual(pr.calc_sask_oil_prov_crown_royalty_rate(royalty_calc, econ_oil_data,
                                                                  'Fourth Tier', 'Heavy', 140, 0), .0966)
        self.assertEqual(pr.calc_sask_oil_prov_crown_royalty_rate(royalty_calc, econ_oil_data,
                                                                  'Fourth Tier', 'Southwest', 136.3, 0), .11624028)
        self.assertEqual(pr.calc_sask_oil_prov_crown_royalty_rate(royalty_calc, econ_oil_data,
                                                                  'Fourth Tier', 'Other', 150, 0), .14956667)
        self.assertEqual(pr.calc_sask_oil_prov_crown_royalty_rate(royalty_calc, econ_oil_data,
                                                                  'Fourth Tier', 'Other', 0, 0), 0)
        self.assertRaises(AppError, pr.calc_sask_oil_prov_crown_royalty_rate, royalty_calc, econ_oil_data,
                          'Fourth Tier', 'BadString', 120, 0)
        self.assertRaises(AppError, pr.calc_sask_oil_prov_crown_royalty_rate, royalty_calc, econ_oil_data,
                          'Fourth Tier', 'BadString', 140, 0)
        self.assertRaises(AppError, pr.calc_sask_oil_prov_crown_royalty_rate, royalty_calc, econ_oil_data,
                          'Bad String', 'Heavy', 120, 0)
        self.assertRaises(AppError, pr.calc_sask_oil_prov_crown_royalty_rate, royalty_calc, econ_oil_data,
                          'Bad String', 'Southwest', 120, 0)
        self.assertRaises(AppError, pr.calc_sask_oil_prov_crown_royalty_rate, royalty_calc, econ_oil_data,
                          'Bad String', 'Other', 120, 0)

        self.assertEqual(pr.calc_sask_oil_prov_crown_royalty_rate(royalty_calc, econ_oil_data,
                                                                  'Third Tier', 'Heavy', 100, 0.0075), .1499)
        self.assertAlmostEqual(pr.calc_sask_oil_prov_crown_royalty_rate(royalty_calc, econ_oil_data,
                                                                        'New', 'Heavy', 100, 0.0075), .19620000)
        self.assertEqual(pr.calc_sask_oil_prov_crown_royalty_rate(royalty_calc, econ_oil_data,
                                                                  'New', 'Heavy', 0, 0), 0)
        self.assertRaises(AppError, pr.calc_sask_oil_prov_crown_royalty_rate, royalty_calc, econ_oil_data,
                          'Third Tier', 'Bad String', 120, 0)

        self.assertEqual(pr.calc_sask_oil_prov_crown_royalty_rate(royalty_calc, econ_oil_data,
                                                                  'Third Tier', 'Southwest', 120, 0), .25495000)
        self.assertEqual(pr.calc_sask_oil_prov_crown_royalty_rate(royalty_calc, econ_oil_data,
                                                                  'New', 'Southwest', 130, 0.0075), .30943846)
        self.assertEqual(pr.calc_sask_oil_prov_crown_royalty_rate(royalty_calc, econ_oil_data,
                                                                  'New', 'Southwest', 0, 0), 0)
        self.assertRaises(AppError, pr.calc_sask_oil_prov_crown_royalty_rate, royalty_calc, econ_oil_data,
                          'New', 'Bad String', 120, 0)

        self.assertEqual(pr.calc_sask_oil_prov_crown_royalty_rate(royalty_calc, econ_oil_data,
                                                                  'Third Tier', 'Other', 120, .0225), .26888333)
        self.assertEqual(pr.calc_sask_oil_prov_crown_royalty_rate(royalty_calc, econ_oil_data,
                                                                  'New', 'Other', 110, 0), .32235455)
        self.assertEqual(pr.calc_sask_oil_prov_crown_royalty_rate(royalty_calc, econ_oil_data,
                                                                  'Old', 'Other', 100, 0.0075), .39720000)
        self.assertEqual(pr.calc_sask_oil_prov_crown_royalty_rate(royalty_calc, econ_oil_data,
                                                                  'Old', 'Other', 0, 0), 0)
        self.assertRaises(AppError, pr.calc_sask_oil_prov_crown_royalty_rate, royalty_calc, econ_oil_data,
                          'Old', 'Bad String', 120, 0)

        self.assertRaises(AppError, pr.calc_sask_oil_prov_crown_royalty_rate, royalty_calc, econ_oil_data,
                          'Old', 'Heavy', 120, 0)
        self.assertRaises(AppError, pr.calc_sask_oil_prov_crown_royalty_rate, royalty_calc, econ_oil_data,
                          'Old', 'Southwest', 120, 0)
        self.assertRaises(AppError, pr.calc_sask_oil_prov_crown_royalty_rate, royalty_calc, econ_oil_data,
                          None, None, 120, 0)

        return

    def test_calc_sask_oil_prov_crown_royalty_volume_value(self):
        pr = ProcessRoyalties()
        m = DataStructure()

        lease_rm = DataStructure()
        lease_rm.MinRoyaltyRate = 0.0
        lease_rm.MinRoyaltyDollar = 0.0
        lease_rm.CrownMultiplier = 1
        lease_rm.ValuationMethod = 'ActSales'
        lease_rm.CrownModifier = None

        calc = DataStructure()
        calc.BaseRoyaltyRate = .25
        calc.BaseRoyaltyCalcRate = .25
        calc.RoyaltyPrice = 223.370366
        calc.BaseRoyaltyVolume = 0.0
        calc.BaseRoyaltyValue = 0.0
        calc.RoyaltyBasedOnVol = 100
        m.TransRate = 2.123455
        m.ProcessingRate = 0.123455

        fn_interest = 1.0
        rp_interest = 100.0

        pr.calc_sask_oil_prov_crown_royalty_volume_value(m, fn_interest, rp_interest, lease_rm, calc)
        self.assertEqual(calc.BaseRoyaltyVolume, 0.0)
        self.assertEqual(calc.BaseRoyaltyValue, 5584.26)

        calc.BaseRoyaltyCalcRate = -.01
        calc.BaseRoyaltyRate = -.01
        lease_rm.MinRoyaltyRate = None
        pr.calc_sask_oil_prov_crown_royalty_volume_value(m, fn_interest, rp_interest, lease_rm, calc)
        self.assertEqual(calc.BaseRoyaltyRate, 0)

        calc.BaseRoyaltyCalcRate = -.01
        calc.BaseRoyaltyRate = -.01
        lease_rm.MinRoyaltyRate = .02
        pr.calc_sask_oil_prov_crown_royalty_volume_value(m, fn_interest, rp_interest, lease_rm, calc)
        self.assertEqual(calc.BaseRoyaltyRate, .02)
        self.assertEqual(calc.BaseRoyaltyValue, 446.74)

        lease_rm.MinRoyaltyDollar = 500.0
        pr.calc_sask_oil_prov_crown_royalty_volume_value(m, fn_interest, rp_interest, lease_rm, calc)
        self.assertEqual(calc.BaseRoyaltyValue, 500.0)

        lease_rm.MinRoyaltyDollar = None
        lease_rm.MinRoyaltyRate = None
        calc.BaseRoyaltyCalcRate = .35
        lease_rm.CrownModifier = .02
        calc.BaseRoyaltyRate = None
        pr.calc_sask_oil_prov_crown_royalty_volume_value(m, fn_interest, rp_interest, lease_rm, calc)
        self.assertEqual(calc.BaseRoyaltyRate, .37)

        # Reset to normal again
        lease_rm.CrownModifier = .0
        calc.BaseRoyaltyCalcRate = .25
        calc.RoyaltyPrice = 223.370366
        calc.BaseRoyaltyVolume = 0.0
        calc.BaseRoyaltyValue = 0.0
        pr.calc_sask_oil_prov_crown_royalty_volume_value(m, fn_interest, rp_interest, lease_rm, calc)
        self.assertEqual(calc.BaseRoyaltyVolume, 0.0)
        self.assertEqual(calc.BaseRoyaltyValue, 5584.26)

        # m.ProdVol = 100
        calc.RoyaltyBasedOnVol = 100
        rp_interest = 50.0
        pr.calc_sask_oil_prov_crown_royalty_volume_value(m, fn_interest, rp_interest, lease_rm, calc)
        self.assertEqual(calc.BaseRoyaltyVolume, 0.0)
        self.assertEqual(calc.BaseRoyaltyValue, 2792.13)

        # m.ProdVol = 100
        calc.RoyaltyBasedOnVol = 100
        rp_interest = 50.0
        fn_interest = 0.5
        pr.calc_sask_oil_prov_crown_royalty_volume_value(m, fn_interest, rp_interest, lease_rm, calc)
        self.assertEqual(calc.BaseRoyaltyVolume, 0.0)
        self.assertEqual(calc.BaseRoyaltyValue, 1396.06)

    def test_calc_sask_oil_prov_crown_deductions(self):

        pr = ProcessRoyalties()
        calc = DataStructure()
        calc.TransBaseValue = 0
        calc.BaseRoyaltyRate = .1
        calc.RoyaltyBasedOnVol = 150

        m = DataStructure()
        m.TransRate = .123
        # m.ProdVol = 150.0

        lease_royalty_master = DataStructure()
        lease_royalty_master.TransDeducted = 'All'
        lease_royalty_master.CrownMultiplier = 1.0

        fn_interest = 1.0
        rp_interest = 100.0

        # Note: this is a round even situation... it's questionable
        self.assertEqual(1.84,
                         pr.calc_sask_oil_prov_crown_deductions(m, fn_interest, rp_interest,
                                                                lease_royalty_master, calc))

        lease_royalty_master.CrownMultiplier = .9

        fn_interest = .8
        rp_interest = 90.

        self.assertEqual(1.2, pr.calc_sask_oil_prov_crown_deductions(m, fn_interest, rp_interest,
                                                                     lease_royalty_master, calc))

    def test_calcSaskOilIOGR1995(self):
        m = DataStructure()
        # m.WellHeadPrice = 221.123456
        m.SalesPrice = 221.123456
        m.TransRate = 2.123455
        m.ProcessingRate = 0.123455
        # m.ProdVol = 70
        m.ProdMonth = 201501

        calc = DataStructure()
        calc.BaseRoyaltyValue = 0.0
        calc.CommencementPeriod = 0
        calc.BaseRoyaltyVolume = 0.0
        calc.RoyaltyPrice = 0.0
        calc.RoyaltyBasedOnVol = 70
        calc.RoyaltyPrice = 221.123456

        crown_multiplier = 1.2
        fn_interest = .25
        rp_interest = 100

        pr = ProcessRoyalties()
        # all tests for SaskWellHead
        pr.calc_sask_oil_iogr1995(datetime(2015, 1, 1), "SaskWellHead",
                                  crown_multiplier, fn_interest, rp_interest, m, calc)
        self.assertEqual(464.36, calc.BaseRoyaltyValue)
        self.assertEqual(calc.CommencementPeriod, 0)
        self.assertEqual(calc.BaseRoyaltyVolume, 7)
        self.assertEqual(calc.RoyaltyPrice, 221.123456)

        # m.ProdVol = 100
        calc.RoyaltyBasedOnVol = 100
        crown_multiplier = 0.25
        fn_interest = 3
        rp_interest = 100
        pr.calc_sask_oil_iogr1995(datetime(2015, 4, 2), "SaskWellHead",
                                  crown_multiplier, fn_interest, rp_interest, m, calc)
        self.assertEqual(calc.BaseRoyaltyValue, 1990.11)

        # m.ProdVol = 170
        calc.RoyaltyBasedOnVol = 170
        crown_multiplier = 1.0
        fn_interest = 1
        rp_interest = 100
        pr.calc_sask_oil_iogr1995(datetime(2015, 5, 1), "SaskWellHead",
                                  crown_multiplier, fn_interest, rp_interest, m, calc)
        self.assertEqual(calc.BaseRoyaltyValue, 5881.88)

        # m.ProdVol = 79.9
        calc.RoyaltyBasedOnVol = 79.9
        crown_multiplier = 3
        fn_interest = 2
        rp_interest = 100
        pr.calc_sask_oil_iogr1995(datetime(2010, 1, 1), "SaskWellHead",
                                  crown_multiplier, fn_interest, rp_interest, m, calc)
        self.assertEqual(calc.BaseRoyaltyValue, 10600.66)

        # m.ProdVol = 150
        calc.RoyaltyBasedOnVol = 150
        crown_multiplier = 2
        fn_interest = 4
        rp_interest = 100
        pr.calc_sask_oil_iogr1995(datetime(2009, 7, 3), "SaskWellHead",
                                  crown_multiplier, fn_interest, rp_interest, m, calc)
        self.assertEqual(calc.BaseRoyaltyValue, 38917.73)

        # m.ProdVol = 500
        calc.RoyaltyBasedOnVol = 500
        crown_multiplier = 1
        fn_interest = 5
        rp_interest = 100
        pr.calc_sask_oil_iogr1995(datetime(2007, 8, 2), "SaskWellHead",
                                  crown_multiplier, fn_interest, rp_interest, m, calc)
        self.assertEqual(calc.BaseRoyaltyValue, 124271.38)

        # m.ProdVol = 800
        calc.RoyaltyBasedOnVol = 800
        crown_multiplier = 5
        fn_interest = 0.1
        rp_interest = 100
        pr.calc_sask_oil_iogr1995(datetime(2008, 9, 9), "SaskWellHead",
                                  crown_multiplier, fn_interest, rp_interest, m, calc)
        self.assertEqual(calc.BaseRoyaltyValue, 21117.29)

        # m.ProdVol = 800
        calc.RoyaltyBasedOnVol = 800
        crown_multiplier = 5
        fn_interest = 0.1
        rp_interest = 50
        pr.calc_sask_oil_iogr1995(datetime(2008, 9, 9), "SaskWellHead",
                                  crown_multiplier, fn_interest, rp_interest, m, calc)
        self.assertEqual(calc.BaseRoyaltyValue, 10558.65)

    # todo These royalties need to be checked by the business
    def test_calc_sask_gas_iogr1995(self):


        pr = ProcessRoyalties()

        calc = DataStructure()
        calc.RTPInterest = 1.0
        calc.PEFNInterest = 1.0
        calc.BaseRoyaltyValue = 0.0
        calc.CommencementPeriod = 0
        calc.BaseRoyaltyVolume = 0.0
        calc.RoyaltyPrice = 0.0
        calc.SuppRoyaltyValue = None

        calc.RoyaltyBasedOnVol = 70
        calc.SalesPrice = 5
        pr.calc_sask_gas_iogr1995(calc)
        self.assertEqual(calc.SuppRoyaltyValue, 0)
        self.assertEqual(calc.BaseRoyaltyValue, 87.5)

        calc.SalesPrice = 20
        pr.calc_sask_gas_iogr1995(calc)
        self.assertEqual(calc.SuppRoyaltyValue, 147.26)
        self.assertEqual(calc.BaseRoyaltyValue, 350)

        calc.SalesPrice = 50
        pr.calc_sask_gas_iogr1995(calc)
        self.assertEqual(calc.SuppRoyaltyValue, 949.86)
        self.assertEqual(calc.BaseRoyaltyValue, 875)

        calc.RTPInterest = .1
        calc.PEFNInterest = .2
        pr.calc_sask_gas_iogr1995(calc)
        self.assertEqual(calc.SuppRoyaltyValue, 19.0)
        self.assertEqual(calc.BaseRoyaltyValue, 17.5)

    def test_calcSaskPenIOGR1995(self):
        pr = ProcessRoyalties()
        calc = DataStructure()

        calc.BaseRoyaltyValue = 0.0
        calc.CommencementPeriod = 0
        calc.BaseRoyaltyVolume = 0.0
        calc.RoyaltyPrice = 0.0
        calc.SuppRoyaltyValue = None

        calc.RoyaltyBasedOnVol = 70
        calc.SalesPrice = 5
        pr.calc_sask_pen_iogr1995(calc)
        self.assertEqual(calc.SuppRoyaltyValue, 0)
        self.assertEqual(calc.BaseRoyaltyValue, 87.5)

        calc.SalesPrice = 50
        pr.calc_sask_pen_iogr1995(calc)
        self.assertEqual(calc.SuppRoyaltyValue, 8.37)
        self.assertEqual(calc.BaseRoyaltyValue, 875)

    def test_calcSaskSulIOGR1995(self):
        pr = ProcessRoyalties()
        m = DataStructure()
        calc = DataStructure()

        calc.BaseRoyaltyValue = 0.0
        calc.CommencementPeriod = 0
        calc.BaseRoyaltyVolume = 0.0
        calc.RoyaltyPrice = 0.0
        calc.SuppRoyaltyValue = None

        calc.RoyaltyBasedOnVol = 70
        calc.SalesPrice = 5
        pr.calc_sask_sul_iogr1995(calc)
        self.assertEqual(calc.SuppRoyaltyValue, 0)
        self.assertEqual(calc.BaseRoyaltyValue, 87.5)

        calc.SalesPrice = 50
        pr.calc_sask_sul_iogr1995(calc)
        self.assertEqual(calc.SuppRoyaltyValue, 3.99)
        self.assertEqual(calc.BaseRoyaltyValue, 875)

    def test_determineCommencementPeriod(self):
        pr = ProcessRoyalties()
        self.assertEqual(pr.determine_commencement_period(201501, datetime(2015, 1, 1)), 0)
        self.assertEqual(pr.determine_commencement_period(201501, datetime(2014, 12, 1)), 0.08)
        self.assertEqual(pr.determine_commencement_period(201501, datetime(2014, 11, 15)), 0.13)
        self.assertEqual(pr.determine_commencement_period(201501, datetime(2014, 1, 1)), 1)
        self.assertEqual(pr.determine_commencement_period(201501, datetime(2014, 1, 1)), 1)
        self.assertEqual(pr.determine_commencement_period(201501, datetime(2010, 1, 1)), 5)
        self.assertEqual(pr.determine_commencement_period(201501, datetime(2009, 12, 1)), 5.09)
        self.assertEqual(pr.determine_commencement_period(201501, None), 5)

    def test_calc_sask_oil_iogr_subsection2(self):
        pr = ProcessRoyalties()
        self.assertEqual(pr.calc_sask_oil_iogr_subsection2(70), 7)
        self.assertEqual(pr.calc_sask_oil_iogr_subsection2(100), 12)
        self.assertEqual(pr.calc_sask_oil_iogr_subsection2(170), 26.6)
        self.assertEqual(pr.calc_sask_oil_iogr_subsection2(200), (24 + .26 * (200 - 160)))
        self.assertEqual(pr.calc_sask_oil_iogr_subsection2(2000), (round(24 + .26 * (2000 - 160), 6)))

    def test_calc_sask_oil_iogr_subsection3(self):

        pr = ProcessRoyalties()
        self.assertEqual(pr.calc_sask_oil_iogr_subsection3(79.9), 7.99)
        self.assertEqual(pr.calc_sask_oil_iogr_subsection3(150), 22)
        self.assertEqual(pr.calc_sask_oil_iogr_subsection3(500), 112.4)
        self.assertEqual(pr.calc_sask_oil_iogr_subsection3(800), 191)
        self.assertEqual(pr.calc_sask_oil_iogr_subsection3(200), 24 + .26 * (200 - 160))
        self.assertEqual(pr.calc_sask_oil_iogr_subsection3(2000), 189 + .4 * (2000 - 795))

    def test_determineRoyaltyPrice(self):

        m = DataStructure()
        m.SalesPrice = 221.123456
        m.TransRate = 2.123455
        m.ProcessingRate = 0.123455

        pr = ProcessRoyalties()
        self.assertEqual((221.123456, None), pr.determine_royalty_price('ActSales', m))

        m.ProdVol = 4.0
        m.SalesVol = 2.0

        self.assertEqual((10.0, "Formula =((prod - sales) * 5) =((4.0 - 2.0) * 5) =10.0"),
                         pr.determine_royalty_price('=((prod - sales) * 5)', m))

    def test_calc_gorr_calc_type(self):
        pr = ProcessRoyalties()
        m = DataStructure()
        calc = DataStructure()

        m.ProdVol = 400
        m.ProdHours = 10
        gorr = "bad string,0,2"
        self.assertRaises(AppError, pr.get_gorr_calc_type, m, gorr, calc)
        m.ProdVol = None
        self.assertRaises(AppError, pr.get_gorr_calc_type, m, gorr, calc)

        gorr = None, "0,2"
        self.assertRaises(AttributeError, pr.get_gorr_calc_type, m, gorr, calc)


        m.ProdVol = 0
        gorr = "mprod,250,%.02,300,%.03,400,%.04,500,%.05,0,%.06"
        self.assertEqual(pr.get_gorr_calc_type(m, gorr, calc),
                         ('%.02', 'mprod = 0'))

        m.ProdVol = 600
        m.ProdHours = 10
        gorr = "dprod,250,%.02,300,%.03,400,%.04,500,%.05,0,%.06"
        self.assertEqual(pr.get_gorr_calc_type(m, gorr, calc),
                         ('%.02', 'dprod = mprod / 30.5 days; 19.67 is <= 250.0'))
        m.ProdVol = 8235
        m.ProdHours = 3
        self.assertEqual(pr.get_gorr_calc_type(m, gorr, calc),
                         ('%.03', 'dprod = mprod / 30.5 days; 270.00 is > 250.0 and <= 300.0'))
        m.ProdVol = 10065
        m.ProdHours = 30.5
        self.assertEqual(pr.get_gorr_calc_type(m, gorr, calc),
                         ('%.04', 'dprod = mprod / 30.5 days; 330.00 is > 300.0 and <= 400.0'))
        m.ProdVol = 13725
        m.ProdHours = 5
        self.assertEqual(pr.get_gorr_calc_type(m, gorr, calc),
                         ('%.05', 'dprod = mprod / 30.5 days; 450.00 is > 400.0 and <= 500.0'))

        m.ProdVol = None
        m.ProdHours = 10
        self.assertRaises(TypeError, pr.get_gorr_calc_type, m, gorr)

        gorr = "mprod,250,%.02,300,%.03,400,%.04,500,%.05,0,%.06"
        m.ProdVol = 200
        m.ProdHours = 10
        self.assertEqual(pr.get_gorr_calc_type(m, gorr, calc),
                         ('%.02', 'mprod = 200 is <= 250.0'))
        m.ProdVol = 300
        m.ProdHours = 4
        self.assertEqual(pr.get_gorr_calc_type(m, gorr, calc),
                         ('%.03', 'mprod = 300 is > 250.0 and <= 300.0'))
        m.ProdVol = 350.6
        m.ProdHours = 1
        self.assertEqual(pr.get_gorr_calc_type(m, gorr, calc),
                         ('%.04', 'mprod = 350.6 is > 300.0 and <= 400.0'))
        m.ProdVol = 410
        m.ProdHours = 2
        self.assertEqual(pr.get_gorr_calc_type(m, gorr, calc),
                         ('%.05', 'mprod = 410 is > 400.0 and <= 500.0'))
        m.ProdVol = 10000
        m.ProdHours = 17
        self.assertEqual(pr.get_gorr_calc_type(m, gorr, calc),
                         ('%.06', 'mprod = 10000 is > 500.0'))

        gorr = "hprod,250,%.02,300,%.03,400,%.04,500,%.05,0,%.06"
        m.ProdVol = 200
        m.ProdHours = 10
        self.assertEqual(pr.get_gorr_calc_type(m, gorr, calc),
                         ('%.02', 'hprod = mprod / hours; 20.00 is <= 250.0'))

        m.ProdVol = 200
        m.SalesVol = 100
        m.ProdHours = 10
        gorr = "=((prod - sales) * 5),250,%.02,300,%.03,400,%.04,500,%.05,0,%.06"
        self.assertEqual(pr.get_gorr_calc_type(m, gorr, calc),
                         ('%.05','Formula =((prod - sales) * 5) =((200 - 100) * 5) =500.0 is > 400.0 and <= 500.0'))
        m.ProdVol = 10000
        m.SalesVol = 10000
        m.ProdHours = 4
        self.assertEqual(pr.get_gorr_calc_type(m, gorr, calc),
                         ('%.02','Formula =((prod - sales) * 5) =((10000 - 10000) * 5) =0.0'))

    def test_gorr_royalty(self):

        pr = ProcessRoyalties()
        leaserm = DataStructure()
        calc = DataStructure()
        calc_specific = DataStructure()
        monthly = DataStructure()

        monthly.ProdVol = 100.0
        monthly.ProdHours = 10.0
        monthly.TransRate = .1234
        leaserm.TransDeducted = 'All'
        leaserm.Gorr = "fixed,0,%.02"

        calc.RTPInterest = 1.0
        calc.PEFNInterest = 1.0
        calc.RoyaltyPrice = 200.0
        calc.TransGorralue = 0.0
        calc.GorrRoyaltyValue = 0.0
        calc.TransGorrValue = 0.0
        calc.RoyaltyBasedOnVol = 100

        pr.calc_gorr(leaserm, monthly, calc, calc_specific)
        self.assertEqual(400.0, calc.GorrRoyaltyValue)
        self.assertEqual(.25, calc.TransGorrValue)
        self.assertEqual("fixed for a Royalty Rate of 2.00%", calc.GorrMessage)

        monthly.ProdVol = 100.0
        calc.RTPInterest = .5
        calc.TransGorrValue = 0.0

        pr.calc_gorr(leaserm, monthly, calc, calc_specific)
        self.assertEqual(200.0, calc.GorrRoyaltyValue)
        self.assertEqual(.12, calc.TransGorrValue)
        self.assertEqual("fixed for a Royalty Rate of 2.00%", calc.GorrMessage)

        calc.PEFNInterest = 1.0
        calc.RTPInterest = .5
        leaserm.Gorr = "fixed,0,$500.02"
        pr.calc_gorr(leaserm, monthly, calc, calc_specific)
        self.assertEqual(250.01, calc.GorrRoyaltyValue)
        self.assertEqual(.12, calc.TransGorrValue)
        self.assertEqual("fixed for a Base Royalty Value of $250.01", calc.GorrMessage)

        monthly.ProdVol = 100.0
        monthly.SalesVol = 90.0
        leaserm.Gorr = "fixed,0,$=((prod - sales) * 100)"
        pr.calc_gorr(leaserm, monthly, calc, calc_specific)
        self.assertEqual(500.00, calc.GorrRoyaltyValue)
        self.assertEqual(.12, calc.TransGorrValue)
        self.assertEqual("fixed for a Royalty Value of Formula $=((prod - sales) * 100) $=((100.0 - 90.0) * 100) "
                         "=1000.0 for a Base Royalty Value of $500.00", calc.GorrMessage)

        # leaserm.Gorr = '=(price),7.5,$=(.15*prod*price),0,$=(.15*(7.50*prod)+.25*((price-7.50)*prod))'
        leaserm.Gorr = '=(price),7.5,$=(.15*prod*price),0,$=(0.15 * (7.50 * prod) + 0.25 * ((price - 7.50) * prod))'
        monthly.ProdVol = 100.0
        calc.RoyaltyPrice = 200.0
        pr.calc_gorr(leaserm, monthly, calc, calc_specific)
        self.assertEqual(2462.5, calc.GorrRoyaltyValue)
        self.assertEqual(.12, calc.TransGorrValue)
        self.assertEqual("Formula =(price) =(200.0) =200.0 is > 7.5 for a Royalty Value of Formula "
                         "$=(0.15 * (7.50 * prod) + 0.25 * ((price - 7.50) * prod)) "
                         "$=(0.15 * (7.50 * 100.0) + 0.25 * ((200.0 - 7.50) * 100.0)) =4925.0 "
                         "for a Base Royalty Value of $2462.50", calc.GorrMessage)

    def test_calcSupplementaryRoyaltiesIOGR1995(self):
        reference_price = {'Pigeon Lake Indian': 24.04, 'Reserve no.138A': 25.37,
                           'Sawridge Indian': 25.13, 'Stony Plain Indian': 24.64}
        pr = ProcessRoyalties()
        # calc = DataStructure()

        self.assertEqual(pr.calc_supplementary_royalties_iogr1995(3.5, 228, 80, 60,
                                                                  reference_price['Pigeon Lake Indian']), 2039.6)
        self.assertEqual(pr.calc_supplementary_royalties_iogr1995(5, 200, 90, 40,
                                                                  reference_price['Reserve no.138A']), 4365.75)
        self.assertEqual(pr.calc_supplementary_royalties_iogr1995(4, 221.123456, 100, 50,
                                                                  reference_price['Sawridge Indian']), 4899.84)
        self.assertEqual(pr.calc_supplementary_royalties_iogr1995(.2, 180, 80, 35,
                                                                  reference_price['Stony Plain Indian']), 3495.6)

        self.assertEqual(pr.calc_supplementary_royalties_iogr1995(6, 228, 80, 60,
                                                                  reference_price['Pigeon Lake Indian']), 2996.5)
        self.assertEqual(pr.calc_supplementary_royalties_iogr1995(5.5, 200, 90, 40,
                                                                  reference_price['Reserve no.138A']), 6391.38)
        self.assertEqual(pr.calc_supplementary_royalties_iogr1995(8, 221.123456, 100, 50,
                                                                  reference_price['Sawridge Indian']), 7192.5)
        self.assertEqual(pr.calc_supplementary_royalties_iogr1995(15, 180, 80, 35,
                                                                  reference_price['Stony Plain Indian']), 5101.88)

    def test_calc_royalties(self):
        dbu = DatabaseUtilities()
        dbu.delete_all_tables()
        dbu.create_some_test_econoil()
        dbu.create_some_test_econgas()

        pr = ProcessRoyalties()
        well = DataStructure()
        royalty = DataStructure()
        calc = DataStructure()
        monthly = DataStructure()

        monthly.Product = 'OIL'
        monthly.ProdMonth = 201501
        monthly.ProdVol = 100
        monthly.SalesVol = 90
        monthly.GJ = 1000
        monthly.ProdHours = 744
        monthly.SalesPrice = 210.0
        royalty.RoyaltyScheme = 'SKProvCrownVar'
        royalty.OverrideRoyaltyClassification = None
        royalty.ValuationMethod = 'ActSales'
        royalty.CrownModifier = None
        royalty.MinRoyaltyRate = None
        royalty.CrownMultiplier = 1.0
        royalty.MinRoyaltyDollar = None
        royalty.TransDeducted = None
        royalty.OilBasedOn = "prod"
        royalty.GasBasedOn = "sales"
        royalty.ProductsBasedOn = "gj"
        well.ID = 123456
        well.CommencementDate = date(2015, 1, 22)
        well.RoyaltyClassification = 'Old'
        well.Classification = 'Other'
        well.SRC = 0.0
        calc.PEFNInterest = 1.0
        calc.RTPInterest = 1.0
        calc.SuppRoyaltyValue = 0.0
        calc.GorrRoyaltyValue = 0.0
        calc.TransGorrValue = 0.0
        calc.SalesPrice = 210.0

        pr.calc_royalties(well, royalty, monthly, calc)

        royalty.RoyaltyScheme = 'IOGR1995'
        pr.calc_royalties(well, royalty, monthly, calc)

        royalty.RoyaltyScheme = 'IOGR1995,GORR'
        royalty.Gorr = "fixed,0,.02"
        pr.calc_royalties(well, royalty, monthly, calc)

        monthly.Product = 'GAS'
        royalty.RoyaltyScheme = 'IOGR1995'
        royalty.Gorr = None
        royalty.GCADeducted = 'N'
        pr.calc_royalties(well, royalty, monthly, calc)

        monthly.Product = 'GAS'
        royalty.RoyaltyScheme = 'SKProvCrownVar'
        royalty.Gorr = None
        calc.RoyaltyVolume = 10.5
        monthly.GCARate = 1.15
        calc.RoyaltyDeductions = 0.0
        royalty.GCADeducted = 'Y'
        well.WellType = 'Gas'
        well.RoyaltyClassification = 'New'
        pr.calc_royalties(well, royalty, monthly, calc)

        monthly.Product = 'PEN'
        royalty.RoyaltyScheme = 'IOGR1995'
        pr.calc_royalties(well, royalty, monthly, calc)

        monthly.Product = 'SUL'
        royalty.RoyaltyScheme = 'IOGR1995'
        pr.calc_royalties(well, royalty, monthly, calc)

        monthly.Product = 'OIL'
        royalty.RoyaltyScheme = 'Bad One'
        self.assertRaises(AppError, pr.calc_royalties, well, royalty, monthly, calc)

    def test_process_all(self):
        db = config.get_database()
        dbu = DatabaseUtilities()
        dbu.delete_all_tables()
        dbu.create_some_test_well_royalty_masters()
        dbu.create_some_test_lease_royalty_masters()
        dbu.create_some_test_leases()
        dbu.create_some_test_well_lease_link()
        dbu.create_some_test_monthly()
        dbu.create_some_test_econoil()
        dbu.create_some_test_econgas()
        dbu.create_some_test_rtp_info()
        dbu.create_calc()

        pr = ProcessRoyalties()
        pr.process_one(4, 201501, 'OIL')

        # Check to see if calc records exist for both royalty payors
        self.assertEqual(2, db.count('calc'))

        pr.process_all()
        self.assertEqual(3, db.count('calc'))

        # Create an error to test the exception
        # Remove the monthly data record should raise an exception
        db.delete("RTPInfo", 1)  # This should cause an exception
        log = AppLogger()
        pr.process_all()
        msg = log.stop_capture()
        self.assertEqual(msg[:83],'"sqlite_database.select1 should have only found 1, but we found 0 in table: RTPInfo')

    def test_process_one(self):

        db = config.get_database()
        dbu = DatabaseUtilities()
        dbu.delete_all_tables()
        dbu.create_some_test_well_royalty_masters()
        dbu.create_some_test_lease_royalty_masters()
        dbu.create_some_test_leases()
        dbu.create_some_test_well_lease_link()
        dbu.create_some_test_monthly()
        dbu.create_some_test_econoil()
        dbu.create_some_test_rtp_info()
        dbu.create_calc()

        pr = ProcessRoyalties()
        pr.process_one(4, 201501, 'OIL')

        db.delete("WellLeaseLink", 4)  # This should cause a well lease link not found exception
        self.assertRaises(AppError, pr.process_one, 4, 201501, 'OIL')

        pr = ProcessRoyalties()
        pr.process_one(1, 201501, 'OIL')

        db.delete("Monthly", 1)  # This should cause a No monthly data found exception
        self.assertRaises(AppError, pr.process_one, 1, 201501, 'OIL')

    def test_royalty_based_on(self):

        pr = ProcessRoyalties()

        leaserm = DataStructure()
        calc = DataStructure()

        monthly = DataStructure()
        monthly.ProdVol = 100.0
        monthly.SalesVol = 90.0
        monthly.GJ = 1000.0

        leaserm.OilBasedOn = "prod"
        leaserm.GasBasedOn = "sales"
        leaserm.ProductsBasedOn = "gj"

        monthly.Product = "OIL"
        pr.determine_based_on(leaserm, monthly, calc)
        self.assertEqual("Prod Vol", calc.RoyaltyBasedOn)
        self.assertEqual(100.0, calc.RoyaltyBasedOnVol)

        monthly.Product = "GAS"
        pr.determine_based_on(leaserm, monthly, calc)
        self.assertEqual("Sales Vol", calc.RoyaltyBasedOn)
        self.assertEqual(90.0, calc.RoyaltyBasedOnVol)

        monthly.Product = "BUT"
        pr.determine_based_on(leaserm, monthly, calc)
        self.assertEqual("GJs", calc.RoyaltyBasedOn)
        self.assertEqual(1000.0, calc.RoyaltyBasedOnVol)

        leaserm.ProductsBasedOn = "stuff"
        monthly.Product = "BUT"
        pr.determine_based_on(leaserm, monthly, calc)
        self.assertEqual("Unknown", calc.RoyaltyBasedOn)
        self.assertEqual(0.0, calc.RoyaltyBasedOnVol)
