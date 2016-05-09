'''
variables in monthly:
ID (add 1 to previous)
ExtractMonth	(where is this from?)
ProdMonth: volumetric_info.ProdMonth
WellID: Well.WellID (using FromTo in volumetric_info to match event)
Product: volumetric_info.Product
AmendNo: volumetric_info.AmendNo
ProdHours: volumetric_info.Hours
ProdVol: volumetric_info.Volume
TransPrice: (need)
WellHeadPrice: (need)
TransRate: (need)
ProcessingRate: (need)
'''

import config
from src.database.data_structure import DataStructure

db = config.get_database()
statement = """SELECT * from VolumetricInfo
JOIN well on VolumetricInfo.FromTo = Well.WellEvent
WHERE VolumetricInfo.Activity='PROD' and VolumetricInfo.Amendment=0 """
volumetric = db.select_sql(statement)
updated_counter = 0
inserted_counter = 0

for a in volumetric:
    ds = db.get_data_structure('Monthly')
    oldprod = a.ProdMonth.isoformat()[0:7]
    ds.ProdMonth = oldprod.replace('-', '')
    ds.WellID = a.ID

    if a.Hours == 'NULL':
        ds.ProdHours = None
    else:
        ds.ProdHours = a.Hours

    ds.Product = a.Product
    ds.AmendNo = a.Amendment
    ds.ProdVol = a.Volume

    try:
        existing = db.select1('Monthly', AmendNo=0, Product=ds.Product, WellId=ds.WellID, ProdMonth=ds.ProdMonth)
        print('Already in the table: ', existing)
        existing.ProdHours = a.Hours
        existing.ProdVol = a.Volume
        db.update(existing)
        updated_counter += 1
    except Exception as e:
        print(e)
        print('Inserting ', ds.WellID)
        db.insert(ds)
        inserted_counter += 1

print('Complete. %i records inserted, %i records updated' % (inserted_counter, updated_counter))