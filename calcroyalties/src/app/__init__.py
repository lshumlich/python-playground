#!/bin/env python3 

from flask import Flask

app = Flask(__name__)
app.secret_key = 'secret'

from src.app.views.main import main
from src.app.views.wellevents import wellevents
from src.app.views.admin import admin
from src.app.views.leases import leases
from src.app.views.wells import wells
from src.app.views.facility import facility
from src.app.views.worksheet import worksheet
from src.app.views.lookups import lookups
from src.app.views.reports import reports
from src.app.views.process import process

app.register_blueprint(main)
app.register_blueprint(wellevents)
app.register_blueprint(admin)
app.register_blueprint(leases)
app.register_blueprint(wells)
app.register_blueprint(facility)
app.register_blueprint(worksheet)
app.register_blueprint(lookups)
app.register_blueprint(reports)
app.register_blueprint(process)