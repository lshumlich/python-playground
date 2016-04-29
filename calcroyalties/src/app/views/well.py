from flask import Blueprint, request, render_template, abort

import config
from .permission_handler import PermissionHandler
from .main import get_proddate_int

well = Blueprint('well', __name__)

@well.route('/well/search')
@PermissionHandler('well_view')
def search():
    return render_template('well/search.html')

@well.route('/api/wellresults')
def results():
    if not request.is_xhr: abort(404)
    # try:
    db = config.get_database()
    results = db.select('Well')
    return render_template('well/results.html', results = results)
    # except:
    #     return "<h2>No results found</h2>"

@well.route('/api/wellinfo')
def details():
    if not request.is_xhr: abort(404)
    try:
        db = config.get_database()
        result = db.select1('Well', ID=request.args.get('ID'))
        return render_template('well/details.html', result = result)
    except:
        abort(404)

@well.route('/well/calculate')
def calculate():
    from src.calc.calcroyalties import ProcessRoyalties
    pr = ProcessRoyalties()
    well_id = request.args.get('WellId')
    try:
        pr.process_one(well_id, get_proddate_int(), 'Oil')
        return 'Calculation successful for %s, %i, %s' % (well_id, get_proddate_int(), 'Oil')
    except Exception as e:
        return 'Something went wrong during calculation for %s, %i, %s:<br />%s' % (well_id, get_proddate_int(), 'Oil', e)