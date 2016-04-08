#!/bin/env python3

import sys
import traceback
import json
from functools import wraps

from flask import render_template, request, redirect, url_for, session, abort

import config
from src.app import app

USERS = """
    [
    { "username": "larry",
      "allowed": [],
      "prod_month": 201501
    },
    { "username": "adrienne",
      "allowed": ["well_search", "well_index"],
      "prod_month": 201502
    }
    ]
"""

def login_handler(f):
    @wraps(f)
    def wrapper(*args, **kwds):
        # if 'login' in session and f.__name__ in session['permissions']:
        #     return f(*args, **kwds)
        # else:
        #     return "You don't have sufficient permissions"
        if 'login' not in session:
            # you need to log in first
            return redirect(url_for('login'))
        else:
            if f.__name__ not in session['permissions']:
                return "You don't have sufficient permissions"
            else:
                return f(*args, **kwds)
    return wrapper

@app.route('/')
@login_handler
def index():
    return render_template('index.html')

def user_helper(login):
    try:
        db = config.get_database()
        result = db.select1('Users', Login=login)
        return result
    except:
        print('Can\'t get the user "%s" from the database' % login)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user = user_helper(request.form['login'])
        if user:
            print(user)
            session['login'] = user.Login
            session['name'] = user.Name
            session['prod_month'] = user.ProdMonth
            session['permissions'] = user.Permissions
            return redirect(url_for('index'))
        else:
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

@app.route('/api/userinfo')
def admin_user_info():
    abort()
    # db = config.get_database()
    # results = db.select1('Users', ID=request.args.get('ID'))
    # return render_template('api/user_info.html', user=results)
    # if request.method == 'POST':
    #     db = config.get_database()
    #     if request.args.get('action') == 'get':
    #         try:
    #             results = db.select1('Users', ID=request.args.get('ID'))
    #             return render_template('api/user_info.html', user=results)
    #         except:
    #             return "<h2>No results found</h2>"
    #     elif request.args.get('action') == 'delete':
    #         try:
    #             None
    #     elif request.args.get('action') == 'update':
    #         None

@app.route('/well/search')
@login_handler
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
@login_handler
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
@login_handler
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
            return "3Something went wrong displaying worksheet for well %i:<br>%s" % (well_id, str(e))
    else:
        return "No monthly data for this well"

@app.errorhandler(404)
def not_found(error):
    return render_template('404.html')


"""
1. Admin page to manage user permissions
2. Production date editable on every search, entry, etc.
"""