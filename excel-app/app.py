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
        
#    printLease = {}
#    for lh in leaseHeaders:
#        printLease[lh] = getattr(db.getLease(lease), lh)
    printLease = []
    for lh in leaseHeaders:
        printLease.append((lh, getattr(db.getLease(lease), lh)))
        
    leaseWells = db.getWellbyLease(lease)

    helpref = {"Lease": "Name of lease.",
               "Prov": "Province of lease.",
               "LeaseType": "Type of lease.",
               "LeaseID": "Lease ID number.",
               "FNReserve": "FN reserve number.",
               "Lessor": "Name of lessor.",
               "Notes" :"Miscellaneous notes."
              }
    
    return render_template("lease.html", leaseWells = leaseWells, lease = lease, printLease = printLease, helpref = helpref)

@app.route("/well/<well>")
def returnWell(well = None):
    printWell = db.getWell(int(well))
    return render_template("well.html", well = printWell)
        

if __name__ == "__main__":
	app.run(debug=True)