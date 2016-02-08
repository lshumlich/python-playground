#!/bin/env python3

"""
The next step is to write a generic worksheet loader that will load any
type of data from a tab. The top row must be the field names, the rest of
the rows are the data. 

"""
import unittest
from openpyxl import load_workbook
from openpyxl import Workbook
from database.apperror import AppError

class DataStructure(object):
    
    def __init__(self):
        None
        
    def __str__(self):
        return str(vars(self))
    
    def headers(self):
        d = vars(self)
        return list(d.keys())

    def data(self):
        d = vars(self)
        return list(d.values())
    @property
    def Lease(self):
        return '{}-{:04d}'.format(self.LeaseType,self.LeaseID)

"""
    Generic class for fetching data.
    This is to simulate a database but much much much easier to change
"""

class DataBase(object):
    
    def __init__(self,worksheetName):
        try:
            self.worksheetName = worksheetName
            self.newWorksheetName = worksheetName + '-2'
            self.wb = load_workbook(worksheetName)
            self.wellTabName = 'Well'
            self.royaltyMasterTabName = 'RoyaltyMaster'
            self.leaseTabName = 'Lease'
            self.monthlyTabName = 'Monthly'
            self.calcTabName = 'Calc'
            self.producingEntityTabName = 'ProducingEntity'
            self.monthlyRecordId = 0
            self.productClausesTabName = 'ProductClauses'
            self.econOilDataTabName = 'ECONData'
            self.calcDataTabName = 'Calc'
        except FileNotFoundError:
            raise AppError('The excel worksheet ' + worksheetName + ' is not found')
        self.loadWellFromExcel()
        self.loadRoyaltyMasterFromExcel()
        self.loadLeaseFromExcel()
#        self.loadProductClausesFromExcel()
        self.loadMonthlyFromExcel()
#        self.loadProducingEntityFromExcel()
        self.loadECONOilDataFromExcel()
        self.loadCalcDataFromExcel()
        
    #
    # Royalty Master
    #
    def loadRoyaltyMasterFromExcel(self):
        stack = self.excelLoadWsTable(self.royaltyMasterTabName)
        self.royaltyMaster = dict()
        for ds in stack:
            self.royaltyMaster[ds.Lease] = ds
    
    def getRoyaltyMaster(self, lease):
        try:
            return self.royaltyMaster[lease]
        except KeyError:
            raise AppError ('Royalty Master not found for Lease: ' + lease)
        
    def updateRoyaltyMaster(self,royaltyMaster):
        self.whatChanged(royaltyMaster)
        
    #
    # Lease
    #
    def loadLeaseFromExcel(self):
        stack = self.excelLoadWsTable(self.leaseTabName)
        self.lease = dict()
        for ds in stack:
#             print(ds)
            self.lease[ds.Lease] = ds
        
    def getLease(self, lease):
        try:
            return self.lease[lease]
        except KeyError:
            raise AppError ('Lease not found for Lease: ' + lease)
            
    def getAllLeases(self):
        al = []
        try:
            for l in self.lease:
                al.append(self.lease[l])
