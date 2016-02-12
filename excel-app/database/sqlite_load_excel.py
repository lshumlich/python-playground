#!/bin/env python3

import os
import datetime
import sqlite3

from openpyxl import load_workbook
from database.apperror import AppError


class Loader(object):

    def connect(self,dbName):
        self.conn = sqlite3.connect(dbName)
        self.cursor = self.conn.cursor()
        
    def execute(self,statement):
        # Create table
#         print(statement)
        return self.cursor.execute(statement)

    def commit(self):
        # Save (commit) the changes
        self.conn.commit()
        
        # We can also close the connection if we are done with it.
        # Just be sure any changes have been committed or they will be lost.
    def close(self):
        self.conn.close()

    def delete_database(self, database):
        try:
            os.remove(database)
        except OSError:
            pass

    def openExcel(self, workbookName):
        self.wb = load_workbook(workbookName)
        
    def loadAllSheets(self):
        sheets = self.wb.get_sheet_names()
        for sheet in sheets:
#             print ('loading:', sheet)
            self.LoadWorksheet(sheet)

    def LoadWorksheet(self,tabName):
        try:
            ws = self.wb[tabName]
            tableName = tabName.replace(' ', '')
            if len(ws.rows) > 1:
                recordNo = 0;
                headerRow = None
                for row in ws.rows:
                    if not headerRow:
                        headerRow = row
                        self.createTable(tableName,headerRow, ws.rows[1])
                    else:
                        recordNo = recordNo +1
                        self.insertData(tableName,row, headerRow)
                self.commit()
#             else:
#                 print('*** No data to load for tab:', tabName)
        except Exception as e:
            raise e
                
    def createTable(self,tableName,headerRow, dataRow):

        try:
            self.deleteTable(tableName)
        except AppError:
            None  # Just means the table does not exist
        
       
        tableCreate = 'CREATE TABLE ' + tableName + ' ('
        cols = ""
        i = 0
        for cell in headerRow:
            name = cell.value.replace('#','')
            name = '"' + name + '"'
            if type(dataRow[i].value) is str:
                cols = cols + name + ' text, '
            elif type(dataRow[i].value) is int:
                cols = cols + str(name) + ' int, '
            elif type(dataRow[i].value) is float:
                cols = cols + str(name) + ' float, '
            elif type(dataRow[i].value) is datetime.datetime:
                cols = cols + str(name) + ' date, '
            else:
                cols = cols + name + ' text, '
#                 print('*** Null first line so defaulting to str',cell.value,type(dataRow[i].value))
            i += 1
            
        cols = cols + ')'
        cols = cols.replace(', )', ')')
        
        tableCreate = tableCreate + cols
    
        
#         print(tableCreate)
        self.execute(tableCreate)
        self.commit()

    def deleteTable(self,tableName):
        
        try:
            self.execute('drop table ' + tableName)
        except sqlite3.OperationalError:
            raise AppError("Table did not exist so not deleted: " + tableName)

        
    def insertData(self,tableName,row, headerRow):
        insert = 'INSERT INTO ' + tableName + ' VALUES ('
        data = ""
        i = 0
        
        for h in headerRow:
            cell = row[i]
            if type(cell.value) is str:
                data = data + "'" + cell.value + "',"
            elif type(cell.value) is int:
                data = data +  str(cell.value) + ","
            elif type(cell.value) is float:
                data = data +  str(cell.value) + ","
            elif type(cell.value) is datetime.datetime:
                data = data +  "'" + str(cell.value) + "',"
#                 data = data +  str(cell.value.strftime("%Y/%m/%d")) + ","
            elif cell.value is None:
                data = data +  " Null,"
            else:
                raise AppError('*** Not Loaded',cell.value, type(cell.value))
            i += 1

            
        data = data + ')'
        data = data.replace(',)', ')')
        
        insert = insert + data
            
        print(insert)
        self.execute(insert)


if __name__ == '__main__':
    database = 'testload.db'
    loader = Loader()
    loader.connect(database)
    loader.openExcel(r'test_database.xlsx')
    loader.loadAllSheets()
    loader.close()