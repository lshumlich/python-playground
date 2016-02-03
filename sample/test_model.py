#!/bin/env python3
"""
This is a sample Python testing module.
"""

import unittest
import model


class SampleMathFunctionsTest(unittest.TestCase):
    """ Testing the SampleMathFunctions class """

    def setUp(self):
        """ 
        Use only when significant set-up is required 
        and if it's easier to read
        """
        self.smf = model.SampleMathFunctions()

    def test_sample_multiplication(self):
        self.assertEqual(self.smf.sample_multiplication(), 50)
        self.assertNotEqual(self.smf.sample_multiplication(), 20)

    def test_sample_division(self):
        self.assertEqual(self.smf.sample_division(5, 1), 5)
        self.assertRaises(ValueError, self.smf.sample_division, 5, 0)

    def tearDown(self):
        """ Dismantling the test harness. Again, use only when needed """
        None


class SampleStringFunctionsTest(unittest.TestCase):
    """ Testing the SampleStringFunctions class 
        Preferred way of organizing test code
    """

    def test_string_multiply(self):
        ssf = model.SampleStringFunctions('hello', 'world', 3)
        self.assertEqual(ssf.string_multiply(2), 'worldworldworld')
        self.assertEqual(ssf.string_multiply(1), 'hellohellohello')
        self.assertRaises(ValueError, ssf.string_multiply, 0)

    def test_string_compare(self):
        ssf = model.SampleStringFunctions('hello', 'test', 5)
        self.assertFalse(ssf.string_compare())

    def test_string_compare_ints(self):
#        ssf = model.SampleStringFunctions(1, 2, 3)
#        self.assertFalse(ssf.string_compare())  


if __name__ == '__main__':
    unittest.main()
