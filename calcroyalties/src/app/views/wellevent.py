from flask import Blueprint, request, config, redirect, url_for, abort, render_template, flash

import config
from .permission_handler import PermissionHandler
from src.util.apperror import AppError
from .main import get_proddate

wellevent = Blueprint('wellevent', __name__)

@wellevent.route('/wellevent/search', methods=['GET'])
def search():
    if not request.args: return render_template('wellevent/search.html')
    statement = """SELECT WellEventInfo.WellEvent, RTAHeader.RTPOperator, WellEventStatus.Status, BAInfo.CorpShortName, WellFacilitylink.Facility, FacilityInfo.Name
    FROM WellEventInfo
    LEFT OUTER JOIN RTAHeader ON WellEventInfo.WellEvent = RTAHeader.WellEvent
    LEFT OUTER JOIN WellEventStatus ON WellEventInfo.WellEvent = WellEventStatus.WellEvent
    LEFT OUTER JOIN BAInfo ON RTAHeader.RTPOperator = BAInfo.BAid
    LEFT OUTER JOIN WellFacilityLink ON WellEventInfo.WellEvent = WellFacilityLink.WellEvent
    LEFT OUTER JOIN FacilityInfo ON FacilityInfo.Facility = WellFacilityLink.Facility
    WHERE (DATE('{proddate}') BETWEEN WellEventInfo.StartDate AND WellEventInfo.EndDate OR WellEventInfo.StartDate IS NULL OR WellEventInfo.StartDate = '')
    AND (DATE('{proddate}') BETWEEN RTAHeader.StartDate AND RTAHeader.EndDate OR RTAHeader.StartDate IS NULL OR RTAHeader.StartDate = '')
    AND (DATE('{proddate}') BETWEEN WellEventStatus.StartDate AND WellEventStatus.EndDate OR WellEventStatus.StartDate IS NULL OR WellEventStatus.StartDate = '')
    AND (DATE('{proddate}') BETWEEN BAInfo.StartDate AND BAInfo.EndDate OR BAInfo.StartDate IS NULL OR BAInfo.StartDate = '')
    AND (DATE('{proddate}') BETWEEN WellFacilityLink.StartDate AND WellFacilityLink.EndDate OR WellFacilityLink.StartDate IS NULL OR WellFacilityLink.StartDate = '')
    AND (DATE('{proddate}') BETWEEN FacilityInfo.StartDate AND FacilityInfo.EndDate OR FacilityInfo.StartDate IS NULL OR FacilityInfo.StartDate = '')""".format(proddate=get_proddate())

    temp = """
    WHERE (WellEventInfo.StartDate <= DATE('{proddate}') AND WellEventInfo.EndDate >= DATE('{proddate}') OR WellEventInfo.StartDate IS NULL)
    AND (RTAHeader.StartDate <= DATE('{proddate}') AND RTAHeader.EndDate >= DATE('{proddate}') OR RTAHeader.StartDate IS NULL)
    AND (WellEventStatus.StartDate <= DATE('{proddate}') AND WellEventStatus.EndDate >= DATE('{proddate}') OR WellEventStatus.StartDate IS NULL)
    AND (BAInfo.StartDate <= DATE('{proddate}') AND BAInfo.EndDate >= DATE('{proddate}') OR BAInfo.StartDate IS NULL)
    AND (WellFacilityLink.StartDate <= DATE('{proddate}') AND WellFacilityLink.EndDate >= DATE('{proddate}') OR WellFacilityLink.StartDate IS NULL)
    AND (FacilityInfo.StartDate <= DATE('{proddate}') AND FacilityInfo.EndDate >= DATE('{proddate}') OR FacilityInfo.StartDate IS NULL)""".format(proddate=get_proddate())

    statement_old = """SELECT WellEventInfo.WellEvent, RTAHeader.RTPOperator, WellEventStatus.Status, BAInfo.CorpShortName, WellFacilitylink.Facility, FacilityInfo.Name
	FROM WellEventInfo, RTAHeader, WellEventStatus, BAInfo, WellFacilitylink, FacilityInfo
	WHERE DATE('{proddate}') BETWEEN WellEventInfo.StartDate AND WellEventInfo.EndDate
	AND DATE('{proddate}') BETWEEN RTAHeader.StartDate AND RTAHeader.EndDate
	AND DATE('{proddate}') BETWEEN WellEventStatus.StartDate AND WellEventStatus.EndDate
	AND DATE('{proddate}') BETWEEN BAInfo.StartDate AND BAInfo.EndDate
	AND DATE('{proddate}') BETWEEN WellFacilitylink.StartDate AND WellFacilitylink.EndDate
	AND DATE('{proddate}') BETWEEN WellEventInfo.StartDate AND WellEventInfo.EndDate
	AND WellEventInfo.WellEvent=RTAHeader.WellEvent
	AND WellEventInfo.WellEvent=WellEventStatus.WellEvent
	AND RTAHeader.RTPOperator=BAInfo.BAid
	AND FacilityInfo.Facility=WellFacilitylink.Facility
	AND WellEventInfo.WellEvent=WellFacilitylink.WellEvent""".format(proddate=get_proddate())

    db = config.get_database()
    # the following allows us to check incoming arguments against a dictionary of allowed ones and match them with a relevant table name:
    argument_tables = {'Meridian': 'WellEventInfo', 'WellEvent': 'WellEventInfo'}
    kwargs = dict((k, v) for k, v in request.args.items() if v)  # this is to get rid of empty values coming from forms
    search_arguments = ""
    for arg in kwargs:
        if arg in argument_tables:
            compound = argument_tables[arg] + '.' + arg + '=' + '"' + kwargs[arg] + '"'
            search_arguments += " AND " + compound

    results = db.select_sql(statement + search_arguments)
    if results:
        return render_template('wellevent/search.html', results=results, search_terms=request.args.to_dict())
    else:
        flash('No results found.')
        return render_template('wellevent/search.html')

