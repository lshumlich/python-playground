#!/bin/env python3

import unittest
from datetime import date
from datetime import datetime
# import sys
# import os

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
                                                                  'Fourth Tier', 220, 0, 'Oil'), 0.17217273)

        self.assertEqual(pr.calc_sask_gas_prov_crown_royalty_rate(royalty_calc, econ_gas_data,
                                                                  'Third Tier', 100, 0.75, None), 0.1359)
        self.assertEqual(pr.calc_sask_gas_prov_crown_royalty_rate(royalty_calc, econ_gas_data,
                                                                  'Third Tier', 200, 1, None), 0.2255)

        self.assertEqual(pr.calc_sask_gas_prov_crown_royalty_rate(royalty_calc, econ_gas_data,
                                                                  'New', 50, 2.25, None), 0.05715)
        self.assertEqual(pr.calc_sask_gas_prov_crown_royalty_rate(royalty_calc, econ_gas_data,
                                                                  'New', 130, 0.75, None), 0.19704615)

        self.assertEqual(pr.calc_sask_gas_prov_crown_royalty_rate(royalty_calc, econ_gas_data,
                                                                  'Old', 20, 1, None), 0.03124)
        self.assertEqual(pr.calc_sask_gas_prov_crown_royalty_rate(royalty_calc, econ_gas_data,
                                                                  'Old', 150, 0.5, None), 0.2879)

        self.assertRaises(AppError, pr.calc_sask_gas_prov_crown_royalty_rate, royalty_calc,
                          econ_gas_data, 'Fourth Tier', 20, 1, 'Bad String')
        self.assertRaises(AppError, pr.calc_sask_gas_prov_crown_royalty_rate, royalty_calc,
                          econ_gas_data, 'Bad String', 20, 1, 'Gas')

    def test_calc_sask_oil_prov_crown_royalty_rate(self):
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
        lease_rm.CrownMultiplier = None
        # lease_rm.CrownMultiplier = 1
        lease_rm.PriceBasedOn = 'ActSales'
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

        calc_specific = DataStructure()
        calc_specific.WellValueForRoyalty = 223.370366 * 100

        calc.PEFNInterest = 1.0
        calc.RTPInterest = 1.0

        pr.calc_sask_prov_crown_royalty_volume_value(m, lease_rm, calc, calc_specific)
        self.assertEqual(calc.BaseRoyaltyVolume, 0.0)
        self.assertEqual(calc.BaseRoyaltyValue, 5584.26)

        calc.BaseRoyaltyCalcRate = -.01
        calc.BaseRoyaltyRate = -.01
        lease_rm.MinRoyaltyRate = None
        pr.calc_sask_prov_crown_royalty_volume_value(m, lease_rm, calc, calc_specific)
        self.assertEqual(calc.BaseRoyaltyRate, 0)

        calc.BaseRoyaltyCalcRate = -.01
        calc.BaseRoyaltyRate = -.01
        lease_rm.MinRoyaltyRate = .02
        pr.calc_sask_prov_crown_royalty_volume_value(m, lease_rm, calc, calc_specific)
        self.assertEqual(calc.BaseRoyaltyRate, .02)
        self.assertEqual(calc.BaseRoyaltyValue, 446.74)

        lease_rm.MinRoyaltyDollar = 500.0
        pr.calc_sask_prov_crown_royalty_volume_value(m, lease_rm, calc, calc_specific)
        self.assertEqual(calc.BaseRoyaltyValue, 500.0)

        lease_rm.MinRoyaltyDollar = None
        lease_rm.MinRoyaltyRate = None
        calc.BaseRoyaltyCalcRate = .35
        lease_rm.CrownModifier = .02
        calc.BaseRoyaltyRate = None
        pr.calc_sask_prov_crown_royalty_volume_value(m, lease_rm, calc, calc_specific)
        self.assertEqual(calc.BaseRoyaltyRate, .37)

        # Reset to normal again
        lease_rm.CrownModifier = .0
        calc.BaseRoyaltyCalcRate = .25
        calc.RoyaltyPrice = 223.370366
        calc.BaseRoyaltyVolume = 0.0
        calc.BaseRoyaltyValue = 0.0
        pr.calc_sask_prov_crown_royalty_volume_value(m, lease_rm, calc, calc_specific)
        self.assertEqual(calc.BaseRoyaltyVolume, 0.0)
        self.assertEqual(calc.BaseRoyaltyValue, 5584.26)

        # m.ProdVol = 100
        calc.RoyaltyBasedOnVol = 100
        calc.RTPInterest = .5
        pr.calc_sask_prov_crown_royalty_volume_value(m, lease_rm, calc, calc_specific)
        self.assertEqual(calc.BaseRoyaltyVolume, 0.0)
        self.assertEqual(calc.BaseRoyaltyValue, 2792.13)

        # m.ProdVol = 100
        calc.RoyaltyBasedOnVol = 100
        calc.PEFNInterest = .5
        calc.RTPInterest = .5
        pr.calc_sask_prov_crown_royalty_volume_value(m, lease_rm, calc, calc_specific)
        self.assertEqual(calc.BaseRoyaltyVolume, 0.0)
        self.assertEqual(calc.BaseRoyaltyValue, 1396.06)

    def test_calc_sask_oil_prov_crown(self):
        dbu = DatabaseUtilities()
        dbu.delete_all_tables()
        dbu.create_some_test_econoil()

        pr = ProcessRoyalties()
        royalty = DataStructure()
        monthly = DataStructure()
        well = DataStructure()
        calc = DataStructure()
        calc_specific = DataStructure()

        monthly.Product = 'OIL'
        monthly.ProdMonth = 201501
        monthly.ProdVol = 100
        monthly.SalesVol = 90
        monthly.GJ = 1000
        monthly.ProdHours = 744
        monthly.SalesPrice = 210.0
        royalty.RoyaltyScheme = 'SKProvCrownVar'
        royalty.OverrideRoyaltyClassification = None
        royalty.OilRoyaltyBasedOn = None
        royalty.OilValueBasedOn = None
        royalty.GasValueBasedOn = None
        royalty.ProductsValueBasedOn = None
        royalty.OilPriceBasedOn = None
        royalty.GasPriceBasedOn = None
        royalty.ProductsPriceBasedOn = None
        royalty.CrownModifier = None
        royalty.MinRoyaltyRate = None
        royalty.CrownMultiplier = 1.0
        royalty.MinRoyaltyDollar = None
        royalty.BaseTrans = None
        royalty.OilBasedOn = "prod"
        royalty.GasBasedOn = "sales"
        royalty.ProductsBasedOn = "gj"
        well.ID = 123456
        well.CommencementDate = date(2015, 1, 22)
        well.RoyaltyClassification = 'Old'
        well.Classification = 'Other'
        well.SRC = 0.0
        calc.RoyaltyBasedOnVol = 100
        calc.PEFNInterest = 1.0
        calc.RTPInterest = 1.0
        calc.SuppRoyaltyValue = 0.0
        calc.GorrRoyaltyValue = 0.0
        calc.TransGorrValue = 0.0
        calc.SalesPrice = 210.0
        calc.BaseGCA = 0.0
        calc_specific.WellValueForRoyalty = 1000.00

        pr.calc_sask_oil_prov_crown(monthly, well, royalty, calc, calc_specific)

    def test_calc_sask_oil_iogr_subsection2(self):
        calc = DataStructure()
        calc_sp = DataStructure()
        pr = ProcessRoyalties()

        calc.BaseRoyaltyVolume = 0.0

        calc.RoyaltyBasedOnVol = 70
        pr.calc_sask_oil_iogr_subsection2(calc, calc_sp)
        self.assertEqual(7, calc.BaseRoyaltyVolume)

        calc.RoyaltyBasedOnVol = 100
        pr.calc_sask_oil_iogr_subsection2(calc, calc_sp)
        self.assertEqual(12, calc.BaseRoyaltyVolume)

        calc.RoyaltyBasedOnVol = 170
        pr.calc_sask_oil_iogr_subsection2(calc, calc_sp)
        self.assertEqual(26.6, calc.BaseRoyaltyVolume)

        calc.RoyaltyBasedOnVol = 200
        pr.calc_sask_oil_iogr_subsection2(calc, calc_sp)
        self.assertEqual((24 + .26 * (200 - 160)), calc.BaseRoyaltyVolume)

        calc.RoyaltyBasedOnVol = 2000
        pr.calc_sask_oil_iogr_subsection2(calc, calc_sp)
        self.assertEqual((round(24 + .26 * (2000 - 160), 6)), calc.BaseRoyaltyVolume)

        calc.RoyaltyBasedOnVol = 70
        pr.calc_sask_oil_iogr_subsection2(calc, calc_sp)
        self.assertEqual(7, calc.BaseRoyaltyVolume)

    def test_calc_sask_oil_iogr_subsection3(self):
        calc = DataStructure()
        calc_sp = DataStructure()
        pr = ProcessRoyalties()

        calc.BaseRoyaltyVolume = 0.0

        calc.RoyaltyBasedOnVol = 79.9
        pr.calc_sask_oil_iogr_subsection3(calc, calc_sp)
        self.assertEqual(7.99, calc.BaseRoyaltyVolume)

        calc.RoyaltyBasedOnVol = 150
        pr.calc_sask_oil_iogr_subsection3(calc, calc_sp)
        self.assertEqual(22, calc.BaseRoyaltyVolume)

        calc.RoyaltyBasedOnVol = 500
        pr.calc_sask_oil_iogr_subsection3(calc, calc_sp)
        self.assertEqual(112.4, calc.BaseRoyaltyVolume)

        calc.RoyaltyBasedOnVol = 800
        pr.calc_sask_oil_iogr_subsection3(calc, calc_sp)
        self.assertEqual(191, calc.BaseRoyaltyVolume)

        calc.RoyaltyBasedOnVol = 200
        pr.calc_sask_oil_iogr_subsection3(calc, calc_sp)
        self.assertEqual(24 + .26 * (200 - 160), calc.BaseRoyaltyVolume)

        calc.RoyaltyBasedOnVol = 2000
        pr.calc_sask_oil_iogr_subsection3(calc, calc_sp)
        self.assertEqual(189 + .4 * (2000 - 795), calc.BaseRoyaltyVolume)

    def test_calcSupplementaryRoyaltiesIOGR1995(self):
        reference_price = {'Pigeon Lake Indian': 24.04, 'Reserve no.138A': 25.37,
                           'Sawridge Indian': 25.13, 'Stony Plain Indian': 24.64}
        pr = ProcessRoyalties()
        calc_sp = DataStructure()
        calc_sp.BaseRoyaltyMessage = ''

        self.assertEqual(pr.calc_supplementary_royalties_iogr1995(3.5, 228, 80, 60,
                                                                  reference_price['Pigeon Lake Indian'], calc_sp), 2039.6)
        self.assertEqual(pr.calc_supplementary_royalties_iogr1995(5, 200, 90, 40,
                                                                  reference_price['Reserve no.138A'], calc_sp), 4365.75)
        self.assertEqual(pr.calc_supplementary_royalties_iogr1995(4, 221.123456, 100, 50,
                                                                  reference_price['Sawridge Indian'], calc_sp), 4899.84)
        self.assertEqual(pr.calc_supplementary_royalties_iogr1995(.2, 180, 80, 35,
                                                                  reference_price['Stony Plain Indian'], calc_sp), 3495.6)

        self.assertEqual(pr.calc_supplementary_royalties_iogr1995(6, 228, 80, 60,
                                                                  reference_price['Pigeon Lake Indian'], calc_sp), 2996.5)
        self.assertEqual(pr.calc_supplementary_royalties_iogr1995(5.5, 200, 90, 40,
                                                                  reference_price['Reserve no.138A'], calc_sp), 6391.38)
        self.assertEqual(pr.calc_supplementary_royalties_iogr1995(8, 221.123456, 100, 50,
                                                                  reference_price['Sawridge Indian'], calc_sp), 7192.5)
        self.assertEqual(pr.calc_supplementary_royalties_iogr1995(15, 180, 80, 35,
                                                                  reference_price['Stony Plain Indian'], calc_sp), 5101.88)


    def test_calc_sask_oil_iogr1995(self):
        self.maxDiff = None
        m = DataStructure()
        m.ProdMonth = 201501
        # m.WellHeadPrice = 221.123456
        m.SalesPrice = 221.123456
        m.TransRate = 2.123455
        m.ProcessingRate = 0.123455

        calc = DataStructure()
        calc.BaseRoyaltyValue = 0.0
        calc.CommencementPeriod = 0
        calc.BaseRoyaltyVolume = 0.0
        calc.IogrBaseRoyaltyValue = 0.0
        calc.IogrSuppRoyaltyValue = 0.0
        calc.BaseTransValue = 0.0
        calc.BaseRoyaltyRate = 0.0
        calc.RoyaltyPrice = 221.123456
        calc.PEFNInterest = .2
        calc.RTPInterest = .3

        royalty = DataStructure()
        royalty.BaseTrans = 'prod'

        calc_sp = DataStructure()
        calc_sp.BaseRoyaltyMessage = None

        pr = ProcessRoyalties()

        # < 5 year commencement period

        calc.RoyaltyBasedOnVol = 70
        m.ProdVol = 70
        pr.calc_sask_oil_iogr1995(royalty, datetime(2015, 1, 1),
                                  m, calc, calc_sp)
        self.assertEqual(calc.CommencementPeriod, 0)
        self.assertEqual(7.0, calc.BaseRoyaltyVolume)           # = 70 * 0.1
        self.assertEqual(1547.86, calc.IogrBaseRoyaltyValue)    # = 7.0 * 221.123456
        self.assertEqual(6177.89, calc.IogrSuppRoyaltyValue)    # = (70 - 7) * 0.5 * (221.123456 - 25)
        self.assertEqual(463.55, calc.BaseRoyaltyValue)         # = (1547.86 + 6177.89) * 0.2 * 0.3
        self.assertEqual(0.49912325, calc.BaseRoyaltyRate)      # = (1547.86 + 6177.89) / (70 * 221.123456)
        self.assertEqual(4.45, calc.BaseTransValue)             # = 70 * 0.49912325 * 2.123455 * 0.2 * 0.3
        self.assertEqual("MOP < 80: RVol = 10% * MOP;"
                         "RVol = 10% * 70.00;"
                         "RVol = 7.00;;"
                         "R$ = RVol * RVal;"
                         "R$ = 7.00 * 221.123456;"
                         "R$ = $1,547.86;;"
                         "S = (T - B) * 0.50 * (P - R);"
                         "S = (70.00 - 7.00) * 0.5 * (221.123456 - 25);"
                         "S = $6,177.89;;"
                         "Royalty = (R$ + S$) * PE FN %	* RP %;"
                         "Royalty = ($1,547.86 + $6,177.89) * 20.000000% * 30.000000%;"
                         "Royalty = $463.55;", calc_sp.BaseRoyaltyMessage)

        calc.RoyaltyBasedOnVol = 100
        m.ProdVol = 100
        pr.calc_sask_oil_iogr1995(royalty, datetime(2015, 1, 1),
                                  m, calc, calc_sp)
        self.assertEqual(calc.CommencementPeriod, 0)
        self.assertEqual(12.0, calc.BaseRoyaltyVolume)          # = 8 + ((100 - 80) * .2)
        self.assertEqual(2653.48, calc.IogrBaseRoyaltyValue)    # = 12.0 * 221.123456
        self.assertEqual(8629.43, calc.IogrSuppRoyaltyValue)    # = (100 - 12) * 0.5 * (221.123456 - 25)
        self.assertEqual(676.97, calc.BaseRoyaltyValue)         # = (2653.48 + 8629.43) * 0.2 * 0.3
        self.assertEqual(0.51025387, calc.BaseRoyaltyRate)        # = (2653.48 + 8629.43) / (100 * 221.123456)
        self.assertEqual(6.50, calc.BaseTransValue)             # = 100 * 0.51025387 * 2.123455 * 0.2 * 0.3
        self.assertEqual("MOP 80 to 160: RVol = 8 + (MOP - 80) * 20%;"
                         "RVol = 8 + (100.00 - 80) * 20%;"
                         "RVol = 12.00;;"
                         "R$ = RVol * RVal;"
                         "R$ = 12.00 * 221.123456;"
                         "R$ = $2,653.48;;"
                         "S = (T - B) * 0.50 * (P - R);"
                         "S = (100.00 - 12.00) * 0.5 * (221.123456 - 25);"
                         "S = $8,629.43;;"
                         "Royalty = (R$ + S$) * PE FN %	* RP %;"
                         "Royalty = ($2,653.48 + $8,629.43) * 20.000000% * 30.000000%;"
                         "Royalty = $676.97;", calc_sp.BaseRoyaltyMessage)

        calc.RoyaltyBasedOnVol = 170
        m.ProdVol = 170
        pr.calc_sask_oil_iogr1995(royalty, datetime(2015, 1, 1),
                                  m, calc, calc_sp)
        self.assertEqual(calc.CommencementPeriod, 0)
        self.assertEqual(26.6, calc.BaseRoyaltyVolume)          # = 24 + ((170 - 160) * .26)
        self.assertEqual(5881.88, calc.IogrBaseRoyaltyValue)    # = 26.6 * 221.123456
        self.assertEqual(14062.05, calc.IogrSuppRoyaltyValue)   # = (170 - 26.6) * 0.5 * (221.123456 - 25)
        self.assertEqual(1196.64, calc.BaseRoyaltyValue)        # = (5881.88 + 14062.05) * 0.2 * 0.3
        self.assertEqual(0.53055084, calc.BaseRoyaltyRate)       # = (5881.88 + 14062.05) / (170 * 221.123456)
        self.assertEqual(11.49, calc.BaseTransValue)            # = 170 * 0.53055084 * 2.123455 * 0.2 * 0.3
        self.assertEqual("MOP > 160: RVol = 24 + (MOP - 160) * 26%;"
                         "RVol = 24 + (170.00 - 160) * 26%;"
                         "RVol = 26.60;;"
                         "R$ = RVol * RVal;"
                         "R$ = 26.60 * 221.123456;"
                         "R$ = $5,881.88;;"
                         "S = (T - B) * 0.50 * (P - R);"
                         "S = (170.00 - 26.60) * 0.5 * (221.123456 - 25);"
                         "S = $14,062.05;;"
                         "Royalty = (R$ + S$) * PE FN %	* RP %;"
                         "Royalty = ($5,881.88 + $14,062.05) * 20.000000% * 30.000000%;"
                         "Royalty = $1,196.64;", calc_sp.BaseRoyaltyMessage)

        calc.RoyaltyBasedOnVol = 1000
        m.ProdVol = 1000
        pr.calc_sask_oil_iogr1995(royalty, datetime(2015, 1, 1),
                                  m, calc, calc_sp)
        self.assertEqual(calc.CommencementPeriod, 0)
        self.assertEqual(242.4, calc.BaseRoyaltyVolume)         # = 24 + ((1000 - 160) * .26)
        self.assertEqual(53600.33, calc.IogrBaseRoyaltyValue)   # = 242.4 * 221.123456
        self.assertEqual(74291.57, calc.IogrSuppRoyaltyValue)   # = (1000 - 242.4) * 0.5 * (221.123456 - 25)
        self.assertEqual(7673.51, calc.BaseRoyaltyValue)        # = (53600.33 + 74291.57) * 0.2 * 0.3
        self.assertEqual(0.57837329, calc.BaseRoyaltyRate)      # = ((53600.33 + 74291.57) / (1000 * 221.123456)
        self.assertEqual(73.69, calc.BaseTransValue)            # = 1000 * 0.57837329 * 2.123455 * 0.2 * 0.3
        self.assertEqual("MOP > 160: RVol = 24 + (MOP - 160) * 26%;"
                         "RVol = 24 + (1,000.00 - 160) * 26%;"
                         "RVol = 242.40;;"
                         "R$ = RVol * RVal;"
                         "R$ = 242.40 * 221.123456;"
                         "R$ = $53,600.33;;"
                         "S = (T - B) * 0.50 * (P - R);"
                         "S = (1,000.00 - 242.40) * 0.5 * (221.123456 - 25);"
                         "S = $74,291.57;;"
                         "Royalty = (R$ + S$) * PE FN %	* RP %;"
                         "Royalty = ($53,600.33 + $74,291.57) * 20.000000% * 30.000000%;"
                         "Royalty = $7,673.51;", calc_sp.BaseRoyaltyMessage)

        # >= 5 year commencement period

        calc.RoyaltyBasedOnVol = 70
        m.ProdVol = 70
        pr.calc_sask_oil_iogr1995(royalty, datetime(2009, 12, 1),
                                  m, calc, calc_sp)
        self.assertEqual(calc.CommencementPeriod, 5.09)
        self.assertEqual(7.0, calc.BaseRoyaltyVolume)           # = 70 * 0.1
        self.assertEqual(1547.86, calc.IogrBaseRoyaltyValue)    # = 7.0 * 221.123456
        self.assertEqual(9068.70, calc.IogrSuppRoyaltyValue)    # = (70 - 7) * (0.75 * (221.123456 - 25 - 12.58) + 6.29)
        self.assertEqual(636.99, calc.BaseRoyaltyValue)         # = (1547.86 + 9068.70) * 0.2 * 0.3
        self.assertEqual(0.68588446, calc.BaseRoyaltyRate)      # = (1547.86 + 9068.70) / (70 * 221.123456)
        self.assertEqual(6.12, calc.BaseTransValue)             # = 70 * 0.68588446 * 2.123455 * 0.2 * 0.3
        self.assertEqual("MOP < 80: RVol = 10% * MOP;"
                         "RVol = 10% * 70.00;"
                         "RVol = 7.00;;"
                         "R$ = RVol * RVal;"
                         "R$ = 7.00 * 221.123456;"
                         "R$ = $1,547.86;;"
                         "S = (T - B) * (0.75 * (P - R - $12.58) + $6.29);"
                         "S = (70.00 - 7.00) * 0.75 * (221.123456 - 25-12.58) + 6.29);"
                         "S = $9,068.70;;"
                         "Royalty = (R$ + S$) * PE FN %	* RP %;"
                         "Royalty = ($1,547.86 + $9,068.70) * 20.000000% * 30.000000%;"
                         "Royalty = $636.99;", calc_sp.BaseRoyaltyMessage)

        calc.RoyaltyBasedOnVol = 100
        m.ProdVol = 100
        pr.calc_sask_oil_iogr1995(royalty, datetime(2009, 12, 1),
                                  m, calc, calc_sp)
        self.assertEqual(calc.CommencementPeriod, 5.09)
        self.assertEqual(12.0, calc.BaseRoyaltyVolume)          # = 8 + ((100 - 80) * .2)
        self.assertEqual(2653.48, calc.IogrBaseRoyaltyValue)    # = 12.0 * 221.123456
        self.assertEqual(12667.39, calc.IogrSuppRoyaltyValue)   # = (100 - 12) * (0.75 * (221.123456 - 25 - 12.58) + 6.29)
        self.assertEqual(919.25, calc.BaseRoyaltyValue)         # = (2653.48 + 12667.39) * 0.2 * 0.3
        self.assertEqual(0.69286498, calc.BaseRoyaltyRate)      # = (2653.48 + 12667.39) / (100 * 221.123456)
        self.assertEqual(8.83, calc.BaseTransValue)             # = 100 * 0.69286499 * 2.123455 * 0.2 * 0.3
        self.assertEqual("MOP 80 to 160: RVol = 8 + (MOP - 80) * 20%;"
                         "RVol = 8 + (100.00 - 80) * 20%;"
                         "RVol = 12.00;;"
                         "R$ = RVol * RVal;"
                         "R$ = 12.00 * 221.123456;"
                         "R$ = $2,653.48;;"
                         "S = (T - B) * (0.75 * (P - R - $12.58) + $6.29);"
                         "S = (100.00 - 12.00) * 0.75 * (221.123456 - 25-12.58) + 6.29);"
                         "S = $12,667.39;;"
                         "Royalty = (R$ + S$) * PE FN %	* RP %;"
                         "Royalty = ($2,653.48 + $12,667.39) * 20.000000% * 30.000000%;"
                         "Royalty = $919.25;", calc_sp.BaseRoyaltyMessage)

        calc.RoyaltyBasedOnVol = 170
        m.ProdVol = 170
        pr.calc_sask_oil_iogr1995(royalty, datetime(2009, 12, 1),
                                  m, calc, calc_sp)
        self.assertEqual(calc.CommencementPeriod, 5.09)
        self.assertEqual(26.6, calc.BaseRoyaltyVolume)          # = 24 + ((170 - 160) * .26)
        self.assertEqual(5881.88, calc.IogrBaseRoyaltyValue)    # = 26.6 * 221.123456
        self.assertEqual(20642.08, calc.IogrSuppRoyaltyValue)   # = (170 - 26.6) * (0.75 * (221.123456 - 25 - 12.58) + 6.29)
        self.assertEqual(1591.44, calc.BaseRoyaltyValue)        # = (5881.88 + 20642.08) * 0.2 * 0.3
        self.assertEqual(0.70559359, calc.BaseRoyaltyRate)      # = (5881.88 + 20642.08) / (170 * 221.123456)
        self.assertEqual(15.28, calc.BaseTransValue)            # = 170 * 0.70559359 * 2.123455 * 0.2 * 0.3
        self.assertEqual("MOP 160 to 795: RVol = 24 + (MOP - 160) * 26%;"
                         "RVol = 24 + (170.00 - 160) * 26%;"
                         "RVol = 26.60;;"
                         "R$ = RVol * RVal;"
                         "R$ = 26.60 * 221.123456;"
                         "R$ = $5,881.88;;"
                         "S = (T - B) * (0.75 * (P - R - $12.58) + $6.29);"
                         "S = (170.00 - 26.60) * 0.75 * (221.123456 - 25-12.58) + 6.29);"
                         "S = $20,642.08;;"
                         "Royalty = (R$ + S$) * PE FN %	* RP %;"
                         "Royalty = ($5,881.88 + $20,642.08) * 20.000000% * 30.000000%;"
                         "Royalty = $1,591.44;", calc_sp.BaseRoyaltyMessage)

        calc.RoyaltyBasedOnVol = 1000
        m.ProdVol = 1000
        pr.calc_sask_oil_iogr1995(royalty, datetime(2009, 12, 1),
                                  m, calc, calc_sp)
        self.assertEqual(calc.CommencementPeriod, 5.09)
        self.assertEqual(271.0, calc.BaseRoyaltyVolume)         # = 189 + ((1000 - 795) * .4)
        self.assertEqual(59924.46, calc.IogrBaseRoyaltyValue)   # = 271.0 * 221.123456
        self.assertEqual(104937.79, calc.IogrSuppRoyaltyValue)  # = (1000 - 271.0) * (0.75 * (221.123456 - 25 - 12.58) + 6.29)
        self.assertEqual(9891.74, calc.BaseRoyaltyValue)       # = (59924.46 + 104937.79) * 0.2 * 0.3
        self.assertEqual(0.74556654, calc.BaseRoyaltyRate)      # = (59924.46 + 104937.79) / (1000 * 221.123456)
        self.assertEqual(94.99, calc.BaseTransValue)           # = 1000 * 0.74556654 * 2.123455 * 0.2 * 0.3
        self.assertEqual("MOP > 795: RVol = 189 + (MOP - 795) * 40%;"
                         "RVol = 189 + (1,000.00 - 795) * 40%;"
                         "RVol = 271.00;;"
                         "R$ = RVol * RVal;"
                         "R$ = 271.00 * 221.123456;"
                         "R$ = $59,924.46;;"
                         "S = (T - B) * (0.75 * (P - R - $12.58) + $6.29);"
                         "S = (1,000.00 - 271.00) * 0.75 * (221.123456 - 25-12.58) + 6.29);"
                         "S = $104,937.79;;Royalty = (R$ + S$) * PE FN %	* RP %;"
                         "Royalty = ($59,924.46 + $104,937.79) * 20.000000% * 30.000000%;"
                         "Royalty = $9,891.74;", calc_sp.BaseRoyaltyMessage)

    def test_calc_sask_gas_iogr1995(self):

        self.maxDiff = None

        pr = ProcessRoyalties()

        lease_rm = DataStructure()
        lease_rm.BaseGCA = 'sales'

        monthly = DataStructure()
        monthly.GCARate = 9.00

        calc = DataStructure()
        calc.RTPInterest = 1.0
        calc.PEFNInterest = 1.0
        calc.IogrSuppRoyaltyValue = None
        calc.IogrBaseRoyaltyValue = 0.0
        calc.BaseRoyaltyValue = 0.0

        calc_sp = DataStructure()
        calc_sp.BaseRoyaltyMessage = None

        calc.RoyaltyBasedOnVol = 70
        monthly.SalesVol = 70
        calc.RoyaltyBasedOn = 'Sales Vol'

        calc.RoyaltyPrice = 5.0
        pr.calc_sask_gas_iogr1995(lease_rm, monthly, calc, calc_sp)
        self.assertEqual(calc.IogrSuppRoyaltyValue, 0)
        self.assertEqual(calc.IogrBaseRoyaltyValue, 87.5)
        self.assertEqual(calc.BaseRoyaltyValue, 87.5)
        self.assertEqual('R$ = 0.25 * Sales Vol * Price;'
                         'R$ = 0.25 * 70.00 * 5.000000;'
                         'R$ = $87.50;;'
                         'price < $10.65;S = $0.00;;'
                         'Royalty = (R$ + S$) * PE FN %	* RP %;'
                         'Royalty = ($87.50 + $0.00) * 100.000000% * 100.000000%;'
                         'Royalty = $87.50;', calc_sp.BaseRoyaltyMessage)

        calc.RoyaltyPrice = 20
        pr.calc_sask_gas_iogr1995(lease_rm, monthly, calc, calc_sp)
        self.assertEqual(calc.IogrSuppRoyaltyValue, 147.26)
        self.assertEqual(calc.IogrBaseRoyaltyValue, 350)
        self.assertEqual(calc.BaseRoyaltyValue, 497.26)
        self.assertEqual('R$ = 0.25 * Sales Vol * Price;'
                         'R$ = 0.25 * 70.00 * 20.000000;'
                         'R$ = $350.00;;'
                         'price <= $10.65);'
                         'S = (0.75 * Sales Vol * 30% * (price  - $10.65);'
                         'S = (0.75 * 70.00 * 30% * (20.000000 - $10.65);'
                         'S = $147.26;;'
                         'Royalty = (R$ + S$) * PE FN %	* RP %;'
                         'Royalty = ($350.00 + $147.26) * 100.000000% * 100.000000%;'
                         'Royalty = $497.26;', calc_sp.BaseRoyaltyMessage)

        calc.RoyaltyPrice = 50
        pr.calc_sask_gas_iogr1995(lease_rm, monthly, calc, calc_sp)
        self.assertEqual(calc.IogrSuppRoyaltyValue, 949.86)
        self.assertEqual(calc.IogrBaseRoyaltyValue, 875)
        self.assertEqual(calc.BaseRoyaltyValue, 1824.86)
        self.assertEqual('R$ = 0.25 * Sales Vol * Price;'
                         'R$ = 0.25 * 70.00 * 50.000000;'
                         'R$ = $875.00;;'
                         'price > $10.65);'
                         'S = (0.75 * Sales Vol * (4.26 + 0.55 * (price  - $24.85));'
                         'S = (0.75 * 70.00 * (4.26 + 0.55 * (50.000000 - $24.85));'
                         'S = $949.86;;'
                         'Royalty = (R$ + S$) * PE FN %	* RP %;'
                         'Royalty = ($875.00 + $949.86) * 100.000000% * 100.000000%;'
                         'Royalty = $1,824.86;', calc_sp.BaseRoyaltyMessage)

        calc.RTPInterest = .1
        calc.PEFNInterest = .2
        pr.calc_sask_gas_iogr1995(lease_rm, monthly, calc, calc_sp)
        self.assertEqual(calc.IogrSuppRoyaltyValue, 949.86)
        self.assertEqual(calc.IogrBaseRoyaltyValue, 875.0)
        self.assertEqual(calc.BaseRoyaltyValue, 36.5)
        self.assertEqual('R$ = 0.25 * Sales Vol * Price;'
                         'R$ = 0.25 * 70.00 * 50.000000;'
                         'R$ = $875.00;;'
                         'price > $10.65);'
                         'S = (0.75 * Sales Vol * (4.26 + 0.55 * (price  - $24.85));'
                         'S = (0.75 * 70.00 * (4.26 + 0.55 * (50.000000 - $24.85));'
                         'S = $949.86;;'
                         'Royalty = (R$ + S$) * PE FN %	* RP %;'
                         'Royalty = ($875.00 + $949.86) * 20.000000% * 10.000000%;'
                         'Royalty = $36.50;', calc_sp.BaseRoyaltyMessage)

    def test_calcSaskPenIOGR1995(self):

        pr = ProcessRoyalties()
        calc = DataStructure()

        calc.BaseRoyaltyValue = 0.0
        calc.CommencementPeriod = 0
        calc.BaseRoyaltyVolume = 0.0
        calc.RoyaltyPrice = 0.0
        calc.SuppRoyaltyValue = None
        calc.IogrSuppRoyaltyValue = 0.0
        calc.IogrBaseRoyaltyValue = 0.0

        calc.RoyaltyBasedOnVol = 70
        calc.SalesPrice = 5
        pr.calc_sask_pen_iogr1995(calc)
        self.assertEqual(calc.IogrSuppRoyaltyValue, 0)
        self.assertEqual(calc.IogrBaseRoyaltyValue, 87.5)

        calc.SalesPrice = 50
        pr.calc_sask_pen_iogr1995(calc)
        self.assertEqual(calc.IogrSuppRoyaltyValue, 8.37)
        self.assertEqual(calc.IogrBaseRoyaltyValue, 875)

    def test_calcSaskSulIOGR1995(self):
        pr = ProcessRoyalties()
        calc = DataStructure()

        calc.BaseRoyaltyValue = 0.0
        calc.CommencementPeriod = 0
        calc.BaseRoyaltyVolume = 0.0
        calc.RoyaltyPrice = 0.0
        calc.SuppRoyaltyValue = None
        calc.IogrSuppRoyaltyValue = 0.0
        calc.IogrBaseRoyaltyValue = 0.0

        calc.RoyaltyBasedOnVol = 70
        calc.SalesPrice = 5
        pr.calc_sask_sul_iogr1995(calc)
        self.assertEqual(calc.IogrSuppRoyaltyValue, 0)
        self.assertEqual(calc.IogrBaseRoyaltyValue, 87.5)

        calc.SalesPrice = 50
        pr.calc_sask_sul_iogr1995(calc)
        self.assertEqual(calc.IogrSuppRoyaltyValue, 3.99)
        self.assertEqual(calc.IogrBaseRoyaltyValue, 875)

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

    def test_determine_royalty_price(self):
        pr = ProcessRoyalties()

        leaserm = DataStructure()
        calc = DataStructure()
        calc_sp = DataStructure()
        monthly = DataStructure()

        calc.RoyaltyPrice = None
        calc.RoyaltyPriceExplanation = None

        monthly.SalesPrice = 130.0
        monthly.TransRate = 10.0

        monthly.Product = "OIL"
        leaserm.OilPriceBasedOn = "=(price)"
        pr.determine_royalty_price(leaserm, monthly, calc, calc_sp)
        self.assertEqual(130.0, calc.RoyaltyPrice)
        self.assertEqual("Formula =(price) =(130.0) =130.0", calc.RoyaltyPriceExplanation)

        monthly.Product = "OIL"
        leaserm.OilPriceBasedOn = "=(price - trans)"
        pr.determine_royalty_price(leaserm, monthly, calc, calc_sp)
        self.assertEqual(120.0, calc.RoyaltyPrice)
        self.assertEqual('Formula =(price - trans) =(130.0 - 10.0) =120.0', calc.RoyaltyPriceExplanation)

        monthly.ProdVol = 4.0
        monthly.SalesVol = 2.0
        leaserm.OilPriceBasedOn = "=((prod - sales) * 5)"
        pr.determine_royalty_price(leaserm, monthly, calc, calc_sp)
        self.assertEqual(10.0, calc.RoyaltyPrice)
        self.assertEqual('Formula =((prod - sales) * 5) =((4.0 - 2.0) * 5) =10.0', calc.RoyaltyPriceExplanation)

        # Default to sales
        leaserm.OilPriceBasedOn = "asdf"
        pr.determine_royalty_price(leaserm, monthly, calc, calc_sp)
        self.assertEqual(130.0, calc.RoyaltyPrice)
        self.assertEqual(None, calc.RoyaltyPriceExplanation)

    def test_determine_well_value_for_royalties(self):
        pr = ProcessRoyalties()
        leaserm = DataStructure()
        calc = DataStructure()
        calc_sp = DataStructure()
        monthly = DataStructure()

        calc_sp.WellValueForRoyalty = None
        calc_sp.WellValueForRoyaltyExplanation = None

        monthly.SalesPrice = 130.0
        monthly.SalesVol = 10.0
        monthly.ProdVol = 20.0
        monthly.GJ = 1000

        # ensure default works
        monthly.Product = "OIL"
        leaserm.OilValueBasedOn = None
        pr.determine_well_value_for_royalties(leaserm, monthly, calc, calc_sp)
        self.assertEqual(1300, calc_sp.WellValueForRoyalty)
        self.assertEqual('Well Value = Sales Vol * Price;Well Value = 10.00 * 130.000000; Well Value = $1,300.00;',
                         calc_sp.WellValueForRoyaltyExplanation)

        leaserm.OilValueBasedOn = "=(price * sales)"
        pr.determine_well_value_for_royalties(leaserm, monthly, calc, calc_sp)
        self.assertEqual(1300, calc_sp.WellValueForRoyalty)
        self.assertEqual('Well Value =(price * sales); Well Value =(130.0 * 10.0); Well Value = $1,300.00;',
                         calc_sp.WellValueForRoyaltyExplanation)

        monthly.Product = "GAS"
        leaserm.GasValueBasedOn = "=(price * gj)"
        pr.determine_well_value_for_royalties(leaserm, monthly, calc, calc_sp)
        self.assertEqual('Well Value =(price * gj); Well Value =(130.0 * 1000); Well Value = $130,000.00;',
                         calc_sp.WellValueForRoyaltyExplanation)
        self.assertEqual(130000.0, calc_sp.WellValueForRoyalty)

        monthly.Product = "BUT"
        leaserm.ProductsValueBasedOn = "=(price * prod)"
        pr.determine_well_value_for_royalties(leaserm, monthly, calc, calc_sp)
        self.assertEqual(2600.0, calc_sp.WellValueForRoyalty)
        self.assertEqual('Well Value =(price * prod); Well Value =(130.0 * 20.0); Well Value = $2,600.00;',
                         calc_sp.WellValueForRoyaltyExplanation)

        leaserm.ProductsValueBasedOn = "asdf"
        self.assertRaises(AppError, pr.determine_well_value_for_royalties, leaserm, monthly, calc, calc_sp)

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

        gorr = None
        self.assertRaises(AppError, pr.get_gorr_calc_type, m, gorr, calc)

        gorr = ''
        self.assertRaises(AppError, pr.get_gorr_calc_type, m, gorr, calc)

        m.ProdVol = 0
        gorr = "mprod,250,%.02,300,%.03,400,%.04,500,%.05,0,%.06"
        self.assertEqual(pr.get_gorr_calc_type(m, gorr, calc),
                         ('%.02', 'mprod = 0;'))

        m.ProdVol = 600
        m.ProdHours = 10
        gorr = "dprod,250,%.02,300,%.03,400,%.04,500,%.05,0,%.06"
        self.assertEqual(pr.get_gorr_calc_type(m, gorr, calc),
                         ('%.02', 'dprod = mprod / 30.5 days; 19.67 is <= 250.0;'))
        m.ProdVol = 8235
        m.ProdHours = 3
        self.assertEqual(pr.get_gorr_calc_type(m, gorr, calc),
                         ('%.03', 'dprod = mprod / 30.5 days; 270.00 is > 250.0 and <= 300.0;'))
        m.ProdVol = 10065
        m.ProdHours = 30.5
        self.assertEqual(pr.get_gorr_calc_type(m, gorr, calc),
                         ('%.04', 'dprod = mprod / 30.5 days; 330.00 is > 300.0 and <= 400.0;'))
        m.ProdVol = 13725
        m.ProdHours = 5
        self.assertEqual(pr.get_gorr_calc_type(m, gorr, calc),
                         ('%.05', 'dprod = mprod / 30.5 days; 450.00 is > 400.0 and <= 500.0;'))

        m.ProdVol = None
        m.ProdHours = 10
        self.assertRaises(TypeError, pr.get_gorr_calc_type, m, gorr)

        gorr = "mprod,250,%.02,300,%.03,400,%.04,500,%.05,0,%.06"
        m.ProdVol = 200
        m.ProdHours = 10
        self.assertEqual(pr.get_gorr_calc_type(m, gorr, calc),
                         ('%.02', 'mprod = 200 is <= 250.0;'))
        m.ProdVol = 300
        m.ProdHours = 4
        self.assertEqual(pr.get_gorr_calc_type(m, gorr, calc),
                         ('%.03', 'mprod = 300 is > 250.0 and <= 300.0;'))
        m.ProdVol = 350.6
        m.ProdHours = 1
        self.assertEqual(pr.get_gorr_calc_type(m, gorr, calc),
                         ('%.04', 'mprod = 350.6 is > 300.0 and <= 400.0;'))
        m.ProdVol = 410
        m.ProdHours = 2
        self.assertEqual(pr.get_gorr_calc_type(m, gorr, calc),
                         ('%.05', 'mprod = 410 is > 400.0 and <= 500.0;'))
        m.ProdVol = 10000
        m.ProdHours = 17
        self.assertEqual(pr.get_gorr_calc_type(m, gorr, calc),
                         ('%.06', 'mprod = 10000 is > 500.0;'))

        gorr = "hprod,250,%.02,300,%.03,400,%.04,500,%.05,0,%.06"
        m.ProdVol = 200
        m.ProdHours = 10
        self.assertEqual(pr.get_gorr_calc_type(m, gorr, calc),
                         ('%.02', 'hprod = mprod / hours; 20.00 is <= 250.0;'))

        m.ProdVol = 200
        m.SalesVol = 100
        m.ProdHours = 10
        gorr = "=((prod - sales) * 5),250,%.02,300,%.03,400,%.04,500,%.05,0,%.06"
        self.assertEqual(pr.get_gorr_calc_type(m, gorr, calc),
                         ('%.05', 'Result =((prod - sales) * 5); =((200 - 100) * 5); =500.0 is > 400.0 and <= 500.0;'))
        m.ProdVol = 10000
        m.SalesVol = 10000
        m.ProdHours = 4
        self.assertEqual(pr.get_gorr_calc_type(m, gorr, calc),
                         ('%.02', 'Result =((prod - sales) * 5); =((10000 - 10000) * 5); =0.0;'))

        m.ProdVol = 200
        m.SalesVol = 100
        m.ProdHours = 10
        gorr = "=((prod - sales) * 5),250,$=(sales * price * .1),0,$=(sales * price * .2)"
        self.assertEqual(pr.get_gorr_calc_type(m, gorr, calc),
                         ('$=(sales * price * .2)',
                          'Result =((prod - sales) * 5); =((200 - 100) * 5); =500.0 is > 250.0;'))

    def test_calc_gorr(self):

        pr = ProcessRoyalties()
        leaserm = DataStructure()
        calc = DataStructure()
        calc_specific = DataStructure()
        monthly = DataStructure()

        monthly.Product = 'OIL'
        monthly.ProdVol = 100.0
        monthly.ProdHours = 10.0
        monthly.TransRate = .1234
        monthly.GCARate = 10.00

        leaserm.GorrTrans = 'prod'
        leaserm.GorrGCA = 'prod'

        calc.PEFNInterest = .6
        calc.RTPInterest = .25
        calc.RoyaltyPrice = 200.0
        calc.GorrTransValue = 0.0
        # calc.GorrRoyaltyValue = 0.0
        calc.RoyaltyBasedOnVol = 100
        calc.GorrMessage = None
        calc.GorrRoyaltyRate = 0.0
        calc_specific.GorrBaseRoyalty = 0.0
        calc.GorrGrossRoyaltyValue = 0.0
        calc_specific.GorrTransValue = 0.0
        calc.GorrNetRoyaltyValue = 0.0
        calc_specific.GorrRoyaltyGrossMessage = None
        calc_specific.GorrTransMessage = None
        calc_specific.GorrNetRoyaltyMessage = None
        calc_specific.GorrGCAMessage = None

        calc_specific.WellValueForRoyalty = 1000.00
        calc_specific.GorrGCAValue = 0.0

        leaserm.OilGorr = "fixed,0,%.02"
        pr.calc_gorr(leaserm, monthly, calc, calc_specific)
        self.assertEqual(.02, calc.GorrRoyaltyRate)
        self.assertEqual(20.00, calc_specific.GorrBaseRoyalty)
        self.assertEqual(3.00, calc.GorrGrossRoyaltyValue)
        self.assertEqual(.04, calc_specific.GorrTransValue)
        self.assertEqual(2.96, calc.GorrNetRoyaltyValue)
        self.assertEqual("fixed; for a Royalty Rate of 2.000000%", calc.GorrMessage)
        self.assertEqual("$ GORR = GORR % * Well Value * PE FN% * RP%;"
                         "$ GORR = 2.000000% * $1,000.00 * 60.000000% * 25.000000%;"
                         "$ GORR = $3.00", calc_specific.GorrRoyaltyGrossMessage)
        self.assertEqual("GORR Trans = Prod Vol * Trans Rate * GORR % * PE FN% * RP %;"
                         "GORR Trans = 100.00 * 0.123400 * 2.000000% * 60.000000% * 25.000000%;"
                         "GORR Trans = $0.04;", calc_specific.GorrTransMessage)
        print('====', calc_specific.GorrNetRoyaltyMessage, '====')
        self.assertEqual('GORR Net Royalty = GORR Royalty Value - Trans;'
                         'GORR Net Royalty = $3.00 - $0.04;'
                         'GORR Net Royalty = $2.96;', calc_specific.GorrNetRoyaltyMessage)

        leaserm.OilGorr = "fixed,0,$500.02"
        pr.calc_gorr(leaserm, monthly, calc, calc_specific)
        self.assertEqual(0.50002, calc.GorrRoyaltyRate)
        self.assertEqual(500.02, calc_specific.GorrBaseRoyalty)
        self.assertEqual(75.00, calc.GorrGrossRoyaltyValue)
        self.assertEqual(.93, calc_specific.GorrTransValue)
        self.assertEqual(74.07, calc.GorrNetRoyaltyValue)
        self.assertEqual("fixed;", calc.GorrMessage)
        self.assertEqual("$ GORR = Base Royalty * PE FN% * RP%;"
                         "$ GORR = $500.02 * 60.000000% * 25.000000%;"
                         "$ GORR = $75.00", calc_specific.GorrRoyaltyGrossMessage)
        self.assertEqual("GORR Trans = Prod Vol * Trans Rate * GORR % * PE FN% * RP %;"
                         "GORR Trans = 100.00 * 0.123400 * 50.002000% * 60.000000% * 25.000000%;"
                         "GORR Trans = $0.93;", calc_specific.GorrTransMessage)
        self.assertEqual('GORR Net Royalty = GORR Royalty Value - Trans;'
                         'GORR Net Royalty = $75.00 - $0.93;'
                         'GORR Net Royalty = $74.07;', calc_specific.GorrNetRoyaltyMessage)

        monthly.ProdVol = 100.0
        monthly.SalesVol = 90.0
        leaserm.OilGorr = "fixed,0,$=((prod - sales) * 100)"
        pr.calc_gorr(leaserm, monthly, calc, calc_specific)
        self.assertEqual(1.0, calc.GorrRoyaltyRate)
        self.assertEqual(1000.00, calc_specific.GorrBaseRoyalty)
        self.assertEqual(150.00, calc.GorrGrossRoyaltyValue)
        self.assertEqual(1.85, calc_specific.GorrTransValue)
        self.assertEqual(148.15, calc.GorrNetRoyaltyValue)
        self.assertEqual("fixed; "
                         "$=((prod - sales) * 100); "
                         "$=((100.0 - 90.0) * 100); "
                         "=1000.0;", calc.GorrMessage)
        self.assertEqual("$ GORR = Base Royalty * PE FN% * RP%;"
                         "$ GORR = $1,000.00 * 60.000000% * 25.000000%;"
                         "$ GORR = $150.00", calc_specific.GorrRoyaltyGrossMessage)
        self.assertEqual("GORR Trans = Prod Vol * Trans Rate * GORR % * PE FN% * RP %;"
                         "GORR Trans = 100.00 * 0.123400 * 100.000000% * 60.000000% * 25.000000%;"
                         "GORR Trans = $1.85;", calc_specific.GorrTransMessage)
        self.assertEqual('GORR Net Royalty = GORR Royalty Value - Trans;'
                         'GORR Net Royalty = $150.00 - $1.85;'
                         'GORR Net Royalty = $148.15;', calc_specific.GorrNetRoyaltyMessage)

        leaserm.OilGorr = '=(royalty_price),' \
                          '7.5,$=(.15 * prod * royalty_price),' \
                          '0,$=(0.15 * (7.50 * prod) + 0.25 * ((royalty_price - 7.50) * prod))'
        monthly.ProdVol = 100.0
        calc.RoyaltyPrice = 200.0
        pr.calc_gorr(leaserm, monthly, calc, calc_specific)
        self.assertEqual(4.925, calc.GorrRoyaltyRate)
        self.assertEqual(4925.00, calc_specific.GorrBaseRoyalty)
        self.assertEqual(738.75, calc.GorrGrossRoyaltyValue)
        self.assertEqual(9.12, calc_specific.GorrTransValue)
        self.assertEqual("Result =(royalty_price); "
                         "=(200.0); "
                         "=200.0 is > 7.5; "
                         "$=(0.15 * (7.50 * prod) + 0.25 * ((royalty_price - 7.50) * prod)); "
                         "$=(0.15 * (7.50 * 100.0) + 0.25 * ((200.0 - 7.50) * 100.0)); "
                         "=4925.0;",
                         calc.GorrMessage)
        self.assertEqual("$ GORR = Base Royalty * PE FN% * RP%;"
                         "$ GORR = $4,925.00 * 60.000000% * 25.000000%;"
                         "$ GORR = $738.75", calc_specific.GorrRoyaltyGrossMessage)
        self.assertEqual("GORR Trans = Prod Vol * Trans Rate * GORR % * PE FN% * RP %;"
                         "GORR Trans = 100.00 * 0.123400 * 492.500000% * 60.000000% * 25.000000%;"
                         "GORR Trans = $9.12;", calc_specific.GorrTransMessage)
        self.assertEqual('GORR Net Royalty = GORR Royalty Value - Trans;'
                         'GORR Net Royalty = $738.75 - $9.12;'
                         'GORR Net Royalty = $729.63;', calc_specific.GorrNetRoyaltyMessage)

        monthly.Product = 'GAS'
        leaserm.GasGorr = "fixed,0,$500.02"
        pr.calc_gorr(leaserm, monthly, calc, calc_specific)
        self.assertEqual(0.50002, calc.GorrRoyaltyRate)
        self.assertEqual(500.02, calc_specific.GorrBaseRoyalty)
        self.assertEqual(75.00, calc.GorrGrossRoyaltyValue)
        self.assertEqual(0.0, calc_specific.GorrTransValue)
        self.assertEqual(37.50, calc_specific.GorrGCAValue)
        self.assertEqual(37.50, calc.GorrNetRoyaltyValue)
        self.assertEqual("fixed;", calc.GorrMessage)
        self.assertEqual("$ GORR = Base Royalty * PE FN% * RP%;"
                         "$ GORR = $500.02 * 60.000000% * 25.000000%;"
                         "$ GORR = $75.00", calc_specific.GorrRoyaltyGrossMessage)
        self.assertEqual("GORR GCA = Prod Vol * GCA Rate * GORR % * PE FN% * RP %;"
                         "GORR GCA = 100.00 * 10.000000 * 50.002000% * 60.000000% * 25.000000%;"
                         "GORR GCA = $75.00;"
                         "GCA > 50% of Royalty therefore GCA = $37.50;", calc_specific.GorrGCAMessage)
        self.assertEqual('GORR Net Royalty = GORR Royalty Value - GCA;'
                         'GORR Net Royalty = $75.00 - $37.50;'
                         'GORR Net Royalty = $37.50;', calc_specific.GorrNetRoyaltyMessage)

    def test_calc_royalties(self):
        dbu = DatabaseUtilities()
        dbu.delete_all_tables()
        dbu.create_some_test_econoil()
        dbu.create_some_test_econgas()

        pr = ProcessRoyalties()
        royalty = DataStructure()
        monthly = DataStructure()
        well = DataStructure()
        calc = DataStructure()
        calc_specific = DataStructure()

        monthly.Product = 'OIL'
        monthly.ProdMonth = 201501
        monthly.ProdVol = 100
        monthly.SalesVol = 90
        monthly.GJ = 1000
        monthly.ProdHours = 744
        monthly.SalesPrice = 210.0
        monthly.GCARate = 9.0
        royalty.RoyaltyScheme = 'SKProvCrownVar'
        royalty.OverrideRoyaltyClassification = None
        royalty.OilValueBasedOn = None
        royalty.GasValueBasedOn = None
        royalty.ProductsValueBasedOn = None
        royalty.OilPriceBasedOn = None
        royalty.GasPriceBasedOn = None
        royalty.ProductsPriceBasedOn = None
        royalty.CrownModifier = None
        royalty.MinRoyaltyRate = None
        royalty.CrownMultiplier = 1.0
        royalty.MinRoyaltyDollar = None
        royalty.BaseTrans = None
        royalty.GorrTrans = None
        royalty.OilRoyaltyBasedOn = "prod"
        royalty.GasRoyaltyBasedOn = "sales"
        royalty.ProductsRoyaltyBasedOn = "gj"
        royalty.BaseGCA = 'sales'
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
        calc.BaseGCAValue = 0.0

        pr.calc_royalties(well, royalty, monthly, calc, calc_specific)

        royalty.RoyaltyScheme = 'IOGR1995'
        pr.calc_royalties(well, royalty, monthly, calc, calc_specific)

        royalty.RoyaltyScheme = 'IOGR1995,GORR'
        royalty.OilGorr = "fixed,0,%.02"
        pr.calc_royalties(well, royalty, monthly, calc, calc_specific)

        monthly.Product = 'GAS'
        royalty.RoyaltyScheme = 'IOGR1995'
        royalty.GasGorr = None
        royalty.GCADeducted = 'N'
        pr.calc_royalties(well, royalty, monthly, calc, calc_specific)

        monthly.Product = 'GAS'
        royalty.RoyaltyScheme = 'SKProvCrownVar'
        royalty.GasGorr = None
        calc.RoyaltyVolume = 10.5
        monthly.GCARate = 1.15
        royalty.BaseGCA = ''
        well.WellType = 'Gas'
        well.RoyaltyClassification = 'New'
        pr.calc_royalties(well, royalty, monthly, calc, calc_specific)

        monthly.Product = 'PEN'
        royalty.RoyaltyScheme = 'IOGR1995'
        pr.calc_royalties(well, royalty, monthly, calc, calc_specific)

        monthly.Product = 'SUL'
        royalty.RoyaltyScheme = 'IOGR1995'
        pr.calc_royalties(well, royalty, monthly, calc, calc_specific)

        monthly.Product = 'OIL'
        royalty.RoyaltyScheme = 'Bad One'
        self.assertRaises(AppError, pr.calc_royalties, well, royalty, monthly, calc, calc_specific)

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
        self.assertEqual(msg[:83],
                         '"sqlite_database.select1 should have only found 1, but we found 0 in table: RTPInfo')

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

    def test_determine_royalty_based_on(self):

        pr = ProcessRoyalties()

        leaserm = DataStructure()
        calc = DataStructure()

        monthly = DataStructure()
        monthly.ProdVol = 100.0
        monthly.SalesVol = 90.0
        monthly.GJ = 1000.0

        leaserm.OilRoyaltyBasedOn = None
        leaserm.GasRoyaltyBasedOn = None
        leaserm.ProductsRoyaltyBasedOn = None
        monthly.Product = "OIL"
        pr.determine_royalty_based_on(leaserm, monthly, calc)
        self.assertEqual("Prod Vol", calc.RoyaltyBasedOn)
        self.assertEqual(100.0, calc.RoyaltyBasedOnVol)

        leaserm.OilRoyaltyBasedOn = "prod"
        leaserm.GasRoyaltyBasedOn = "sales"
        leaserm.ProductsRoyaltyBasedOn = "gj"

        calc.RoyaltyBasedOn = None
        calc.RoyaltyBasedOnVol = None

        monthly.Product = "OIL"
        pr.determine_royalty_based_on(leaserm, monthly, calc)
        self.assertEqual("Prod Vol", calc.RoyaltyBasedOn)
        self.assertEqual(100.0, calc.RoyaltyBasedOnVol)

        monthly.Product = "GAS"
        pr.determine_royalty_based_on(leaserm, monthly, calc)
        self.assertEqual("Sales Vol", calc.RoyaltyBasedOn)
        self.assertEqual(90.0, calc.RoyaltyBasedOnVol)

        monthly.Product = "BUT"
        pr.determine_royalty_based_on(leaserm, monthly, calc)
        self.assertEqual("GJs", calc.RoyaltyBasedOn)
        self.assertEqual(1000.0, calc.RoyaltyBasedOnVol)

        leaserm.ProductsRoyaltyBasedOn = "stuff"
        monthly.Product = "BUT"
        pr.determine_royalty_based_on(leaserm, monthly, calc)
        self.assertEqual("Prod Vol", calc.RoyaltyBasedOn)
        self.assertEqual(100.0, calc.RoyaltyBasedOnVol)

    def test_calc_deduction(self):

        pr = ProcessRoyalties()
        monthly = DataStructure()
        calc = DataStructure()

        monthly.ProdVol = 100.0
        monthly.SalesVol = 90.0
        monthly.TransRate = 12.34
        monthly.GCARate = 23.45

        calc.PEFNInterest = .6
        calc.RTPInterest = .9

        self.assertRaises(AppError, pr.calc_deduction, "Base", "GCA", "xxsales", 'CR %', .30, 1000, monthly, calc)

        self.assertRaises(AppError, pr.calc_deduction, "Base", "GCAs", "sales", 'CR %', .30, 1000, monthly, calc)

        monthly.GCARate = None
        self.assertEqual((0.0, "Base GCA = Sales Vol * GCA Rate * CR % * PE FN% * RP %;"
                               "Base GCA = 90.00 * 0.000000 * 30.000000% * 60.000000% * 90.000000%;"
                               "Base GCA = $0.00;"),
                         pr.calc_deduction("Base", "GCA", "sales", 'CR %', .30, 1000, monthly, calc))

        monthly.GCARate = ''
        self.assertEqual((0.0, "Base GCA = Sales Vol * GCA Rate * CR % * PE FN% * RP %;"
                               "Base GCA = 90.00 * 0.000000 * 30.000000% * 60.000000% * 90.000000%;"
                               "Base GCA = $0.00;"),
                         pr.calc_deduction("Base", "GCA", "sales", 'CR %', .30, 1000, monthly, calc))

        monthly.GCARate = 23.45
        self.assertEqual((0.0, ""), pr.calc_deduction("Base", "GCA", "     ", 'CR %', .30, 1000, monthly, calc))

        self.assertEqual((0.0, ""), pr.calc_deduction("Base", "GCA", None, 'CR %', .30, 1000, monthly, calc))

        monthly.GCARate = 0.0
        self.assertEqual((0.0, "Base GCA = Sales Vol * GCA Rate * CR % * PE FN% * RP %;"
                               "Base GCA = 90.00 * 0.000000 * 30.000000% * 60.000000% * 90.000000%;"
                               "Base GCA = $0.00;"),
                         pr.calc_deduction("Base", "GCA", "sales", 'CR %', .30, 1000, monthly, calc))

        monthly.GCARate = 23.45
        self.assertEqual((341.9, "Base GCA = Sales Vol * GCA Rate * CR % * PE FN% * RP %;"
                                 "Base GCA = 90.00 * 23.450000 * 30.000000% * 60.000000% * 90.000000%;"
                                 "Base GCA = $341.90;"),
                         pr.calc_deduction("Base", "GCA", "sales", 'CR %', .30, 1000, monthly, calc))

        self.assertEqual((250.00, "Base GCA = Sales Vol * GCA Rate * CR % * PE FN% * RP %;"
                                  "Base GCA = 90.00 * 23.450000 * 30.000000% * 60.000000% * 90.000000%;"
                                  "Base GCA = $341.90;"
                                  "GCA > 50% of Royalty therefore GCA = $250.00;"),
                         pr.calc_deduction("Base", "GCA", "sales", 'CR %', .30, 500, monthly, calc))

        self.assertEqual((379.89, "Base GCA = Prod Vol * GCA Rate * Eff CR % * PE FN% * RP %;"
                                  "Base GCA = 100.00 * 23.450000 * 30.000000% * 60.000000% * 90.000000%;"
                                  "Base GCA = $379.89;"),
                         pr.calc_deduction("Base", "GCA", "prod", 'Eff CR %', .30, 1000, monthly, calc))

        self.assertEqual((199.91, "Base Trans = Prod Vol * Trans Rate * Eff CR % * PE FN% * RP %;"
                                  "Base Trans = 100.00 * 12.340000 * 30.000000% * 60.000000% * 90.000000%;"
                                  "Base Trans = $199.91;"),
                         pr.calc_deduction("Base", "Trans", "prod", 'Eff CR %', .30, 1000, monthly, calc))

        monthly.TransRate = None
        self.assertEqual((179.98, "Base Trans = Prod Vol * Trans Rate * Eff CR % * PE FN% * RP %;"
                                  "Base Trans = 100.00 * 11.110000 * 30.000000% * 60.000000% * 90.000000%;"
                                  "Base Trans = $179.98;"),
                         pr.calc_deduction("Base", "Trans", "prod,11.11", 'Eff CR %', .30, 1000, monthly, calc))

        self.assertEqual((323.97, "Base Trans = Sales Vol * Trans Rate * Eff CR % * PE FN% * RP %;"
                                  "Base Trans = 90.00 * 22.220000 * 30.000000% * 60.000000% * 90.000000%;"
                                  "Base Trans = $323.97;"),
                         pr.calc_deduction("Base", "Trans", "sales,22.22", 'Eff CR %', .30, 1000, monthly, calc))

    def test_base_net_royalty(self):

        pr = ProcessRoyalties()

        calc = DataStructure()
        calc_sp = DataStructure()

        calc.BaseRoyaltyValue = 100.00
        calc.BaseGCAValue = 0.00
        calc.BaseTransValue = 0.00
        calc_sp.BaseNetRoyaltyMessage = None

        pr.calc_base_net_royalty(calc, calc_sp)
        self.assertEqual('', calc_sp.BaseNetRoyaltyMessage)

        calc.BaseGCAValue = 10.00
        pr.calc_base_net_royalty(calc, calc_sp)
        self.assertEqual('Base Net Royalty = Base Royalty Value - GCA;'
                         'Base Net Royalty = $100.00 - $10.00;'
                         'Base Net Royalty = $90.00;', calc_sp.BaseNetRoyaltyMessage)

        calc.BaseTransValue = 12.00
        pr.calc_base_net_royalty(calc, calc_sp)
        self.assertEqual('Base Net Royalty = Base Royalty Value - GCA - Trans;'
                         'Base Net Royalty = $100.00 - $10.00 - $12.00;'
                         'Base Net Royalty = $78.00;', calc_sp.BaseNetRoyaltyMessage)

    def test_number_formats(self):

        pr = ProcessRoyalties()
        self.assertEqual('$10.11', pr.fm_value(10.111))
        self.assertEqual('$10.12', pr.fm_value(10.115))
        self.assertEqual('$100.12', pr.fm_value(100.12))
        self.assertEqual('$1,000.12', pr.fm_value(1000.12))

        self.assertEqual('10.11', pr.fm_vol(10.111))
        self.assertEqual('10.12', pr.fm_vol(10.115))
        self.assertEqual('100.12', pr.fm_vol(100.12))
        self.assertEqual('1,000.12', pr.fm_vol(1000.12))

        self.assertEqual('100.000000%', pr.fm_percent(1.))
        self.assertEqual('12.345678%', pr.fm_percent(.12345678))
        self.assertEqual('12.345679%', pr.fm_percent(.123456789))
        self.assertEqual('1,011.100000%', pr.fm_percent(10.111))

        self.assertEqual('1.000000', pr.fm_rate(1.))
        self.assertEqual('0.123457', pr.fm_rate(.12345678))
        self.assertEqual('10.111000', pr.fm_rate(10.111))
