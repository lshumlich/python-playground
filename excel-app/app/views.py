#!/bin/env python3

from flask import render_template, request, redirect, url_for, flash
import json
import sys,traceback

from app import app
from database import database
from database import calcroyalties
from database.sqlite_show import Shower
from database.utils import Utils
import config


db = database.DataBase(config.get_file_dir() + 'database new.xlsx')
pr = calcroyalties.ProcessRoyalties()
rw = calcroyalties.RoyaltyWorksheet()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/2')
def index2():
    return render_template('index2.html')

@app.route('/searchwells/')
def searchwells():
    return render_template('searchwells.html')

@app.route('/well/<wellid>')
def well(wellid):
    if wellid:
        well=db.getWell(int(wellid))
        return render_template('well.html', well=well)

@app.route('/leases')
def leases():
    all_leases = db.getAllLeases()
    return_leases = []
    if request.args:
        for l in all_leases:
#            if l.Lease == request.args['leaseid']:
            if (request.args['leaseid'] == "" or request.args['leaseid'] == l.Lease) and \
                (request.args['prov'] == "" or request.args['prov'] == l.Prov):
                    return_leases.append(l)
        if len(return_leases) == 0:
            flash('No matching leases found.')
            return redirect(url_for('searchleases'))
        elif len(return_leases) == 1:
            return redirect(url_for('lease', leaseid=return_leases[0].Lease))
        else:
            return render_template('leases.html', leases=return_leases)
    else:
        return render_template('leases.html', leases=all_leases)

@app.route('/lease/<leaseid>')
def lease(leaseid):
    if leaseid:
        lease=db.getLease(leaseid)
        rm=db.getRoyaltyMaster(leaseid)
        return render_template('lease.html', lease=lease, rm=rm)

@app.route('/wells')
def wells():
    all_wells = db.getAllWells()
    return_wells = []
    if request.args:
        for w in all_wells:
            if (request.args['wellid'] == "" or int(request.args['wellid']) == w.WellId) \
                and (request.args['welltype'] == "" or request.args['welltype'] == w.WellType) \
                and (request.args['uwi'] == "" or request.args['uwi'] == w.UWI):
                    return_wells.append(w)
        if len(return_wells) == 0:
            flash('No matching wells found.')
            return redirect(url_for('searchwells'))
        elif len(return_wells) == 1:
            return redirect(url_for('well', wellid=return_wells[0].WellId))
        else:
            return render_template('wells.html', wells=return_wells)
    else:
        return render_template('wells.html', wells=all_wells)

@app.route('/searchleases')
def searchleases():
    return render_template('searchleases.html')


@app.route("/data/",methods=['GET','POST'])
def data():
    try:
        db_instance = config.get_database_instance()
        shower = Shower()

        table=request.args.get('table')
        attr=request.args.get('attr')
        key=request.args.get('key')
        links = {}
        links['BAid'] = '?table=BAInfo&attr=BAid&key=' 
        links['WellEvent'] = '?table=WellInfo&attr=Well&key='
        
        tables = db_instance.get_table_names()
        header = None
        rows = None
        print('Table:',table)
        if table:
            header = shower.show_columns(table)
            rows = shower.show_table(table,attr,key)
        html = render_template('data.html',table=table,tables=tables,header=header,rows=rows,links=links)
    except Exception as e:
        print('views.data: ***Error:',e)
        traceback.print_exc(file=sys.stdout)

    return html

@staticmethod
@app.route("/data/updateLinkRow.json",methods=['POST']) 
def update_link_row():
    utils = Utils()
    db = config.get_database()
    return_data = dict()
    try:
        print('AppServer.update_link_row running',request.method)
        data = utils.json_decode(request)
        print('data:',data)
        linktab = db.get_data_structure('LinkTab')
        utils.dict_to_obj(data,linktab)
        print('just before if data:',data)
        print('just before if data:',data['ID'])
        if data['ID'] == '0':
            db.insert(linktab)
        else:
            db.update(linktab)
        
        return_data['StatusCode'] = 0
        return json.dumps(return_data)
    
    except Exception as e:
        print('AppServer.link: ***Error:',e)
        traceback.print_exc(file=sys.stdout)
        return_data['StatusCode'] = -1
        return_data['Message'] = str(e)
        return json.dumps(return_data)
        
