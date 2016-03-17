    #!/bin/env python3

import datetime
from openpyxl import load_workbook

import config
from database.sqlite_database_test import DatabaseUtilities
from database.apperror import AppError


class Loader(object):
    """ 
    Load data from execl into sql tables. The tab names are the table
    names. The first row must contain the column names. Be carefull there
    are no blank lines at the end of you sheets.
    """
    EXCLUDE_SHEETS = ['Roy Module Construct']
    
    def __init__(self):
        self.dbu = DatabaseUtilities()

    def connect(self):
        self.dbi = config.get_database_instance()
        
    def open_excel(self, workbookName):
        self.wb = load_workbook(workbookName)
        
    def load_all_sheets(self):
        sheets = self.wb.get_sheet_names()
        for sheet in sheets:
            if sheet not in self.EXCLUDE_SHEETS:
                self.load_worksheet(sheet)

    def load_worksheet(self,tabName):
        recordNo = 0;
        try:
            ws = self.wb[tabName]
            tableName = tabName.replace(' ', '')
            if len(ws.rows) > 1:
                headerRow = None
                for row in ws.rows:
                    if not headerRow:
                        headerRow = row
                        if not tableName in self.dbi.get_table_names():
                            self.create_table(tableName,headerRow, ws.rows[1])
                    else:
                        recordNo = recordNo +1
                        self.insert_data(tableName,row, headerRow)
                self.dbi.commit()
#             else:
#                 print('*** No data to load for tab:', tabName)
        except Exception as e:
            print('*** sqlite_load_excel.load_worksheet -- Tab:', tabName , ' row:', recordNo, row )
            raise e
                
    def create_table(self,tableName,headerRow, dataRow):
        
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

        self.dbi.execute(tableCreate)
        self.dbi.commit()

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
    worksheet = config.get_file_dir() + 'database.xlsx'
    config.set_database_name('browse.db')
    loader = Loader()
    loader.open_excel(worksheet)
    loader.load_all_sheets()
    loader.close()
