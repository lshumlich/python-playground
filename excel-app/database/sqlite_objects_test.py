#!/bin/env python3

import unittest

import config
import database.sqlite_objects


class Test(unittest.TestCase):

    def test_sqlite_objects(self):
        #Preparing the database
        dbi = config.get_database_instance()
        for table in dbi.get_table_names():
        	dbi.execute('DROP TABLE %s' % table)
        dbi.commit()
        do = database.sqlite_objects.DataObject()
        statement= """
			CREATE TABLE Well ('WellId' int, 'UWI' text, 'Prov' text, 'WellType' text, 'LeaseType' text, 'LeaseID' int, 'RoyaltyClassification' text, 'Classification' text, 'SRC' int, 'IndianInterest' float, 'CommencementDate' date, 'ReferencePrice' int);
			CREATE TABLE Lease ('LeaseType' text, 'LeaseID' int, 'Prov' text, 'FNReserve' int, 'Lessor' int, 'Notes' text);
			INSERT INTO Well VALUES(1,'SKWI111062705025W300','SK','Oil','OL',1,'New Oil','Heavy',0,0.25,'2014-12-01 00:00:00',1);
			INSERT INTO Well VALUES(2,'SKWI112062705025W300','SK','Oil','OL',2,'Third Tier Oil','Southwest',0,0.95,'2014-12-01 00:00:00',1);
			INSERT INTO Well VALUES(3,'SKWI113062705025W300','SK','Oil','OL',3,'Fourth Tier Oil','Other',0,1.0,NULL,NULL);
			INSERT INTO Well VALUES(4,'SKWI114062705025W300','SK','Oil','OL',4,'Old Oil','Other',0,1.0,NULL,NULL);
			INSERT INTO Lease VALUES('OL',1,'SK',123,2345,NULL);
			INSERT INTO Lease VALUES('OL',2,'SK',123,2345,NULL);
			INSERT INTO Lease VALUES('OL',3,'SK',123,2345,NULL);
			INSERT INTO Lease VALUES('OL',4,'AB',123,2345,NULL);
			"""
        for line in statement.splitlines():
        	dbi.execute(line)
        dbi.commit()

        #Testing the wells
        self.assertEqual(len(do.get_all_wells()), 4)
        self.assertEqual(len(do.get_well_by_id(2)), 1)
        self.assertEqual(do.get_well_by_id(2)[0].WellId, 2)
        self.assertRaises(database.apperror.AppError, do.get_well_by_id, 99)
        self.assertEqual(len(do.get_wells_by_lease(2)), 1)
        self.assertRaises(database.apperror.AppError, do.get_wells_by_lease, 666)

        #Testing the leases
        self.assertEqual(len(do.get_all_leases()), 4)
        self.assertEqual(len(do.get_lease_by_id(3)), 1)
        self.assertEqual(do.get_lease_by_id(3)[0].LeaseID, 3)
        self.assertRaises(database.apperror.AppError, do.get_lease_by_id, 99)

        #Testing the universal sql select
        self.assertEqual(len(do.universal_select('Well', RoyaltyClassification='Old Oil')), 1)
        self.assertEqual(len(do.universal_select('Well')), 4)
        self.assertRaises(database.apperror.AppError, do.universal_select, 'Well', DoesNotExist=5)
        self.assertEqual(len(do.universal_select('Lease')), 4)
        self.assertEqual(len(do.universal_select('Lease', Prov='SK')), 3)
        self.assertRaises(database.apperror.AppError, do.universal_select, 'WrongTable')

        #Cleaning up
        dbi.close()

if __name__ == '__main__':
    unittest.main()