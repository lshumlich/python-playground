from src.util.apperror import AppError


class Incentives(object):
    def __init__(self):
        self.volume_array = []

    @staticmethod
    def index(start_date, prod_date):
        """ Determine the number of months between the start date and the current months production date"""
        start_year = int(start_date / 100)
        start_month = start_date - start_year * 100
        prod_year = int(prod_date / 100)
        prod_month = prod_date - prod_year * 100
        i = (((prod_year - start_year) * 12) + (prod_month - start_month))
        if i < 0:
            raise AppError('Incentive Start Date: ' + str(start_date) + ' must be before Prod Date: ' + str(prod_date))
        return i

    def volume(self, start_date, prod_date, volume):
        """
        A volume is being added or modified to the total incentive
        this will return what the total incentive volume is
        """
        print(len(self.volume_array))
        i = self.index(start_date, prod_date)
        print(i)
        while len(self.volume_array) <= i:
            self.volume_array.append(0.0)

        self.volume_array[i] = volume
        print('Volumes: ', self.volume_array)
        total_incentive = 0.0
        for v in self.volume_array:
            total_incentive += v
        return total_incentive
