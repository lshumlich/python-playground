import sys
import traceback
from flask import Blueprint, request, config, render_template

import config
from .main import get_proddate_int
from src.util.apperror import AppError
from src.util.appdate import prod_month_to_date
from src.util.app_formatter import format_gorr
from src.database.data_structure import DataStructure

worksheet = Blueprint('worksheet', __name__)


@worksheet.route('/worksheet')
def calc_worksheet():
    if "ID" in request.args:
        id = int(request.args["ID"])
        return(generate_worksheet_from_id(id))

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
        return generate_worksheet('Well', well_id, prod_month, rpba, product)
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

# todo delete me when the other generate works
def generate_worksheet(entity, entity_id, prod_month, rpba, product):
    try:
        db = config.get_database()
        # product = "SUL"
        if entity == 'Well':
            well = db.select1('WellRoyaltyMaster', ID=entity_id)
        else:
            well = None
        entity_lease_link_array = db.select('EntityLeaseLink', Entity=entity, EntityID=entity_id)
        if len(entity_lease_link_array) == 0:
            raise AppError("There were no EntityLeaseLink records for " + entity + ' ' + str(entity_id) + str(prod_month))
        entity_lease_link = entity_lease_link_array[0]
        royalty = db.select1('LeaseRoyaltyMaster', ID=entity_lease_link.LeaseID)
        lease = db.select1('Lease', ID=entity_lease_link.LeaseID)

        if rpba:
            monthly_array = db.select('Monthly', Entity=entity, EntityID=entity_id, prodMonth=prod_month, product=product, RPBA=rpba)
        else:
            monthly_array = db.select('Monthly', Enriry=entity, EntityID=entity_id, prodMonth=prod_month, product=product)
        if len(monthly_array) == 0:
            raise AppError("There were no monthly records for " + entity + ": " + str(entity_id) + " ProdDate: " +
                           str(prod_month) + " Product: " + product)
        monthly = monthly_array[0]  # if there are multiple pick the first one

        ba = db.select1('BAInfo', BAid=monthly.RPBA, BAType='RTP')
        calc = db.select1('Calc', Entity=entity, EntityID=entity_id, ProdMonth=prod_month, RPBA=monthly.RPBA, Product=product)
        calc_specific = DataStructure(calc.RoyaltySpecific)
        rtp_info = db.select1('RTPInfo', WellEvent=well.WellEvent, Product=product, Payer=monthly.RPBA,
                              Date=prod_month_to_date(prod_month))
        royalty.format_gorr = format_gorr(calc.Gorr)
        return render_template('worksheet/calc_worksheet.html',
                               well=well, rm=royalty, m=monthly, lease=lease,
                               calc=calc, calc_sp=calc_specific, entity_lease_link=entity_lease_link,
                               ba=ba, rtp_info=rtp_info)
    except Exception as e:
        print('views.worksheet: ***Error:', e)
        traceback.print_exc(file=sys.stdout)
        tb = traceback.format_exc()
        return "<h2>Error displaying worksheet for " + entity + " %s</h2><br>" % entity_id + str(e) + '<plaintext>' + \
               tb + '</plaintext>'


def generate_worksheet_from_id(id):
    try:
        db = config.get_database()
        calc = db.select1('Calc', ID=id)
        return generate_worksheet_from_calc(calc)
    except Exception as e:
        print('views.worksheet: ***Error:', e)
        traceback.print_exc(file=sys.stdout)
        tb = traceback.format_exc()
        return "<h2>Error displaying worksheet for well %s</h2><br>" % calc.WellID + str(e) + '<plaintext>' + \
               tb + '</plaintext>'


def generate_worksheet_from_calc(calc):
    try:
        db = config.get_database()
        if calc.Entity == 'Well':
            well = db.select1('WellRoyaltyMaster', ID=calc.EntityID)
        else:
            well = None
        entity_lease_link_array = db.select('EntityLeaseLink', Entity=calc.Entity, EntityID=calc.EntityID)
        if len(entity_lease_link_array) == 0:
            raise AppError("There were no well_lease_link records for " + str(calc.WellID) + str(calc.ProdMonth))
        entity_lease_link = entity_lease_link_array[0]
        royalty = db.select1('LeaseRoyaltyMaster', ID=calc.LeaseID)
        lease = db.select1('Lease', ID=calc.LeaseID)

        monthly_array = db.select('Monthly', Entity=calc.Entity, EntityID=calc.EntityID, prodMonth=calc.ProdMonth, product=calc.Product, RPBA=calc.RPBA)
        if len(monthly_array) == 0:
            raise AppError("There were no monthly records for well: " + str(calc.WellID) + " ProdDate: " +
                           str(calc.ProdMonth) + " Product: " + calc.Product)
        monthly = monthly_array[0]  # if there are multiple pick the first one

        ba = db.select1('BAInfo', BAid=monthly.RPBA, BAType='RTP')
        # calc = db.select1('Calc', WellID=calc.WellID, ProdMonth=calc.ProdMonth, RPBA=monthly.RPBA, Product=calc.Product)
        calc_specific = DataStructure(calc.RoyaltySpecific)
        rtp_info = db.select1('RTPInfo', WellEvent=well.WellEvent, Product=calc.Product, Payer=monthly.RPBA,
                              Date=prod_month_to_date(calc.ProdMonth))
        royalty.format_gorr = format_gorr(calc.Gorr)
        return render_template('worksheet/calc_worksheet.html',
                               well=well, rm=royalty, m=monthly, lease=lease,
                               calc=calc, calc_sp=calc_specific, entity_lease_link=entity_lease_link,
                               ba=ba, rtp_info=rtp_info)
    except Exception as e:
        print('views.worksheet: ***Error:', e)
        traceback.print_exc(file=sys.stdout)
        tb = traceback.format_exc()
        return "<h2>Error displaying worksheet for " + calc.Entity + " %s</h2><br>" % calc.EntityID + str(e) + '<plaintext>' + \
               tb + '</plaintext>'
