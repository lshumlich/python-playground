#!/bin/env python3

import unittest

from database.apperror import AppError
from database.data_structure import DataStructure


class Test(unittest.TestCase):

    def test_data_structure(self):
        well = DataStructure()
        well.ID = 123
        well.Name = 'WellName'
        
        # This returns a dictionary object for the attributes in an object
        dd = vars(well)
        self.assertEqual(len(dd),2)
        self.assertEqual(dd['ID'],123)
        self.assertEqual(dd['Name'],'WellName')
        
    def test_format_lease(self):
        well = DataStructure()
        well.ID = 123
        well.LeaseID = 1
        well.LeaseType = 'OL'
        
        # If there is an attribute in the object called 'LeaseID' use it to format the lease string
        self.assertEqual(well.Lease,'OL-0001')
        
        st = well.Lease
        
        print(st)
        
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
