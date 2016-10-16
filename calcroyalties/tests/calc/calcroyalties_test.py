#!/bin/env python3

import unittest
from datetime import date
from datetime import datetime

import config
from src.database.data_structure import DataStructure
from src.calc.calcroyalties import ProcessRoyalties
from src.util.apperror import AppError
from tests.database.testhelper import TestHelper
from tests.database.sqlite_utilities_test import DatabaseUtilities


class DataObj(object):
    None


class TestSaskRoyaltyCalc(unittest.TestCase):

    def setUp(self):
        self.assertEqual(config.get_environment(), 'unittest') # Destructive Tests must run in unittest environment


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

    def test_calc_sask_oil_regulations_subsection2(self):
        """ subsection (2) """
        pr = ProcessRoyalties()
        self.assertEqual(pr.calc_sask_oil_regulation_subsection2(70), 7)
        self.assertEqual(pr.calc_sask_oil_regulation_subsection2(90), 10)
        self.assertEqual(pr.calc_sask_oil_regulation_subsection2(200), (24 + .26 * (200 - 160)))
        self.assertEqual(pr.calc_sask_oil_regulation_subsection2(2000), (24 + .26 * (2000 - 160)))
        return
    
    def test_calc_sask_oil_regulation_subsection3(self):
        """ subsection (3) """
        pr = ProcessRoyalties()
        self.assertEqual(pr.calc_sask_oil_regulation_subsection3(70), 7)
        self.assertEqual(pr.calc_sask_oil_regulation_subsection3(90), 10)
        self.assertEqual(pr.calc_sask_oil_regulation_subsection3(200), (24 + .26 * (200 - 160)))
        self.assertEqual(pr.calc_sask_oil_regulation_subsection3(2000), (189 + .4 * (2000 - 795)))
        return

    def test_determine_commencement_period(self):
        pr = ProcessRoyalties()
        self.assertEqual(pr.determine_commencement_period(201501, date(2014, 12, 1)), .08)
        self.assertEqual(pr.determine_commencement_period(201501, date(2014, 12, 31)), 0)
        self.assertEqual(pr.determine_commencement_period(201501, date(2014, 1, 1)), 1)
        self.assertEqual(pr.determine_commencement_period(201501, date(2010, 11, 30)), 4.09)
        self.assertEqual(pr.determine_commencement_period(201501, date(2010, 1, 1)), 5)
        self.assertEqual(pr.determine_commencement_period(201501, date(2010, 1, 31)), 4.92)
        self.assertEqual(pr.determine_commencement_period(201501, date(2010, 1, 1)), 5.0)
        self.assertEqual(pr.determine_commencement_period(None, None),5)
        self.assertEqual(pr.determine_commencement_period(201501, datetime(2003, 1, 1)), 12.01)
        return
    
    def test_calcSaskGasProvCrownRoyaltyRate(self):
        econStringData =  \
