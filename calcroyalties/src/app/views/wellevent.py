from flask import Blueprint, request, config, redirect, url_for, abort, render_template, flash

import config
from .permission_handler import PermissionHandler

wellevent = Blueprint('wellevent', __name__)

@wellevent.route('/wellevent/search', methods=['GET'])
def search():
    if not request.args: return render_template('wellevent/search.html')
    # values = {'Meridian': 'WellEvent', 'WellEvent'}
    # for arg in request.args:
    #     if arg in values:
    #         arg = "WellEvent."+arg

    db = config.get_database()
    statement = """SELECT WellEventInfo.WellEvent, WellEventInfo.Meridian, RTAHeader.RTPOperator, WellEventStatus.Status, BAInfo.CorpShortName
	FROM WellEventInfo, RTAHeader, WellEventStatus, BAInfo
	WHERE DATE('2016-04-01') BETWEEN WellEventInfo.StartDate AND WellEventInfo.EndDate AND WellEventInfo.WellEvent=RTAHeader.WellEvent
	AND DATE('2016-04-01') BETWEEN WellEventStatus.StartDate AND WellEventStatus.EndDate AND WellEventInfo.WellEvent=WellEventStatus.WellEvent
	AND DATE('2016-04-01') BETWEEN WellEventStatus.StartDate AND WellEventStatus.EndDate
	AND RTAHeader.RTPOperator=BAInfo.BAid AND DATE('2016-04-01') BETWEEN BAInfo.StartDate AND BAInfo.EndDate
    """
    results = db.select_sql(statement)
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
    statement = """SELECT Lease.* FROM Lease, WellLeaseLink WHERE WellLeaseLink.WellEvent="%s" AND Lease.ID=WellLeaseLink.LeaseID"""
    leases = db.select_sql(statement % wellevent_num)
    return render_template('wellevent/details.html', wellevent=wellevent, leases=leases)
    # except:
    #     abort(404)