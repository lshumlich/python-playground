#!/bin/env python3

import datetime
from openpyxl import load_workbook

import config
from src.util.apperror import AppError


class Loader(object):
    """ 
    Load data from execl into sql tables. The tab names are the table
    names. The first row must contain the column names. Be careful there
    are no blank lines at the end of you sheets.
    """
    EXCLUDE_SHEETS = ['Roy Module Construct']

    def __init__(self):
        self.dbi = config.get_database_instance()
        self.wb = None

    def open_excel(self, workbook_name):
        self.wb = load_workbook(workbook_name)

    def load_all_sheets(self):
        sheets = self.wb.get_sheet_names()
        for sheet in sheets:
            if sheet not in self.EXCLUDE_SHEETS:
                self.load_worksheet(sheet)

    def load_worksheet(self, tab_name):
        record_no = 0
        row = None
        try:
            ws = self.wb[tab_name]
            table_name = tab_name.replace(' ', '')
            if len(ws.rows) > 1:
                header_row = None
                for row in ws.rows:
                    if not header_row:
                        header_row = row
                        if table_name not in self.dbi.get_table_names():
                            self.create_table(table_name, header_row, ws.rows[1])
                    else:
                        record_no += 1
                        self.insert_data(table_name, row, header_row)
                self.dbi.commit()
                #             else:
                #                 print('*** No data to load for tab:', tabName)
        except Exception as e:
            print('*** sqlite_load_excel.load_worksheet -- Tab:', tab_name, ' row:', record_no, row)
            raise e

    def create_table(self, table_name, header_row, data_row):

        try:
            table_create = 'CREATE TABLE ' + table_name + ' ('
            cols = ""
            i = 0
            for cell in header_row:
                name = cell.value.replace('#', '')
                name = '"' + name + '"'
                if type(data_row[i].value) is str:
                    cols = cols + name + ' text, '
                elif type(data_row[i].value) is int:
                    cols = cols + str(name) + ' int, '
                elif type(data_row[i].value) is float:
                    cols = cols + str(name) + ' float, '
                elif type(data_row[i].value) is datetime.datetime:
                    cols = cols + str(name) + ' timestamp, '
                else:
                    cols = cols + name + ' text, '
                # print('*** Null first line so defaulting to str',cell.value,type(dataRow[i].value))
                i += 1

            cols += ')'
            cols = cols.replace(', )', ')')

            table_create += cols

            self.dbi.execute(table_create)
            self.dbi.commit()

        except Exception as e:
            print('*** sqlite_load_excel.creat_table  -- Table:', table_name, ' row:', header_row, data_row)
            raise e

    def insert_data(self, table_name, row, header_row):
        insert = 'INSERT INTO ' + table_name + ' VALUES ('
        data = ""
        i = 0

        for h in header_row:
            cell = row[i]
            if type(cell.value) is str:
                data = data + "'" + cell.value + "',"
            elif type(cell.value) is int:
                data = data + str(cell.value) + ","
            elif type(cell.value) is float:
                data = data + str(cell.value) + ","
            elif type(cell.value) is datetime.datetime:
                data = data + "'" + str(cell.value) + "',"
            elif cell.value is None:
                data += " Null,"
            else:
                raise AppError('*** Not Loaded: ' + cell.value + " " + type(cell.value))
            i += 1

        data += ')'
        data = data.replace(',)', ')')

        insert += data

        print(insert)
        self.dbi.execute(insert)

    def commit(self):
        self.dbi.commit()

    def close(self):
        self.dbi.close()

from src.database.database_create import DatabaseCreate

def load_all_from_scratch():
    db_create = DatabaseCreate()
    db_create.create_all()

    worksheet = config.get_temp_dir() + 'new.xlsx'
    loader = Loader()
    loader.open_excel(worksheet)
    loader.load_all_sheets()

    # worksheet = config.get_temp_dir() + 'sample_data.xlsx'
    # loader = Loader()
    # loader.open_excel(worksheet)
    # loader.load_all_sheets()
    #loader.close()

def load_sheet():
    worksheet = config.get_temp_dir() + 'new.xlsx'
    loader = Loader()
    loader.open_excel(worksheet)
    loader.load_all_sheets()

if __name__ == '__main__':
    #
    # Note: Set the new database in config.json
    #
    load_sheet()