import sys, traceback
from flask import Blueprint, request, config, render_template

import config
from .permission_handler import PermissionHandler

worksheet = Blueprint('worksheet', __name__)

@worksheet.route('/worksheet')
def ws():
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