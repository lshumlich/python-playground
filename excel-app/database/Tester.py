#!/bin/env python3

from database import DataBase
from calcroyalties import ProcessRoyalties, RoyaltyWorksheet

db = DataBase("database.xlsx")
pr = ProcessRoyalties()
rw = RoyaltyWorksheet()

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

# for l in db.getAllLeases():
#     print (l)
    
# lease = "OL-0001"

# leaseHeaders = []
# for c in db.lease[lease].HeaderRow:
#     leaseHeaders.append(c.value)

# final = {}
# for lh in leaseHeaders:
#     final[lh] = getattr(db.getLease("OL-0001"), lh)

# print (final)

# royalty = db.getRoyaltyMaster("OL-0001")
# print(royalty)

#lease = db.getLease("OL-0001")
#print(lease)

# if "5" == 5:
# 	print("is equal")
# else:
# 	print("not equal")

# leases = db.getAllLeases()
# print(leases)

# lease="OL-0004"
# rm = db.getRoyaltyMaster(lease)
# print(rm)

###
#print(db.getMonthlyByWell(6))

md = db.getMonthlyByWell(6)
# well = db.getWell(monthlyData.WellId)
# royalty = db.getRoyaltyMaster(well.Lease)
# lease = db.getLease(well.Lease)
# royaltyCalc=db.getRoyaltyCalc(monthlyData.ProdMonth,monthlyData.WellId)

#printSaskOilRoyaltyRate(self, monthlyData, well, royalty, lease, royaltyCalc)
pr.process('database.xlsx', md)
#rw.printSaskOilRoyaltyRate(monthlyData, well, royalty, lease, royaltyCalc)