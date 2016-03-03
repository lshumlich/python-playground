#!/bin/env python3
"""
This module will connect to the sqlite database and return Python objects.
"""

import config
from database.apperror import AppError
from database.data_structure import DataStructure


class Database(object):

    def __init__(self):
        self.dbi = config.get_database_instance()
    
    def sql_to_object(self, table_name, input_list):
        header_row = self.dbi.get_column_names() # must run after the select statement
        result = []
        for row in input_list:
            ds=self.get_data_structure(table_name)
            setattr(ds, "_table_name", table_name)
            result.append(ds)
            i = 0
            for cell in header_row:
                setattr(ds, cell, row[i])
                i += 1
        return result
#         if len(result) == 1:
#             return result[0]
#         elif len(result) == 0:
#             return None
#         else:
#             return result

    def get_data_structure(self,table_name):
        """ This method must be called to create a valid database data structure. """ 
        ds = DataStructure()
        ds._table_name = table_name
        return ds

    def select(self, table, **kwargs):
        statement = "SELECT * FROM %s " % table
        if kwargs:
            statement += "WHERE"
            i = len(kwargs)
            for arg in kwargs:
                statement += " %s = '%s' " % (arg, str(kwargs[arg]))
                i -= 1
                if i > 0:
                    statement += 'AND'
        self.dbi.execute(statement)
#         print('The Value of x:',x)
        result = self.dbi.cursor.fetchall()
        result = self.sql_to_object(table, result)
        return result
        
    def to_db_value (self,value):
        
        if type(value) is str:
            return '"' + value +'"'
        elif type(value) is int or type(value) is float:
            return str(value)
        elif type(value) is bool:
            return '1' if (value) else '0';
        
        raise AppError('sqlite_database.to_db_value can not handle update of: ' + str(type(value)) + ':' + str(value))
    
    def insert(self, ds):
        dic = ds.__dict__
        
        to_insert_attr = '('
        to_insert_value  = '('
        
        for attr in dic:
            # This logic is to ignore attributes that start with _ and if the 
            # ID attribute is not givin in all the ways it can be not given.
            ignore = False
            if attr.startswith('_'):
                ignore = True 
            if attr == 'ID':
                if not dic[attr]:
                    ignore = True
                elif dic[attr] is str and dic[attr] == '': 
                    ignore = True
                elif dic[attr] is int and dic[attr] == 0:
                    ignore = True
                elif dic[attr] == '0':
                    ignore = True
            if not ignore:
                if len(to_insert_attr) > 1:
                    to_insert_attr += ','
                    to_insert_value += ','
                to_insert_attr += attr
                to_insert_value += self.to_db_value(dic[attr])
                
        to_insert_attr += ')'
        to_insert_value += ')'
        
        insert_stmt = 'insert into ' + ds._table_name + ' ' + to_insert_attr + ' values ' + to_insert_value
        
        self.dbi.execute(insert_stmt)
        ds.ID = self.dbi.get_id()
        
        self.dbi.commit()

    def update(self, ds):
        # Rule 1: all tables that can be updated must have an ID attrabute that is the primary key.
        orig_ds = self.select(ds._table_name, ID=ds.ID)
        if len(orig_ds) == 0:
            raise AppError('sqlite_database.update can not find: ' + str(ds.ID) + ' to update.')
            
        orig_dict = orig_ds[0].__dict__
        new_dict = ds.__dict__
        to_update = ''
        for attr in  orig_dict:
            if not attr.startswith('_'):
                if orig_dict[attr] != new_dict[attr]:
                    #todo: Do that audit of the records right here.
#                     print('difference:',attr,orig_dict[attr])
                    if len(to_update) > 0:
                        to_update += ','
                    to_update += attr + '=' + self.to_db_value(new_dict[attr])
                    
        if len(to_update) > 0:
            statement = 'UPDATE ' +  ds._table_name + ' SET ' + to_update + ' where ID = ' + str(ds.ID)
            self.dbi.execute(statement)
            self.dbi.commit()

    def delete(self, table, ds_id):
        statement = 'DELETE FROM %s where ID = %i' % (table, ds_id)
        self.dbi.execute(statement)
        self.dbi.commit()
        