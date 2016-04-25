from flask import Blueprint, request, config, redirect, url_for, abort, render_template, flash

import config
from .permission_handler import PermissionHandler

wellevent = Blueprint('wellevent', __name__)

@wellevent.route('/wellevent/search', methods=['GET'])
def search():
    if not request.args: return render_template('wellevent/search.html')
    db = config.get_database()
    statement = """SELECT WellEventInfo.WellEvent, WellEventInfo.Meridian, RTAHeader.RTPOperator, WellEventStatus.Status, BAInfo.CorpShortName
	FROM WellEventInfo, RTAHeader, WellEventStatus, BAInfo
	WHERE DATE('2016-04-01') BETWEEN WellEventInfo.StartDate AND WellEventInfo.EndDate AND WellEventInfo.WellEvent=RTAHeader.WellEvent
	AND DATE('2016-04-01') BETWEEN WellEventStatus.StartDate AND WellEventStatus.EndDate AND WellEventInfo.WellEvent=WellEventStatus.WellEvent
	AND DATE('2016-04-01') BETWEEN WellEventStatus.StartDate AND WellEventStatus.EndDate
	AND RTAHeader.RTPOperator=BAInfo.BAid AND DATE('2016-04-01') BETWEEN BAInfo.StartDate AND BAInfo.EndDate"""

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
    # try:
    db = config.get_database()
    wellevent = db.select1('WellEventInfo', WellEvent=wellevent_num)
    statement_leases = """SELECT Lease.* FROM Lease, WellLeaseLink WHERE WellLeaseLink.WellEvent="%s" AND Lease.ID=WellLeaseLink.LeaseID"""
    leases = db.select_sql(statement_leases % wellevent_num)
    statement_facilities = """SELECT FacilityInfo.* FROM FacilityInfo, WellFacilitylink WHERE FacilityInfo.Facility=WellFacilitylink.Facility AND WellFacilitylink.WellEvent="%s" """
    facilities = db.select_sql(statement_facilities % wellevent_num)
    # facilities = db.select("WellFacilitylink", WellEvent=wellevent_num)
    return render_template('wellevent/details.html', wellevent=wellevent, leases=leases, facilities=facilities)
    # except:
    #     abort(404)