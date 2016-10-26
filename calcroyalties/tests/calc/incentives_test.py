import unittest

from src.calc.incentives import Incentives
from src.util.apperror import AppError


class TestSaskRoyaltyCalc(unittest.TestCase):
    """
     Things to handle
     - If the incentive start date changes (Could have been a data entry error)
     - Storing and Retrieving incentive dates
    """
    def test_calc_index(self):
        incentives = Incentives()
        self.assertEqual(0, incentives.index(201601, 201601))
        self.assertEqual(1, incentives.index(201601, 201602))
        self.assertEqual(12, incentives.index(201601, 201701))
        self.assertEqual(1, incentives.index(201612, 201701))
        self.assertEqual(24, incentives.index(201601, 201801))
        self.assertEqual(25, incentives.index(201601, 201802))

        self.assertRaises(AppError, incentives.index, 201601, 201512)

    def test_calc_incentive_volume(self):
        incentives = Incentives()
        incentives.volume(201601, 201601, 100)

        self.assertEqual(100, incentives.volume(201601, 201601, 100))
        self.assertEqual(200, incentives.volume(201601, 201602, 100))
        self.assertEqual(300, incentives.volume(201601, 201612, 100))
        self.assertEqual(400, incentives.volume(201601, 201701, 100))
        """ the prod vol is decreasing by 50 therefore the total should be 50 less """
        self.assertEqual(350, incentives.volume(201601, 201601, 50))

        self.assertRaises(AppError, incentives.volume, 201601, 201512, 50)
