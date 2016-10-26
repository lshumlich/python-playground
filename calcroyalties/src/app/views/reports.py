from flask import Blueprint, render_template

import config
from .permission_handler import PermissionHandler
from .main import get_proddate_int

reports = Blueprint('reports', __name__)


@reports.route('/reports/royalties')
@PermissionHandler('well_view')
def royalties():
    db = config.get_database()
    proddate = get_proddate_int()
    statement = """SELECT * from calc, wellleaselink where calc.wellid = wellleaselink.wellid
                and calc.prodmonth = {proddate}""".format(proddate=proddate)
    result = db.select_sql(statement)
    if result:
        return render_template('reports/royalties.html', result=result)
    else:
        return "Nothing found"


@reports.route('/reports/calclist')
@PermissionHandler('well_view')
def calc_list():
    db = config.get_database()
    statement = """SELECT * from calc, wellroyaltymaster where calc.wellid = wellroyaltymaster.id"""
    result = db.select_sql(statement)
    print('we have found: ', len(result))
    if result:
        return render_template('reports/calclist.html', result=result)
    else:
        return "Nothing found"
