#!/bin/env python3

from database import DataBase
from apperror import AppError
import copy
import io

class TestHelper(object):
    
    testWorkSheet = 'database.xlsx'
    database = None


    def loadObjectCSVStyle(self,o,s):
        ss = s.split('\n')
        header = ss[1].split(',')
        data = ss[2].split(',')
        i = 0
        for h in header:
            d = self.whatAmI(data[i])
            setattr(o, h, d)
            i += 1 
    
    def whatAmI(self,s):
        "utility to Convert strings to float, int, or leave as a string"

        try:
            return int(s)
        except ValueError:
            None

        try:
            return float(s)
        except ValueError:
            None
        return s
    
    """
 These methods must be rethought out. Not sure we should do this.     
    @staticmethod
    def getDataBase():
        if TestHelper.database == None:
            TestHelper.database = DataBase(TestHelper.testWorkSheet)
        return TestHelper.database
   
    @staticmethod
    def getMonthlyDataClone():
        return copy.copy(TestHelper.getDataBase().getMonthlyData())
    """ 

