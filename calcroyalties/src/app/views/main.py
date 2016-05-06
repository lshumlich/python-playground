#!/bin/env python3
from flask import Blueprint, render_template, request, redirect, url_for, session, flash, make_response

import config
from src.app import app
from .permission_handler import PermissionHandler
from src.util.apperror import AppError

main = Blueprint('main', __name__)

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
    resp = make_response(redirect(url_for('index')))
    if 'login' in session:
        session.clear()
        resp.set_cookie('proddate', expires=0)
    return resp  # used instead of regular redirect because set_cookie only works on a custom response

@app.route('/map')
def map():
    import random, json
    db = config.get_database()
    statement_wellevents = "SELECT * FROM WellEventInfo LIMIT 5"
    wellevents = db.select_sql(statement_wellevents)

    results = []
    for wellevent in wellevents:
        json_obj = {}
        json_obj['type'] = 'Feature'
        json_obj['properties'] = {}
        json_obj['properties']['name'] = wellevent.WellEvent
        json_obj['properties']['popupContent'] = '<b>%s</b> <br> Pool Name: %s<br><a href="/wellevent/%s">Details</a>' % (wellevent.WellEvent, wellevent.PoolName, wellevent.WellEvent)
        json_obj['geometry'] = {}
        json_obj['geometry']['type'] = 'Point'
        json_obj['geometry']['coordinates'] = [random.randint(-50, 50), random.randint(-100, 100)]
        results.append(json_obj)
    return render_template('map.html', results=json.dumps(results))

@app.errorhandler(404)
def not_found(error):
    return render_template('404.html')

def get_proddate():
    cookie = request.cookies['proddate']
    if not cookie: raise AppError('Proddate cookie not set for some reason')
    proddate = cookie[0:4] + "-" + cookie[4:6] + "-01"
    return proddate

def get_proddate_int():
    try:
        return int(request.cookies['proddate'])
    except:
        raise AppError('Proddate cookie not set for some reason')

"""
1. Well event view - search field verification
2. Make flash messages work from JS (i.e. on AJAX request status)
3. Idea: change all db.select functions to take into account the production date (to avoid setting it manually on every query)

PRWI101010610825W300; 199001
"""
