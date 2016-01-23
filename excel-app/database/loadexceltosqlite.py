import os
import sys
import datetime
import sqlite3
from sqlite3 import OperationalError

from openpyxl import load_workbook
from openpyxl import Workbook

class Loader(object):

        
    def connect(self,dbName):
        self.conn = sqlite3.connect(dbName)
        self.cursor = self.conn.cursor()
        
    def execute(self,statement):
        # Create table
        return self.cursor.execute(statement)

    def commit(self):
        # Save (commit) the changes
        self.conn.commit()
        
        # We can also close the connection if we are done with it.
        # Just be sure any changes have been committed or they will be lost.
    def close(self):
        self.conn.close()

    def openExcel(self, workbookName):
        self.wb = load_workbook(workbookName)
        
    def loadAllSheets(self):
        sheets = self.wb.get_sheet_names()
        for sheet in sheets:
            print ('loading:', sheet)
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
            else:
                print('*** No data to load for tab:', tabName)
        except Exception as e:
            raise e
                
#                     ds = DataStructure()
#                     stack.append(ds)
#                     i = 0
#                     for cell in headerRow:
#                         setattr(ds, cell.value, row[i].value)
#                         i = i + 1
#         except KeyError:
#             raise AppError('The excel worksheet ' + self.worksheetName + ' does not have tab: ' + tabName)
#         except AttributeError as e:
#             print('Error Loading tab:',tabName,' column:',i,'Record:',recordNo,'Error:',e)
#             print('   cell.value:',cell.value)
#             print('   headerRow:',headerRow)
#             print('         row:',row)
#             raise e
#         except TypeError as e:
#             print('Error Loading tab:',tabName,' column:',i,'Record:',recordNo,'Error:',e)
#             print('   headerRow:',headerRow)
#             print('         row:',row)
#             raise e
        
    def createTable(self,tableName,headerRow, dataRow):

        self.deleteTable(tableName)
       
        tableCreate = 'CREATE TABLE ' + tableName + '('
        cols = ""
        i = 0
        for cell in headerRow:
            name = cell.value.replace('#','')
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
                print('*** Null first line so defaulting to str',cell.value,type(dataRow[i].value))
            i += 1
            
        cols = cols + ')'
        cols = cols.replace(', )', ')')
        
        tableCreate = tableCreate + cols
    
        
        print(tableCreate)
        self.execute(tableCreate)
        self.commit()

    def deleteTable(self,tableName):
        
        try:
            self.execute('drop table ' + tableName)
        except sqlite3.OperationalError:
            print("Table did not exist so not deleted:", tableName)

        
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
                print('*** Not Loaded',cell.value, type(cell.value))
            i += 1

            
        data = data + ')'
        data = data.replace(',)', ')')
        
        insert = insert + data
    
        
        print(insert)
        self.execute(insert)
        
    def showTable(self,tableName):
        stmt = 'select * from ' + tableName
        values = self.execute(stmt)
        for row in values:
            print(row)
        
    def showTables(self):
        stmt = 'select tbl_name from sqlite_master'
        values = self.execute(stmt)
        for row in values:
            print(row)

    def showColumns(self,tableName):
        stmt = 'pragma table_info(' + tableName + ')'
        values = self.execute(stmt)
        for row in values:
            print(row)
        

print('Hello World from ' + sys.argv[0])
loader = Loader()
loader.connect('testload.db')
loader.openExcel(r'd:/$temp/Onion Lake SK wells.xlsx')
loader.loadAllSheets()
# loader.loadExcel("database.xlsx")
# loader.LoadWorksheet('Well')
# loader.showTables()
# loader.showTable('well')
# loader.showTables()
# loader.showColumns('well')


print('as df  a s d f'.replace(' ',''))


loader.close()

print("*** Done ***")

"""
        self.cursor.execute('''CREATE TABLE stocks
                     (date text, trans text, symbol text, qty real, price real)''')
        
        # Insert a row of data
        self.cursor.execute("INSERT INTO stocks VALUES ('2006-01-05','BUY','RHAT',100,35.14)")
"""