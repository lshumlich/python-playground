from flask import Blueprint, render_template, abort, request, json

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

@reports.route('/reports/wellrange')
def wellrange():
    return render_template('/reports/wellrange.html')


@reports.route('/reports/battdiagram')
def battdiagram():
    try:
        db = config.get_database()
        statement = """SELECT distinct facility from VolumetricInfo"""
        results = db.select_sql(statement)
        return render_template('/reports/battdiagram.html', result=results)
    except Exception as e:
        print(e)
        abort(404)


@reports.route('/reports/lfs')
def lfs():
    print('in lfs() -->', request.args)
    print('in lfs() -->', request.args["batt"])
    data = """
{
  "items": [
    {
      "key": "First",
      "value": 100
    },{
      "key": "Second",
      "value": false
    },{
      "key": "Last",
      "value": "Mixed"
    }
  ],
  "obj": {
    "number": 1.2345e-6,
    "enabled": true
  },
  "message": "Strings have to be in double-quotes."
}
"""
    db = config.get_database()
    proddate = get_proddate_int()
    results = db.select("VolumetricInfo", Facility = request.args["batt"])

    data = {}
    facilities = []
    print(results)
    for r in results:
        facl = {}
        facl['Facility'] = r.Facility
        facl['Activity'] = r.Activity
        facl['Product'] = r.Product
        facl['FromTo'] = r.FromTo
        facl['Volume'] = r.Volume
        facl['InorOut'] = inorout.get(r.Activity, '?')
        facl['Key'] = faclsort(facl)
        facilities.append(facl)

    facilities.sort(key=faclsort)

    data['facilities'] = facilities
    # print(json.dumps(data))
    return json.dumps(data)


def faclsort(facl):
    f = facl['FromTo']
    if not f : f = ''
    return facl['Product'] + facl['InorOut'] + f


inorout = {
    "PROD": "in",
    "REC": "in",
    "DISP": "out",
    "FUEL": "out"
}
