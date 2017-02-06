from flask import Blueprint, request, render_template
from openpyxl import load_workbook
from batch import drop_create_tables, process_royalties, start_logging
from src.calc import volumetric_to_monthly
from src.tool import sqlite_load_excel
import config
import logging
import datetime

process = Blueprint('process', __name__)

@process.route('/process/load_petrinex')
# @PermissionHandler('well_view')
def load_petrinex():
    return(volumetric_to_monthly.volumetric_to_monthly())

@process.route('/process/load_xls', methods=['GET', 'POST'])
def load_xls():
    if request.method == 'GET':
        return render_template('/process/load_xls.html')
    elif request.method == 'POST':
        file = request.files['fileToUpload']
        results, log = process_xls(file)
        log = "<xmp>" + log + "</xmp>"
        return render_template('/process/load_xls.html', results=results, log=log)

def process_xls(file):
    try:
        start_logging()
        logging.info('Batch started: ' + str(datetime.datetime.now()))
        results = 'Testing the Excel file...'
        wb_temp = load_workbook(file, read_only=True)
        del wb_temp
        results += '<br>Seems OK. Dropping tables...'
        drop_create_tables()
        results += '<br>Loading data from the Excel sheet...'
        sqlite_load_excel.load_sheet(file)
        results += '<br>Processing royalties...'
        process_royalties()
        results += '<br><span style="color:green;">Done. File <b>%s</b> processed successfully.</span>' % file.filename
        logging.info('Batch finished: ' + str(datetime.datetime.now()))
    except Exception as e:
        results += '<span style="color:red;"><br>Error: %s</span>' % str(e)
    try:
        with open(config.get_temp_dir() + 'calc.log') as f:
            log = f.read()
    except:
        log = None
    return results, log