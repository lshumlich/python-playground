#!/bin/env python3

import sqlite3

from openpyxl import Workbook, load_workbook


class Shower(object):
    
    def __init__(self):
        print('Shower.__init__', self)

    def connect(self,dbName):
        print('Shower opening connection to:', dbName)
        self.conn = sqlite3.connect(dbName)
        self.cursor = self.conn.cursor()
        
    def insertLink(self,tab,att,lnk):
        stmt = 'insert into linktab values("' + tab + '", "' + att + '", "' + lnk + '")'
        self.cursor.execute(stmt)
        self.conn.commit()
        
    def execute(self,statement):
        return self.cursor.execute(statement)
    
    def commit(self):
        self.conn.commit()

    def close(self):
        self.conn.close()

    def showTable(self,tableName,attr=None,key=None):
        stmt = 'select * from ' + tableName
        if key:
            type = self.columnType(tableName, attr)
            where = ''
            if type == 'int':
                where = attr + "=" + key
            elif type =='text':
                where = attr + "='" + key + "'"
            else:
                print('***** Type not delt with:', type,tableName,attr)
            
            stmt = stmt + " where " + where
        elif attr:
            stmt = stmt + " order by " + attr
        print('SQL:', stmt)
        values = self.execute(stmt)
        table_rows = []
        for row in values:
            table_rows.append(row)
        return table_rows
        
    def showTables(self):
        stmt = 'select tbl_name from sqlite_master'
        values = self.execute(stmt)
        tables = []
        for row in values:
            tables.append(row[0])
        return(tables)

    def showColumns(self,tableName):
        stmt = 'pragma table_info(' + tableName + ')'
        values = self.execute(stmt)
        columns = []
        for row in values:
            columns.append(row[1])
        return(columns)
    
    def columnType(self,table,column):
        stmt = 'pragma table_info(' + table + ')'
        values = self.execute(stmt)
        for row in values:
            if row[1] == column:
                return row[2]
        return(None)


def showTable(dbName, tableName):
    shower = Shower()
    shower.connect(dbName)
    header = shower.showColumns(tableName)
    print(header)
    rows = shower.showTable(tableName,'Prov','SK')
    for row in rows:
        print(row)


if __name__ == '__main__':
    dbName = 'testload.db'
    tableName = 'Well'
    showTable(dbName, tableName)