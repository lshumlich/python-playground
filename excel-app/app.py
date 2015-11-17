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
    leaseWells = db.getWellbyLease(lease)
    newlease = db.getLease(lease)
    return render_template("lease.html", leaseWells = leaseWells, lease = newlease)

@app.route("/well/<well>")
def returnWell(well = None):
    try: 
        newwell = db.getWell(int(well))
        return render_template("well.html", well = newwell)
    except:
        raise
        #return "Something awful has occured"
        

if __name__ == "__main__":
	app.run(debug=True)