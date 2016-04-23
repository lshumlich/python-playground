from flask import Blueprint, render_template, abort, request, json
import config
from .permission_handler import PermissionHandler

lease = Blueprint('lease', __name__)

@lease.route('/lease/search')
def search():
    return render_template('lease_search.html')

@lease.route('/lease/<lease_num>')
def details(lease_num):
    if not lease_num: abort(404)
    try:
        db = config.get_database()
        result_lease = db.select1('Lease', ID=lease_num)
        result_royaltymaster = db.select1('RoyaltyMaster', ID=lease_num)
        return render_template('lease_details.html', lease = result_lease, royaltymaster = result_royaltymaster)
    except:
        abort(404)

@lease.route('/api/leaseresults', methods=['GET', 'POST'])
def results():
    if not request.is_xhr: abort(404)
    try:
        db = config.get_database()
        req_data = request.get_json()
        results = db.select('Lease', **req_data)
        return render_template('api/lease_results.html', results = results)
    except Exception as e:
        print(e)
        return json.dumps({'success': False}), 404, {'ContentType': 'application/json'}
