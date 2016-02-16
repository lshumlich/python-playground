#!/bin/env python3

import os
import datetime
import sqlite3
from openpyxl import load_workbook

import config
from database.apperror import AppError


class Loader(object):

    EXCLUDE_SHEETS = ['Roy Module Construct']

    def connect(self,dbName):
        self.dbi = config.get_database_instance(dbName)
        
    def delete_database(self, database):
        try:
            print('delete_database:', database)
            os.remove(database)
        except OSError:
            print('could not delete_database:', database)
            pass

    def open_excel(self, workbookName):
        self.wb = load_workbook(workbookName)
        
    def load_all_sheets(self):
        sheets = self.wb.get_sheet_names()
        for sheet in sheets:
            if sheet not in self.EXCLUDE_SHEETS:
                self.load_worksheet(sheet)

    def load_worksheet(self,tabName):
        try:
            ws = self.wb[tabName]
            tableName = tabName.replace(' ', '')
            if len(ws.rows) > 1:
                recordNo = 0;
                headerRow = None
                for row in ws.rows:
                    if not headerRow:
                        headerRow = row
                        self.create_table(tableName,headerRow, ws.rows[1])
                    else:
                        recordNo = recordNo +1
                        self.insert_data(tableName,row, headerRow)
                self.dbi.commit()
#             else:
#                 print('*** No data to load for tab:', tabName)
        except Exception as e:
            raise e
                
    def create_table(self,tableName,headerRow, dataRow):

        try:
            self.delete_table(tableName)
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
        self.dbi.execute(tableCreate)
        self.dbi.commit()

    def delete_table(self,tableName):
        
        try:
            self.dbi.execute('drop table ' + tableName)
        except sqlite3.OperationalError:
            raise AppError("Table did not exist so not deleted: " + tableName)

        
    def insert_data(self,tableName,row, headerRow):
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
        self.dbi.execute(insert)
        
    def commit (self):
        self.dbi.commit()
        
    def close(self):
        self.dbi.close()


if __name__ == '__main__':
    None
    # run from batch.py
