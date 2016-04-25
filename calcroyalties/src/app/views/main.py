#!/bin/env python3
from flask import Blueprint, render_template, request, redirect, url_for, session, flash

import config
from src.app import app
from .permission_handler import PermissionHandler

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
    if 'login' in session:
        session.pop('login')
        session.pop('name')
        session.pop('prod_month')
        session.pop('permissions')
    return redirect(url_for('index'))

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
    e. Search fields verification; get rid of empty fields in JS
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
