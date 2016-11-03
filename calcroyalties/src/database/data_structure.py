#!/bin/env python3

"""
DataStructure is the base object for all the data objects in the system.
"""


class DataStructure(object):
    
    def __init__(self):
        self._format = Formatter(self)
        
    def __str__(self):
        return str(vars(self))
    
    def headers(self):
        d = vars(self)
        return list(d.keys())

    def data(self):
        d = vars(self)
        return list(d.values())

    # NOTE: Delete this method once we move to the new sql world
    @property
    def Lease(self):
        if hasattr(self, 'LeaseID'):
            lid = self.LeaseID
        else:
            lid = self.ID
        return '{}-{:04d}'.format(self.LeaseType, lid)


class Formatter(object):
    """
    Formatter: formats the attributes for various reports.
    """

    def __init__(self, data_obj):
        self.data_obj = data_obj
    
    @property
    def Lease(self):
        if hasattr(self.data_obj, 'LeaseID'):
            lid = self.data_obj.LeaseID
        else:
            lid = self.data_obj.ID
        return '{}-{:04d}'.format(self.data_obj.LeaseType, lid)

    @property
    def ProdMonth(self):
        dts = str(self.data_obj.ProdMonth)
        return dts[0:4]+'-'+dts[4:6]

    def yyyy_mm_dd(self, dt):
        if dt:
            return dt.strftime('%Y-%m-%d')
        else:
            return ""
