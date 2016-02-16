#!/bin/env python3

"""
This module will connect to the sqlite database and return Python objects.
"""

import sqlite3

import config
from database.apperror import AppError

class DataStructure(object):
    """ Nothing so far """


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

    def sql_to_object(self, table_name, input):
        header_row = self.get_table_headers(table_name)
        result = []
        for row in input:
            ds = DataStructure()
            result.append(ds)
            i = 0
            for cell in header_row:
                setattr(ds, cell, row[i])
                i += 1
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
        return self.dbi.cursor.fetchall()


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
