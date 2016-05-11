#!/bin/env python3 

from flask import Flask

app = Flask(__name__)
app.secret_key = 'secret'

from src.app.views.main import main
from src.app.views.wellevent import wellevent
from src.app.views.admin import admin
from src.app.views.lease import lease
from src.app.views.well import well
from src.app.views.facility import facility
from src.app.views.worksheet import worksheet
from src.app.views.lookups import lookup

app.register_blueprint(main)
app.register_blueprint(wellevent)
app.register_blueprint(admin)
app.register_blueprint(lease)
app.register_blueprint(well)
app.register_blueprint(facility)
app.register_blueprint(worksheet)
app.register_blueprint(lookup)