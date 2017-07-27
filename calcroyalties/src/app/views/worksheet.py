import sys
import traceback
from flask import Blueprint, request, config, render_template

import config
from src.util.apperror import AppError
from src.util.appdate import prod_month_to_date
from src.util.app_formatter import format_gorr
from src.database.data_structure import DataStructure
import pdfkit

worksheet = Blueprint('worksheet', __name__)


@worksheet.route('/worksheet')
def calc_worksheet():
    args = request.args.to_dict()
    db = config.get_database()
    calcs = db.select('Calc', **args)
    result = ""
    for calc in calcs:
        result += generate_worksheet_from_calc(calc)
        # result += "<hr>"

    return result


@worksheet.route('/worksheettopdf')
def calc_worksheettopdf():
    try:
        args = request.args.to_dict()
        print(args)
        db = config.get_database()
        calcs = db.select('Calc', **args)
        result = ""
        for calc in calcs:
            result += generate_worksheet_from_calc(calc, 'n')
            result += "<hr>"

        # text_file = open("out.html", "w", encoding="utf-8")
        # text_file.write(result)
        # text_file.write(result. .encode("UTF-8"))
        # text_file.close()

        print("about to set path")
        path_wkthmltopdf = r'C:\Program Files (x86)\wkhtmltopdf\bin\wkhtmltopdf.exe'
        print("about to set config")
        configpdf = pdfkit.configuration(wkhtmltopdf=path_wkthmltopdf)
        print("about to pdfkit")
        pdfkit.from_string(result, 'out.pdf', configuration=configpdf)

        return "pdf should have been created"

    except Exception as e:
        print('PDF worksheet: ***Error:', e)
        traceback.print_exc(file=sys.stdout)
        tb = traceback.format_exc()
        return "<h2>Error generating pdf" + \
               '<plaintext>' + tb + '</plaintext>'


def generate_worksheet_from_calc(calc, with_js='y'):
    """
    Generate html for the calc row that is passed
    :param calc: a full calc record
    :param with_js: default is 'y' only other option is 'n' and should only be used to work around a
                    pdf generation issue
    :return: html of the worksheet for the calc record
    """
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

        history = db.select_sql("""SELECT *
                   from Calc
                   WHERE ProdMonth = "{}" and LeaseID = "{}" and Entity = "{}" and EntityID = "{}"
                   and Product = "{}" and RPBA = "{}"
                   order by ExtractDate""".format(calc.ProdMonth, calc.LeaseID, calc.Entity, calc.EntityID,
                                                  calc.Product, calc.RPBA))
        # history = db.select_sql("""SELECT ID, ExtractDate, BaseNetRoyaltyValue, GorrNetRoyaltyValue
        #            from Calc
        #            WHERE ProdMonth = "{}" and LeaseID = "{}" and Entity = "{}" and EntityID = "{}"
        #            and Product = "{}" and RPBA = "{}"
        #            order by ExtractDate""".format(calc.ProdMonth, calc.LeaseID, calc.Entity, calc.EntityID,
        #                                           calc.Product, calc.RPBA))

        prev_BaseNetRoyaltyValue = 0.0
        prev_GorrNetRoyaltyValue = 0.0
        i = 0
        for h in history:
            h.BookedBaseNetRoyaltyValue = h.BaseNetRoyaltyValue - prev_BaseNetRoyaltyValue
            h.BookedGorrNetRoyaltyValue = h.GorrNetRoyaltyValue - prev_GorrNetRoyaltyValue
            h.Booked = h.BookedBaseNetRoyaltyValue + h.BookedGorrNetRoyaltyValue
            prev_BaseNetRoyaltyValue = h.BaseNetRoyaltyValue
            prev_GorrNetRoyaltyValue = h.GorrNetRoyaltyValue
            # Set the original calc record to the history record the one before this one
            if h.ExtractDate == calc.ExtractDate and i > 0:
                calc.original(history[i-1])

            i += 1

        monthly_array = db.select('Monthly', ExtractDate=calc.ExtractDate, Entity=calc.Entity, EntityID=calc.EntityID,
                                  prodMonth=calc.ProdMonth, product=calc.Product, RPBA=calc.RPBA)
        if len(monthly_array) == 0:
            raise AppError("There were no monthly records for well: " + str(calc.WellID) + " ProdDate: " +
                           str(calc.ProdMonth) + " Product: " + calc.Product)
        monthly = monthly_array[0]  # if there are multiple pick the first one

        ba = db.select1('BAInfo', BAid=monthly.RPBA, BAType='RTP')

        calc_specific = DataStructure(calc.RoyaltySpecific)
        rtp_info = db.select1('RTPInfo', WellEvent=well.WellEvent, Product=calc.Product, Payer=monthly.RPBA,
                              Date=prod_month_to_date(calc.ProdMonth))

        royalty.format_gorr = format_gorr(calc.Gorr)

        return render_template('worksheet/calc_worksheet.html',
                               with_js=with_js,
                               well=well, rm=royalty, m=monthly, lease=lease,
                               calc=calc, calc_sp=calc_specific, entity_lease_link=entity_lease_link,
                               ba=ba, rtp_info=rtp_info, history=history)
    except Exception as e:
        print('views.worksheet: ***Error:', e)
        traceback.print_exc(file=sys.stdout)
        tb = traceback.format_exc()
        return "<h2>Error displaying worksheet for " + calc.Entity + " %s</h2><br>" % calc.EntityID + str(e) + \
               '<plaintext>' + tb + '</plaintext>'


