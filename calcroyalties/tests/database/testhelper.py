#!/bin/env python3

class TestHelper(object):
    
    testWorkSheet = 'database.xlsx'
    database = None


    def load_object_csv_style(self,o,s):
        ss = s.split('\n')
        header = ss[1].split(',')
        data = ss[2].split(',')
        i = 0
        for h in header:
            d = self.what_am_i(data[i])
            setattr(o, h, d)
            i += 1 
    
    def what_am_i(self,s):
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
    
