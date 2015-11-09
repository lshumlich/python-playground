
import subprocess
from datetime import date
from DataBase import *

"""

Big Note: *************
          Putting all this code in one module is very bad programming technique.
          Let me repeat VERY BAD programming technique...

BUT..... Now the justification.....
         Because we are using this code to further our analysis and design, we are
         moving and changing our variable names. It is way easier to work in one file
         for now. Please keep the classes the right size...


This is the royalty calculation class that actually calculates the royalties.
It is a work in progress. Today it uses an Excel Worksheet that must
be formated just so... to simulate a database. This is being done simply 
for agility purposes.

Now all you real good programmers out there...This is written so we can
show real smart people who are not programmers and have them verify our
process. Please do not be too harsh when I have used some real procedural
code rather than good OO code.

The intent is to have test data that tests 100% of the code as tested
by code coverage.
    
"""
class ProcessRoyalties(object):

    def __init__(self):
        None

    """
    The place where the calculations begin.
    """
    def process(self, wsName):

        self.db = DataBase(wsName)
        self.ws = RoyaltyWorksheet()

        errorCount = 0
        log = open('log.txt','w')
        log.write ("Hello World.\n")

        firstTime = True

        for monthlyData in self.db.monthlyData():
            try:
                well = self.db.getWell(monthlyData.WellId)
                royalty = self.db.getRoyaltyMaster(monthlyData.LeaseType, monthlyData.LeaseNumber)
                lease = self.db.getLease(monthlyData.LeaseType, monthlyData.LeaseNumber)
                pe =  self.db.getProducingEntity(monthlyData.LeaseType, monthlyData.LeaseNumber)
                royaltyCalc = self.db.getRoyaltyCalc(monthlyData.ProdYear,monthlyData.ProdMonth,monthlyData.WellId)

                log.write('Processing: ' + str(monthlyData.RecordNumber) + ' ' + str(monthlyData.ProdYear) +
                          ' ' + str(monthlyData.ProdMonth) + ' ' + monthlyData.LeaseNumber + ' ' +
                          monthlyData.Product + ' ' + well.TaxClassification + ' ' +
                          well.ProductClassification + ' ' + str(monthlyData.ProdVol) +
                          '\n')

                if(lease.Prov == 'SK' and monthlyData.Product == 'Oil') and royalty.RoyaltyScheme == 'ProvCrownVar' :
                    self.saskOilRoyaltyRate(monthlyData, well, royalty, lease, pe, royaltyCalc)
                else:
                    raise AppError('Royalty Scheme not yet developed: ' + lease.Prov + ' ' + monthlyData.Product)


                # Note: If there is no sales. Use last months sales value... Not included in this code

                royaltyCalc.RoyaltyVolume = round((royaltyCalc.RoyaltyRate / 100) * monthlyData.ProdVol,1)

                royaltyCalc.GrossRoyaltyValue = royaltyCalc.RoyaltyVolume * monthlyData.SalesPrice
                royaltyCalc.NetRoyaltyValue = royaltyCalc.GrossRoyaltyValue

                if (royalty.TransportationDeducted == 'Y'):
                    royaltyCalc.RoyaltyTransportation = royaltyCalc.RoyaltyVolume * monthlyData.TransPrice
                    royaltyCalc.RoyaltyDeductions += royaltyCalc.RoyaltyTransportation
                    royaltyCalc.NetRoyaltyValue -= royaltyCalc.RoyaltyTransportation
                
                self.ws.saskOilRoyaltyRate(monthlyData, well, royalty, lease, pe, royaltyCalc)
                log.write('--- Royalty Calculated: {} {}/{:0>2} {} prod: {} Crown Rate: {} FH Tax Rate: {}\n'.format(monthlyData.Row, royaltyCalc.ProdYear, royaltyCalc.ProdMonth,
                                                                                             royaltyCalc.WellId, monthlyData.ProdVol, royaltyCalc.RoyaltyRate, royaltyCalc.FreeholdTaxRate))
                self.db.updateRoyaltyCalc(royaltyCalc)

            except AppError as e:
                errorCount +=1
                log.write ('Record #: ' + str(monthlyData.RecordNumber) + ' ' + str(e) + '\n')

        log.write ("*** That's it folks " + str(errorCount) + ' errors \n')
        log.close()

        del self.ws

    #
    # Sask Oil Royalty Calculation... Finally we are here...
    #
    # These calculations are fully document in two documents included in this project
    # under the Sask Folder:
    #   Factor Circulars.pdf
    #   OilFactors.pdf
    #
    def saskOilRoyaltyRate(self, monthlyData, well, royalty, lease, pe, royaltyCalc):
        econOilData = self.db.getECONOilData(monthlyData.ProdYear, monthlyData.ProdMonth)
        mop = monthlyData.ProdVol
        crownRoyaltyRate = 0
        freeholdProdTaxRate = 0

        if well.TaxClassification == 'Fourth Tier Oil':

            if mop < 25:
                crownRoyaltyRate = 0

            elif mop <= 136.2:
                if well.ProductClassification == 'Heavy':
                    royaltyCalc.C = econOilData.H4T_C
                    royaltyCalc.D = econOilData.H4T_D
                elif well.ProductClassification == 'Southwest':
                    royaltyCalc.C = econOilData.SW4T_C
                    royaltyCalc.D = econOilData.SW4T_D
                elif well.ProductClassification == 'Other':
                    royaltyCalc.C = econOilData.O4T_C
                    royaltyCalc.D = econOilData.O4T_D
                else:
                    raise AppError('Product Classification: ' + well.ProductClassification + ' not known. Royalty not calculated.')
                royaltyCalc.RoyaltyRate = (royaltyCalc.C * mop) - royaltyCalc.D

            else:
                if well.ProductClassification == 'Heavy':
                    royaltyCalc.K = econOilData.H4T_K
                    royaltyCalc.X = econOilData.H4T_X
                elif well.ProductClassification == 'Southwest':
                    royaltyCalc.K = econOilData.SW4T_K
                    royaltyCalc.X = econOilData.SW4T_X
                elif well.ProductClassification == 'Other':
                    royaltyCalc.K = econOilData.O4T_K
                    royaltyCalc.X = econOilData.O4T_X
                else:
                    raise AppError('Product Classification: ' + well.ProductClassification + ' not known. Royalty not calculated.')
                royaltyCalc.RoyaltyRate = royaltyCalc.K - (royaltyCalc.X / mop)
        else:
            if well.ProductClassification == 'Heavy':
                if well.TaxClassification == 'Third Tier Oil':
                    royaltyCalc.K = econOilData.H3T_K
                    royaltyCalc.X = econOilData.H3T_X
                elif well.TaxClassification == 'New Oil':
                    royaltyCalc.K = econOilData.HNEW_K
                    royaltyCalc.X = econOilData.HNEW_X
                else:
                    raise AppError('Tax Classification: ' + well.TaxClassification + ' not known. Royalty not calculated.')
            elif well.ProductClassification == 'Southwest':
                if well.TaxClassification == 'Third Tier Oil':
                    royaltyCalc.K = econOilData.SW3T_K
                    royaltyCalc.X = econOilData.SW3T_X
                elif well.TaxClassification == 'New Oil':
                    royaltyCalc.K = econOilData.SWNEW_K
                    royaltyCalc.X = econOilData.SWNEW_X
                else:
                    raise AppError('Tax Classification: ' + well.TaxClassification + ' not known. Royalty not calculated.')
            elif well.ProductClassification == 'Other':
                if well.TaxClassification == 'Third Tier Oil':
                    royaltyCalc.K = econOilData.O3T_K
                    royaltyCalc.X = econOilData.O3T_X
                elif well.TaxClassification == 'New Oil':
                    royaltyCalc.K = econOilData.ONEW_K
                    royaltyCalc.X = econOilData.ONEW_X
                elif well.TaxClassification == 'Old Oil':
                    royaltyCalc.K = econOilData.OOLD_K
                    royaltyCalc.X = econOilData.OOLD_X
                else:
                    raise AppError('Tax Classification: ' + well.TaxClassification + ' not known. Royalty not calculated.')
            else:
                raise AppError('Product Classification: ' + well.ProductClassification + ' not known. Royalty not calculated.')

            royaltyCalc.RoyaltyRate = royaltyCalc.K - (royaltyCalc.X / mop) - well.SRC
            
        royaltyCalc.RoyaltyRate = round(royaltyCalc.RoyaltyRate,6)
        royaltyCalc.FreeholdTaxRate = royaltyCalc.RoyaltyRate - well.PTF
        return

