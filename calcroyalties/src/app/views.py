#!/bin/env python3

import sys
import traceback
import json
from functools import wraps

from flask import render_template, request, redirect, url_for, session, abort

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
        except:
            return "No such user was found in the system"
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

@app.route('/api/userresults')
def admin_user_results():
    if not request.is_xhr: abort(404)
    try:
        db = config.get_database()
        results = db.select('Users')
        return render_template('api/user_results.html', users=results)
    except:
        abort(404)

@app.route('/api/user', methods=['GET', 'DELETE', 'POST', 'PUT', 'PATCH'])
def admin_user_info():
    if not request.is_xhr: abort(404)
    db = config.get_database()
    if request.method == 'GET':
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

@app.route('/well/search')
# @login_handler
@PermissionHandler('well_search')
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
@PermissionHandler('facility_search')
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
@PermissionHandler('worksheet')
def worksheet():
    if request.args:
        try:
            db = config.get_database()
            well_id = int(request.args["WellId"])
            prod_month = session['prod_month']
            product = "Oil"
            well = db.select1('Well', ID=well_id)
            royalty = db.select1('Royaltymaster', ID=well.LeaseID)
            lease = db.select1('Lease', ID=well.LeaseID)
            monthly = db.select1('Monthly', WellID = well_id, prodMonth = prod_month, product = product)
            calc_array = db.select('Calc', WellID=well_id, prodMonth = prod_month)
            calc = calc_array[0]
            print(monthly)
            return render_template('worksheet.html', well=well, rm=royalty, m=monthly, lease=lease, calc=calc)
        except BaseException as e:
            return "Something went wrong displaying worksheet for well %i:<br>%s" % (well_id, str(e))
    else:
        return "No monthly data for this well"

@app.errorhandler(404)
def not_found(error):
    return render_template('404.html')


"""
1. Authentication system
    a. Checkboxes for permissions (names like well_edit, on server added to a list if checked, then list = permissions in db)
    b. Flash messages for all actions (how to use flash from JS?)
2. Production month
    a. Stored in DB for every user or just set as a cookie, reset on logout?
    b. In case of cookies, set in JS instead of server side?
3. New view
    a. Start by designing url structure!

CREATE TABLE `Users` (
	`ID`	INTEGER PRIMARY KEY AUTOINCREMENT UNIQUE,
	`Login`	TEXT UNIQUE,
	`Name`	TEXT,
	`Email`	TEXT,
	`ProdMonth`	INTEGER,
	`Permissions`	TEXT
)
"""