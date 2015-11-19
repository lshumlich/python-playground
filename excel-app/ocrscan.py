from openpyxl import load_workbook
from openpyxl import Workbook
from openpyxl import utils
import re

"""
LeaseType    LeaseID    RightsGranted    RoyaltyScheme    CrownMultiplier    MinRoyalty    ValuationMethod    TruckingDeducted    ProcessingDeducted    Notes
OL    1    All    SKProvCrownVar    1.2    50    SaskWellHead    Y    Y    
"""
def lookForString (sToLookIn,pattern,result,sToAppend):
        m = pattern.search(sToLookIn)
        if m != None:
            if result != '':
                result +=','
            result += sToAppend
        return result


leasenoCol=0 # A
royschemCol=13 # N
gorrCol=46 # N

regulationP = re.compile('regulation royalty rate',re.I)
crownVar1P = re.compile('multiples of provincial',re.I)
crownVar2P = re.compile('modified provincial crown',re.I)
gorrP = re.compile('gorr',re.I)
percentP = re.compile('[0-9.]+%')


leaseWorksheetName = "Lease Analysis.xlsx"

leasewb = load_workbook(leaseWorksheetName)
ws = leasewb.active

headerRow = None
i = 0
 
for row in ws.rows:
    i += 1
    if headerRow == None:
        headerRow = row
#         print('---Col:', row[gorrCol].value)
    else:
        leaseId = row[leasenoCol].value
        
        s = row[royschemCol].value
        royaltyScheme = lookForString(s,regulationP,'','Regulation1995')
        royaltyScheme = lookForString(s,crownVar1P,royaltyScheme,'SKProvCrownVar')
        royaltyScheme = lookForString(s,crownVar2P,royaltyScheme,'SKProvCrownVar')
        royaltyScheme = lookForString(s,gorrP,royaltyScheme,'GORR')
        if royaltyScheme == '':
            royaltyScheme += '???Unknown???'

        gorrStuff = ''
        if 'GORR' in royaltyScheme:
            s = row[gorrCol].value
            gorrStuff = percentP.findall(s)
        
        print(i,leaseId,royaltyScheme,gorrStuff)
        
