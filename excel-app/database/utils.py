#!/bin/env python3

from database.data_structure import DataStructure
class Utils(object):
    
    def obj_to_dict(self,obj,dic = None):
        """ 
        This will append or create a dictionary object with property attributes of an object
        The dictionary object is returned for convenience. 
        """
        if not dic:
            dic = dict()
        for attr in obj.__dict__:
            if not attr.startswith('_'):
                dic[attr] =obj. __dict__[attr]
        return dic

    def dict_to_obj(self,dic,obj=None):
        if not obj:
            obj = DataStructure()
        for k in dic:
            obj.__dict__[k] = dic[k]
            
        return obj
        