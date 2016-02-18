#!/bin/env python3

"""
This module will connect to the sqlite database and return Python objects.
"""

import sqlite3

import config
from database.apperror import AppError

class DataStructure(object):
    def __str__(self):
        return str(vars(self))


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

    def universal_select(self, table, **kwargs):
        """ Not used anywhere right now, just an idea. """
        statement = "SELECT * FROM %s " % table
        if table in self.dbi.get_table_names():
            if kwargs:
                statement += "Where"
            i = len(kwargs)
            for arg in kwargs:
                if arg in self.get_table_headers(table):
                    statement += ' "%s" = "%s" ' % (arg, str(kwargs[arg]))
                    i -= 1
                    if i > 0:
                        statement += 'AND'
                else:
                    raise AppError('No column "%s" in table "%s"' % (arg, table))
        else:
            raise AppError('Table %s is not in the database' % table)

        self.dbi.execute(statement)
        result = self.dbi.cursor.fetchall()
        result = self.sql_to_object(table, result)
        return result

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
            raise AppError('Wells could not be loaded')

    def get_well_by_id(self, well_id):
        statement = 'SELECT * FROM Well WHERE WellId = %i' % well_id
        self.dbi.execute(statement)
        result = self.dbi.cursor.fetchall()
        result = self.sql_to_object('Well', result)
        if result:
            return result
        else:
            raise AppError('Well with ID %i not found' % well_id)

    def get_wells_by_lease(self, lease_id):
        statement = 'SELECT * FROM Well WHERE LeaseID = %i' % lease_id
        self.dbi.execute(statement)
        result = self.dbi.cursor.fetchall()
        result = self.sql_to_object('Well', result)
        if result:
            return result
        else:
            raise AppError('Well with lease %i not found' % lease_id)


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
        statement = 'SELECT * FROM Lease WHERE LeaseID = %i' % lease_id
        self.dbi.execute(statement)
        result = self.dbi.cursor.fetchall()
        result = self.sql_to_object('Lease', result)
        if result:
            return result
        else:
            raise AppError('Lease with ID %i not found' % lease_id)

    #Royalty master
    def get_royalty_master(self, lease_id):
        statement = 'SELECT * FROM RoyaltyMaster WHERE LeaseID = %i' % lease_id
        self.dbi.execute(statement)
        result = self.dbi.cursor.fetchall()
        result = self.sql_to_object('RoyaltyMaster', result)
        if result:
            return result
        else:
            raise AppError('Royalty Master record for lease %i not found' %
                    lease_id)

    #Monthly data
    def get_monthly_data(self):
        statement = 'SELECT * FROM Monthly'
        self.dbi.execute(statement)
        result = self.dbi.cursor.fetchall()
        result = self.sql_to_object('Monthly', result)
        return iter(result)

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

    #ECON data
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
