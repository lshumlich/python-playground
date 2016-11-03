import json

from src.util.apperror import AppError


class Incentives(object):
    def __init__(self, incentive_data=dict()):
        if incentive_data:
            data = json.loads(incentive_data)
            self.start_date = data["start_date"]
            self.volume_array = data["prod_volumes"]
            self.last_prod_date = data["last_prod_date"]
        else:
            self.volume_array = []
            self.start_date = 0
            self.last_prod_date = 0

    def __str__(self):
        data = dict()
        data["start_date"] = self.start_date
        data["prod_volumes"] = self.volume_array
        data["last_prod_date"] = self.last_prod_date
        return json.dumps(data)

    @staticmethod
    def index(start_date, prod_date):
        """ Determine the number of months between the start date and the current months production date"""
        start_year = int(start_date / 100)
        start_month = start_date - start_year * 100
        prod_year = int(prod_date / 100)
        prod_month = prod_date - prod_year * 100
        i = (((prod_year - start_year) * 12) + (prod_month - start_month))
        return i

    def volume(self, start_date, prod_date, volume):
        """
        A volume is being added or modified to the total incentive
        this will return what the total incentive volume is
        """
        if start_date > prod_date:
            raise AppError('Incentive Start Date: ' + str(start_date) + ' must be before Prod Date: ' + str(prod_date))

        if self.start_date is not start_date:
            if start_date > prod_date:
                raise AppError('Incentive Start Date: ' + str(start_date) +
                               ' must be before Prod Date: ' + str(prod_date))
            self.start_date_changed(start_date)

        i = self.index(start_date, prod_date)
        while len(self.volume_array) <= i:
            self.volume_array.append(0.0)

        self.volume_array[i] = volume
        if prod_date > self.last_prod_date:
            self.last_prod_date = prod_date

        return self.total()

    def start_date_changed(self, start_date):
        if self.start_date == 0:
            self.start_date = start_date
            return

        i = self.index(self.start_date, start_date)
        while i < 0:
            # add to the beginning
            self.volume_array.insert(0, 0)
            i += 1

        while i > 0:
            # remove from the front
            self.volume_array.pop(0)
            i -= 1

        self.start_date = start_date

    def volume_for(self, prod_date):
        if prod_date < self.start_date or prod_date > self.last_prod_date:
            return 0
        i = self.index(self.start_date, prod_date)
        return self.volume_array[i]

    def total(self):
        total_incentive = 0.0
        for v in self.volume_array:
            total_incentive += v
        return total_incentive

    def get_dates(self):
        date = self.start_date
        yy = int(date / 100)
        mm = date - (yy * 100)
        date_list = []
        while date <= self.last_prod_date:
            date_list.append(date)
            mm += 1
            if mm == 13:
                yy += 1
                mm = 1
            date = (yy * 100) + mm
        return date_list

    def print_volumes(self):
        for d, e in zip(self.get_dates(), self.volume_array):
            print("Vol -->", d, e)