@staticmethod
@app.route("/data/getLinkRow.json",methods=['POST']) 
def get_link_row():
    utils = Utils()
    db = config.get_database()
    try:
        print('AppServer.get_link_row running',request.method)
        print('Instance:',config.get_database_name(),config.get_environment())
        print('Tables',config.get_database_instance().get_table_names())
        data = utils.json_decode(request)
        link = db.select("LinkTab", TabName = data['TabName'], AttrName = data['AttrName'])
        print('link',link)
        if not link:
            data['ID'] = 0
            data['LinkName'] = ''
            data['BaseTab'] = 0
            data['ShowAttrs'] = ''
        else:
            data['ID'] = link[0].ID
            data['LinkName'] = link[0].LinkName
            data['BaseTab'] = link[0].BaseTab
            data['ShowAttrs'] = link[0].ShowAttrs

        return json.dumps(data)
    
    except Exception as e:
        print('AppServer.link: ***Error:',e)
        traceback.print_exc(file=sys.stdout)

@staticmethod
@app.route("/data/getLinkData.json",methods=['POST']) 
def get_link_data():
    utils = Utils()
    db = config.get_database()
    try:
        data = utils.json_decode(request)
#             print('data', data)
        link = db.select("LinkTab", TabName = data['TabName'], AttrName = data['AttrName'])
#             print('link',link)
        if len(link) > 0:
            result_rows = db.select("LinkTab", LinkName=link[0].LinkName, BaseTab=1)
#                 print('result:',result_rows)
#                 print('result.type:',type(result_rows))
            
            # Get the base table
            for result in result_rows:
                print('We have a base table')
                attrs_to_show = result.ShowAttrs.split(',')
                args = dict()
                args[result.AttrName] = data['AttrValue']
                key_data_rows = db.select(result.TabName,**args)
                rows = []
                for keyData in key_data_rows:
                    row = []
                    for a in attrs_to_show:
                        row.append(keyData.__dict__[a])
                    rows.append(attrs_to_show)
                    rows.append(row)
                data['BaseData'] = rows
            
            # Get all the tables that the link uses
            result_rows = db.select("LinkTab", LinkName=link[0].LinkName)
            
            rows = []
            for result in result_rows:
                row = []
                row.append(result.TabName)
                row.append(result.AttrName)
                rows.append(row)
            data['Links'] = rows
            
        else:
            data["Message"] = data['AttrName'] + " has not been linked."
        return json.dumps(data)
#         
    except Exception as e:
        print('AppServer.link: ***Error:',e)
        traceback.print_exc(file=sys.stdout)


@app.route('/worksheet')
def worksheet():
#    if request.args:
#        md = db.getMonthlyByWell(int(request.args["WellId"]))
#    pr.process('database/database.xlsx')
    with open("Royalty Worksheet.txt", 'r') as f:
        ws = f.read()
        return render_template('worksheet.html', ws=ws)


@app.route('/adriennews')
def adriennews():
    if request.args:
        wellIds = request.args["WellId"]
        wellId = int(wellIds)
        prodMonth = 201501
        product = "Oil"
        well=db.getWell(wellId)
        lease=db.getLease(well.Lease)
        royalty = db.getRoyaltyMaster(well.Lease)
        royaltyCalc= db.getCalcDataByWellProdMonthProduct(wellId,prodMonth,product)
        monthlydata = db.getMonthlyDataByWellProdMonthProduct(wellId,prodMonth,product)

        commencement_period = pr.determineCommencementPeriod(prodMonth, well.CommencementDate)
        well_head_price = monthlydata.WellHeadPrice
        prod_vol = monthlydata.ProdVol
        method = royalty.ValuationMethod
        royalty_regulation2 = pr.calcSaskOilRegulationSubsection2(prod_vol)
        royalty_regulation3 = pr.calcSaskOilRegulationSubsection3(prod_vol)
        if commencement_period <= 5:
            royalty_regulation = royalty_regulation2
        else:
            royalty_regulation = royalty_regulation3
        reference_price = 25
        supplementary_royalty = pr.calcSupplementaryRoyaltiesIOGR1995(commencement_period, well_head_price, prod_vol, royalty_regulation, reference_price)

        #calc = db.getCalcDataByWellProdMonthProduct(wellId,prodMonth,product)
        #yyyy_mm = str[0:4]+'-'+str[4:6]
        print(monthlydata)
    else:
        print("No monthly data for this well")





    return render_template('worksheetas.html', well=well, rm=royalty, m=monthlydata, product=product, lease=lease,
                           royaltyCalc=royaltyCalc, prodMonth=prodMonth, commencement_period = commencement_period,
                           well_head_price = well_head_price, prod_vol = prod_vol, method = method, royalty_regulation2 = royalty_regulation2,
                           royalty_regulation3 = royalty_regulation3, reference_price = reference_price, supplementary_royalty = supplementary_royalty)

#    return "from adriennes well is" + wellId + "and the well is " + str(well.headers()) + str(well.data())


@app.errorhandler(404)
def not_found(error):
    return render_template('404.html')
