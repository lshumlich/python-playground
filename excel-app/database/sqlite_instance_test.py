#!/bin/env python3
"""
This tests all the primary features in the sqlite_insance. It is written as one
big method which is generally not a good idea but in this case it seemed like
the best way to test it.
"""
import unittest
import config
from database.sqlite_instance import SqliteInstance

class TestSqliteInstance(unittest.TestCase):
    
    TEST_TABLE_NAME = 'mytable'

    def test_all_features(self):
        instance = SqliteInstance(config.get_temp_dir() + 'unitest.db')
        dropStmt = 'drop table ' + self.TEST_TABLE_NAME

        # Make sure the table does not exist from the last run
        tables = instance.get_table_names()
        if self.TEST_TABLE_NAME in tables:
            instance.execute(dropStmt)

        createStmt = 'create table ' + self.TEST_TABLE_NAME  + ' (myKey int, myText text, myDate date)'
        instance.execute(createStmt)
        instance.commit()
        
        self.assertIn(self.TEST_TABLE_NAME, instance.get_table_names(), 'Should have created table: ' + self.TEST_TABLE_NAME)
        
        insertStmt = 'insert into ' + self.TEST_TABLE_NAME + " values (1, 'Test Item One', '2016-02-14')"
        instance.execute(insertStmt)
        insertStmt = 'insert into ' + self.TEST_TABLE_NAME + " values (2, 'Test Item Two', '2016-02-14')"
        instance.execute(insertStmt)
        instance.commit()
        
        selectStmt = 'select * from ' + self.TEST_TABLE_NAME + ' order by myKey'
        values = instance.execute(selectStmt)
        
        rows = []
        for row in values:
            rows.append(row)

        self.assertEqual(2,len(rows), 'Should be two rows in the table')
        self.assertEqual(1,rows[0][0], 'First key should be 1')
        self.assertEqual(2,rows[1][0], 'First key should be 1')
        
        instance.close()

if __name__ == "__main__":
    unittest.main()