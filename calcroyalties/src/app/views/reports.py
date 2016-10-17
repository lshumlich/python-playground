from flask import Blueprint, request, render_template, abort

import config
from .permission_handler import PermissionHandler
from .main import get_proddate_int

reports = Blueprint('reports', __name__)

@reports.route('/reports/royalties')
@PermissionHandler('well_view')
def royalties():
    db = config.get_database()
    proddate=get_proddate_int()
    statement = """SELECT * from calc, wellleaselink where calc.wellid = wellleaselink.wellid
                and calc.prodmonth = {proddate}""".format(proddate=proddate)
    result = db.select_sql(statement)
    if result:
        return render_template('reports/royalties.html', result=result)
    else:
        return "Nothing found"