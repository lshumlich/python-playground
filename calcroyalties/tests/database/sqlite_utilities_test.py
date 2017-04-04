
import unittest
import logging
import config
from src.database.database_create import DatabaseCreate


class UnittestConfigTest(unittest.TestCase):
    """
    This has the database utilities for unit testing.

    The utilities and the tests are in the same py file so that
    this module is not accidently  used in the production code.
    """

    def test_execute_statement_delete_table(self):
        self.assertEqual(config.get_environment(), 'unittest')  # Destructive Tests must run in unittest environment
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

    def table_exists(self, name):
        tables = self.db_instance.get_table_names()
        if name not in tables:
            return False
        return True
    
    def delete_all_tables(self):
        """ Used only for unit tests. It was put here so the database itself did not have distructive code in it """
        for table in self.db_instance.get_table_names():
            # print('!!! DELETING !!!')
            logging.info('Deleting table %s' % table)
            self.delete_table(table)
        self.db_instance.commit()
        
    def delete_table(self, table):
        self.db_instance.execute('DROP TABLE %s' % table)

    def create_some_test_well_royalty_masters(self):
        if 'WellRoyaltyMaster' not in self.db_instance.get_table_names():
            self.db_create.well_royalty_master()
            
        statement = """
            INSERT INTO WellRoyaltyMaster VALUES(1, '2010-01-01 00:00:00', '9999-12-31 23:59:59.000005',
                'SKWI111062705025W300','SK','Oil','res1','New', 'Heavy', 0, '2014-12-01 00:00:00',1.0,
                '9999-12-31 23:59:59.000005', 'HORIZONTAL','Some Note');
            INSERT INTO WellRoyaltyMaster VALUES(2, '2011-11-01 00:00:00', '9999-12-31 23:59:59.000005',
                'SKWI112062705025W300','SK','Oil','res1','Third Tier', 'Southwest',0,'2014-12-01 00:00:00',1.0,
                '9999-12-31 23:59:59.000005', 'HORIZONTAL','Some Note');
            INSERT INTO WellRoyaltyMaster VALUES(3, '2004-10-01 00:00:00', '9999-12-31 23:59:59.000005',
                'SKWI113062705025W300','SK','Oil','res1','Fourth Tier','Other', 0,'2014-12-01 00:00:00',1.0,
                '9999-12-31 23:59:59.000005', 'VERTICAL','Some Note');
            INSERT INTO WellRoyaltyMaster VALUES(4, '2013-01-01 00:00:00', '2016-12-31 23:59:59.000005',
                'SKWI114062705025W300','SK','Oil','res1','Old', 'Other', 0,'2014-12-01 00:00:00',1.0,
                '9999-12-31 23:59:59.000005', 'VERTICAL','Some Note');
        """
        
        self.db_instance.execute_statement(statement)

    def create_some_test_lease_royalty_masters(self):
        if 'LeaseRoyaltyMaster' not in self.db_instance.get_table_names():
            self.db_create.lease_royalty_master()

        statement = """
            INSERT INTO LeaseRoyaltyMaster VALUES(1, '2001-01-08 00:00:00', '2016-01-07 00:00:00', 'All',
            'SKProvCrownVar,GORR', 0.12, 0.02, 'SaskWellHead', 'Prod', 'Sales', 'Prod', 'Y', 'Y', 'Y',
            'mprod,250,2,300,3,400,4,500,5,0,6',
            NULL, 0, 50, 50, NULL)
        """

        self.db_instance.execute_statement(statement)

    def create_some_test_well_lease_link(self):
        if 'WellLeaseLink' not in self.db_instance.get_table_names():
            self.db_create.well_lease_link()
        statement = """
            INSERT INTO WellLeaseLink VALUES(1, '2001-01-08 00:00:00', '2016-01-07 00:00:00', 1, 1, 1.0);
            INSERT INTO WellLeaseLink VALUES(2, '2001-01-08 00:00:00', '2016-01-07 00:00:00', 2, 1, 1.0);
            INSERT INTO WellLeaseLink VALUES(3, '2001-01-08 00:00:00', '2016-01-07 00:00:00', 3, 1, 1.0);
            INSERT INTO WellLeaseLink VALUES(4, '2001-01-08 00:00:00', '2015-01-01 00:00:00', 4, 1, 1.0);

        """

        self.db_instance.execute_statement(statement)

    def create_some_test_monthly(self):
        if 'Monthly' not in self.db_instance.get_table_names():
            self.db_create.monthly()

        statement = """
            INSERT INTO Monthly Values(1, '2015-09-29 00:00:00', 201501, 1,
                'OIL', 2, 740, 100, 90.0, 26.2, 0, "Payor1", 100.0, 221.123456, 2.123455, 0.123455, 0.0);
            INSERT INTO Monthly Values(2, '2015-09-29 00:00:00', 201501, 4,
                'OIL', 2, 740, 100, 90.0, 35.61, 0, "Payor1", 50.0, 221.123456, 2.123455, 0.123455, 0.0);
            INSERT INTO Monthly Values(4, '2015-09-29 00:00:00', 201501, 4,
                'OIL', 2, 740, 100, 90.0, 27.55, 0, "Payor1", 50.0, 221.123456, 2.123455, 0.123455, 0.0);
        """
        self.db_instance.execute_statement(statement)

    def create_orphin_monthly(self):
        statement = """
            INSERT INTO Monthly Values(37, '2015-09-29 00:00:00', 201501, 1,
                'Stuff', 2, 740, 100, 0, "Payor1", 100.0, 221.123456, 2.123455, 0.123455, 0.0);
        """
        self.db_instance.execute_statement(statement)

    def create_calc(self):
        if 'Calc' not in self.db_instance.get_table_names():
            self.db_create.calc()

    def create_some_test_leases(self):
        if 'Lease' not in self.db_instance.get_table_names():
            self.db_create.lease()
        statement = """
            INSERT INTO Lease VALUES(1,'2001-01-08 00:00:00', '2016-01-07 00:00:00', 'OL', 'SK', 7022, 123, NULL);
            INSERT INTO Lease VALUES(2,'1994-07-09 00:00:00', '2014-07-08 00:00:00', 'OL', 'SK', 7332, 123, NULL);
            INSERT INTO Lease VALUES(3,'1998-06-18 00:00:00', '2014-03-31 00:00:00', 'OL', 'SK', 7022, 123, NULL);
            INSERT INTO Lease VALUES(4,'1998-06-18 00:00:00', '2015-01-01 00:00:00', 'OL', 'SK', 7022, 123, NULL);
        """
        self.db_instance.execute_statement(statement)

    def create_some_test_econoil(self):
        if 'ECONOil' not in self.db_instance.get_table_names():
            self.db_create.econ_oil()
        statement = """
            INSERT INTO ECONOil VALUES(39,'Jan.',201501,181,223,262,
                0.0934,2.34,23.12,1734,21.73,502,27.11,626,0.1085,2.71,
                26.84,2013,32.38,747,38.94,899,0.1181,2.95,29.22,2192,35.58,821,40.54,936,52.3,1207);
        """
        self.db_instance.execute_statement(statement)

    def create_some_test_econgas(self):
        if 'ECONGas' not in self.db_instance.get_table_names():
            self.db_create.econ_gas()
        statement = """
            INSERT INTO ECONGas VALUES(13,'Jan.',201501,0.1199,3,24.67,1596,0.1443,33.31,1922,0.16,36.92,2130,
                0.2071,47.78,2756);
        """
        self.db_instance.execute_statement(statement)

    def create_some_test_rtp_info(self):
        if 'RTPInfo' not in self.db_instance.get_table_names():
            self.db_create.rtp_info()
        statement = """
            insert into RTPInfo values (1, 'SKWI111062705025W300', 'OIL', '2001-01-08 00:00:00', '2016-01-07 00:00:00',
                'Payor1', 'MinOwership',100);
            insert into RTPInfo values (2, 'SKWI114062705025W300', 'OIL', '2001-01-08 00:00:00', '2016-01-07 00:00:00',
                'Payor1', 'MinOwership',100);
        """
        self.db_instance.execute_statement(statement)

    def delete_lookups(self):
        if not self.table_exists("Lookups"):
            self.db_create.lookups()
        else:
            statement = """
                delete from Lookups;
            """
            self.db_instance.execute_statement(statement)

    def insert_lookups(self, name, prod_month, value):
        statement = "insert into Lookups (Name, ProdMonth, Value) values('" + name + "'," + str(prod_month) + ',' + str(value) + ');'
        self.db_instance.execute_statement(statement)
