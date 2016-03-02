#!/bin/env python3

import unittest

from database.data_structure import DataStructure
from database.utils import Utils


class UtilsTest(unittest.TestCase):

    def test_obj_to_dict(self):
        ds = DataStructure()
        utils = Utils()
        ds.ID = 123
        ds.Name = "My Name"

        result = utils.obj_to_dict(ds, dict())
        self.assertEqual(result['ID'],123)
        self.assertEqual(result['Name'],'My Name')

        result = utils.obj_to_dict(ds)
        self.assertEqual(result['ID'],123)
        self.assertEqual(result['Name'],'My Name')

    def test_dict_to_obj(self):
        utils= Utils()
        d = dict()
        d['fld1'] = 'val1'
        d['fld2'] = 'val2'
        obj = utils.dict_to_obj(d)

        self.assertEqual(obj.fld1,'val1')
        self.assertEqual(obj.fld2,'val2')
        
        ds = DataStructure()
        ds.__dict__['myValue'] = 'Important'
        
        utils.dict_to_obj(d,ds)
        
        self.assertEqual(ds.myValue,'Important')
        self.assertEqual(ds.fld1,'val1')
        self.assertEqual(ds.fld2,'val2')
        
