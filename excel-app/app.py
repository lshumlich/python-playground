#!/bin/env python3

from flask import Flask, render_template
from database import DataBase

app = Flask(__name__)

db = DataBase("database.xlsx")

@app.route("/")
def mainpage():
    wells = db.getAllWells()
    leases = db.getAllLeases()
    return render_template("index.html", leases = leases, wells = wells)

#@app.route("/lease")
#def returnAllLeases():
#    leases = db.getAllLeases()
#    return render_template("lease.html", leases = leases)

@app.route("/lease/<lease>")
def returnLease(lease = None):
    leaseHeaders = []
    for c in db.lease[lease].HeaderRow:
        leaseHeaders.append(c.value)

    printLease = {}
    for lh in leaseHeaders:
        printLease[lh] = getattr(db.getLease(lease), lh)

    leaseWells = db.getWellbyLease(lease)

    helpref = {"Lease": "Name of lease<br>Alphanumeric",
               "Province": "Province of lease<br>Alphanumeric"
              }
    
    return render_template("lease.html", leaseWells = leaseWells, lease = printLease, helpref = helpref)

@app.route("/well/<well>")
def returnWell(well = None):
    wellHeaders = []
    try:
        for c in db.well[int(well)].HeaderRow:
            wellHeaders.append(c.value)
    except:
        raise 
    newwell = db.getWell(int(well))
    return render_template("well.html", well = newwell, wellHeaders = wellHeaders)
        

if __name__ == "__main__":
	app.run(debug=True)