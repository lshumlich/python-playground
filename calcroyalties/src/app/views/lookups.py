from flask import Blueprint, request, config, redirect, url_for, abort, render_template, flash, Response
import json, io, csv

import config
from .permission_handler import PermissionHandler
from src.util.apperror import AppError
from .main import get_proddate

lookup = Blueprint('lookup', __name__)

@lookup.route('/lookup/ba')
def ba():
    return render_template('lookups/ba.html')

@lookup.route('/lookup/ba_results')
def ba_results():
    db = config.get_database()
    statement = """SELECT * FROM BAInfo WHERE (DATE('{proddate}') BETWEEN BAInfo.StartDate AND BAInfo.EndDate OR BAInfo.StartDate IS NULL)""".format(proddate=get_proddate())
    argument_tables = {'CorpLegalName': 'BAInfo', 'BAType': 'BAInfo', 'BAid': 'BAInfo'}
    kwargs = dict((k, v) for k, v in request.args.items() if v)  # this is to get rid of empty values coming from forms
    search_arguments = ""
    for arg in kwargs:
        if arg in argument_tables:
            compound = argument_tables[arg] + '.' + arg + '=' + '"' + kwargs[arg] + '"'
            if arg == 'CorpLegalName': compound = argument_tables[arg] + '.' + arg + ' LIKE ' + '"%' + kwargs[arg] + '%"'
            search_arguments += " AND " + compound
    print(statement + search_arguments)
    results = db.select_sql(statement + search_arguments)
    return render_template('lookups/ba_results.html', results = results)