from flask import Blueprint, request, config, redirect, url_for, abort, render_template, flash, Response
import json, io, csv

import config
from .permission_handler import PermissionHandler
from src.util.apperror import AppError
from .main import get_proddate

wellevents = Blueprint('wellevents', __name__)

@wellevents.route('/wellevents', methods=['GET'])
def search():
    if not request.args: return render_template('wellevents/search.html')
    statement = """SELECT WellEventInfo.WellEvent, RTAHeader.RTPOperator, WellEventStatus.Status, WellLicence.Licensee, BAInfo.CorpShortName, WellFacilitylink.Facility, FacilityInfo.Name, WellEventLoc.Lat, WellEventLoc.Long
    FROM WellEventInfo
    LEFT OUTER JOIN RTAHeader ON WellEventInfo.WellEvent = RTAHeader.WellEvent
    AND (DATE('{proddate}') BETWEEN RTAHeader.StartDate AND RTAHeader.EndDate OR RTAHeader.StartDate IS NULL OR RTAHeader.StartDate = '')
    LEFT OUTER JOIN WellEventStatus ON WellEventInfo.WellEvent = WellEventStatus.WellEvent
    AND (DATE('{proddate}') BETWEEN WellEventStatus.StartDate AND WellEventStatus.EndDate OR WellEventStatus.StartDate IS NULL OR WellEventStatus.StartDate = '')
    LEFT OUTER JOIN BAInfo ON RTAHeader.RTPOperator = BAInfo.BAid
    AND (DATE('{proddate}') BETWEEN BAInfo.StartDate AND BAInfo.EndDate OR BAInfo.StartDate IS NULL OR BAInfo.StartDate = '')
    LEFT OUTER JOIN WellFacilityLink ON WellEventInfo.WellEvent = WellFacilityLink.WellEvent
    AND (DATE('{proddate}') BETWEEN WellFacilityLink.StartDate AND WellFacilityLink.EndDate OR WellFacilityLink.StartDate IS NULL OR WellFacilityLink.StartDate = '')
    LEFT OUTER JOIN FacilityInfo ON FacilityInfo.Facility = WellFacilityLink.Facility
    AND (DATE('{proddate}') BETWEEN FacilityInfo.StartDate AND FacilityInfo.EndDate OR FacilityInfo.StartDate IS NULL OR FacilityInfo.StartDate = '')
    LEFT OUTER JOIN WellEventLoc ON WellEventInfo.WellEvent = WellEventLoc.WellEvent
    LEFT OUTER JOIN WellInfo ON WellEventInfo.Well = WellInfo.Well
    AND (DATE('{proddate}') BETWEEN WellInfo.StartDate AND WellInfo.EndDate OR WellInfo.StartDate IS NULL OR WellInfo.StartDate = '')
    LEFT OUTER JOIN WellLicence ON WellLicence.WellLicence = WellInfo.WellLicence
    AND (DATE('{proddate}') BETWEEN WellLicence.StartDate AND WellLicence.EndDate OR WellLicence.StartDate IS NULL OR WellLicence.StartDate = '')
    WHERE (DATE('{proddate}') BETWEEN WellEventInfo.StartDate AND WellEventInfo.EndDate OR WellEventInfo.StartDate IS NULL OR WellEventInfo.StartDate = '')""".format(proddate=get_proddate())

    db = config.get_database()
    # the following allows us to check incoming arguments against a dictionary of allowed ones and match them with a relevant table name:
    argument_tables = {'WellEvent': 'WellEventInfo', 'Licensee': 'WellLicence', 'RTPOperator': 'RTAHeader', 'LSD': 'WellEventInfo', 'Section': 'WellEventInfo', 'Township': 'WellEventInfo', 'Range': 'WellEventInfo', 'Meridian': 'WellEventInfo'}
    kwargs = dict((k, v) for k, v in request.args.items() if v)  # this is to get rid of empty values coming from forms
    search_arguments = ""
    for arg in kwargs:
        if arg in argument_tables:
            compound = argument_tables[arg] + '.' + arg + '=' + '"' + kwargs[arg] + '"'
            search_arguments += " AND " + compound

    results = db.select_sql(statement + search_arguments)
    d = request.args.to_dict()
    output = 'browse'
    print('The Request is:',request.args.to_dict())
    if 'Output' in d:
        if d['Output'] == 'map':
            output = "map"
        elif d['Output'] == 'excel':
            output = "excel"
    print('The output is:',output)
    if results:
        if output == 'map':
            points = []
            for result in results:
                if result.Long:
                    json_obj = {}
                    json_obj['type'] = 'Feature'
                    json_obj['properties'] = {}
                    json_obj['properties']['name'] = result.WellEvent
                    json_obj['properties']['popupContent'] = '<b>%s</b> <br> Pool Name: %s<br><a href="/wellevent/%s">Details</a>' % (
                        result.WellEvent, result.RTPOperator, result.WellEvent)
                    json_obj['geometry'] = {}
                    json_obj['geometry']['type'] = 'Point'
                    json_obj['geometry']['coordinates'] = [round(result.Long * -1, 5), round(result.Lat, 5)]
                    points.append(json_obj)
            print('***** points: ', json.dumps(points))
            print('Center is...:',center_point(points))
            return render_template('map.html', results=json.dumps(points), center=center_point(points))

        elif output == 'excel':
            """ Export relies on python's csv module to generate csv, StringIO writer to simulate a file for csv,
                as we don't need to save it on hard drive, and dbi.execute and cursor to get raw results of a query
                as that's what we need for csv to work properly"""
            db.dbi.execute(statement + search_arguments)
            output = io.StringIO()
            writer = csv.writer(output, quoting=csv.QUOTE_NONNUMERIC)
            writer.writerow([i[0] for i in db.dbi.cursor.description])
            writer.writerows(db.dbi.cursor)
            return Response(output.getvalue(), mimetype="text/csv", headers={"Content-disposition": "attachment; filename=WellEvent_export.csv"})

        else:
            return render_template('wellevents/search.html', results=results, search_terms=request.args.to_dict())
    else:
        flash('No well events found.', 'error')
        return render_template('wellevents/search.html', search_terms=request.args.to_dict())

