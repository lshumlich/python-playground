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
volumetric = db.select('VolumetricInfo', Activity='PROD', Amendment=0)
wells = db.select('Well')
counter = 0
well_counter = 0
for a in volumetric:
    counter += 1
    ds = db.get_data_structure('Monthly')
    oldprod = a.ProdMonth.isoformat()[0:7]
    ds.ProdMonth = oldprod.replace('-', '')
    for well in wells:
        if well.WellEvent == a.FromTo:
            ds.WellID = well.ID
            well_counter += 1
    if a.Hours == 'NULL':
        ds.ProdHours = None
    else:
        ds.ProdHours = a.Hours

    ds.Product = a.Product
    ds.AmendNo = a.Amendment
    ds.ProdVol = a.Volume

    db.insert(ds)

print('Complete. %i records inserted' % counter)