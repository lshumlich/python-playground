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
        return '{}-{:04d}'.format(self.LeaseType,lid)

"""
Formatter: formats the attrabutes for various reports. 
"""

class Formatter(object):
    
    def __init__(self, dataObj):
        self.dataObj = dataObj
    
    @property
    def Lease(self):
        if hasattr(self.dataObj, 'LeaseID'):
            lid = self.dataObj.LeaseID
        else:
            lid = self.dataObj.ID
        return '{}-{:04d}'.format(self.dataObj.LeaseType,lid)

    @property
    def ProdMonth(self):
        dts = str(self.dataObj.ProdMonth)
        return dts[0:4]+'-'+dts[4:6]

    def yyyy_mm_dd(self, dt):
        if dt:
            return dt.strftime('%Y-%m-%d')
        else:
            return ""