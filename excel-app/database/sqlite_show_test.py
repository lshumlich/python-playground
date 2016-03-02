#!/bin/env python3

import unittest

import config
from database.sqlite_show import Shower
from database.sqlite_database_test import DatabaseUtilities


class SqliteShowerTest(unittest.TestCase):


    def test_check_linktab(self):
        self.assertEqual(config.get_environment(),'unittest') # Distructive Tests must run in unittest enviornment
        dbi = config.get_database_instance()
        
        dbu = DatabaseUtilities()
        dbu.delete_all_tables()
        shower = Shower()

        shower.connect()
        tables = dbi.get_table_names()
        self.assertEqual(len(tables), 1)
        self.assertIn(Shower.LINK_TABLE,tables)

        shower.insert_link('tabname1', 'attName1', 'linkName1', 1, 'ID1,Name1')
        shower.insert_link('tabname2', 'attName2', 'linkName2', 1, 'ID2,Name2')
        shower.insert_link('tabname3', 'attName3', 'linkName3', 1, 'ID3,Name3')

        rows = shower.show_table(Shower.LINK_TABLE, 'TabName', 'tabname2')
        self.assertEqual(len(rows), 1)
        
        rows = shower.show_table(Shower.LINK_TABLE)
        self.assertEqual(len(rows), 3)
        
        link = shower.get_link('tabname2','attName2')
        self.assertEqual(link[0].LinkName,'linkName2')
        
        # Update a record then read antoher and then read this one again to make sure it works
#         link = shower.get_link('tabname1','attName1')
#         link.LinkName = 'New Link Name'
#         shower.update_link(link)
        
        # Fails because this is the next thing we are going to make work... Sorry about the failure
        link = shower.get_link('tabname2','attName2')
        self.assertEqual(link[0].LinkName,'linkName2')
        
