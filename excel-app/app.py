#!/bin/env python3

from flask import Flask, render_template
from database import DataBase

app = Flask(__name__)

db = DataBase("database.xlsx")

@app.route("/")
def mainpage():
	return render_template("index.html")

@app.route("/lease")
def returnAllLeases():
    leases = db.getAllLeases()
    return render_template("lease.html", leases = leases)

@app.route("/lease/<lease>")
def returnLease(lease=None):
    wells = db.getWellbyLease(lease)
    return render_template("wells.html", wells = wells)

if __name__ == "__main__":
	app.run(debug=True)