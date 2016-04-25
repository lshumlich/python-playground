import sys, traceback
from flask import Blueprint, render_template, request, abort

import config
from .permission_handler import PermissionHandler

facility = Blueprint('facility', __name__)

@facility.route('/facility/search')
@PermissionHandler('facility_view')
def search():
    return render_template('facility/search.html')

@facility.route('/api/facility_results')
def results():
    if not request.is_xhr: abort(404)
    try:
        db = config.get_database()
        results = db.select('FacilityInfo')
        return render_template('facility/results.html', results = results)
    except Exception as e:
        print('views.new_facility_results: ***Error:',e)
        traceback.print_exc(file=sys.stdout)
        return "<h2>No results found</h2>"

@facility.route('/api/facility_details')
def details():
    if not request.is_xhr: abort(404)
    try:
        db = config.get_database()
        result = db.select1('FacilityInfo', Facility=request.args.get('ID'))
        wells  = db.select('WellFacilityLink', Facility=request.args.get('ID'))
        print('new_facility_info:',len(wells),"found")
        return render_template('facility/details.html', result = result, wells = wells)
    except Exception as e:
        print('views.new_facility_info: ***Error:',e)
        traceback.print_exc(file=sys.stdout)
        return "<h2>Facility details not found</h2>"