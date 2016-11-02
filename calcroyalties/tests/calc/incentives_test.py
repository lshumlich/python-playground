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

        self.assertEqual(-1, incentives.index(201601, 201512))

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

    def test_last_prod_date(self):
        incentives = Incentives()
        incentives.volume(201601, 201601, 100)
        self.assertEqual(201601, incentives.last_prod_date)

        self.assertEqual(200, incentives.volume(201601, 201701, 100))
        self.assertEqual(201701, incentives.last_prod_date)

        self.assertEqual(300, incentives.volume(201601, 201602, 100))
        self.assertEqual(201701, incentives.last_prod_date)

    def test_persisting_incentives(self):
        incentive_data = '{"start_date":201610,"last_prod_date":201701,"prod_volumes":[5,10,20,40]}'
        incentives = Incentives(incentive_data)
        self.assertEqual(75, incentives.total())

        self.assertEqual(85, incentives.volume(201610, 201611, 20))

        s = str(incentives)

        new_incentives = Incentives(s)
        self.assertEqual(85, new_incentives.total())
        self.assertEqual(95, new_incentives.volume(201610, 201611, 30))

    def test_change_start_date(self):
        incentives = Incentives()
        self.assertEqual(10, incentives.volume(201610, 201610, 10))
        self.assertEqual(10, incentives.volume_for(201610))
        self.assertEqual(0, incentives.volume_for(201608))
        self.assertEqual(0, incentives.volume_for(201612))

        self.assertEqual(11, incentives.volume(201601, 201601, 1))
        self.assertEqual(1, incentives.volume_for(201601))
        self.assertEqual(10, incentives.volume_for(201610))

        self.assertEqual(12, incentives.volume(201610, 201612, 2))
        self.assertEqual(15, incentives.volume(201610, 201701, 3))

        self.assertEqual(15, incentives.volume(201608, 201701, 3))
        self.assertEqual(19, incentives.volume(201608, 201608, 4))
        self.assertEqual(15, incentives.volume(201610, 201701, 3))
        self.assertEqual(17, incentives.volume(201610, 201701, 5))

    def test_get_dates(self):
        incentives = Incentives()

        self.assertEqual(10, incentives.volume(201610, 201701, 10))
        self.assertEqual([201610, 201611, 201612, 201701], incentives.get_dates())
