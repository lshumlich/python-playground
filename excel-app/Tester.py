from database import DataBase

db = DataBase("database.xlsx")

lease = "xxx"
    
print (db.getWellbyLease(lease))

for w in db.getWellbyLease(lease):
    print (w.UWI, w.Lease)