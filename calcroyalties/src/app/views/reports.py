from flask import Blueprint, render_template, abort

import config
from .permission_handler import PermissionHandler
from .main import get_proddate_int

reports = Blueprint('reports', __name__)


@reports.route('/reports/royalties')
#@PermissionHandler('well_view')
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
#@PermissionHandler('well_view')
def calc_list():
    db = config.get_database()
    statement = """SELECT * from calc, wellroyaltymaster,monthly
        where calc.wellid = wellroyaltymaster.id and
        calc.wellid = monthly.wellid  and
        calc.ProdMonth = monthly.ProdMonth
        order by calc.prodMonth,calc.wellid
    """
    result = db.select_sql(statement)
    print('we have found: ', len(result))
    if result:
        return render_template('reports/calclist.html', result=result)
    else:
        return "Nothing found"


@reports.route('/reports/wellroyaltymastermissing')
def wellroyaltymastermissing():
    try:
        db = config.get_database()
        statement = """SELECT * FROM WellRoyaltyMaster
                       WHERE WellEvent NOT IN (SELECT WellEvent FROM WellEventInfo)"""
        results = db.select_sql(statement)
        return render_template('/reports/wellroyaltymastermissing.html', result=results)
    except Exception as e:
        print(e)
        abort(404)

@reports.route('/reports/welleventinfomissing')
def welleventinfomissing():
    try:
        db = config.get_database()
        statement = """SELECT * FROM WellEventInfo
                       WHERE WellEvent NOT IN (SELECT WellEvent FROM WellRoyaltyMaster)"""
        results = db.select_sql(statement)
        return render_template('/reports/welleventinfomissing.html', result=results)
    except Exception as e:
        print(e)
        abort(404)

@reports.route('/reports/wellrane')
def wellrange():
    return render_template('/reports/wellrange.html')