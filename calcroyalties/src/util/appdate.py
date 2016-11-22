#!/bin/env python3
from datetime import datetime

def prod_month_to_date(prod_date):
    y = int(prod_date / 100)
    m = prod_date - (y * 100)
    return datetime(y, m, 1, 12, 0)
