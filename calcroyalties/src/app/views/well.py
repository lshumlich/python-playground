from flask import Blueprint, request, render_template, abort

import config
from .permission_handler import PermissionHandler

well = Blueprint('well', __name__)

@well.route('/well/search')
@PermissionHandler('well_view')
def search():
    return render_template('well/search.html')

@well.route('/api/wellresults')
def results():
    if not request.is_xhr: abort(404)
    try:
        db = config.get_database()
        results = db.select('Well')
        return render_template('well/results.html', results = results)
    except:
        return "<h2>No results found</h2>"

@well.route('/api/wellinfo')
def details():
    if not request.is_xhr: abort(404)
    try:
        db = config.get_database()
        result = db.select1('Well', ID=request.args.get('ID'))
        return render_template('well/details.html', result = result)
    except:
        abort(404)