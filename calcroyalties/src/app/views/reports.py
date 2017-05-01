import traceback
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
    statement = """SELECT * from calc, WellRoyaltyMaster where calc.wellid = WellRoyaltyMaster.ID
                and calc.prodmonth = {proddate}""".format(proddate=proddate)
    # statement = """SELECT * from calc, wellleaselink where calc.wellid = wellleaselink.wellid
    #             and calc.prodmonth = {proddate}""".format(proddate=proddate)
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
        calc.ProdMonth = monthly.ProdMonth and
        calc.Product = monthly.Product
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
        traceback.print_exc(file=sys.stdout)
        abort(404)

@reports.route('/reports/wellrange')
def wellrange():
    return render_template('/reports/wellrange.html')


@reports.route('/reports/battdiagram')
def battdiagram():
    # try:
    db = config.get_database()
    # statement = """SELECT distinct facility from VolumetricInfo"""
    statement = """SELECT facility, sum(volume) as totalVol from VolumetricInfo group by facility"""
    results = db.select_sql(statement)
    return render_template('/reports/battdiagram.html', result=results)
    # except Exception as e:
    #     print(e)
    #     abort(404)


@reports.route('/reports/lfs')
def lfs():

    print('--lfs()', request.args["batt"])
    db = config.get_database()
    proddate = get_proddate_int()
    results = db.select("VolumetricInfo", Facility = request.args["batt"])

    data = {}
    facilities = []
    wells = []
    disps = []
    unique = {}

    # print(results)
    for r in results:
        facl = {}
        facl['Facility'] = r.Facility
        facl['Activity'] = r.Activity
        facl['Product'] = r.Product
        facl['FromTo'] = r.FromTo
        facl['Volume'] = r.Volume
        setattr(r, 'InorOut', inorout.get(r.Activity, '?'))
        facl['InorOut'] = inorout.get(r.Activity, '?')
        facl['Key'] = faclsort(facl)
        setattr(r, 'Key', faclsort(facl))
        facilities.append(facl)
        if r.FromTo and r.FromTo not in unique:
            unique[r.FromTo] = 0
            if len(r.FromTo) > 12:
                wells.append({"name":r.FromTo})
            else:
                disps.append({"name":r.FromTo})

    facilities.sort(key=faclsort)
    results.sort(key=lambda r: r.Key)

    html = render_template('/reports/battdiagramvolinout.html', result=results, facility=request.args["batt"])
    data['html'] = html


    data['facilities'] = facilities
    data['wells'] = wells
    data['disps'] = disps
    data['batt'] = [{"name":request.args["batt"]}]
    data['count'] = len(results)
    print('---lfs()--', wells)
    # print('---lfs()--->', len(results))
    # print(json.dumps(data))
    return json.dumps(data)


def faclsort(facl):
    f = facl['FromTo']
    if not f : f = ''
    if facl['InorOut'] == '+':
        order = 1
    elif facl['InorOut'] == '?':
        order = 2
    else:
        order = 3
    return facl['Product'] + str(order) + f


inorout = {
    "PROD": "+",
    "REC": "+",
    "DISP": "-",
    "FUEL": "-"
}
