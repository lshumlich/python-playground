#!/bin/env python3

import sys
import traceback
import json
from functools import wraps

from flask import render_template, request, redirect, url_for, session, abort, flash

import config
from src.app import app


class PermissionHandler():
    ''' Checks for permissions. Works both as a decorator (easy to apply to endpoints)
        and as a context manager (for more fine-grained control).
        Checks to see if a user is logged in, then if the user has the necessary permission'''
    def __init__(self, perm):
        self.perm = perm

    def __call__(self, f):
        # decorator implementation
        @wraps(f)
        def wrapper(*args, **kwds):
            if 'login' not in session: return redirect(url_for('login'))
            if self.perm not in session['permissions']:
                abort(403)
            else:
                return f(*args, **kwds)
        return wrapper

    def __enter__(self):
        # context manager implementation
        if 'login' not in session: return redirect(url_for('login'))
        if not self.perm in session['permissions']:
            abort(403)

    def __exit__(self, exc_type, exc_val, exc_tb):
        return False


@app.route('/')
def index():
    if 'login' not in session: return redirect(url_for('login'))
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        try:
            db = config.get_database()
            user = db.select1('Users', Login=request.form['login'])
            if user:
                session['login'] = user.Login
                session['name'] = user.Name
                session['prod_month'] = user.ProdMonth
                session['permissions'] = user.Permissions
                return redirect(url_for('index'))
            else:
                return "User not found"
        except:
            flash("No such user was found in the system.")
            return redirect(url_for('index'))
    return render_template('login.html')

@app.route('/logout')
def logout():
    if 'login' in session:
        session.pop('login')
        session.pop('name')
        session.pop('prod_month')
        session.pop('permissions')
    return redirect(url_for('index'))

@app.route('/admin/users')
def admin_users():
    return render_template('users.html')

@app.route('/api/users', methods=['GET', 'DELETE', 'POST', 'PUT', 'PATCH'])
def admin_user():
    """ handles all user-related ajax calls, both for user list and individual users """
    if not request.is_xhr: abort(404)
    db = config.get_database()
    if request.method == 'GET' and not request.args:
        """ get an entire user list """
        results = db.select('Users')
        return render_template('api/user_results.html', users=results)
    elif request.method == 'GET':
        """ get info for a user """
        results = db.select1('Users', ID=request.args.get('ID'))
        return render_template('api/user.html', user=results)
    elif request.method == 'DELETE':
        """ delete user """
        db.delete('Users', int(request.form['ID']))
        return json.dumps({'success': True}), 200, {'ContentType': 'application/json'}
    elif request.method == 'POST':
        """ update info for a user """
        req_data = request.get_json()
        print(req_data)
        user = db.select1('Users', ID=req_data['ID'])
        user.Login = req_data['Login']
        user.Name = req_data['Name']
        user.Email = req_data['Email']
        user.Permissions = req_data['Permissions']
        db.update(user)
        return json.dumps({'success': True}), 200, {'ContentType': 'application/json'}
    elif request.method == 'PATCH':
        """ get an empty form to create a new user """
        return render_template('api/user.html', user=None)
    elif request.method == 'PUT':
        """ create new user """
        class User():
            None
        req_data = request.get_json()
        user = User()
        user._table_name = 'Users'
        user.Login = req_data['Login']
        user.Name = req_data['Name']
        user.Email = req_data['Email']
        user.Permissions = req_data['Permissions']
        db.insert(user)
        return json.dumps({'success': True}), 200, {'ContentType': 'application/json'}
    else:
        abort(400)

@app.route('/lease/search')
def lease_search():
    return render_template('lease_search.html')

@app.route('/lease/<lease_num>')
def lease_details(lease_num):
    if not lease_num: abort(404)
    try:
        db = config.get_database()
        result_lease = db.select1('Lease', ID=lease_num)
        result_royaltymaster = db.select1('RoyaltyMaster', ID=lease_num)
        return render_template('lease_details.html', lease = result_lease, royaltymaster = result_royaltymaster)
    except:
        abort(404)

@app.route('/api/leaseresults', methods=['GET', 'POST'])
def api_lease_results():
    if not request.is_xhr: abort(404)
    try:
        db = config.get_database()
        req_data = request.get_json()
        results = db.select('Lease', **req_data)
        return render_template('api/lease_results.html', results = results)
    except:
        return json.dumps({'success': False}), 404, {'ContentType': 'application/json'}

