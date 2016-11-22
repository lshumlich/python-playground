#!/bin/env python3

import unittest
from src.util.appdate import prod_month_to_date


class TestLoader(unittest.TestCase):
    def test_run(self):

        t = prod_month_to_date(201611)
        self.assertEqual(2016, t.year)
        self.assertEqual(11, t.month)
        self.assertEqual(1, t.day)
        self.assertEqual(12, t.hour)
        self.assertEqual(0, t.minute)