#            al.sort()
            return al
        except KeyError:
            raise AppError ('No leases found')        

    def updateLease(self,lease):
        self.whatChanged(lease)
    #
    # Well
    #
    def loadWellFromExcel(self):
        self.wellList = self.excelLoadWsTable(self.wellTabName)
        self.well = dict()
        for ds in self.wellList:
            self.well[ds.WellId] = ds
        
    def getWell(self, wellId):
        try:
            return self.well[wellId]
        except KeyError:
            raise AppError ('Well not found for WellId: ' + str(wellId))
    
    def getAllWells(self):
        try:
            wl = []
            for w in self.well:
                wl.append(self.well[w])
            return wl
        except:
            raise AppError ("Wells not found")
        
    def getWellbyLease(self, lease):
        wl = []
        for w in self.wellList:
            if w.Lease == lease:
                wl.append(w)
        return wl
    def updateWell(self,well):
        self.whatChanged(well)
    #
    # Producing Entity 
    #
    def loadProducingEntityFromExcel(self):
        stack = self.excelLoadWsTable(self.producingEntityTabName)
        self.producingEntity = dict()
        for ds in stack:
            self.producingEntity[ds.PEID] = ds
        
    def getProducingEntity(self, lease):
        try:
            return self.producingEntity[lease]
        except KeyError:
            raise AppError ('Producing Entity not found for Lease: ' + lease)
    #
    # Product Clauses
    #
    def loadProductClausesFromExcel(self):
        stack = self.excelLoadWsTable(self.productClausesTabName)
        self.productClauses = dict()
        for ds in stack:
            self.royaltyMaster[ds.Lease] = ds

    #
    # Monthly Data 
    #
    def loadMonthlyFromExcel(self):
        self.monthlyTable = self.excelLoadWsTable(self.monthlyTabName)
        self.monthly = iter(self.monthlyTable)
    
    def monthlyDataNextRow(self):
        return next(self.monthly)

    def monthlyData(self):
        return self.monthly

    def getMonthlyByWell(self, wellId):
        wellResults = []
        for row in self.monthlyTable:
            if row.WellId == wellId:
                wellResults.append(row)
        return wellResults
    
    def getMonthlyData(self):
        return self.monthlyTable[0]
    
    def getMonthlyDataByWellProdMonthProduct(self,wellId,prodMonth,product):
        for md in self.monthlyData():
            if md.WellId == wellId and md.ProdMonth == prodMonth and md.Product == product:
#             if (md.WellId == wellId and md.ProdMonth == prodMonth and md.Product = product):
                return md
        raise AppError ('Monthly Data not found for: ' + str(wellId) + ' ' + str(prodMonth) + ' ' + product)

    #
    # ECON Monthly Oil Factors Data
    #
    def loadECONOilDataFromExcel(self):
        stack = self.excelLoadWsTable(self.econOilDataTabName)
        self.econOilData = dict()
        for ds in stack:
            self.econOilData[ds.ProdMonth] = ds
        
    def getECONOilData(self, prodMonth):
        try:
            return self.econOilData[prodMonth]
        except KeyError:
            raise AppError ('ECONOilData not found for: ' + str(prodMonth))

    #
    # Royalty Calculation
    #
    def getRoyaltyCalc(self,month,wellId):
        rc = DataStructure()
        setattr(rc, 'ProdMonth', month)
        setattr(rc, 'WellId', wellId)

        setattr(rc, 'K', 0.0)
        setattr(rc, 'X', 0.0)
        setattr(rc, 'C', 0.0)
        setattr(rc, 'D', 0.0)

        setattr(rc, 'RoyaltyPrice', 0.0)
        setattr(rc, 'RoyaltyVolume', 0.0)

        setattr(rc, 'ProvCrownRoyaltyRate', 0.0)
        setattr(rc, 'ProvCrownUsedRoyaltyRate', 0.0)
        setattr(rc, 'IOGR1995RoyaltyRate', 0.0)
        setattr(rc, 'GorrRoyaltyRate', 0.0)
        
        setattr(rc, 'ProvCrownRoyaltyVolume', 0.0)
        setattr(rc, 'GorrRoyaltyVolume', 0.0)
        setattr(rc, 'IOGR1995RoyaltyVolume', 0.0)
        
        setattr(rc, 'ProvCrownRoyaltyValue', 0.0)
        setattr(rc, 'IOGR1995RoyaltyValue', 0.0)
        setattr(rc, 'GorrRoyaltyValue', 0.0)
        
        setattr(rc, 'RoyaltyValuePreDeductions', 0.0)
        setattr(rc, 'RoyaltyTransportation', 0.0)
        setattr(rc, 'RoyaltyProcessing', 0.0)
        setattr(rc, 'RoyaltyDeductions', 0.0)
        setattr(rc, 'RoyaltyValue', 0.0)
        
        setattr(rc, 'CommencementPeriod', None)
        setattr(rc, 'Message', None)
        setattr(rc, 'GorrMessage', None)
        
        return rc

    def updateRoyaltyCalc(self, rc):
        try: 
            ws = self.wb[self.calcTabName]
            headerRow = ws.rows[0]
            tab = []
            for cell in headerRow:
                print(cell.value,getattr(rc,cell.value))
                tab.append(getattr(rc,cell.value))
            ws.append(tab)
                
            print(headerRow)
        except KeyError as e:
            raise AppError('The excel worksheet ' + self.worksheetName + " does not have tab: '" + self.calcTabName + "'")
            raise e
        except AttributeError as e:
            raise AppError("Royalty Calc Object has no value for attribute: '" + cell.value + "' correct worksheet header and continue.")
            raise e

        except Exception as e:
            raise e
        
    def loadCalcDataFromExcel(self):
        self.calc = self.excelLoadWsTable(self.calcDataTabName)

    
    def getCalcDataByWellProdMonthProduct(self,wellId,prodMonth,product):
        for md in self.calc:
            if md.WellId == wellId and md.ProdMonth == prodMonth:
