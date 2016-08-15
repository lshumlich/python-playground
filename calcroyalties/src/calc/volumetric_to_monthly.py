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
from src.util.apperror import AppError
from src.database.data_structure import DataStructure

def volumetric_to_monthly():

    db = config.get_database()
    statement = """SELECT * from VolumetricInfo
    JOIN Well on VolumetricInfo.FromTo = Well.WellEvent
    WHERE VolumetricInfo.Activity='PROD' and VolumetricInfo.Amendment=0 """
    volumetric = db.select_sql(statement)
    print(volumetric)
    updated_counter = 0
    inserted_counter = 0
    total_counter = 0

    for a in volumetric:
        total_counter += 1
        old_prod = a.ProdMonth.isoformat()[0:7]
        new_prod = old_prod.replace('-', '')

        existing = db.select('Monthly', AmendNo=0, Product=a.Product, WellId=a.ID, ProdMonth=new_prod)
        if len(existing) == 1:
            print('Already in the table: ', existing)
            existing[0].ProdHours = a.Hours
            existing[0].ProdVol = a.Volume
            db.update(existing[0])
            updated_counter += 1
        elif len(existing) == 0:
            ds = db.get_data_structure('Monthly')
            ds.ProdMonth = new_prod
            ds.WellID = a.ID

            if a.Hours == 'NULL':
                ds.ProdHours = None
            else:
                ds.ProdHours = a.Hours

            ds.Product = a.Product
            ds.AmendNo = a.Amendment
            ds.ProdVol = a.Volume
            print(e)
            print('Inserting ', ds.WellID)
            db.insert(ds)
            inserted_counter += 1

        else:
            raise AppError(len(existing), " records found in table Monthly for ", a)

    return('Complete. %i records traversed, %i records inserted, %i records updated' % (total_counter, inserted_counter, updated_counter))