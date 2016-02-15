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

    WELL_TAB_NAME = 'Well'
    LEASE_TAB_NAME = 'Lease'

    def __init__(self):
        """ Nothing here for now"""

    def connect(self, db_name):
        self.conn = sqlite3.connect(db_name)
        self.cursor = self.conn.cursor()

    def execute(self, statement):
        return self.cursor.execute(statement)

    def close(self):
        self.conn.close()

    def table_headers(self, table_name):
        statement = 'PRAGMA table_info(' + table_name + ')'
        values = self.execute(statement)
        columns = []
        for row in values:
            columns.append(row[1])
        return(columns)

    def get_tables(self):
        statement = 'SELECT tbl_name FROM sqlite_master'
        values = self.execute(statement)
        result = []
        for x in values:
            for y in x:
                result.append(y)
        return result

    def load_sqlite_table(self, table_name):
        header_row = self.table_headers(table_name)
        statement = 'SELECT * FROM ' + table_name
        values = self.execute(statement)
        stack = []
        record_no = 0
        for row in values:
            record_no += 1
            ds = DataStructure()
            stack.append(ds)
            i = 0
            for cell in header_row:
                setattr(ds, cell, row[i])
                i += 1
            setattr(ds, 'RecordNumber', record_no)
            setattr(ds, 'SQLRow', row)
            setattr(ds, 'HeaderRow', header_row)
        return stack

    def universal_select(self, table, **kwargs):
        """ Not used anywhere right now, just an idea. """
        statement = "SELECT * FROM %s " % table
        if table in self.get_tables():
            i = len(kwargs)
            for arg in kwargs:
                statement += "WHERE" if i == len(kwargs) else None
                if arg in self.table_headers(table):
                    statement += ' "%s" = "%s" ' % (arg, str(kwargs[arg]))
                    i -= 1
                    if i > 0:
                        statement += ' AND '
                else:
                    raise AppError('No column "%s" in table "%s"' % (arg, table))
        else:
            raise AppError('Table %s is not in the database' % table)
        print(statement)

        values = self.execute(statement)
        results = []
        for v in values:
            results.append(v)
        return results



class DataWell(DataObject):

    def load_wells_from_sqlite(self):
        self.well_list = self.load_sqlite_table(self.WELL_TAB_NAME)
        self.wells = {}
        for w in self.well_list:
            self.wells[w.WellId] = w

    def get_all_wells(self):
        return self.well_list

    def get_well(self, well_id):
        try:
            return self.wells[well_id]
        except KeyError:
            raise AppError('Well with ID %s not found' % str(well_id))

    def get_wells_by_lease(self, lease_id):
        wells_by_lease = []
        for w in self.well_list:
            if w.LeaseID == lease_id:
                wells_by_lease.append(w)
        if wells_by_lease:
            return wells_by_lease
        else:
            raise AppError('Well with lease %s not found' % lease_id)


class DataLease(DataObject):

    def load_leases_from_sqlite(self):
        self.lease_list = self.load_sqlite_table(self.LEASE_TAB_NAME)
        self.leases = {}
        for l in self.lease_list:
            self.leases[l.LeaseID] = l

    def get_all_leases(self):
        return self.lease_list

    def get_lease(self, lease_id):
        try:
            return self.leases[lease_id]
        except:
            raise AppError('Lease with ID %s not found' % str(lease_id))


if __name__ == '__main__':
    do = DataObject()
    db = config.getFileDir() + 'test_database.db'
    do.connect(db)
    print(do.universal_select('Well', RoyaltyClassification2='Old Oil'))
