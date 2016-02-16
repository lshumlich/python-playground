#!/bin/env python3
"""
This is the database instance object if we are using sqlite3. It should only
be served from the 'config.py' in the root. There is only to be one database
instance object for the application.
"""
import sqlite3


class SqliteInstance(object):
    
    def __init__(self, databaseName):
        self.databaseName = databaseName
        self.conn = sqlite3.connect(self.databaseName)
        self.cursor = self.conn.cursor()

    def execute(self,stmt):
#         print('Execute: ' + stmt)
        return self.cursor.execute(stmt)
        
    def get_table_names(self):
        stmt = 'SELECT tbl_name FROM sqlite_master'
        values = self.execute(stmt)
        tables = []
        if values:
            for row in values:
                tables.append(row[0])
        return(tables)
        
    def commit(self):
        # Save (commit) the changes
        self.conn.commit()
        
    def close(self):
        self.conn.close()
        
