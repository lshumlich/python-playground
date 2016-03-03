#!/bin/env python3

import config

class Shower(object):
    
    LINK_TABLE = "LinkTab"
    def __init__(self):
        None

    def connect(self):
        self.dbi = config.get_database_instance()
        
    def show_table(self,tableName,attr=None,key=None):
        stmt = 'select * from ' + tableName
        if key:
            ctype = self.column_type(tableName, attr)
            where = ''
            if ctype == 'int':
                where = attr + "=" + key
            elif ctype =='text':
                where = attr + "='" + key + "'"
            else:
                print('***** Type not delt with:', type,tableName,attr)
            
            stmt = stmt + " where " + where
        elif attr:
            stmt = stmt + " order by " + attr
#         print('SQL:', stmt)
        values = self.dbi.execute(stmt)
        table_rows = []
        for row in values:
            table_rows.append(row)
        return table_rows
        
#     Use dbi.get_table_names()
#     def show_tables(self):
#         stmt = 'select tbl_name from sqlite_master'
#         values = self.dbi.execute(stmt)
#         tables = []
#         for row in values:
#             tables.append(row[0])
#         return(tables)

    def show_columns(self,tableName):
        stmt = 'pragma table_info(' + tableName + ')'
        values = self.dbi.execute(stmt)
        columns = []
        for row in values:
            columns.append(row[1])
        return(columns)
    
    def column_type(self,table,column):
        stmt = 'pragma table_info(' + table + ')'
        values = self.dbi.execute(stmt)
        for row in values:
            if row[1] == column:
                return row[2]
        return(None)

