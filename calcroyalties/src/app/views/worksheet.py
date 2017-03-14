import sys
import traceback
from flask import Blueprint, request, config, render_template

import config
from .main import get_proddate_int
from src.util.apperror import AppError
from src.util.appdate import prod_month_to_date
from src.util.app_formatter import format_gorr

worksheet = Blueprint('worksheet', __name__)


@worksheet.route('/worksheet')
def calc_worksheet():
    if "ProdDate" in request.args:
        prod_month = int(request.args["ProdDate"])
    else:
        prod_month = get_proddate_int()

    if "RPBA" in request.args:
        rpba = request.args["RPBA"]
    else:
        rpba = None

    if "Product" in request.args:
        product = request.args["Product"]
    else:
        product = None

    if "WellId" in request.args:
        well_id = int(request.args["WellId"])
        return generate_worksheet(well_id, prod_month, rpba, product)
    elif "WellStart" in request.args and "WellEnd" in request.args and "WellId" not in request.args:
        well_start = int(request.args["WellStart"])
        well_end = int(request.args["WellEnd"])
        result = ""
        for w in range(well_start, well_end + 1):
            result += generate_worksheet(w, prod_month, rpba, product)
            result += "<hr>"
        return result
    else:
        return "worksheet.calc_worksheet Something wasn't right"


def generate_worksheet(well_id, prod_month, rpba, product):
    try:
        db = config.get_database()
        # product = "SUL"
        well = db.select1('WellRoyaltyMaster', ID=well_id)
        well_lease_link_array = db.select('WellLeaseLink', WellID=well_id)
        if len(well_lease_link_array) == 0:
            raise AppError("There were no well_lease_link records for " + str(well_id) + str(prod_month))
        well_lease_link = well_lease_link_array[0]
        royalty = db.select1('LeaseRoyaltyMaster', ID=well_lease_link.LeaseID)
        royalty.format_gorr = format_gorr(royalty.Gorr)
        lease = db.select1('Lease', ID=well_lease_link.LeaseID)

        if rpba:
            monthly_array = db.select('Monthly', WellID=well_id, prodMonth=prod_month, product=product, RPBA=rpba)
        else:
            monthly_array = db.select('Monthly', WellID=well_id, prodMonth=prod_month, product=product)
        if len(monthly_array) == 0:
            raise AppError("There were no monthly records for " + str(well_id) + str(prod_month) + product)
        monthly = monthly_array[0]  # if there are multiple pick the first one

        ba = db.select1('BAInfo', BAid=monthly.RPBA, BAType='RTP')
        calc = db.select1('Calc', WellID=well_id, ProdMonth=prod_month, RPBA=monthly.RPBA, Product=product)
        rtp_info = db.select1('RTPInfo', WellEvent=well.WellEvent, Product=product, Payer=monthly.RPBA,
                              Date=prod_month_to_date(prod_month))
        # calc = calc_array[0]
        # print(monthly)
        return render_template('worksheet/calc_worksheet.html',
                               well=well, rm=royalty, m=monthly, lease=lease,
                               calc=calc, well_lease_link=well_lease_link, ba=ba, rtp_info=rtp_info)
    except Exception as e:
        print('views.worksheet: ***Error:', e)
        traceback.print_exc(file=sys.stdout)
        tb = traceback.format_exc()
        return "<h2>Error displaying worksheet for well %s</h2><br>" % well_id + str(e) + '<plaintext>' + \
               tb + '</plaintext>'
