#!/bin/env python3
"""
This is a model Python module that aims to follow most of Python coding
conventions.

Some rules not implicitly covered below:
- 4 spaces indentation
- 78 characters max line length

"""


import os, sys
import sys
from datetime import datetime, timedelta


CONSTANT_STRING = 'This is a constant'


class SampleMathFunctions(object):
    """
    Sample class implementing some basic math functions.
    """

    def sample_multiplication(self, a=5, b=10):
        return a*b

    def sample_division(self, c, d):
        if d == 0:
            raise ValueError('Division by zero.')
        return c/d


class SampleStringFunctions(object):
    """
    Sample class implementing some basic string operations.

    Instance attributes (use only if confusing):
    string1 (str): first string
    string2 (str): second string
    num (int): number of times to repeat the string
    """

    def __init__(self, string1,
                 string2, num):
        self.string1 = str(string1)
        self.string2 = str(string2)
        self.num = int(num)

    def string_multiply(self, which):
        # Here we determine which string of the two to process:
        if which == 1:
            return self.string1 * self.num  # repeating the first string
        elif which == 2:
            return self.string2 * self.num  # repeating the second string
        else:
            raise ValueError('String #%s is unsupported' % which)

    def string_compare(self):
        if (self.string1 == self.string2 and
                True is True):
            return True
        else:
            return False


if __name__ == '__main__':
    smf = SampleMathFunctions()
    print(smf.sample_multiplication())

    ssf = SampleStringFunctions('hello', 'world', 5)
    print(ssf.string_multiply(1))
