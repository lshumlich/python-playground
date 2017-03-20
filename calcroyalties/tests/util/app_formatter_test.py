#!/bin/env python3

import unittest
from src.util.app_formatter import format_gorr


class TestAppFormater(unittest.TestCase):
    def test_format_gorr(self):

        self.assertEqual('', format_gorr(None))
        self.assertEqual('', format_gorr(''))

        self.assertEqual('Monthly Prod: (<=250: 2.5%) (<=300: 3.0%) (<=400: 4.0%) (<=500: 5.0%)(>500: 6.0%)',
                         format_gorr('mprod,250,.025,300,.03,400,.04,500,.05,0,.06'))

        self.assertEqual('Monthly Prod: (<=250: 2.5%) (<=300: 3.0%) (<=400: 4.0%) (<=500: 5.0%)(>500: 6.0%)',
                         format_gorr('mprod,250,.025,300,.03,400,.04,500,.05,0,.06'))
        self.assertEqual('Daily Prod: (<=250: 2.5%) (<=300: 3.0%) (<=400: 4.0%) (<=500: 5.0%)(>500: 6.0%)',
                         format_gorr('dprod,250,.025,300,.03,400,.04,500,.05,0,.06'))
        self.assertEqual('Revenue: (<=250: 2.5%) (<=300: 3.0%) (<=400: 4.0%) (<=500: 5.0%)(>500: 6.0%)',
                         format_gorr('rev,250,.025,300,.03,400,.04,500,.05,0,.06'))
        self.assertEqual('=(prod - sales + gj): (<=250: 2.5%) (<=300: 3.0%) (<=400: 4.0%) (<=500: 5.0%)(>500: 6.0%)',
                         format_gorr('=(prod - sales + gj),250,.025,300,.03,400,.04,500,.05,0,.06'))


