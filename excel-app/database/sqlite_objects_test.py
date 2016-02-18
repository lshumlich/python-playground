#!/bin/env python3

import unittest

import config
import database.sqlite_objects
from database.apperror import AppError


class Test(unittest.TestCase):

    def setUp(self):
        #Preparing the database
        self.dbi = config.get_database_instance()
        for table in self.dbi.get_table_names():
        	self.dbi.execute('DROP TABLE %s' % table)
        self.dbi.commit()
        self.do = database.sqlite_objects.DataObject()

    def execute_statement(self, statement):
        for line in statement.splitlines():
            self.dbi.execute(line)
        self.dbi.commit()

    def test_wells(self):
        statement = """
            CREATE TABLE Well ('WellId' int, 'UWI' text, 'Prov' text, 'WellType' text, 'LeaseType' text, 'LeaseID' int, 'RoyaltyClassification' text, 'Classification' text, 'SRC' int, 'IndianInterest' float, 'CommencementDate' date, 'ReferencePrice' int);
            INSERT INTO Well VALUES(1,'SKWI111062705025W300','SK','Oil','OL',1,'New Oil','Heavy',0,0.25,'2014-12-01 00:00:00',1);
            INSERT INTO Well VALUES(2,'SKWI112062705025W300','SK','Oil','OL',2,'Third Tier Oil','Southwest',0,0.95,'2014-12-01 00:00:00',1);
            INSERT INTO Well VALUES(3,'SKWI113062705025W300','SK','Oil','OL',3,'Fourth Tier Oil','Other',0,1.0,NULL,NULL);
            INSERT INTO Well VALUES(4,'SKWI114062705025W300','SK','Oil','OL',4,'Old Oil','Other',0,1.0,NULL,NULL);
        """
        self.execute_statement(statement)
        self.assertEqual(len(self.do.get_all_wells()), 4)
        self.assertEqual(self.do.get_well_by_id(2).WellId, 2)
        self.assertRaises(AppError, self.do.get_well_by_id, 99)
        self.assertIsNotNone(self.do.get_wells_by_lease(2))
        self.assertRaises(AppError, self.do.get_wells_by_lease, 666)

    def test_leases(self):
        statement = """
            CREATE TABLE Lease ('LeaseType' text, 'LeaseID' int, 'Prov' text, 'FNReserve' int, 'Lessor' int, 'Notes' text);            
            INSERT INTO Lease VALUES('OL',1,'SK',123,2345,NULL);
            INSERT INTO Lease VALUES('OL',2,'SK',123,2345,NULL);
            INSERT INTO Lease VALUES('OL',3,'SK',123,2345,NULL);
            INSERT INTO Lease VALUES('OL',4,'AB',123,2345,NULL);
        """
        self.execute_statement(statement)
        self.assertEqual(len(self.do.get_all_leases()), 4)
        self.assertIsNotNone(self.do.get_lease_by_id(3))
        self.assertEqual(self.do.get_lease_by_id(3).LeaseID, 3)
        self.assertRaises(AppError, self.do.get_lease_by_id, 99)

    def test_royalty_master(self):
        statement = """
            CREATE TABLE RoyaltyMaster ("LeaseType" text, "LeaseID" int, "RightsGranted" text, "RoyaltyScheme" text, "CrownMultiplier" float, "MinRoyalty" int, "ValuationMethod" text, "TruckingDeducted" text, "ProcessingDeducted" text, "Gorr" text, "Notes" text);            
            INSERT INTO RoyaltyMaster VALUES('OL',1,'All','SKProvCrownVar, GORR',1.2,50,'SaskWellHead','Y','Y','mprod,250,2,300,3,400,4,500,5,0,6',NULL);
            INSERT INTO RoyaltyMaster VALUES('OL',2,'All','SKProvCrownVar, GORR',1.1,25,'ActSales','Y',NULL,'dprod,250,2,300,3,400,4,500,5,0,6',NULL);
            INSERT INTO RoyaltyMaster VALUES('OL',3,'AllExB','SKProvCrownVar, GORR',0.9,NULL,'ActSales',NULL,'Y','fixed,0,2',NULL);
            INSERT INTO RoyaltyMaster VALUES('OL',4,'AllExB','SKProvCrownVar',1.25,NULL,'ActSales','Y','Y',NULL,NULL);        
        """
        self.execute_statement(statement)
        self.assertIsNotNone(self.do.get_royalty_master(1))
        self.assertEqual(self.do.get_royalty_master(4).RoyaltyScheme, 'SKProvCrownVar')
        self.assertRaises(AppError, self.do.get_royalty_master, 555)

    def test_monthly(self):
        statement = """
            CREATE TABLE Monthly ("Row" int, "ExtractMonth" date, "ProdMonth" int, "WellId" int, "Product" text, "AmendNo" int, "ProdHours" int, "ProdVol" int, "TransPrice" float, "WellHeadPrice" float, "TransRate" float, "ProcessingRate" float);
            INSERT INTO Monthly VALUES(1,'2015-09-29 00:00:00',201501,6,'Oil',2,740,100,2.2,221.123456,2.123455,0.123455);
            INSERT INTO Monthly VALUES(2,'2015-09-29 00:00:00',201501,7,'Oil',2,740,100,2.2,221.123456,2.123455,0.123455);
            INSERT INTO Monthly VALUES(1,'2015-09-29 00:00:00',201501,2000,'Oil',2,740,20,2.2,221.123456,2.123455,0.123455);
            INSERT INTO Monthly VALUES(2,'2015-09-29 00:00:00',201501,2000,'Oil',2,740,100,2.2,221.123456,2.123455,0.123455);
        """
        self.execute_statement(statement)
        # not sure how to test iterator get_monthly_data() at the moment
        self.assertEqual(self.do.get_monthly_by_well(6).WellId, 6)
        self.assertRaises(AppError, self.do.get_monthly_by_well, 555)
        self.assertEqual(self.do.get_monthly_by_well_prodmonth_product(7, 201501, 'Oil').WellId, 7)
        self.assertRaises(AppError, self.do.get_monthly_by_well_prodmonth_product, 7, 201501, 'Tar')

    def test_calc(self):
        statement = """
            CREATE TABLE Calc ("ProdMonth" int, "WellId" int, "K" int, "X" int, "C" int, "D" int, "RoyaltyPrice" float, "RoyaltyVolume" int, "ProvCrownRoyaltyRate" int, "ProvCrownUsedRoyaltyRate" int, "IOGR1995RoyaltyRate" int, "GorrRoyaltyRate" int, "ProvCrownRoyaltyVolume" int, "GorrRoyaltyVolume" int, "IOGR1995RoyaltyVolume" int, "ProvCrownRoyaltyValue" int, "IOGR1995RoyaltyValue" float, "GorrRoyaltyValue" float, "RoyaltyValuePreDeductions" float, "RoyaltyTransportation" int, "RoyaltyProcessing" int, "RoyaltyDeductions" int, "RoyaltyValue" float, "CommencementPeriod" float, "Message" text, "GorrMessage" text);
            INSERT INTO Calc VALUES(201501,6,0,0,0,0,223.370366,14,0,0,0,2,0,2,12,0,2680.44,446.740732,3127.180732,0,0,0,3127.180732,0.08,NULL,'dprod = 0.135135 = 100 / 740 is between 0.0 - 250.0 for a RR of 2.0%');
            INSERT INTO Calc VALUES(201501,7,0,0,0,0,223.370366,14,0,0,0,2,0,2,12,0,2680.44,446.740732,3127.180732,0,0,0,3127.180732,0.08,NULL,'dprod = 0.135135 = 100 / 740 is between 0.0 - 250.0 for a RR of 2.0%');
            INSERT INTO Calc VALUES(201504,10,24.7,570,0,0,223.370366,16.15,19,19,0,0,16.15,0,0,3607.43,0.0,0.0,3607.43,0,0,0,3607.43,NULL,NULL,NULL);
            INSERT INTO Calc VALUES(201504,10,24.7,570,0,0,223.370366,16.15,19,19,0,0,16.15,0,0,3607.43,0.0,0.0,3607.43,0,0,0,3607.43,NULL,NULL,NULL);
        """
        self.execute_statement(statement)
        self.assertEqual(self.do.get_royalty_calc(201501, 6).WellId, 6)        
        self.assertRaises(AppError, self.do.get_royalty_calc, 200014, 10)

    def test_econ_oil_data(self):
        statement= """
            CREATE TABLE ECONData ("CharMonth" text, "ProdMonth" int, "HOP" int, "SOP" int, "NOP" int, "H4T_C" float, "H4T_D" float, "H4T_K" float, "H4T_X" int, "H3T_K" float, "H3T_X" int, "HNEW_K" float, "HNEW_X" int, "SW4T_C" float, "SW4T_D" float, "SW4T_K" float, "SW4T_X" int, "SW3T_K" float, "SW3T_X" int, "SWNEW_K" float, "SWNEW_X" int, "O4T_C" float, "O4T_D" float, "O4T_K" float, "O4T_X" int, "O3T_K" float, "O3T_X" int, "ONEW_K" float, "ONEW_X" int, "OOLD_K" float, "OOLD_X" int);
            INSERT INTO ECONData VALUES('Sept.',201509,162,210,276,0.0841,2.1,20.81,1561,20.46,472,26.48,611,0.1045,2.61,25.85,1939,31.57,729,38.54,890,0.1209,3.02,29.91,2243,36.08,833,40.79,941,52.61,1214);
            INSERT INTO ECONData VALUES('Aug.',201508,198,232,273,0.1003,2.51,24.81,1861,22.65,523,27.58,637,0.111,2.77,27.46,2060,32.89,759,39.2,905,0.1203,3.01,29.77,2233,35.98,830,40.74,940,52.55,1213);
            INSERT INTO ECONData VALUES('Feb.',201202,442,507,555,0.1405,3.51,34.77,2608,28.09,648,30.29,699,0.1447,3.62,35.81,2686,39.73,917,42.62,984,0.1472,3.68,36.42,2732,40.82,942,43.16,996,55.57,1283);
            INSERT INTO ECONData VALUES('Jan.',201201,487,537,581,0.1435,3.59,35.52,2664,28.5,658,30.5,704,0.1463,3.66,36.2,2715,40.05,924,42.78,987,0.1483,3.71,36.7,2753,41.02,947,43.26,998,55.7,1286);
            """
        self.execute_statement(statement)
        self.assertEqual(self.do.get_econ_oil_data(201509).ProdMonth, 201509)
        self.assertRaises(AppError, self.do.get_econ_oil_data, 202013)

    def test_universal_select(self):
        statement = """
            CREATE TABLE Well ('WellId' int, 'UWI' text, 'Prov' text, 'WellType' text, 'LeaseType' text, 'LeaseID' int, 'RoyaltyClassification' text, 'Classification' text, 'SRC' int, 'IndianInterest' float, 'CommencementDate' date, 'ReferencePrice' int);
            INSERT INTO Well VALUES(1,'SKWI111062705025W300','SK','Oil','OL',1,'New Oil','Heavy',0,0.25,'2014-12-01 00:00:00',1);
            INSERT INTO Well VALUES(2,'SKWI112062705025W300','SK','Oil','OL',2,'Third Tier Oil','Southwest',0,0.95,'2014-12-01 00:00:00',1);
            INSERT INTO Well VALUES(3,'SKWI113062705025W300','SK','Oil','OL',3,'Fourth Tier Oil','Other',0,1.0,NULL,NULL);
            INSERT INTO Well VALUES(4,'SKWI114062705025W300','SK','Oil','OL',4,'Old Oil','Other',0,1.0,NULL,NULL);
            CREATE TABLE Lease ('LeaseType' text, 'LeaseID' int, 'Prov' text, 'FNReserve' int, 'Lessor' int, 'Notes' text);            
            INSERT INTO Lease VALUES('OL',1,'SK',123,2345,NULL);
            INSERT INTO Lease VALUES('OL',2,'SK',123,2345,NULL);
            INSERT INTO Lease VALUES('OL',3,'SK',123,2345,NULL);
            INSERT INTO Lease VALUES('OL',4,'AB',123,2345,NULL);            
        """
        self.execute_statement(statement)        
        self.assertIsNotNone(self.do.universal_select('Well', RoyaltyClassification='Old Oil'))
        self.assertEqual(len(self.do.universal_select('Well', Prov='SK', Classification='Other')), 2)
        self.assertEqual(len(self.do.universal_select('Well')), 4)
        self.assertRaises(AppError, self.do.universal_select, 'WrongTable')
        self.assertRaises(AppError, self.do.universal_select, 'Well', Foo='bar')
        self.assertEqual(len(self.do.universal_select('Lease')), 4)
        self.assertEqual(len(self.do.universal_select('Lease', Prov='SK')), 3)

if __name__ == '__main__':
    unittest.main()
