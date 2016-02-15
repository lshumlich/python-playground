#!/bin/env python3

import unittest

import config
import database.sqlite_load_excel
import database.sqlite_objects


class Test(unittest.TestCase):

    def test_sqlite_objects(self):
        #Preparing the database
        db = config.getFileDir() + 'test_database.db'
        worksheet = config.getFileDir() + 'database.xlsx'
        loader = database.sqlite_load_excel.Loader()
        loader.delete_database(db)
        loader.connect(db)
        loader.openExcel(worksheet)
        loader.loadAllSheets()
        loader.close()

        #Testing the wells
        dw = database.sqlite_objects.DataWell()
        dw.connect(db)
        dw.load_wells_from_sqlite()
        self.assertEqual(len(dw.get_all_wells()), 33)
        self.assertEqual(dw.get_well(5).WellId, 5)
        self.assertRaises(database.apperror.AppError, dw.get_well, 99)
        self.assertEqual(len(dw.get_wells_by_lease(5)), 5)
        self.assertRaises(database.apperror.AppError, dw.get_wells_by_lease, 666)
        dw.close()

        #Testing the leases
        dl = database.sqlite_objects.DataLease()
        dl.connect(db)
        dl.load_leases_from_sqlite()
        self.assertEqual(len(dl.get_all_leases()), 10)
        self.assertEqual(dl.get_lease(8).LeaseID, 8)
        self.assertRaises(database.apperror.AppError, dl.get_lease, 99)
        dl.close()

        #Testing the universal sql select
        dw.connect(db)
        self.assertEqual(len(dw.universal_select('Well', RoyaltyClassification='Old Oil')), 5)
        self.assertEqual(len(dw.universal_select('Well')), 33)
        self.assertRaises(database.apperror.AppError, dw.universal_select, 'Well', DoesNotExist=5)
        self.assertEqual(len(dw.universal_select('Lease')), 10)
        self.assertEqual(len(dw.universal_select('Lease', Prov='SK')), 5)
        self.assertRaises(database.apperror.AppError, dw.universal_select, 'WrongTable')
        dw.close

        #Cleaning up
        loader.delete_database(db)


if __name__ == '__main__':
    unittest.main()