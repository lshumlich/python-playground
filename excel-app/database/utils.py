#!/bin/env python3
import json

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


    def json_decode(self,req):
        """
        This is used primarly in the browser app. 
        Do not remove this method. In the app we could use request.json 
        instead of all
        this but... and it's a big but... flask unit testing does not 
        suport the request.json method we wrote this.
        """
        reqDataBytes = req.data
        reqDataString = reqDataBytes.decode(encoding='UTF-8')
        return json.loads(reqDataString)
            