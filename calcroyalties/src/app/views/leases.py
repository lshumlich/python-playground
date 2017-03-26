from flask import Blueprint, render_template, abort, request, json, redirect, url_for, flash

import config
from src.database.data_structure import DataStructure
from .permission_handler import PermissionHandler
from .main import get_proddate

leases = Blueprint('leases', __name__)

@leases.route('/leases/')
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

@leases.route('/leases/<lease_num>', methods=['GET', 'POST'])
def details(lease_num):
    db = config.get_database()
    if request.method == 'POST' and request.form['action'] == 'delete':
        print(request.form)
        print('about to delete')
        try:
            lease_id = int(request.form['ID'])
            print(lease_id)
            db.delete('Lease', lease_id)
            db.delete('LeaseRoyaltyMaster', lease_id)
            flash('Successfully deleted lease ' + str(lease_id))
            return redirect(url_for('leases.search'))
        except Exception as e:
            print('Failed to delete lease ' + request.form['ID'], e)
            flash('Failed to delete lease ' + request.form['ID'])
            return redirect(url_for('leases.search'))
    elif request.method == 'POST' and request.form['action'] == 'update':
        print('about to update')
        ds = db.select1('Lease', ID=lease_num)
        print(ds)
        try:
            for i in request.form:
                if i != 'action':
                    setattr(ds, i, request.form[i])
            print(ds)
            db.update(ds)
            flash('Successfully updated lease ' + lease_num)
            return redirect(url_for('leases.details', lease_num=lease_num))
        except Exception as e:
            flash('Couldn\'t update a lease')
            print('Couldn\'t update a lease: ', e)
            return redirect(url_for('leases.search'))
    elif request.method == 'GET':
        try:
            db = config.get_database()
            lease = db.select1('Lease', ID=lease_num)
            royaltymaster = db.select1('LeaseRoyaltyMaster', ID=lease_num)
            wellevent_statement = """SELECT WellEventInfo.* FROM WellEventInfo, WellLeaseLink
                           WHERE WellLeaseLink.LeaseID="%s"
                           AND WellEventInfo.WellEvent=WellLeaseLink.WellID"""
            # wellevents = db.select_sql(wellevent_statement % lease_num)  # not sure what the situation is here, None for now
            wellevents = None
            return render_template('leases/details.html', new = False, lease = lease, royaltymaster = royaltymaster, wellevents=wellevents)
        except Exception as e:
            print(e)
            abort(404)

@leases.route('/leases/new', methods=['GET', 'POST'])
def new():
    db = config.get_database()
    if request.method == 'GET':
        return render_template('leases/details.html', new = True, lease = None, royaltymaster = None)
    elif request.method == 'POST' and request.form['action'] == 'cancel':
        return redirect(url_for('leases.search'))
    elif request.method == 'POST' and request.form['action'] == 'add':
        ds = DataStructure()
        setattr(ds, '_table_name', 'Lease')
        for i in request.form:
            if i != 'action':
                setattr(ds, i, request.form[i])
        try:
            new_id = db.insert(ds)
            flash('Lease successfully added')
            return redirect(url_for('leases.details', lease_num=new_id))
        except Exception as e:
            flash('Couldn\'t add a new lease')
            print('Couldn\'t add a new lease: ', e)
            return redirect(url_for('leases.search'))


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
PUT /leases/1 - updates a lease, returns 200
DELETE /leases/1 - deletes a lease, returns 200
"""