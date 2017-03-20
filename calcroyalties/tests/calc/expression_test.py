import unittest
from py_expression_eval import Parser

from src.calc.expression import Expression
from src.util.apperror import AppError
from src.database.data_structure import DataStructure
from tests.database.sqlite_utilities_test import DatabaseUtilities


class TestExpresion(unittest.TestCase):

    def test_stuff(self):
        parser = Parser()
        v = parser.parse('m.myvalue * m.yourvalue').evaluate({"m.myvalue": 3, 'm.yourvalue': 4})
        print(v)

    def test_find_expression(self):
        expression = Expression()

        s = "no formula in here"
        self.assertRaises(AppError, expression.find_expression, s)  # Note there is no expression

        s = "asdf =(abc + (def * 3)) more stuff in here"
        self.assertEqual((5, 22), expression.find_expression(s))

        s = "=(abc + (def * 3)) more stuff in here"
        self.assertEqual((0, 17), expression.find_expression(s))

        s = "=(abc + (def * 3))"
        self.assertEqual((0, 17), expression.find_expression(s))

        s = "asdf =(abc + (def * 3) more stuff in here"  # Note the expression does not end
        self.assertRaises(AppError, expression.find_expression, s)

    def test_get_expression(self):
        expression = Expression()

        s = "no formula in here"
        self.assertRaises(AppError, expression.get_expression, s)  # Note there is no expression

        s = "asdf =(abc + (def * 3)) more stuff in here"
        self.assertEqual("abc + (def * 3)", expression.get_expression(s))

    def test_lookup_vars(self):
        expression = Expression()

        util = DatabaseUtilities()
        util.delete_lookups()
        util.insert_lookups('somevalue', 0, 1234)
        util.insert_lookups('m.monthval', 201703, 5678)

        monthly = DataStructure()
        monthly.ProdMonth = 201703
        monthly.ProdVol = 100
        monthly.SalesVol = 90
        monthly.GJ = 1000

        rv = expression.lookup_vars({"prod", "sales", "gj", "somevalue", "m.monthval"}, monthly)

        self.assertEqual(100, rv["prod"])
        self.assertEqual(90, rv["sales"])
        self.assertEqual(1000, rv["gj"])
        self.assertEqual(1234, rv["somevalue"])
        self.assertEqual(5678, rv["m.monthval"])

        self.assertRaises(AppError, expression.lookup_vars, {"notfooundvalue"}, monthly)

        monthly.GJ = None
        self.assertRaises(AppError, expression.lookup_vars, {"gj", "sales"}, monthly)

    def test_evaluate_expression(self):
        expression = Expression()

        util = DatabaseUtilities()
        util.delete_lookups()
        util.insert_lookups('somevalue', 0, 2)
        util.insert_lookups('m.monthval', 201703, 4)

        monthly = DataStructure()
        monthly.ProdMonth = 201703
        monthly.ProdVol = 100
        monthly.SalesVol = 90
        monthly.GJ = 1000

        s = "asdf =(prod + sales + gj + somevalue + m.monthval) more stuff in here"

        self.assertEqual(1196, expression.evaluate_expression(s, monthly))
        self.assertEqual("asdf =(100 + 90 + 1000 + 2 + 4) more stuff in here", expression.resolve_expression(s, monthly))

        s = "asdf =(prod + sales + gj + notfoundvalue) more stuff in here"
        self.assertRaises(AppError, expression.evaluate_expression, s, monthly)
