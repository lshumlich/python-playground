import unittest
from database.testhelper import TestHelper

class DataObj(object):
    None

class Test(unittest.TestCase):

    def test_loadObjectCSVStyle(self):
        th = TestHelper()
        o = DataObj()
        s = \
"""
fld1,fld2,fld3,ival,fval
val1,val2,val3,1234,12.0
"""
        th.loadObjectCSVStyle(o,s)
        self.assertTrue(hasattr(o,'fld1'))
        self.assertFalse(hasattr(o,'fldx'))
        self.assertEqual(o.fld1,'val1')
        self.assertEqual(o.fld3,'val3')
        self.assertEqual(o.ival,1234)
        self.assertEqual(o.fval,12.0)

    def test_whatAmI(self):
        th = TestHelper()
        self.assertEqual(th.whatAmI('123.4'),123.4)
        self.assertEqual(th.whatAmI('1'),1)
        self.assertEqual(type(th.whatAmI('1')),int)
        self.assertEqual(th.whatAmI('asdf'),'asdf')
        

if __name__ == "__main__":
    unittest.main()