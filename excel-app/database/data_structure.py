#!/bin/env python3

"""
DataStructure is the base object for all the data objects in the system.
"""


class DataStructure(object):
    
    def __init__(self):
        None
        
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