"""
CharMonth,ProdMonth,G4T_C,G4T_D,G4T_K,G4T_X,G3T_C,G3T_K,G3T_X,GNEW_C,GNEW_K,GNEW_X,GOLD_C,GOLD_K,GOLD_X
Sept.,201509,0.1185,2.96,24.39,1578,0.1434,33.10,1910,0.1593,36.77,2121,0.2062,47.59,2745
"""
        th = TestHelper()
        econGasData = DataStructure()
        th.load_object_csv_style(econGasData, econStringData)
        pr = ProcessRoyalties()
        royaltyCalc = DataStructure()

        self.assertEqual(pr.calc_sask_gas_prov_crown_royalty_rate(royaltyCalc, econGasData, 'Fourth Tier Gas', 0, 0, 'GasWells'), 0)
        self.assertEqual(pr.calc_sask_gas_prov_crown_royalty_rate(royaltyCalc, econGasData, 'Fourth Tier Gas', 30, 0, 'GasWells'), 0.595)
        self.assertEqual(pr.calc_sask_gas_prov_crown_royalty_rate(royaltyCalc, econGasData, 'Fourth Tier Gas', 200, 0, 'GasWells'), 16.5)

        self.assertEqual(pr.calc_sask_gas_prov_crown_royalty_rate(royaltyCalc, econGasData, 'Fourth Tier Gas', 0, 0, 'OilWells'), 0)
        self.assertEqual(pr.calc_sask_gas_prov_crown_royalty_rate(royaltyCalc, econGasData, 'Fourth Tier Gas', 220, 0, 'OilWells'), 17.217273)

        self.assertEqual(pr.calc_sask_gas_prov_crown_royalty_rate(royaltyCalc, econGasData, 'Third Tier Gas', 100, 0.75, None), 13.59)
        self.assertEqual(pr.calc_sask_gas_prov_crown_royalty_rate(royaltyCalc, econGasData, 'Third Tier Gas', 200, 1, None), 22.55)

        self.assertEqual(pr.calc_sask_gas_prov_crown_royalty_rate(royaltyCalc, econGasData, 'New Gas', 50, 2.25, None), 5.715)
        self.assertEqual(pr.calc_sask_gas_prov_crown_royalty_rate(royaltyCalc, econGasData, 'New Gas', 130, 0.75, None), 19.704615)

        self.assertEqual(pr.calc_sask_gas_prov_crown_royalty_rate(royaltyCalc, econGasData, 'Old Gas', 20, 1, None), 3.124)
        self.assertEqual(pr.calc_sask_gas_prov_crown_royalty_rate(royaltyCalc, econGasData, 'Old Gas', 150, 0.5, None), 28.79)

        self.assertRaises(AppError, pr.calc_sask_gas_prov_crown_royalty_rate, royaltyCalc, econGasData, 'Fourth Tier Gas', 20, 1, 'Bad String')
        self.assertRaises(AppError, pr.calc_sask_gas_prov_crown_royalty_rate, royaltyCalc, econGasData, 'Bad String', 20, 1, 'GasWells')



    def test_calcSaskOilProvCrownRoyaltyRate(self):
        econStringData = \
