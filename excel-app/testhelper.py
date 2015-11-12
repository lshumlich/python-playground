#!/bin/env python3

from database import DataBase
import copy

class TestHelper(object):
    
    testWorkSheet = 'database.xlsx'
    database = None
    
    @staticmethod
    def getDataBase():
        if TestHelper.database == None:
            TestHelper.database = DataBase(TestHelper.testWorkSheet)
        return TestHelper.database
    
    @staticmethod
    def getMonthlyDataClone():
        return copy.copy(TestHelper.getDataBase().getMonthlyData())
