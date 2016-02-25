#!/bin/env python3

"""
This module will connect to the sqlite database and return Python objects.
"""

import sqlite3

import config
from database.apperror import AppError
from database.data_structure import DataStructure


class DataObject(object):

    def __init__(self):
        self.dbi = config.get_database_instance()

    # Shared
    def get_table_headers(self, table_name):
        statement = 'PRAGMA table_info(' + table_name + ')'
        values = self.dbi.execute(statement)
        columns = []
        for row in values:
            columns.append(row[1])
        return(columns)

    def get_table_ids(self, table_name):
        statement = 'SELECT ID FROM %s' % table_name
        self.dbi.execute(statement)
        values = self.dbi.cursor.fetchall()
        result = []
        for row in values:
            result.append(row[0])
        return result

    def sql_to_object(self, table_name, input_list):
        header_row = self.get_table_headers(table_name)
        result = []
        for row in input_list:
            ds = DataStructure()
            result.append(ds)
            i = 0
            for cell in header_row:
                setattr(ds, cell, row[i])
                i += 1
        if len(result) == 1:
            return result[0]
        else:
            return result

    def universal_selector(self, table, **kwargs):
        """ Not used anywhere right now, just an idea. """
        if table not in self.dbi.get_table_names():
            raise AppError('Table %s is not in the database' % table)
        statement = "SELECT * FROM %s " % table
        if kwargs:
            statement += "WHERE"
            i = len(kwargs)
            for arg in kwargs:
                if arg in self.get_table_headers(table):
                    statement += ' "%s" = "%s" ' % (arg, str(kwargs[arg]))
                    i -= 1
                    if i > 0:
                        statement += 'AND'
                else:
                    raise AppError('No column "%s" in table "%s"' % (arg, table))
        self.dbi.execute(statement)
        result = self.dbi.cursor.fetchall()
        result = self.sql_to_object(table, result)
        return result

    def universal_updater(self, table, id, **kwargs):
        statement = 'UPDATE %s SET ' % table
        if table not in self.dbi.get_table_names():
            raise AppError('Trying to update table %s which does not exist' % table)
        if not kwargs:
            raise AppError('Trying to update table %s, no arguments received' % table)
        if id not in self.get_table_ids(table):
            raise AppError('Trying to update table %s, record with ID %i does not exist' % (table, id))
        i = len(kwargs)
        for arg in kwargs:
            if arg in self.get_table_headers(table):
                statement += '%s="%s"' % (arg, kwargs[arg])
                i -= 1
                if i > 0:
                    statement += ', '
            else:
                raise AppError('Trying to update column %s which is not in the table %s' % (arg, table))
        statement += ' WHERE ID = %i' % id
        print(statement)
        try:
            self.dbi.execute(statement)
        except:
            raise AppError('Some unhandled sqlite error occured')

    def universal_inserter(self, table, **kwargs):
        # we need to either use sqlite's rowid or to make our ID a primary key
        # then we need to make sure you can't insert a record without it
        if table not in self.dbi.get_table_names():
            raise AppError('Trying to insert into table %s which does not exist' % table)
        if not kwargs:
            raise AppError('Trying to insert into table %s, no arguments received' % table)
        statement = 'INSERT INTO %s (' % table
        i = len(kwargs)
        for arg in kwargs:
            if arg in self.get_table_headers(table):
                statement += '%s' % arg
                i -= 1
                if i > 0:
                    statement += ', '
            else:
                raise AppError('Trying to insert into column %s which is not in the table %s' % (arg, table))
        statement += ') VALUES ('
        i = len(kwargs)
        for arg in kwargs:
            statement += '"%s"' % kwargs[arg]
            i -= 1
            if i > 0:
                statement += ', '
        statement += ')'
        try:
            self.dbi.execute(statement)
        except:
            raise AppError('Some unhandled sqlite error occured')

    def universal_deleter(self, table, id):
        if table not in self.dbi.get_table_names():
            raise AppError('Trying to delete from table %s which does not exist' % table)
        if id not in self.get_table_ids(table):
            raise AppError('Trying to delete from table %s, record with ID %i does not exist' % (table, id))
        statement = 'DELETE FROM %s where ID = %i' % (table, id)
        try:
            self.dbi.execute(statement)
        except:
            raise AppError('Some unhandled sqlite error occured')

    # def get_object(self, table, object_id):
    #     """ Another experiment for the future. Will hopefully replace
    #         individual getters for each object type
    #     """
    #     statement = 'SELECT * FROM %s' % table
    #     if object_id:
    #         statement += ' WHERE ID = %i' % object_id
    #     self.dbi.execute(statement)
    #     result = self.dbi.cursor(fetchall)
    #     result = self.sql_to_object(table, result)
    #     return result

    # Wells
    def get_all_wells(self):
        statement = 'SELECT * FROM Well'
        self.dbi.execute(statement)
        result = self.dbi.cursor.fetchall()
        result = self.sql_to_object('Well', result)
        if result:
            return result
        else:
            raise AppError('Getting all wells failed')

    def get_well_by_id(self, well_id):
        statement = 'SELECT * FROM Well WHERE ID = %i' % well_id
        self.dbi.execute(statement)
        result = self.dbi.cursor.fetchall()
        result = self.sql_to_object('Well', result)
        if result:
            return result
        else:
            raise AppError('Well with ID %i not found' % well_id)

    def get_wells_by_lease(self, lease_id):
        statement = 'SELECT * FROM Well WHERE ID = %i' % lease_id
        self.dbi.execute(statement)
        result = self.dbi.cursor.fetchall()
        result = self.sql_to_object('Well', result)
        if result:
            return result
        else:
            raise AppError('Well with lease %i not found' % lease_id)

    def update_well(self, well_id, **kwargs):
        self.universal_updater('Well', well_id, **kwargs)


    # Leases
    def get_all_leases(self):
        statement = 'SELECT * FROM Lease'
        self.dbi.execute(statement)
        result = self.dbi.cursor.fetchall()
        result = self.sql_to_object('Lease', result)
        if result:
            return result
        else:
            raise AppError('Leases could not be loaded')

    def get_lease_by_id(self, lease_id):
        statement = 'SELECT * FROM Lease WHERE ID = %i' % lease_id
        self.dbi.execute(statement)
        result = self.dbi.cursor.fetchall()
        result = self.sql_to_object('Lease', result)
        if result:
            return result
        else:
            raise AppError('Lease with ID %i not found' % lease_id)

    def update_lease(self, lease_id, **kwargs):
        self.universal_updater('Lease', lease_id, **kwargs)

    # Royalty master
    def get_royalty_master(self, lease_id):
        statement = 'SELECT * FROM RoyaltyMaster WHERE LeaseID = %i' % lease_id
        self.dbi.execute(statement)
        result = self.dbi.cursor.fetchall()
        result = self.sql_to_object('RoyaltyMaster', result)
        if result:
            return result
        else:
            raise AppError('Royalty Master record for lease %i not found' % lease_id)

    # Monthly data
    def get_monthly_data(self):
        statement = 'SELECT * FROM Monthly'
        self.dbi.execute(statement)
        result = self.dbi.cursor.fetchall()
        result = self.sql_to_object('Monthly', result)
        return result

    def get_monthly_by_well(self, well_id):
        statement = 'SELECT * FROM Monthly WHERE WellId = %i' % well_id
        self.dbi.execute(statement)
        result = self.dbi.cursor.fetchall()
        result = self.sql_to_object('Monthly', result)
        if result:
            return result
        else:
            raise AppError('No monthly data for well %i' % well_id)

    def get_monthly_by_well_prodmonth_product(self, well_id, prod_month, product):
        statement = 'SELECT * FROM Monthly WHERE WellID = %i AND ProdMonth = %i AND Product = "%s"' % (well_id, prod_month, product)
        self.dbi.execute(statement)
        result = self.dbi.cursor.fetchall()
        result = self.sql_to_object('Monthly', result)
        if result:
            return result
        else:
            raise AppError('Monthly data for well %i, production month %i, product %s does not exist' % (well_id, prod_month, product))

    # ECON data
    def get_econ_oil_data(self, prod_month):
        statement = 'SELECT * FROM ECONData WHERE ProdMonth = %i' % prod_month
        self.dbi.execute(statement)
        result = self.dbi.cursor.fetchall()
        result = self.sql_to_object('ECONData', result)
        if result:
            return result
        else:
            raise AppError('No ECON oil data for production month %i' % prod_month)

    #Royalty calculation
    def get_royalty_calc(self, prod_month, well_id):
        statement = 'SELECT * FROM Calc WHERE ProdMonth = %i AND WellID = %i' % (prod_month, well_id)
        self.dbi.execute(statement)
        result = self.dbi.cursor.fetchall()
        result = self.sql_to_object('Calc', result)
        if result:
            return result
        else:
            raise AppError('No royalty calc data for production month %i, well %i' % (prod_month, well_id))