"""
CharMonth,ProdMonth,HOP,SOP,NOP,H4T_C,H4T_D,H4T_K,H4T_X,H3T_K,H3T_X,HNEW_K,HNEW_X,SW4T_C,SW4T_D,SW4T_K,SW4T_X,SW3T_K,SW3T_X,SWNEW_K,SWNEW_X,O4T_C,O4T_D,O4T_K,O4T_X,O3T_K,O3T_X,ONEW_K,ONEW_X,OOLD_K,OOLD_X
Sept.,201509,162,210,276,0.0841,2.1,20.81,1561,20.46,472,26.48,611,0.1045,2.61,25.85,1939,31.57,729,38.54,890,0.1209,3.02,29.91,2243,36.08,833,40.79,941,52.61,1214
"""
        # All this work so we don't need to read from the database. It's a way better test.
        econ_oil_data = DataStructure()
        th = TestHelper()
        royalty_calc = DataStructure()

        th.load_object_csv_style(econ_oil_data, econStringData)
              
        pr = ProcessRoyalties()

        self.assertEqual(pr.calc_sask_oil_prov_crown_royalty_rate(royalty_calc, econ_oil_data, 'Fourth Tier Oil', 'Heavy', 24, 0), 0)
        self.assertEqual(pr.calc_sask_oil_prov_crown_royalty_rate(royalty_calc, econ_oil_data, 'Fourth Tier Oil', 'Heavy', 100, 0), .0631)
        self.assertEqual(pr.calc_sask_oil_prov_crown_royalty_rate(royalty_calc, econ_oil_data, 'Fourth Tier Oil', 'Southwest', 100, 0), .0784)
        self.assertEqual(pr.calc_sask_oil_prov_crown_royalty_rate(royalty_calc, econ_oil_data, 'Fourth Tier Oil', 'Other', 130, 0), .12697)
        self.assertEqual(pr.calc_sask_oil_prov_crown_royalty_rate(royalty_calc, econ_oil_data, 'Fourth Tier Oil', 'Heavy', 140, 0), .0966)
        self.assertEqual(pr.calc_sask_oil_prov_crown_royalty_rate(royalty_calc, econ_oil_data, 'Fourth Tier Oil', 'Southwest', 136.3, 0), .11624028)
        self.assertEqual(pr.calc_sask_oil_prov_crown_royalty_rate(royalty_calc, econ_oil_data, 'Fourth Tier Oil', 'Other', 150, 0), .14956667)
        self.assertEqual(pr.calc_sask_oil_prov_crown_royalty_rate(royalty_calc, econ_oil_data, 'Fourth Tier Oil', 'Other', 0, 0), 0)
        self.assertRaises(AppError, pr.calc_sask_oil_prov_crown_royalty_rate, royalty_calc, econ_oil_data, 'Fourth Tier Oil', 'BadString', 120, 0)
        self.assertRaises(AppError, pr.calc_sask_oil_prov_crown_royalty_rate, royalty_calc, econ_oil_data, 'Fourth Tier Oil', 'BadString', 140, 0)
        self.assertRaises(AppError, pr.calc_sask_oil_prov_crown_royalty_rate, royalty_calc, econ_oil_data, 'Bad String', 'Heavy', 120, 0)
        self.assertRaises(AppError, pr.calc_sask_oil_prov_crown_royalty_rate, royalty_calc, econ_oil_data, 'Bad String', 'Southwest', 120, 0)
        self.assertRaises(AppError, pr.calc_sask_oil_prov_crown_royalty_rate, royalty_calc, econ_oil_data, 'Bad String', 'Other', 120, 0)

        self.assertEqual(pr.calc_sask_oil_prov_crown_royalty_rate(royalty_calc, econ_oil_data, 'Third Tier Oil', 'Heavy', 100, 0.0075), .1499)
        self.assertAlmostEqual(pr.calc_sask_oil_prov_crown_royalty_rate(royalty_calc, econ_oil_data, 'New Oil', 'Heavy', 100, 0.0075), .19620000)
        self.assertEqual(pr.calc_sask_oil_prov_crown_royalty_rate(royalty_calc, econ_oil_data, 'New Oil', 'Heavy', 0, 0), 0)
        self.assertRaises(AppError, pr.calc_sask_oil_prov_crown_royalty_rate, royalty_calc, econ_oil_data, 'Third Tier Oil', 'Bad String', 120, 0)

        self.assertEqual(pr.calc_sask_oil_prov_crown_royalty_rate(royalty_calc, econ_oil_data, 'Third Tier Oil', 'Southwest', 120, 0), .25495000)
        self.assertEqual(pr.calc_sask_oil_prov_crown_royalty_rate(royalty_calc, econ_oil_data, 'New Oil', 'Southwest', 130, 0.0075), .30943846)
        self.assertEqual(pr.calc_sask_oil_prov_crown_royalty_rate(royalty_calc, econ_oil_data, 'New Oil', 'Southwest', 0, 0), 0)
        self.assertRaises(AppError, pr.calc_sask_oil_prov_crown_royalty_rate, royalty_calc, econ_oil_data, 'New Oil', 'Bad String', 120, 0)

        self.assertEqual(pr.calc_sask_oil_prov_crown_royalty_rate(royalty_calc, econ_oil_data, 'Third Tier Oil', 'Other', 120, .0225), .26888333)
        self.assertEqual(pr.calc_sask_oil_prov_crown_royalty_rate(royalty_calc, econ_oil_data, 'New Oil', 'Other', 110, 0), .32235455)
        self.assertEqual(pr.calc_sask_oil_prov_crown_royalty_rate(royalty_calc, econ_oil_data, 'Old Oil', 'Other', 100, 0.0075), .39720000)
        self.assertEqual(pr.calc_sask_oil_prov_crown_royalty_rate(royalty_calc, econ_oil_data, 'Old Oil', 'Other', 0, 0), 0)
        self.assertRaises(AppError, pr.calc_sask_oil_prov_crown_royalty_rate, royalty_calc, econ_oil_data, 'Old Oil', 'Bad String', 120, 0)

        self.assertRaises(AppError, pr.calc_sask_oil_prov_crown_royalty_rate, royalty_calc, econ_oil_data, 'Old Oil', 'Heavy', 120, 0)
        self.assertRaises(AppError, pr.calc_sask_oil_prov_crown_royalty_rate, royalty_calc, econ_oil_data, 'Old Oil', 'Southwest', 120, 0)

        return

    """
    def test_calcSaskOilProvCrownRoyaltyVolumeValue(self):
        royStringData = \

ProvCrownUsedRoyaltyRate, CrownMultiplier, PEFNInterest, MinRoyalty, RoyaltyPrice
6.31, 1, 1, 3.21,

        royOilData = DataStructure()
        th = TestHelper()
        royaltyCalc = DataStructure()

        th.load_object_csv_style(royOilData, royStringData)
        print('ProvCrownUsedRoyaltyRate:',royOilData.ProvCrownUsedRoyaltyRate)
        print('CrownMultiplier:',royOilData.CrownMultiplier)
        print(vars(royOilData))
        print(vars(royOilData).values())

        pr = ProcessRoyalties()
    """

    def test_process_one(self):
        pr = ProcessRoyalties()
        well_id = 6
        prod_month = 201501
        product = "Oil"
        well = DataStructure()
        well_lease_link_array = DataStructure()
        self.assertRaises(AppError, pr.process_one, well_id, prod_month, product)

    """
    def calc_royalties(self):
        pr = ProcessRoyalties()
        well, royalty, lease, calc, monthly, well_lease_link
        well = DataStructure()
        royalty = DataStructure()
        lease = DataStructure()
        calc = DataStructure()
        monthly = DataStructure()
        well_lease_link = DataStructure()
        monthly.Product = 'Oil'
        royalty.RoyaltyScheme = 'IOGR1995'
        pr.calc_sask_oil_iogr1995(datetime(2015, 4, 2), "SaskWellHead", 0.25, 3, monthly, calc)
        self.assertEqual(calc.IOGR1995RoyaltyValue,1990.11)


        ??? How do i do this??

        royalty.RoyaltyScheme = 'BadString'
        well.WellID = 2001010202
        self.assertRaises(AppError, well, royalty, lease, calc, monthly, well_lease_link)
    """

    def test_calc_sask_oil_prov_crown_royalty_volume_value(self):
        pr = ProcessRoyalties()
        calc = DataStructure()
        m = DataStructure()
        royalty = DataStructure()
        m.ProdVol = 100
        royalty.MinRoyaltyRate = 0.0
        royalty.MinRoyaltyDollar = 0.0
        royalty.CrownMultiplier = 1
        royalty.ValuationMethod = 'ActSales'
        calc.ProvCrownUsedRoyaltyRate = .25
        calc.ProvCrownRoyaltyRate = .25
        calc.RoyaltyPrice = 210
        m.WellHeadPrice = 221.123456
        m.TransRate = 2.123455
        m.ProcessingRate = 0.123455

        pr.calc_sask_oil_prov_crown_royalty_volume_value(m, 1, royalty, calc)
        self.assertEqual(calc.ProvCrownRoyaltyVolume, 25.0)
        self.assertEqual(calc.ProvCrownRoyaltyValue, 5584.26)

        calc.ProvCrownRoyaltyRate = -.01
        calc.ProvCrownUsedRoyaltyRate = -.01
        royalty.MinRoyaltyRate = None

        pr.calc_sask_oil_prov_crown_royalty_volume_value(m, 1, royalty, calc)

        self.assertEqual(calc.ProvCrownUsedRoyaltyRate, 0)

        calc.ProvCrownRoyaltyRate = -.01
        calc.ProvCrownUsedRoyaltyRate = -.01
        royalty.MinRoyaltyRate = .02
        pr.calc_sask_oil_prov_crown_royalty_volume_value(m, 1, royalty, calc)
        self.assertEqual(calc.ProvCrownUsedRoyaltyRate, .02)

        self.assertEqual(calc.ProvCrownRoyaltyValue, 446.74)
        royalty.MinRoyaltyDollar = 500.0
        pr.calc_sask_oil_prov_crown_royalty_volume_value(m, 1, royalty, calc)
        self.assertEqual(calc.ProvCrownRoyaltyValue, 500.0)



        # self.assertEqual(pr.calcSaskOilProvCrownRoyaltyVolumeValue(m, 1, royalty, calc), (20.0, 2000.0))
        # self.assertEqual(pr.calcSaskOilProvCrownRoyaltyVolumeValue(m, 2, royalty, calc), (5, 500.0))
        # self.assertEqual(pr.calcSaskOilProvCrownRoyaltyVolumeValue(2, m ,1, None, 1,100, calc, 'ActSales'), (2.0, 200.0))
        # self.assertEqual(pr.calcSaskOilProvCrownRoyaltyVolumeValue(10, m ,1, 2, 1,120, calc, 'ActSales'), (12, 1440.0))


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
        pr.calc_sask_oil_iogr1995(datetime(2015, 1, 1), "SaskWellHead", 1.2, 0.25, m, calc)
        self.assertEqual(calc.IOGR1995RoyaltyValue,464.36)
        self.assertEqual(calc.CommencementPeriod,0)
        self.assertEqual(calc.IOGR1995RoyaltyVolume,7)
        self.assertEqual(calc.RoyaltyPrice,221.123456)

        m.ProdVol = 100
        pr.calc_sask_oil_iogr1995(datetime(2015, 4, 2), "SaskWellHead", 0.25, 3, m, calc)
        self.assertEqual(calc.IOGR1995RoyaltyValue,1990.11)
        m.ProdVol = 170
        pr.calc_sask_oil_iogr1995(datetime(2015, 5, 1), "SaskWellHead", 1, 1, m, calc)
        self.assertEqual(calc.IOGR1995RoyaltyValue, 5881.88)
        m.ProdVol = 79.9
        pr.calc_sask_oil_iogr1995(datetime(2010, 1, 1), "SaskWellHead", 3, 2, m, calc)
        self.assertEqual(calc.IOGR1995RoyaltyValue,10600.66)
        m.ProdVol = 150
        pr.calc_sask_oil_iogr1995(datetime(2009, 7, 3), "SaskWellHead", 2, 4, m, calc)
        self.assertEqual(calc.IOGR1995RoyaltyValue, 38917.73)
        m.ProdVol = 500
        pr.calc_sask_oil_iogr1995(datetime(2007, 8, 2), "SaskWellHead", 1, 5, m, calc)
        self.assertEqual(calc.IOGR1995RoyaltyValue, 124271.38)
        m.ProdVol = 800
        pr.calc_sask_oil_iogr1995(datetime(2008, 9, 9), "SaskWellHead", 5, 0.1, m, calc)

        self.assertEqual(calc.IOGR1995RoyaltyValue, 21117.29)

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
        #write tests for ActSales



    def test_calcSaskOilRegulationSubsection2(self):
        pr = ProcessRoyalties()
        self.assertEqual(pr.calc_sask_oil_regulation_subsection2(70), 7)
        self.assertEqual(pr.calc_sask_oil_regulation_subsection2(100), 12)
        self.assertEqual(pr.calc_sask_oil_regulation_subsection2(170), 26.6)



    def test_calcSaskOilRegulationSubsection3(self):
        pr = ProcessRoyalties()
        self.assertAlmostEqual(pr.calc_sask_oil_regulation_subsection3(79.9), 7.99)
        self.assertEqual(pr.calc_sask_oil_regulation_subsection3(150), 22)
        self.assertEqual(pr.calc_sask_oil_regulation_subsection3(500), 112.4)
        self.assertEqual(pr.calc_sask_oil_regulation_subsection3(800), 191)

    def test_determineRoyaltyPrice(self):
        m = DataStructure()
        m.WellHeadPrice = 221.123456
        m.TransRate = 2.123455
        m.ProcessingRate = 0.123455

        pr = ProcessRoyalties()
        self.assertAlmostEqual(pr.determine_royalty_price('ActSales', m), 223.370366)

        m.WellHeadPrice = 225
        m.TransRate = 3
        m.ProcessingRate = 1

        self.assertAlmostEqual(pr.determine_royalty_price('ActSales', m), 229)


    def test_calcGorrPercent(self):
        pr = ProcessRoyalties()

        gorr = "bad string,0,2"
        self.assertRaises(AppError, pr.calc_gorr_percent, 400, 10, gorr)
        self.assertRaises(AppError, pr.calc_gorr_percent, None, 10, gorr)

        gorr = None,"0,2"
        self.assertRaises(AttributeError, pr.calc_gorr_percent, 400, 10, gorr)

        gorr = "dprod,250,.02,300,.03,400,.04,500,.05,0,.06"
        self.assertEqual(pr.calc_gorr_percent(600, 10, gorr), (.02, 'dprod = mprod / 30.5 days; 19.67 is > 0.0 and <= 250.0 for a RoyRate of 2.00%'))
        self.assertEqual(pr.calc_gorr_percent(8235, 3, gorr), (.03, 'dprod = mprod / 30.5 days; 270.00 is > 250.0 and <= 300.0 for a RoyRate of 3.00%'))
        self.assertEqual(pr.calc_gorr_percent(10065, 4, gorr), (.04, 'dprod = mprod / 30.5 days; 330.00 is > 300.0 and <= 400.0 for a RoyRate of 4.00%'))
        self.assertEqual(pr.calc_gorr_percent(13725, 5, gorr), (.05, 'dprod = mprod / 30.5 days; 450.00 is > 400.0 and <= 500.0 for a RoyRate of 5.00%'))

        self.assertRaises(TypeError, pr.calc_gorr_percent, None, 10, gorr)

        gorr = "mprod,250,.02,300,.03,400,.04,500,.05,0,.06"
        self.assertEqual(pr.calc_gorr_percent(200, 10, gorr), (.02, 'mprod = 200 is > 0.0 and <= 250.0 for a RoyRate of 2.00%'))
        self.assertEqual(pr.calc_gorr_percent(300, 4, gorr), (.03, 'mprod = 300 is > 250.0 and <= 300.0 for a RoyRate of 3.00%'))
        self.assertEqual(pr.calc_gorr_percent(350.6, 1, gorr), (.04, 'mprod = 350.6 is > 300.0 and <= 400.0 for a RoyRate of 4.00%'))
        self.assertEqual(pr.calc_gorr_percent(410, 2, gorr), (.05, 'mprod = 410 is > 400.0 and <= 500.0 for a RoyRate of 5.00%'))
        self.assertEqual(pr.calc_gorr_percent(10000, 17, gorr), (.06, 'mprod = 10000 is > 500.0 for a RoyRate of 6.00%'))

        gorr = "hprod,250,.02,300,.03,400,.04,500,.05,0,.06"
        self.assertEqual(pr.calc_gorr_percent(200, 10, gorr), (.02, 'hprod = mprod / hours; 20.00 is > 0.0 and <= 250.0 for a RoyRate of 2.00%'))

        gorr = "fixed,0,.02"
        self.assertEqual(pr.calc_gorr_percent(200, 10, gorr), (.02, 'fixed for a RoyRate of 2.00%'))
        self.assertEqual(pr.calc_gorr_percent(10000, 4, gorr), (.02, 'fixed for a RoyRate of 2.00%'))
        self.assertEqual(pr.calc_gorr_percent(None, 10, gorr), (.02, 'fixed for a RoyRate of 2.00%'))

    def test_calcSupplementaryRoyaltiesIOGR1995(self):
        reference_price = {'Pigeon Lake Indian': 24.04, 'Reserve no.138A': 25.37, 'Sawridge Indian': 25.13, 'Stony Plain Indian': 24.64}
        pr = ProcessRoyalties()
        calc = DataStructure()

        self.assertEqual(pr.calc_supplementary_royalties_iogr1995(3.5, 228, 80, 60, reference_price['Pigeon Lake Indian']), 2039.6)
        self.assertEqual(pr.calc_supplementary_royalties_iogr1995(5, 200, 90, 40, reference_price['Reserve no.138A']), 4365.75)
        self.assertEqual(pr.calc_supplementary_royalties_iogr1995(4, 221.123456, 100, 50, reference_price['Sawridge Indian']), 4899.84)
        self.assertEqual(pr.calc_supplementary_royalties_iogr1995(.2, 180, 80, 35, reference_price['Stony Plain Indian']), 3495.6)

        self.assertEqual(pr.calc_supplementary_royalties_iogr1995(6, 228, 80, 60, reference_price['Pigeon Lake Indian']), 2996.5)
        self.assertEqual(pr.calc_supplementary_royalties_iogr1995(5.5, 200, 90, 40, reference_price['Reserve no.138A']), 6391.38)
        self.assertEqual(pr.calc_supplementary_royalties_iogr1995(8, 221.123456, 100, 50, reference_price['Sawridge Indian']), 7192.5)
        self.assertEqual(pr.calc_supplementary_royalties_iogr1995(15, 180, 80, 35, reference_price['Stony Plain Indian']), 5101.88)

    def test_process_monthly(self):
        self.dbu = DatabaseUtilities()
        self.dbu.delete_all_tables()
        self.dbu.create_some_test_wells()
        self.dbu.create_some_test_royalties()
        self.dbu.create_some_test_leases()
        self.dbu.create_some_test_well_lease_link()
        self.dbu.create_some_test_monthly()
        self.dbu.create_some_test_econdata()
        self.dbu.create_calc()
        pr = ProcessRoyalties()
        pr.process_one(4, 201501, 'Oil')
