'''
This has the database utilities for unit testing.

The utilities and the tests are in the same py file so that
this module is not accidently  used in the production code. 
'''

import unittest

import config
from database.database_create import DatabaseCreate

class UnittestConfigTest(unittest.TestCase):
    
    def test_execute_statement_delete_table(self):
        self.assertEqual(config.get_environment(),'unittest') # Distructive Tests must run in unittest enviornment
        dbi = config.get_database_instance()
        dbu = DatabaseUtilities()
        dbu.delete_all_tables()
        self.assertEqual(len(dbi.get_table_names()), 0, 'These should be no tables in the database.')
        
        statement = """
            CREATE TABLE table1 ('ID' int, 'Name' text);
            CREATE TABLE table2 ('ID' int, 'Name' text);
            CREATE TABLE table3 ('ID' int, 'Name' text);
        """
        dbi.execute_statement(statement)
        self.assertEqual(len(dbi.get_table_names()), 3)
        self.assertIn('table2', dbi.get_table_names())

        dbu.delete_table('table2')
        self.assertEqual(len(dbi.get_table_names()), 2)
        self.assertNotIn('table2', dbi.get_table_names())
        
        dbu.delete_all_tables()
        self.assertEqual(len(dbi.get_table_names()), 0, 'These should be no tables in the database.')

class DatabaseUtilities(object):

    def __init__(self):
        self.db_instance = config.get_database_instance()
        self.db_create = DatabaseCreate()
    
    def delete_all_tables(self):
        """ Used only for unit tests. It was put here so the database itself did not have distructive code in it """
        for table in self.db_instance.get_table_names():
            self.delete_table(table)
        self.db_instance.commit()
        
    def delete_table(self,table):
        self.db_instance.execute('DROP TABLE %s' % table)

    def create_some_test_wells(self):
        self.db_create.well()
        statement = """
            INSERT INTO Well VALUES(1,'SKWI111062705025W300','SK','Oil','OL',1,'New Oil','Heavy',0,0.25,'2014-12-01 00:00:00',1);
            INSERT INTO Well VALUES(2,'SKWI112062705025W300','SK','Oil','OL',2,'Third Tier Oil','Southwest',0,0.95,'2014-12-01 00:00:00',1);
            INSERT INTO Well VALUES(3,'SKWI113062705025W300','SK','Oil','OL',3,'Fourth Tier Oil','Other',0,1.0,NULL,NULL);
            INSERT INTO Well VALUES(4,'SKWI114062705025W300','SK','Oil','OL',4,'Old Oil','Other',0,1.0,NULL,NULL);
        """
#             CREATE TABLE Well ('ID' int, 'UWI' text, 'Prov' text, 'WellType' text, 'LeaseType' text, 'LeaseID' int, 'RoyaltyClassification' text, 'Classification' text, 'SRC' int, 'IndianInterest' float, 'CommencementDate' date, 'ReferencePrice' int);

        self.db_instance.execute_statement(statement)

    def create_some_test_leases(self):
        statement = """
            CREATE TABLE Lease ('LeaseType' text, 'ID' int, 'Prov' text, 'FNReserve' int, 'Lessor' int, 'Notes' text);
            INSERT INTO Lease VALUES('OL',1,'SK',123,2345,NULL);
            INSERT INTO Lease VALUES('OL',2,'SK',123,2345,NULL);
            INSERT INTO Lease VALUES('OL',3,'SK',123,2345,NULL);
            INSERT INTO Lease VALUES('OL',4,'AB',123,2345,NULL);
        """
        self.db_instance.execute_statement(statement)

