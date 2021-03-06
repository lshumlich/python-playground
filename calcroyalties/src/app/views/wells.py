from flask import Blueprint, request, render_template, abort, flash, redirect, url_for, json
import sys
import traceback

import config
from .main import get_proddate
from src.database.data_structure import DataStructure

wells = Blueprint('wells', __name__)


@wells.route('/wells/')
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
        statement = """SELECT WellRoyaltyMaster.*, FNBand.FNBandName, Lease.FNBandID FROM WellRoyaltyMaster, FNBand, EntityLeaseLink, Lease
                       WHERE WellRoyaltyMaster.ID = EntityLeaseLink.EntityID
                       AND EntityLeaseLink.Entity = 'Well'
                       AND EntityLeaseLink.LeaseID = Lease.ID
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


# @wells.route('/wells/<well_num>', methods=['GET','POST'])
# def details(well_num):
#     try:
#         db = config.get_database()
#         result = db.select1('WellRoyaltyMaster', ID=well_num)
#         return render_template('wells/details.html', new = False, well=result)
#     except Exception as e:
#         print(e)
#         abort(404)

@wells.route('/wells/<well_num>', methods=['GET', 'POST'])
def details(well_num):
    db = config.get_database()
    if request.method == 'POST' and request.form['action'] == 'delete':
        try:
            print('about to delete')
            well_id = int(request.form['ID'])
            print(well_id)
            db.delete('WellRoyaltyMaster', well_id)
            flash('Successfully deleted well ' + str(well_id))
            return redirect(url_for('wells.search'))
        except Exception as e:
            print('Failed to delete well ' + request.form['ID'], e)
            flash('Failed to delete well ' + request.form['ID'])
            return redirect(url_for('wells.search'))
    elif request.method == 'POST' and request.form['action'] == 'update':
        ds = db.select1('WellRoyaltyMaster', ID=well_num)
        try:
            for i in request.form:
                if i != 'action':
                    setattr(ds, i, request.form[i])
            db.update(ds)
            flash('Successfully updated well ' + well_num)
            return redirect(url_for('wells.details', well_num=well_num))
        except Exception as e:
            flash('Couldn\'t update a well')
            print('Couldn\'t update a well: ', e)
            return redirect(url_for('wells.search'))
    elif request.method == 'GET':
        try:
            db = config.get_database()
            result = db.select1('WellRoyaltyMaster', ID=well_num)
            return render_template('wells/details.html', new=False, well=result)
        except Exception as e:
            print(e)
            abort(404)


@wells.route('/wells/new', methods=['GET', 'POST'])
def new():
    db = config.get_database()
    if request.method == 'GET':
        return render_template('wells/details.html', new=True, well=None)
    elif request.method == 'POST' and request.form['action'] == 'cancel':
        return redirect(url_for('wells.search'))
    elif request.method == 'POST' and request.form['action'] == 'add':
        ds = DataStructure()
        setattr(ds, '_table_name', 'WellRoyaltyMaster')
        setattr(ds, 'StartDate', '1999-01-01 00:00:00')
        setattr(ds, 'EndDate', '9999-01-01 00:00:00')
        for i in request.form:
            if i != 'action':
                setattr(ds, i, request.form[i])
        try:
            new_id = db.insert(ds)
            flash('Well successfully added')
            return redirect(url_for('wells.details', well_num=new_id))
        except Exception as e:
            flash('Couldn\'t add a new well')
            print('Couldn\'t add a new well: ', e)
            return redirect(url_for('wells.search'))


@wells.route('/wells/<lease_num>/leases.json', methods=['GET', 'POST'])
def leases(lease_num):
    db = config.get_database()
    leases_statement = """SELECT LeaseRoyaltyMaster.* FROM LeaseRoyaltyMaster, WellLeaseLink
               WHERE WellLeaseLink.WellID="%s"
               AND LeaseRoyaltyMaster.ID=WellLeaseLink.LeaseID"""
    lease_r = db.select_sql(leases_statement % lease_num)
    result = []
    for l in lease_r:
        result.append(l.json_dumps())
    return json.dumps(result)


@wells.route('/well/calculate')
def calculate():
    from src.calc.calcroyalties import ProcessRoyalties
    pr = ProcessRoyalties()

    print("We are in the calculate thing..... for ", request.args)
    db = config.get_database()
    for monthly in db.select('Monthly', ExtractDate=int(request.args.get('ExtractDate')),
                             ProdMonth=int(request.args.get('ProdMonth')),
                             Entity=request.args.get('Entity'),
                             EntityId=int(request.args.get('EntityID'))):
        try:
            print("about to calculate...")
            pr.process_one(monthly.ExtractDate, monthly.Entity, monthly.EntityID, monthly.ProdMonth, monthly.Product)
        except Exception as e:
            print("We have an error")
            traceback.print_exc(file=sys.stdout)
            tb = traceback.format_exc()
            return "<h2>Error displaying worksheet for " + monthly.Entity + " %s</h2><br>" % monthly.EntityID + \
                   str(e) + '<plaintext>' + \
                   tb + '</plaintext>'

            # print(e)
            # return 'Something went wrong during calculation for %s, %s, %i, %s:<br />%s' % \
            #        (monthly.Entity, monthly.EntityID, monthly.ProdMonth, monthly.Product, str(e))

    return "Processing complete."