#             if (md.WellId == wellId and md.ProdMonth == prodMonth and md.Product = product):
                return md
        raise AppError ('Calc Data not found for: ' + str(wellId) + ' ' + str(prodMonth) + ' ' + product)
    #
    # Generic load a tab into a data structure
    #
    def excelLoadWsTable(self,tabName):
        try: 
            ws = self.wb[tabName]
            stack = []
            recordNo = 0;
            headerRow = None
            for row in ws.rows:
                if headerRow == None:
                    headerRow = row
                else:
                    recordNo = recordNo +1
                    ds = DataStructure()
                    stack.append(ds)
                    i = 0
                    for cell in headerRow:
                        setattr(ds, cell.value, row[i].value)
                        i = i + 1
                    setattr(ds, 'RecordNumber', recordNo)
                    setattr(ds, 'ExcelRow', row)
                    setattr(ds, 'HeaderRow', headerRow)
        except KeyError:
            raise AppError('The excel worksheet ' + self.worksheetName + ' does not have tab: ' + tabName)
        except AttributeError as e:
            print('Error Loading tab:',tabName,' column:',i,'Record:',recordNo,'Error:',e)
            print('   cell.value:',cell.value)
            print('   headerRow:',headerRow)
            print('         row:',row)
            raise e
        except TypeError as e:
            print('Error Loading tab:',tabName,' column:',i,'Record:',recordNo,'Error:',e)
            print('   headerRow:',headerRow)
            print('         row:',row)
            raise e
            
        return stack
    
    def whatChanged(self,ds):
        i = 0
        for cell in ds.HeaderRow:
            vOrig = ds.ExcelRow[i].value # What was in the excel row
            vNew  = getattr(ds, cell.value)
            if vOrig != vNew:
                print(cell.value,'was',vOrig,'is',vNew)
                ds.ExcelRow[i].value = vNew
            i = i + 1
    # Note... We can change this to the same name once we are confident 
    def commit(self):
        print("*** Should be saving ***",self.newWorksheetName)
        self.wb.save(self.newWorksheetName)
        print("*** Should have saved ***")
    #
    # Used for testing
    #
    def forceWorkBook(self, workBook):
        self.wb = workBook
##    def royaltyMaster(self, id):
##        try:
##            return self.royaltyMasterData[id]
##        except AttributeError as e:
##            print('*** Time to load the royalty master buddy***')
            
