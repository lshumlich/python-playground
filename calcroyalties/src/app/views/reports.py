import traceback
import sys
# import math
from flask import Blueprint, render_template, abort, request, json

import config
# from .permission_handler import PermissionHandler
from .main import get_proddate_int


reports = Blueprint('reports', __name__)


@reports.route('/reports/royalties')
# @PermissionHandler('well_view')
def royalties():
    db = config.get_database()
    proddate = get_proddate_int()
    statement = """SELECT * from calc, WellRoyaltyMaster where calc.EntityID = WellRoyaltyMaster.ID
                and calc.prodmonth = {proddate}""".format(proddate=proddate)
    result = db.select_sql(statement)
    if result:
        return render_template('reports/royalties.html', result=result)
    else:
        return "Nothing found"


@reports.route('/reports/calclist')
# @PermissionHandler('well_view')
def calc_list():
    db = config.get_database()
    statement = """SELECT calc.ID, calc.ExtractDate, calc.ProdMonth, calc.BaseNetRoyaltyValue,
        calc.GorrNetRoyaltyValue, calc.FNBandID, calc.FNReserveID, calc.LeaseID, calc.Entity,
        calc.EntityID, calc.RPBA, calc.Product, wrm.WellEvent
        from calc, wellroyaltymaster wrm
        where calc.EntityID = wrm.id
        order by calc.ExtractDate, calc.prodMonth, calc.EntityID
    """
    result = db.select_sql(statement)
    # print('we have found: ', len(result))
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


@reports.route('/reports/proofed')
def proofed():
    try:
        db = config.get_database()
        results = db.select_sql("SELECT * FROM Proofed order by ExtractDate, ProdMonth, LeaseID, Entity, EntityID, "
                                "Product, RPBA")
        error_no = 0
        proofed_no = 0
        for r in results:
            r.Message = None
            calc = db.select('Calc', ExtractDate=r.ExtractDate, ProdMonth=r.ProdMonth, LeaseID=r.LeaseID,
                             Entity=r.Entity, EntityID=r.EntityID, RPBA=r.RPBA, Product=r.Product)
            if len(calc) > 1:
                r.Message = 'More than one calc record. We have a system problem.'
            elif len(calc) == 0:
                r.Message = "Can't find a calc record"
            else:
                r.BaseNetRoyaltyValue = calc[0].BaseNetRoyaltyValue
                r.GorrNetRoyaltyValue = calc[0].GorrNetRoyaltyValue

                # r.Message = 'Proofed.'
                if abs(r.BaseRoyalty - calc[0].BaseNetRoyaltyValue) > .001:
                    r.Message = 'Royalty is not the Same'
                if abs(r.GorrRoyalty - calc[0].GorrNetRoyaltyValue) > .001:
                    r.Message = 'Royalty is not the Same'
            if r.Message:
                error_no += 1
            else:
                r.Message = 'Proofed'
                proofed_no += 1
        return render_template('/reports/proofed.html', result=results, errors=error_no, proofed=proofed_no)
    except Exception as e:
        print('***Error:', e)
        traceback.print_exc(file=sys.stdout)
        tb = traceback.format_exc()
        return "<h2>Error generating" + \
               '<plaintext>' + tb + '</plaintext>'
        # print(e)
        # traceback.print_exc(file=sys.stdout)
        # abort(404)


@reports.route('/reports/adrienne')
def adrienne():
    return render_template('/reports/adrienne.html')


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

    # print('--lfs()', request.args["batt"])
    db = config.get_database()
    # proddate = get_proddate_int()
    results = db.select("VolumetricInfo", Facility=request.args["batt"])

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
                wells.append({"name": r.FromTo})
            else:
                disps.append({"name": r.FromTo})

    facilities.sort(key=faclsort)
    # results.sort(key=lambda r: r.Key)
    results.sort(key=lambda x: x.Key)

    html = render_template('/reports/battdiagramvolinout.html', result=results, facility=request.args["batt"])
    data['html'] = html

    data['facilities'] = facilities
    data['wells'] = wells
    data['disps'] = disps
    data['batt'] = [{"name": request.args["batt"]}]
    data['count'] = len(results)
    # print('---lfs()--', wells)
    # print('---lfs()--->', len(results))
    # print(json.dumps(data))
    return json.dumps(data)


def faclsort(facl):
    f = facl['FromTo']
    if not f:
        f = ''
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
