#!/bin/env python3

from app import app
from flask import render_template

@app.route('/')
def index():
    return render_template("index.html")

@app.route('/wells/')
def wells():
    return render_template("wells.html")