@wellevents.route('/wellevents/<wellevent_num>')
def details(wellevent_num):
    if not wellevent_num: redirect(url_for('wellevents.search'))
    try:
        db = config.get_database()
        statement="""SELECT WellEventInfo.*, RTAMineralOwnership.Product
        FROM WellEventInfo
        LEFT OUTER JOIN RTAMineralOwnership ON WellEventInfo.WellEvent = RTAMineralOwnership.WellEvent
        AND (DATE('{proddate}') BETWEEN RTAMineralOwnership.StartDate AND RTAMineralOwnership.EndDate)
        WHERE (DATE('{proddate}') BETWEEN WellEventInfo.StartDate AND WellEventInfo.EndDate)
        AND WellEventInfo.WellEvent = '{wellevent}'""".format(proddate=get_proddate(), wellevent=wellevent_num)
        wellevent = db.select_sql(statement)[0]
    except Exception as e:
        print(e)
        abort(404)

    statement_volumetric = """SELECT * From VolumetricInfo WHERE FromTo = '{wellevent}' AND DATE(ProdMonth) = DATE('{proddate}')""".format(wellevent=wellevent_num, proddate=get_proddate())
    volumetric = db.select_sql(statement_volumetric)

    try:
        well = db.select1('WellRoyaltyMaster', WellEvent=wellevent_num)

        statement_leases = """SELECT Lease.*, WellLeaseLink.PEFNInterest FROM Lease, WellLeaseLink WHERE WellLeaseLink.WellID="%s" AND Lease.ID=WellLeaseLink.LeaseID"""
        leases = db.select_sql(statement_leases % well.ID)

        statement_facilities = """SELECT FacilityInfo.* FROM FacilityInfo, WellFacilitylink WHERE FacilityInfo.Facility=WellFacilitylink.Facility AND WellFacilitylink.WellEvent="%s" """
        facilities = db.select_sql(statement_facilities % wellevent_num)
    except Exception as e:
        print(e)
        pass

    return render_template('wellevent/details.html', wellevent=wellevent, leases=leases, facilities=facilities, volumetric=volumetric, well=well)

def center_point(points):
    x,y  = points[0]['geometry']['coordinates']
    ux = x
    lx = x
    uy = y
    ly = y
    # print('---start',x,y)
    for point in points:
        x,y = point['geometry']['coordinates']
        if x > ux : ux = x
        if x < lx : lx = x
        if y > uy : uy = y
        if y < ly : ly = y
        # print('---',point['geometry']['coordinates'])

    # print('+++', ux, lx)
    # print('+++', uy, ly)
    return (lx + ((ux - lx) / 2)), (ly + ((uy - ly) / 2))