@wellevent.route('/wellevent')
def handle_redirect():
    return redirect(url_for('wellevent.search'))

@wellevent.route('/wellevent/<wellevent_num>')
def details(wellevent_num):
    if not wellevent_num: redirect(url_for('wellevent.search'))
    db = config.get_database()
    statement = """SELECT WellEventInfo.*, RTAMineralOwnership.Product
    FROM WellEventInfo, RTAMineralOwnership
    WHERE DATE('{proddate}') BETWEEN WellEventInfo.StartDate AND WellEventInfo.EndDate
    AND DATE('{proddate}') BETWEEN RTAMineralOwnership.StartDate AND RTAMineralOwnership.EndDate
    AND WellEventInfo.WellEvent = RTAMineralOwnership.WellEvent
    AND WellEventInfo.WellEvent = '{wellevent}'""".format(proddate=get_proddate(), wellevent=wellevent_num)
    wellevent = db.select_sql(statement)[0]

    statement_volumetric = """SELECT * From VolumetricInfo WHERE FromTo = '{wellevent}' AND DATE(ProdMonth) = DATE('{proddate}')""".format(wellevent=wellevent_num, proddate=get_proddate())
    volumetric = db.select_sql(statement_volumetric)

    well = db.select1('Well', WellEvent=wellevent_num)

    statement_leases = """SELECT Lease.*, WellLeaseLink.PEFNInterest FROM Lease, WellLeaseLink WHERE WellLeaseLink.WellEvent="%s" AND Lease.ID=WellLeaseLink.LeaseID"""
    leases = db.select_sql(statement_leases % wellevent_num)

    statement_facilities = """SELECT FacilityInfo.* FROM FacilityInfo, WellFacilitylink WHERE FacilityInfo.Facility=WellFacilitylink.Facility AND WellFacilitylink.WellEvent="%s" """
    facilities = db.select_sql(statement_facilities % wellevent_num)
    return render_template('wellevent/details.html', wellevent=wellevent, leases=leases, facilities=facilities, volumetric=volumetric, well=well)