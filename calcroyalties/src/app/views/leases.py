from flask import Blueprint, render_template, abort, request, json, redirect, url_for, flash

import config
from .permission_handler import PermissionHandler
from .main import get_proddate

leases = Blueprint('leases', __name__)

@leases.route('/leases')
def search():
    if not request.args: return render_template('leases/search.html')
    try:
        db = config.get_database()
        argument_tables = {'Prov': 'Lease', 'ID': 'Lease'}  # allowed Property:Table pairs
        kwargs = dict((k, v) for k, v in request.args.items() if v and k in argument_tables)  # this is to get rid
        # of empty values coming from forms and convert multidict to dict and to check if argument is allowed
        search_arguments = ""
        for arg in kwargs:
            compound = argument_tables[arg] + '.' + arg + '=' + '"' + kwargs[arg] + '"'
            search_arguments += " AND " + compound
        statement = """SELECT * FROM Lease
                       WHERE DATE("{proddate}") BETWEEN Lease.StartDate and Lease.EndDate
                    """.format(proddate=get_proddate()) + search_arguments
        result = db.select_sql(statement)
        if result:
            return render_template('leases/search.html', results=result, search_terms=request.args.to_dict())
        else:
            flash('No matching leases found', 'error')
            return render_template('leases/search.html', search_terms=request.args.to_dict())
    except Exception as e:
        print(e)
        abort(404)

@leases.route('/leases/<lease_num>')
def details(lease_num):
    try:
        db = config.get_database()
        lease = db.select1('Lease', ID=lease_num)
        royaltymaster = db.select1('LeaseRoyaltyMaster', ID=lease_num)
        wellevent_statement = """SELECT WellEventInfo.* FROM WellEventInfo, WellLeaseLink
                       WHERE WellLeaseLink.LeaseID="%s"
                       AND WellEventInfo.WellEvent=WellLeaseLink.WellID"""
        # wellevents = db.select_sql(wellevent_statement % lease_num)  # not sure what the situation is here, None for now
        wellevents = None
        return render_template('leases/details.html', lease = lease, royaltymaster = royaltymaster, wellevents=wellevents)
    except Exception as e:
        print(e)
        abort(404)

"""
@leases.route('/api/leaseresults', methods=['GET', 'POST'])
def results():
    if not request.is_xhr: abort(404)
    try:
        db = config.get_database()
        req_data = request.get_json()
        results = db.select('Lease', **req_data)
        print(req_data, results)
        return render_template('leases/results.html', results = results)
    except Exception as e:
        print(e)
        return json.dumps({'success': False}), 404, {'ContentType': 'application/json'}
"""

"""
GET /leases - empty search form
GET /leases?searchparams - search results
GET /leases/1 - lease details
POST /leases - adds a new lease, returns new ID
POST /leases/1 - updates a lease, returns 200
DELETE /leases/1 - deletes a lease, returns 200
"""