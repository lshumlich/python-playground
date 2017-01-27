from flask import Blueprint, request, render_template

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
    drop_create_tables()
    sqlite_load_excel.load_sheet(file)
    process_royalties()
    results = 'File <b>%s</b> processed successfully.' % file.filename
    print(results)
    return results