def generate_pdfworksheet_from_calc(calc):
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

        history = db.select_sql("""SELECT ID, ExtractDate, BaseNetRoyaltyValue, GorrNetRoyaltyValue
                   from Calc
                   WHERE ProdMonth = "{}" and LeaseID = "{}" and Entity = "{}" and EntityID = "{}"
                   and Product = "{}" and RPBA = "{}"
                   order by ExtractDate""".format(calc.ProdMonth, calc.LeaseID, calc.Entity, calc.EntityID,
                                                  calc.Product, calc.RPBA))

        prev_BaseNetRoyaltyValue = 0.0
        prev_GorrNetRoyaltyValue = 0.0
        for h in history:
            h.BookedBaseNetRoyaltyValue = h.BaseNetRoyaltyValue - prev_BaseNetRoyaltyValue
            h.BookedGorrNetRoyaltyValue = h.GorrNetRoyaltyValue - prev_GorrNetRoyaltyValue
            h.Booked = h.BookedBaseNetRoyaltyValue + h.BookedGorrNetRoyaltyValue
            prev_BaseNetRoyaltyValue = h.BaseNetRoyaltyValue
            prev_GorrNetRoyaltyValue = h.GorrNetRoyaltyValue

        monthly_array = db.select('Monthly', ExtractDate=calc.ExtractDate, Entity=calc.Entity, EntityID=calc.EntityID,
                                  prodMonth=calc.ProdMonth, product=calc.Product, RPBA=calc.RPBA)
        if len(monthly_array) == 0:
            raise AppError("There were no monthly records for well: " + str(calc.WellID) + " ProdDate: " +
                           str(calc.ProdMonth) + " Product: " + calc.Product)
        monthly = monthly_array[0]  # if there are multiple pick the first one

        ba = db.select1('BAInfo', BAid=monthly.RPBA, BAType='RTP')

        calc_specific = DataStructure(calc.RoyaltySpecific)
        rtp_info = db.select1('RTPInfo', WellEvent=well.WellEvent, Product=calc.Product, Payer=monthly.RPBA,
                              Date=prod_month_to_date(calc.ProdMonth))

        royalty.format_gorr = format_gorr(calc.Gorr)

        return render_template('worksheet/pdfcalc_worksheet.html',
                               well=well, rm=royalty, m=monthly, lease=lease,
                               calc=calc, calc_sp=calc_specific, entity_lease_link=entity_lease_link,
                               ba=ba, rtp_info=rtp_info, history=history)
    except Exception as e:
        print('views.worksheet: ***Error:', e)
        traceback.print_exc(file=sys.stdout)
        tb = traceback.format_exc()
        return "<h2>Error displaying worksheet for " + calc.Entity + " %s</h2><br>" % calc.EntityID + str(e) + \
               '<plaintext>' + tb + '</plaintext>'
