#!/bin/env python3

from database import DataBase

db = DataBase("database.xlsx")

#lease = "xxx"
#    
#print (db.getWellbyLease(lease))
#
#for w in db.getWellbyLease(lease):
#    print (w.UWI, w.Lease)

#for w in db.well:
    #print (db.well[w].WellId)

#for c in list(db.lease.values())[0].HeaderRow:
#    print (c.value)

for l in db.getAllLeases():
    print (l)
    
lease = "OL-0001"

leaseHeaders = []
for c in db.lease[lease].HeaderRow:
    leaseHeaders.append(c.value)

final = {}
for lh in leaseHeaders:
    final[lh] = getattr(db.getLease("OL-0001"), lh)

print (final)