#!/bin/env python3

import json

"""
DataStructure is the base object for all the data objects in the system.
"""


class DataStructure(object):
    
    def __init__(self, json_string=None):
        self._format = Formatter(self)
        if json_string:
            json.loads(json_string, object_hook=self.json_decode)
        
    def __str__(self):
        return str(vars(self))
    
    def headers(self):
        d = vars(self)
        return list(d.keys())

    def data(self):
        d = vars(self)
        return list(d.values())

    def json_decode(self, dictionary_data):
        for k in dictionary_data:
            setattr(self, k, dictionary_data[k])

    def json_dumps(self):
        d = dict(self.__dict__)
        del d['_format']
        return json.dumps(d, sort_keys=True)

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
