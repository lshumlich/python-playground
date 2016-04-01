#!/bin/env python3

import json
import sys, traceback
from flask import render_template, request, redirect, url_for, flash

import config
from src.app import app


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/well/index')
def well_index():
    return render_template('well_search.html')

@app.route('/well/search')
def well_search():
    return render_template('well_search.html')

@app.route('/api/wellresults')
def well_results():
    try:
        db = config.get_database()
        results = db.select('Well')
        return render_template('api/well_results.html', results = results)
    except:
        return "<h2>No results found</h2>"

@app.route('/api/wellinfo')
def well_info():
    try:
        db = config.get_database()
        result = db.select1('Well', ID=request.args.get('ID'))
        return render_template('api/well_info.html', result = result)
    except:
        return "<h2>Well details not found</h2>"

@app.route('/facility/search')
def facility_search():
    return render_template('facility_search.html')

@app.route('/api/facility_results')
def facility_results():
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

@app.route('/adriennews')
def adriennews():
    if request.args:
        db = config.get_database()
        wellIds = request.args["WellId"]
        well_id = int(wellIds)
        prodMonth = 201501
        product = "Oil"
        well = db.select1('Well', ID=well_id)
        royalty = db.select1('Royaltymaster', ID=well.LeaseID)
        lease = db.select1('Lease', ID=well.LeaseID)
        monthly = db.select1('Monthly', WellID = well_id, prodMonth = prodMonth, product = product)
        calc_array = db.select('Calc', WellID=well_id, prodMonth = prodMonth)
        calc = calc_array[0]
        print(monthly)
    else:
        print("No monthly data for this well")
    return render_template('worksheetas.html', well=well, rm=royalty, m=monthly,  lease=lease, calc=calc)

@app.errorhandler(404)
def not_found(error):
    return render_template('404.html')
