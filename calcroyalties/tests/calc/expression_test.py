import unittest
from py_expression_eval import Parser

from src.calc.expression import Expression
from src.util.apperror import AppError
from src.database.data_structure import DataStructure


class TestExpresion(unittest.TestCase):

    def test_stuff(self):
        parser = Parser()
        v = parser.parse('m.myvalue * m.yourvalue').evaluate({"m.myvalue": 3, 'm.yourvalue': 4})
        print(v)

    def test_find_expression(self):
        expression = Expression()

        s = "no formula in here"
        self.assertRaises(AppError, expression.find_expression, s) # Note there is no expression

        s = "asdf =(abc + (def * 3)) more stuff in here"
        self.assertEqual((5, 22), expression.find_expression(s))

        s = "=(abc + (def * 3)) more stuff in here"
        self.assertEqual((0, 17), expression.find_expression(s))

        s = "=(abc + (def * 3))"
        self.assertEqual((0, 17), expression.find_expression(s))

        s = "asdf =(abc + (def * 3) more stuff in here" # Note the expression does not end
        self.assertRaises(AppError, expression.find_expression, s)

    def test_get_expression(self):
        expression = Expression()

        s = "no formula in here"
        self.assertRaises(AppError, expression.get_expression, s) # Note there is no expression

        s = "asdf =(abc + (def * 3)) more stuff in here"
        self.assertEqual("abc + (def * 3)", expression.get_expression(s))

    def test_evaluate_expression(self):
        expression = Expression()

        m = DataStructure()
        m.ProdMonth = 201703
        m.ProdVol = 100
        m.SalesVol = 90
        m.GJ = 1000

        s = "asdf =(prod + sales + gj) more stuff in here"
        self.assertEqual("abc + (def * 3)", expression.evaluate_expression(s, m))

    def test_var_list(self):
        expression = Expression()

        m = DataStructure()
        m.ProdMonth = 201703
        m.ProdVol = 100
        m.SalesVol = 90
        m.GJ = 1000

        rv = expression.lookup({"prod", "sales", "gj", "somevalue", "m.somevalue" }, m)

        print(rv)