import unittest
from py_expression_eval import Parser

class TestSaskRoyaltyCalc(unittest.TestCase):

    def test_stuff(self):
        parser = Parser()
        v = parser.parse('m.myvalue * m.yourvalue').evaluate({"m.myvalue":3, 'm.yourvalue':4})
        print(v)