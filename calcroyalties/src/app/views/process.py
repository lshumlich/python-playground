from flask import Blueprint, request, render_template, abort

import config
from .permission_handler import PermissionHandler
from .main import get_proddate_int
from src.calc import volumetric_to_monthly

process = Blueprint('process', __name__)

@process.route('/process/load_petrinex')
# @PermissionHandler('well_view')
def load_petrinex():
    return(volumetric_to_monthly.volumetric_to_monthly())