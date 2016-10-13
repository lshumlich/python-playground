'''
This has the database utilities for unit testing.

The utilities and the tests are in the same py file so that
this module is not accidently  used in the production code. 
'''

import unittest

import config
from src.database.database_create import DatabaseCreate

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
            self.db_create.well()
            
        statement = """
            INSERT INTO Well VALUES(1, '2010-01-01 00:00:00', '9999-12-31 23:59:59.000005', 'SKWI111062705025W300','SK','Oil','New Oil',        'Heavy',    0,'2014-12-01 00:00:00',1.0,'9999-12-31 23:59:59.000005', 'HORIZONTAL');
            INSERT INTO Well VALUES(2, '2011-11-01 00:00:00', '9999-12-31 23:59:59.000005', 'SKWI112062705025W300','SK','Oil','Third Tier Oil', 'Southwest',0,'2014-12-01 00:00:00',1.0,'9999-12-31 23:59:59.000005', 'HORIZONTAL');
            INSERT INTO Well VALUES(3, '2004-10-01 00:00:00', '9999-12-31 23:59:59.000005', 'SKWI113062705025W300','SK','Oil','Fourth Tier Oil','Other',    0,'2014-12-01 00:00:00',1.0,'9999-12-31 23:59:59.000005', 'VERTICAL');
            INSERT INTO Well VALUES(4, '2013-01-01 00:00:00', '9999-12-31 23:59:59.000005', 'SKWI114062705025W300','SK','Oil','Old Oil',        'Other',    0,'2014-12-01 00:00:00',1.0,'9999-12-31 23:59:59.000005', 'VERTICAL');
        """
        
        self.db_instance.execute_statement(statement)

    def create_some_test_royalties(self):
        if not 'RoyaltyMaster' in self.db_instance.get_table_names():
            self.db_create.royalty_master()

        statement = """
            INSERT INTO RoyaltyMaster VALUES(1, '2001-01-08 00:00:00', '2016-01-07 00:00:00', 'All', 'SKProvCrownVar,
            GORR', 1.2, 'SaskWellHead', 'Y', 'Y', 'Y', 'mprod,250,2,300,3,400,4,500,5,0,6', NULL, 0, 50, 50, NULL)
        """

        self.db_instance.execute_statement(statement)

    def create_some_test_well_lease_link(self):
        if not 'WellLeaseLink' in self.db_instance.get_table_names():
            self.db_create.well_lease_link()
        statement = """
            INSERT INTO WellLeaseLink VALUES(1, '2001-01-08 00:00:00', '2016-01-07 00:00:00', 1, 1, 1.0);
            INSERT INTO WellLeaseLink VALUES(2, '2001-01-08 00:00:00', '2016-01-07 00:00:00', 2, 1, 1.0);
            INSERT INTO WellLeaseLink VALUES(3, '2001-01-08 00:00:00', '2016-01-07 00:00:00', 3, 1, 1.0);
            INSERT INTO WellLeaseLink VALUES(4, '2001-01-08 00:00:00', '2015-01-01 00:00:00', 4, 1, 1.0);

        """

        self.db_instance.execute_statement(statement)


    def create_some_test_monthly(self):
        if not 'Monthly' in self.db_instance.get_table_names():
            self.db_create.monthly()

        statement = """
            INSERT INTO Monthly Values(4, '2015-09-29 00:00:00', 201501, 4, 'Oil', 2, 740, 100, 2.2, 221.123456, 2.123455, 0.123455, 0.0)
        """
        self.db_instance.execute_statement(statement)

    def create_calc(self):
        if not 'Calc' in self.db_instance.get_table_names():
            self.db_create.calc()

    def create_some_test_leases(self):
        if not 'Lease' in self.db_instance.get_table_names():
            self.db_create.lease()
        statement = """
            INSERT INTO Lease VALUES(1,'2001-01-08 00:00:00', '2016-01-07 00:00:00', 'OL', 'SK', 7022,123,2345,NULL);
            INSERT INTO Lease VALUES(2,'1994-07-09 00:00:00', '2014-07-08 00:00:00', 'OL', 'SK', 7332, 123,2346,NULL);
            INSERT INTO Lease VALUES(3,'1998-06-18 00:00:00', '2014-03-31 00:00:00', 'OL', 'SK', 7022, 123,2347,NULL);
            INSERT INTO Lease VALUES(4,'1998-06-18 00:00:00', '2015-01-01 00:00:00', 'OL', 'SK', 7022, 123,2347,NULL);
        """
        self.db_instance.execute_statement(statement)

    def create_some_test_econdata(self):
        if not 'ECONdata' in self.db_instance.get_table_names():
            self.db_create.econ_data()
        statement = """
            INSERT INTO ECONData VALUES(39,'Jan.',201501,181,223,262,0.0934,2.34,23.12,1734,21.73,502,27.11,626,0.1085,2.71,
            26.84,2013,32.38,747,38.94,899,0.1181,2.95,29.22,2192,35.58,821,40.54,936,52.3,1207);
        """
        self.db_instance.execute_statement(statement)
