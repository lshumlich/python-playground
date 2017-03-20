from flask import Blueprint, request, render_template, abort, flash

import config
from .main import get_proddate, get_proddate_int

wells = Blueprint('wells', __name__)


@wells.route('/wells')
# @PermissionHandler('well_view')
def search():
    if not request.args:
        return render_template('wells/search.html')
    try:
        argument_tables = {'Prov': 'WellRoyaltyMaster', 'WellType': 'WellRoyaltyMaster',
                           'ID': 'WellRoyaltyMaster', 'Classification': 'WellRoyaltyMaster',
                           'FNBandID': 'Lease'}  # allowed Property:Table pairs
        kwargs = dict((k, v) for k, v in request.args.items() if v and k in argument_tables)  # this is to get rid
        # of empty values coming from forms and convert multidict to dict and to check if argument is allowed
        print(kwargs)
        search_arguments = ""
        for arg in kwargs:
            compound = argument_tables[arg] + '.' + arg + '=' + '"' + kwargs[arg] + '"'
            search_arguments += " AND " + compound
        statement = """SELECT WellRoyaltyMaster.*, FNBand.FNBandName, Lease.FNBandID FROM WellRoyaltyMaster, FNBand, WellLeaseLink, Lease
                       WHERE WellRoyaltyMaster.ID = WellLeaseLink.WellID
                       AND WellLeaseLink.LeaseID = Lease.ID
                       AND Lease.FNBandID = FNBand.ID
                       AND DATE("{proddate}") BETWEEN WellRoyaltyMaster.StartDate and WellRoyaltyMaster.EndDate
                    """.format(proddate=get_proddate()) + search_arguments
        db = config.get_database()
        print(statement)
        result = db.select_sql(statement)
        if result:
            print(result)
            return render_template('wells/search.html', results=result, search_terms=request.args.to_dict())
        else:
            flash('No matching wells found', 'error')
            return render_template('wells/search.html', search_terms=request.args.to_dict())
    except Exception as e:
        print(e)
        abort(404)


@wells.route('/wells/<well_num>')
def details(well_num):
    try:
        db = config.get_database()
        result = db.select1('WellRoyaltyMaster', ID=well_num)
        return render_template('wells/details.html', well=result)
    except Exception as e:
        print(e)
        abort(404)


@wells.route('/well/calculate')
def calculate():
    from src.calc.calcroyalties import ProcessRoyalties
    pr = ProcessRoyalties()
    well_id = int(request.args.get('WellId'))
    prod_date = int(request.args.get('ProdDate'))
    print("We are in the calculate thing..... for ", well_id)
    db = config.get_database()
    for monthlyData in db.select('Monthly',WellId=well_id,ProdMonth=prod_date):
        try:
            print("about to calculate...")
            pr.process_one(well_id, monthlyData.ProdMonth, monthlyData.Product)
        except Exception as e:
            print("We have an error")
            print(e)
            return 'Something went wrong during calculation for %s, %i, %s:<br />%s' % \
                   (well_id, monthlyData.ProdMonth, monthlyData.Product, str(e))

    return "Processing complete for well: %i %i" % (well_id, prod_date)