'''
Created on Jan 17, 2016

@author: lshumlich

*** Major Note: This is just to show an example of how to use SQLAlchemy...


Use as an example and then delete...


'''
from openpyxl import load_workbook
import datetime
from sqlalchemy import *
import sqlalchemy
from sqlalchemy.orm import sessionmaker

from sqlalchemy.ext.declarative.api import declarative_base
import sys

Base = declarative_base()

class RoyaltyMaster(Base):
    __tablename__ = 'royaltymaster'
    Id = Column(Integer, Sequence('royaltymaster_seq'), primary_key=True)
    LeaseType = Column(String)
    LeaseID = Column(Integer)
    RightsGranted = Column(String)
    RoyaltyScheme = Column(String)
    CrownMultiplier = Column(Float)
    MinRoyalty = Column(Float)
    ValuationMethod = Column(String)
    TruckingDeduction = Column(String)
    Processing = Column(String)
    Gorr = Column(String)
    
    @property
    def Lease(self):
        return '{}-{:04d}'.format(self.LeaseType,self.LeaseID)
    
    def __repr__(self):
        return "<RoyaltyMaster(id=%s,lease=%s)>" % (
                str(self.Id), self.LeaseType + str(self.LeaseID))



class SqlAchemyDataBase(object):
    
    def __init__(self,worksheetName):
        try:
            self.worksheetName = worksheetName
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
        except FileNotFoundError:
            raise Exception('The excel worksheet ' + worksheetName + ' is not found')
        self.loadRoyaltyMasterFromExcel()

    #
    # Royalty Master
    #
    def loadRoyaltyMasterFromExcel(self):
        stack = self.excelLoadWsTable(self.royaltyMasterTabName,RoyaltyMaster)
        self.royaltyMaster = dict()
        for ds in stack:
            self.royaltyMaster[ds.Lease] = ds

    #
    # Generic load a tab into a data structure
    #
    def excelLoadWsTable(self,tabName,c):
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
                    ds = c()
                    stack.append(ds)
                    i = 0
                    for cell in headerRow:
                        setattr(ds, cell.value, row[i].value)
                        i = i + 1
                    setattr(ds, 'RecordNumber', recordNo)
                    setattr(ds, 'ExcelRow', row)
                    setattr(ds, 'HeaderRow', headerRow)
                    print('In Load:', ds)
        except KeyError:
            raise Exception('The excel worksheet ' + self.worksheetName + ' does not have tab: ' + tabName)
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
        
    def getRM(self):
        return self.royaltyMaster

print(sys.argv[0], 'Started: ', datetime.datetime.now())
print('sqlalchemy' , sqlalchemy.__version__)

engine = create_engine('sqlite:///royalties.db', echo=True)
Session = sessionmaker(bind=engine)
Base.metadata.create_all(engine)

session = Session()


rm = RoyaltyMaster(LeaseType='OL',LeaseID=1)
print(rm)
rm.stuff = 'This is more stuff'
session.add(rm)

session.commit()



db = SqlAchemyDataBase('database.xlsx')
rmList = db.getRM()

for rm in rmList:
    print(rmList[rm])
    session.add(rmList[rm])
    session.commit()

print(sys.argv[0], 'Ended:   ', datetime.datetime.now())