@app.route('/wellevent/search', methods=['GET'])
def wellevent_search():
    if not request.args: return render_template('wellevent_search.html')
    db = config.get_database()
    results = db.select('WellEventInfo', **request.args.to_dict())
    # sql select ideas:
    # results = []
    # for wellevent in wellevents:
    #     result = db.select_sql('SELECT * FROM RTAWellsinPE WHERE WellEvent="%s"' % wellevent.WellEvent)
    #     if result: results.append(result)
    if results:
        print(results)
        return render_template('wellevent_search.html', results=results, search_terms=request.args.to_dict())
    else:
        flash('No results found.')
        return render_template('wellevent_search.html')

@app.route('/wellevent')
def wellevent_redirect():
    return redirect(url_for('wellevent_search'))

@app.route('/wellevent/<wellevent_num>')
def wellevent_details(wellevent_num):
    if not wellevent_num: redirect(url_for('wellevent_search'))
    try:
        db = config.get_database()
        req_data = request.get_json()
        results = db.select('WellEventInfo', **req_data)
        return render_template('api/wellevent_details.html', results=results)
    except:
        abort(404)

@app.route('/well/search')
@PermissionHandler('well_view')
def well_search():
    return render_template('well_search.html')

@app.route('/api/wellresults')
def well_results():
    if not request.is_xhr: abort(404)
    try:
        db = config.get_database()
        results = db.select('Well')
        return render_template('api/well_results.html', results = results)
    except:
        return "<h2>No results found</h2>"

@app.route('/api/wellinfo')
def well_info():
    if not request.is_xhr: abort(404)
    try:
        db = config.get_database()
        result = db.select1('Well', ID=request.args.get('ID'))
        return render_template('api/well_info.html', result = result)
    except:
        abort(404)

@app.route('/facility/search')
@PermissionHandler('facility_view')
def facility_search():
    return render_template('facility_search.html')

@app.route('/api/facility_results')
def facility_results():
    if not request.is_xhr: abort(404)
    try:
        db = config.get_database()
        results = db.select('FacilityInfo')
        return render_template('api/facility_results.html', results = results)
    except Exception as e:
        print('views.new_facility_results: ***Error:',e)
        traceback.print_exc(file=sys.stdout)
        return "<h2>No results found</h2>"

@app.route('/api/facility_info')
def facility_info():
    if not request.is_xhr: abort(404)
    try:
        db = config.get_database()
        result = db.select1('FacilityInfo', Facility=request.args.get('ID'))
        wells  = db.select('WellFacilityLink', Facility=request.args.get('ID'))
        print('new_facility_info:',len(wells),"found")
        return render_template('api/facility_info.html', result = result, wells = wells)
    except Exception as e:
        print('views.new_facility_info: ***Error:',e)
        traceback.print_exc(file=sys.stdout)
        return "<h2>Facility details not found</h2>"

@app.route('/worksheet')
#@PermissionHandler('worksheet_view')
def worksheet():
    try:
        if request.args:
            db = config.get_database()
            well_id = int(request.args["WellId"])
            prod_month = 201503
            product = "Oil"
            well = db.select1('Well', ID=well_id)
            royalty = db.select1('Royaltymaster', ID=well.LeaseID)
            lease = db.select1('Lease', ID=well.LeaseID)

            monthly = db.select1('Monthly', WellID = well_id, prodMonth = prod_month, product = product)
            calc_array = db.select('Calc', WellID=well_id, prodMonth = prod_month)
            calc = calc_array[0]
            print(monthly)
            return render_template('worksheet.html', well=well, rm=royalty, m=monthly, lease=lease, calc=calc)
        else:
            return "No monthly data for this well"

    except Exception as e:
        print('views.worksheet: ***Error:',e)
        traceback.print_exc(file=sys.stdout)
        return "<h2>Error displaying worksheet</h2><br>" + str(e)

@app.errorhandler(404)
def not_found(error):
    return render_template('404.html')


"""
V 1. Authentication system
    V a. Checkboxes for permissions (names like well_edit, on server added to a list if checked, then list = permissions in db)
    V b. JS-based form verification before submitting (use jQuery dialog demo for example)
    V c. If permissions not set, default them to Disabled
2. Well event view
    a. Search by well event only
    b. Search results based on Lorraine's table
    c. Details page - show entire record
    d. Details page - show related wells
3. Lease view
    V a. Start by designing url structure!
    b. No search for now
    c. Search results - show entire record
    d. Details page - show entire record
    e. Details page - show related wells
3. Larry's data view
    a. Make sure it's working
4. Production month
    a. Store in cookies, make sure persistent for user on this computer
    b. Prompt a user if it's not set
    c. Write a function that would get it consistently
5. Misc
    a. Implement flash messages (how to make it work from JS?)
    b. Change all endpoints to make use of GET parameters: /lease/search?ID=1&Prov=AB, then populate the form if these were passed on:
       value = {{ lease.ID or "" }}
"""
