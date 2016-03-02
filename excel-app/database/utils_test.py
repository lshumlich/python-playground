
import unittest

from database.data_structure import DataStructure
from database.utils import Utils


class Test(unittest.TestCase):


    def test_obj_dict(self):
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

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()