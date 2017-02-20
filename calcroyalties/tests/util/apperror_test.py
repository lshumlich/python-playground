#!/bin/env python3

import unittest
from src.util.apperror import AppError

class TestLoader(unittest.TestCase):
    def test_apperror(self):
        self.assertRaises(AppError, self.raise_app_error)
        try:
            self.raise_app_error()
        except AppError as e:
            self.assertEqual("'There is an apperror'", str(e))


    def raise_app_error(self):
        raise AppError("There is an apperror")
