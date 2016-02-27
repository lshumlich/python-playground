'''
This has the database utilities for unit testing.

The utilities and the tests are in the same py file so that
this module is not accidently  used in the production code. 
'''

import unittest

import config


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
        dbu.execute_statement(statement)
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

    def execute_statement(self,statement):
        for line in statement.splitlines():
            self.db_instance.execute(line)
        self.db_instance.commit()
    
    def delete_all_tables(self):
        """ Used only for unit tests. It was put here so the database itself did not have distructive code in it """
        for table in self.db_instance.get_table_names():
            self.delete_table(table)
        self.db_instance.commit()
        
    def delete_table(self,table):
        self.db_instance.execute('DROP TABLE %s' % table)

