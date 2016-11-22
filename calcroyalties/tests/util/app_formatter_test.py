#!/bin/env python3

import unittest
from src.util.app_formatter import format_gorr


class TestAppFormater(unittest.TestCase):
    def test_format_gorr(self):

        self.assertEqual('', format_gorr(None))
        self.assertEqual('', format_gorr(''))
        self.assertEqual('Monthly Prod: (0.0-250:.02%) (250-300:.03%) (300-400:.04%) (400-500:.05%)(>500:.06%)',
                         format_gorr('mprod,250,.02,300,.03,400,.04,500,.05,0,.06'))
