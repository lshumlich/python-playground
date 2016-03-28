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
        if not 'Well' in self.db_instance.get_table_names():
            self.db_create.Well()
            
        statement = """
            INSERT INTO Well VALUES(1,'SKWI111062705025W300','SK','Oil','OL',1,'New Oil','Heavy',0,0.25,'2014-12-01 00:00:00',1);
            INSERT INTO Well VALUES(2,'SKWI112062705025W300','SK','Oil','OL',2,'Third Tier Oil','Southwest',0,0.95,'2014-12-01 00:00:00',1);
            INSERT INTO Well VALUES(3,'SKWI113062705025W300','SK','Oil','OL',2,'Fourth Tier Oil','Other',0,1.0,NULL,NULL);
            INSERT INTO Well VALUES(4,'SKWI114062705025W300','SK','Oil','OL',3,'Old Oil','Other',0,1.0,NULL,NULL);
        """
        
        self.db_instance.execute_statement(statement)

    def create_some_test_royalties(self):
        if not 'RoyaltyMaster' in self.db_instance.get_table_names():
            self.db_create.Royaltymaster()

        statement = """
            INSERT INTO RoyaltyMaster VALUES(3, 'OL', 'All', 'SKProvCrownVar, GORR', 1.2, 50, 'SaskWellHead', 'Y', 'Y', 'mprod,250,2,300,3,400,4,500,5,0,6', NULL)
        """

        self.db_instance.execute_statement(statement)


    def create_some_test_monthly(self):
        if not 'Monthly' in self.db_instance.get_table_names():
            self.db_create.Monthly()

        statement = """
            INSERT INTO Monthly Values(4, '2015-09-29 00:00:00', 201501, 4, 'Oil', 2, 740, 100, 2.2, 221.123456, 2.123455, 0.123455)
        """
        self.db_instance.execute_statement(statement)

    def create_calc(self):
        if not 'Calc' in self.db_instance.get_table_names():
            self.db_create.Calc()

    def create_some_test_leases(self):
        if not 'Lease' in self.db_instance.get_table_names():
            self.db_create.Lease()
        statement = """
            INSERT INTO Lease VALUES(1,'OL','SK',123,2345,NULL);
            INSERT INTO Lease VALUES(2,'OL','SK',123,2346,NULL);
            INSERT INTO Lease VALUES(3,'OL','SK',123,2347,NULL);
        """
        self.db_instance.execute_statement(statement)
    
    def create_some_test_econdata(self):
        if not 'Econdata' in self.db_instance.get_table_names():
            self.db_create.Econdata()
        statement = """
            INSERT INTO ECONData VALUES(39,'Jan.',201501,181,223,262,0.0934,2.34,23.12,1734,21.73,502,27.11,626,0.1085,2.71,
            26.84,2013,32.38,747,38.94,899,0.1181,2.95,29.22,2192,35.58,821,40.54,936,52.3,1207);
        """
        self.db_instance.execute_statement(statement)