class RoyaltyWorksheet(object):

    def __init__(self):
        self.ws = open('Royalty Worksheet.txt','w')
        self.ws.write ("Hello World - Royalty Worksheet.\n")

    def saskOilRoyaltyRate(self, monthlyData, well, royalty, lease, pe, royaltyCalc):
        self.ws.write ('\n')
        self.ws.write ('Well: {:<3} {:<29} Lease : {}-{}\n'.format(well.WellId,well.UWI,lease.LeaseType,lease.LeaseNumber ))
        fs = '{:>45} : {}\n'
        self.ws.write (fs.format("Right", royalty.RightsGranted))
        self.ws.write (fs.format("Royalty Base:", royalty.RoyaltyScheme))
        self.ws.write (fs.format("Crown Multiplier:", royalty.CrownMultiplier))
        self.ws.write (fs.format("Well Interest:", well.WellInterest))
        self.ws.write (fs.format("SRC", well.SRC))
        self.ws.write (fs.format("PTF", well.PTF))
        self.ws.write (fs.format("Product Classification", well.ProductClassification))
        self.ws.write (fs.format("Tax Classification", well.TaxClassification))
        self.ws.write ('\n')

        fsh = '   {:^7} {:^7} {:>8}  {:>8}  {:>6}  {:>6}\n'
        fsd = '   {}-{:0>2}   {:3}  {:>9,.1f} {:>9,.1f} {:>7,.2f} {:>7,.2f}\n'
        self.ws.write (fsh.format('Prod','Product','Prod','Sales','Sales','Trans'))
        self.ws.write (fsh.format('Month','','Vol','Vol','Price','Price'))
        self.ws.write (fsd.format(monthlyData.ProdYear,monthlyData.ProdMonth,
                                  monthlyData.Product,monthlyData.ProdVol,
                                  monthlyData.SalesVol,monthlyData.SalesPrice,
                                  monthlyData.TransPrice))
        
        #if well.TaxClassification == 'Fourth Tier Oil':
        if royaltyCalc.X > 0:
            self.ws.write('\n')
            self.ws.write('\n')
            self.ws.write('           x            |             {}                \n'.format(royaltyCalc.X))
            self.ws.write('   (K - ------ ) - SRC  |  ({} - -------- )  - {} = {}  \n'.format(royaltyCalc.K, well.SRC, royaltyCalc.RoyaltyRate))
            self.ws.write('          MOP           |             {}                \n'.format(monthlyData.ProdVol))
            self.ws.write('\n')

        if royaltyCalc.C > 0: # Do not make this an else. Leave this as an if. If for some strange reason bot X and C > 0 this will show it.
            self.ws.write('\n')
            self.ws.write('   (C * MOP) - D   |  ({} * {}) - {} = {}\n'.format(royaltyCalc.C,monthlyData.ProdVol,royaltyCalc.D,royaltyCalc.RoyaltyRate))
            self.ws.write('\n')

        self.ws.write ('\n')
        fsh = '   {:>9}  {:>9}  {:>9}\n'
        fsd = '   {:>9,.6f} {:>10,.1f} {:>10,.2f}\n'
        self.ws.write (fsh.format('','','Gross'))
        self.ws.write (fsh.format('Royalty','Royalty','Royalty'))
        self.ws.write (fsh.format('Rate','Volume','Value'))
        self.ws.write (fsd.format(royaltyCalc.RoyaltyRate, royaltyCalc.RoyaltyVolume,royaltyCalc.GrossRoyaltyValue))

        self.ws.write ('\n')
        if (royaltyCalc.GrossRoyaltyValue > 0 and
            royaltyCalc.GrossRoyaltyValue != royaltyCalc.NetRoyaltyValue):
            self.ws.write ('   Gross Royalty:                  {:>10,.2f}\n'.format(royaltyCalc.GrossRoyaltyValue))
        if royaltyCalc.RoyaltyTransportation > 0:
            self.ws.write ('      Less Transportation{:>10,.2f}\n'.format(royaltyCalc.RoyaltyTransportation))
        if royaltyCalc.RoyaltyProcessing > 0:
            self.ws.write ('      Less Processing    {:>10,.2f}\n'.format(royaltyCalc.RoyaltyProcessing))
        if royaltyCalc.RoyaltyDeductions > 0:
            self.ws.write ('      Total Deductions:  {:>10,.2f}\n'.format(royaltyCalc.RoyaltyDeductions))
        self.ws.write ('   Royalty Payable:                {:>10,.2f}\n'.format(royaltyCalc.NetRoyaltyValue))
        self.ws.write ('\n')

    def __del__(self):
        self.ws.write ("*** That's it folks ***\n")
        self.ws.close()

    
"""
*******************************************************************
    Test Code....

"""
from datetime import date

class TestSaskRoyaltyCalc(unittest.TestCase):

#        
    def test_SaskSrc(self):
        pr = ProcessRoyalties()
        self.assertEqual(pr.saskOilSrcCalc(2013,4,'V',date(2001,1,1),'Oil','Forth Tier'),2.5)
        self.assertEqual(pr.saskOilSrcCalc(2013,4,'H',date(2001,1,1),'Oil','Forth Tier'),0)
        self.assertEqual(pr.saskOilSrcCalc(2013,5,'V',date(2001,1,1),'Oil','Forth Tier'),0)

          

pr = ProcessRoyalties()
pr.process('database.xlsx')
subprocess.call(['notepad.exe', 'Royalty Worksheet.txt'])
subprocess.call(['notepad.exe', 'log.txt'])

"""
if __name__ == '__main__':
    unittest.main()

"""
