#!/bin/env python3
"""
This is the database instance object if we are using sqlite3. It should only
be served from the 'config.py' in the root. There is only to be one database
instance object for the application.
"""
import sqlite3
from sqlite3 import OperationalError

from database.apperror import AppError
import config


class SqliteInstance(object):
    
    def __init__(self, databaseName):
        self.databaseName = databaseName
        self.conn = sqlite3.connect(self.databaseName, detect_types=sqlite3.PARSE_DECLTYPES|sqlite3.PARSE_COLNAMES)
        self.cursor = self.conn.cursor()
        self.debug_sql = config.debug_sql()

    def execute(self,stmt):
        if self.debug_sql:
            print('SqliteInstance.execute:',stmt)
        try:
            return self.cursor.execute(stmt)
        except OperationalError as e:
            raise AppError(str(e) + '--> ' + stmt)
        
    def get_id(self):
        return self.cursor.lastrowid

    def execute_statement(self,statement):
        for line in statement.split(';'):
            n_line = line.strip()
            if n_line != '':
                self.execute(n_line)
        self.commit()

    def get_column_names(self):
        """ Get the column names of the last select. This only works after a select """
        return [description[0] for description in self.cursor.description]
        
        
    def get_table_names(self):
        stmt = 'SELECT tbl_name FROM sqlite_master'
        values = self.execute(stmt)
        tables = []
        if values:
            for row in values:
                if row[0] != 'sqlite_sequence':
                    tables.append(row[0])
        return(tables)
        
    def commit(self):
        # Save (commit) the changes
        self.conn.commit()
        
    def close(self):
        self.conn.close()
        
