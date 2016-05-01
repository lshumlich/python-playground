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