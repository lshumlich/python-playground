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
        monthly.Heat = 65.01
        monthly.SalesPrice = 50.00
        monthly.TransRate = 10.00
        monthly.ProcessingRate = 5.00
        monthly.GCARate = 3.00
        calc = DataStructure()
        calc.RoyaltyPrice = 27.12

        rv = expression.lookup_vars({"prod", "sales", "gj", "heat", "price", "trans", "processing", "gca",
                                     "royalty_price", "somevalue", "m.monthval"}, monthly, calc)

        self.assertEqual(100, rv["prod"])
        self.assertEqual(90, rv["sales"])
        self.assertEqual(1000, rv["gj"])
        self.assertEqual(65.01, rv["heat"])
        self.assertEqual(50, rv["price"])
        self.assertEqual(10, rv["trans"])
        self.assertEqual(5, rv["processing"])
        self.assertEqual(3, rv["gca"])
        self.assertEqual(27.12, rv["royalty_price"])
        self.assertEqual(1234, rv["somevalue"])
        self.assertEqual(5678, rv["m.monthval"])

        self.assertRaises(AppError, expression.lookup_vars, {"notfooundvalue"}, monthly)

        monthly.GJ = None
        self.assertRaises(AppError, expression.lookup_vars, {"gj", "sales"}, monthly)

    def test_evaluate_and_resolve_expression(self):
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
        monthly.Heat = 65.01

        s = "asdf =(prod + sales + gj + heat + somevalue + m.monthval) more stuff in here"

        self.assertEqual(1196 + 65.01, expression.evaluate_expression(s, monthly))
        self.assertEqual("asdf =(100 + 90 + 1000 + 65.01 + 2 + 4) more stuff in here", expression.resolve_expression(s, monthly))

        s = "asdf =(prod + sales + gj + notfoundvalue) more stuff in here"
        self.assertRaises(AppError, expression.evaluate_expression, s, monthly)