"""
    Test Code....

    For these test to work there must be an excel file named "sample.xlsx"
    with the correct tabs.
"""
class TestDataBase(unittest.TestCase):
    
    def setUp(self):
        self.validExcelFile = 'database.xlsx'
        self.validExcelTab = 'Well'
        
    def test_getWorkSheetThatDoesNotExist(self):
        self.assertRaises(AppError,DataBase,'no way this exists.xlsxx')
        
    def test_excelLoadWsTable(self):
        fd = DataBase(self.validExcelFile)
        fd.excelLoadWsTable(self.validExcelTab)
        
    def test_excelLoadWsTableTabFales(self):
        fd = DataBase(self.validExcelFile)
        fd.forceWorkBook(Workbook()) # force an emply workbook
        self.assertRaises(AppError,fd.excelLoadWsTable,'SomeTabName')
        
    def test_readingMonthlyData(self):
        DataBase(self.validExcelFile)
        
    def test_getRoyaltyMasterNotFound(self):
        fd = DataBase(self.validExcelFile)
        self.assertRaises(AppError,fd.getRoyaltyMaster,'BadLease')

    def test_wellUpdate(self):
        wellId = 3000
        newUWI = 'Changed'
        newProv = 'Ch'
        NewReferencePrice = 10101.010101
        
        db = DataBase(self.validExcelFile)
        well = db.getWell(wellId)
        # Make sure we are not testing an already updated well
        self.assertNotEqual(well.UWI,newUWI) # If this fails we are testing with an already updated file
        
        well.UWI = newUWI
        well.Prov = newProv
        well.ReferencePrice = NewReferencePrice
        db.updateWell(well)
        db.commit()

        # New look into the new database and make sure the changes are made
        newDb = DataBase(db.newWorksheetName)
        newWell = newDb.getWell(wellId)
        self.assertEqual(newWell.UWI,newUWI)
        self.assertEqual(newWell.Prov,newProv)
        self.assertEqual(newWell.ReferencePrice,NewReferencePrice)

    def test_UpdateRoyaltyMaster(self):
        lease = 'OL-3000'
        newRoyaltyScheme = 'Changed'
        newProcessingDeducted = 'WhatEver'
        NewCrownMultiplier = 10101.010101
        
        db = DataBase(self.validExcelFile)
        rm = db.getRoyaltyMaster(lease)
        # Make sure we are not testing an already updated royalty master
        self.assertNotEqual(rm.RoyaltyScheme,newRoyaltyScheme) # If this fails we are testing with an already updated file
        
        rm.RoyaltyScheme = newRoyaltyScheme
        rm.ProcessingDeducted = newProcessingDeducted
        rm.CrownMultiplier = NewCrownMultiplier
        db.updateRoyaltyMaster(rm)
        db.commit()
        
        # New look into the new database and make sure the changes are made
        newDb = DataBase(db.newWorksheetName)
        newRM = newDb.getRoyaltyMaster(lease)
        self.assertEqual(newRM.RoyaltyScheme,newRoyaltyScheme)
        self.assertEqual(newRM.ProcessingDeducted,newProcessingDeducted)
        self.assertEqual(newRM.CrownMultiplier,NewCrownMultiplier)

    def test_UpdateLease(self):
        leaseId = 'OL-3000'
        newProv = 'Changed'
        newLessor = 'WhatEver'
        
        db = DataBase(self.validExcelFile)
        lease = db.getLease(leaseId)
        # Make sure we are not testing an already updated royalty master
        self.assertNotEqual(lease.Prov,newProv) # If this fails we are testing with an already updated file
        
        lease.Prov = newProv
        lease.Lessor = newLessor
        db.updateLease(lease)
        db.commit()

        # New look into the new database and make sure the changes are made
        newDb = DataBase(db.newWorksheetName)
        newLease = newDb.getLease(leaseId)
        self.assertEqual(newLease.Prov,newProv)
        self.assertEqual(newLease.Lessor,newLessor)

    def test_leaseGetter(self):
        ds = DataStructure()
        ds.LeaseType = 'OL'
        ds.LeaseID = 1
        self.assertEqual('OL-0001',ds.Lease)
        ds.LeaseID = 2
        self.assertEqual('OL-0002',ds.Lease)

    def getDataBase(self):
        """ for test purposes get a database instance """
        return DataBase(self.validExcelFile)


#print ('Looking for ID 3 - ', self.royaltyMaster[3])
#print ('Looking for ID 500 - ', self.royaltyMaster[500])


"""
The crux of each test is a call to assertEqual() to check for an expected
result; assertTrue() or assertFalse() to verify a condition; or assertRaises()
to verify that a specific exception gets raised. These methods are used instead
of the assert statement so the test runner can accumulate all test results and
produce a report.

"""

# if __name__ == '__main__':
#     unittest.main()


##d = {1:0, 2:0, 3:0}
##print(d.keys())
##print(list(d.keys()))
##print(list(d.values()))
