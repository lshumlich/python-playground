from flask import Blueprint, request, render_template
from openpyxl import load_workbook
from batch import drop_create_tables, process_royalties
from src.calc import volumetric_to_monthly
from src.tool import sqlite_load_excel

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
        results = process_xls(file)
        return render_template('/process/load_xls.html', results=results)

def process_xls(file):
    try:
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
    except Exception as e:
        results += '<span style="color:red;"><br>Error: %s</span>' % str(e)
    return results