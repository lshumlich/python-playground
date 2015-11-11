
import subprocess
from DataBase import DataBase,AppError
import unittest

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

        for monthlyData in self.db.monthlyData():
            try:
                well = self.db.getWell(monthlyData.WellId)
                royalty = self.db.getRoyaltyMaster(well.Lease)
                lease = self.db.getLease(well.Lease)
                #pe =  self.db.getProducingEntity(well.Lease)
                royaltyCalc = self.db.getRoyaltyCalc(monthlyData.ProdMonth,monthlyData.WellId)

#                 log.write('Processing: ' + str(monthlyData.RecordNumber) + 
#                           ' ' + str(monthlyData.ProdMonth) + ' ' +
#                           monthlyData.Product + ' ' + well.RoyaltyClassification + ' ' +
#                           well.Classification + ' ' + str(monthlyData.ProdVol) +
#                           '\n')

                if(lease.Prov == 'SK' and monthlyData.Product == 'Oil') and royalty.RoyaltyScheme == 'ProvCrownVar' :
                    self.calcSaskOilRoyaltyRate(monthlyData, well, royalty, lease, royaltyCalc)
                else:
                    raise AppError('Royalty Scheme not yet developed: ' + lease.Prov + ' ' + monthlyData.Product)


                # Note: If there is no sales. Use last months sales value... Not included in this code

                if royalty.ValuationMethod == None or royalty.ValuationMethod == 'SaskWellHead':
                    royaltyCalc.Price = monthlyData.WellHeadPrice
                else:
                    royaltyCalc.Price = monthlyData.WellHeadPrice + monthlyData.TransRate + monthlyData.ProcessingRate

                royaltyCalc.RoyaltyRate = royaltyCalc.CalcRoyaltyRate
                if royalty.MinRoyalty != None:
                    if royalty.MinRoyalty > royaltyCalc.CalcRoyaltyRate:
                        royaltyCalc.RoyaltyRate = royalty.MinRoyalty
                    
                royaltyCalc.RoyaltyVolume = ((royaltyCalc.RoyaltyRate / 100) * 
                                                              royalty.CrownMultiplier * 
                                                              monthlyData.ProdVol *
                                                              well.IndianInterest)

                royaltyCalc.RoyaltyValuePreDeductions = round((royaltyCalc.RoyaltyRate / 100) * 
                                                              royalty.CrownMultiplier * 
                                                              monthlyData.ProdVol *
                                                              well.IndianInterest *
                                                              royaltyCalc.Price ,2)

                royaltyCalc.RoyaltyValue = royaltyCalc.RoyaltyValuePreDeductions

                if (royalty.TruckingDeducted == 'Y'):
                    royaltyCalc.RoyaltyTransportation = royaltyCalc.RoyaltyVolume * monthlyData.TransRate
                    royaltyCalc.RoyaltyDeductions += royaltyCalc.RoyaltyTransportation
                    royaltyCalc.RoyaltyValue -= royaltyCalc.RoyaltyTransportation

                if (royalty.ProcessingDeducted == 'Y'):
                    royaltyCalc.RoyaltyProcessing = royaltyCalc.RoyaltyVolume * monthlyData.ProcessingRate
                    royaltyCalc.RoyaltyDeductions += royaltyCalc.RoyaltyProcessing
                    royaltyCalc.RoyaltyValue -= royaltyCalc.RoyaltyProcessing
                
                self.ws.printSaskOilRoyaltyRate(monthlyData, well, royalty, lease, royaltyCalc)
#                 log.write('--- Royalty Calculated: {} {} {} prod: {} Crown Rate: {}\n'.format(monthlyData.Row, royaltyCalc.ProdMonth,
#                                                                                              royaltyCalc.WellId, monthlyData.ProdVol, royaltyCalc.RoyaltyRate))
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
    def calcSaskOilRoyaltyRate(self, monthlyData, well, royalty, lease, royaltyCalc):
        econOilData = self.db.getECONOilData(monthlyData.ProdMonth)
        mop = monthlyData.ProdVol

        if well.RoyaltyClassification == 'Fourth Tier Oil':

            if mop < 25:
                royaltyCalc.CalcRoyaltyRate = 0

            elif mop <= 136.2:
                if well.Classification == 'Heavy':
                    royaltyCalc.C = econOilData.H4T_C
                    royaltyCalc.D = econOilData.H4T_D
                elif well.Classification == 'Southwest':
                    royaltyCalc.C = econOilData.SW4T_C
                    royaltyCalc.D = econOilData.SW4T_D
                elif well.Classification == 'Other':
                    royaltyCalc.C = econOilData.O4T_C
                    royaltyCalc.D = econOilData.O4T_D
                else:
                    raise AppError('Classification: ' + well.Classification + ' not known. Royalty not calculated.')
                royaltyCalc.CalcRoyaltyRate = (royaltyCalc.C * mop) - royaltyCalc.D

            else:
                if well.Classification == 'Heavy':
                    royaltyCalc.K = econOilData.H4T_K
                    royaltyCalc.X = econOilData.H4T_X
                elif well.Classification == 'Southwest':
                    royaltyCalc.K = econOilData.SW4T_K
                    royaltyCalc.X = econOilData.SW4T_X
                elif well.Classification == 'Other':
                    royaltyCalc.K = econOilData.O4T_K
                    royaltyCalc.X = econOilData.O4T_X
                else:
                    raise AppError('Classification: ' + well.Classification + 'Not known. Royalty not calculated.')
                royaltyCalc.CalcRoyaltyRate = royaltyCalc.K - (royaltyCalc.X / mop)
        else:
            if well.Classification == 'Heavy':
                if well.RoyaltyClassification == 'Third Tier Oil':
                    royaltyCalc.K = econOilData.H3T_K
                    royaltyCalc.X = econOilData.H3T_X
                elif well.RoyaltyClassification == 'New Oil':
                    royaltyCalc.K = econOilData.HNEW_K
                    royaltyCalc.X = econOilData.HNEW_X
                else:
                    raise AppError('Royalty Classification: ' + well.RoyaltyClassification + ' not known. Royalty not calculated.')
            elif well.Classification == 'Southwest':
                if well.RoyaltyClassification == 'Third Tier Oil':
                    royaltyCalc.K = econOilData.SW3T_K
                    royaltyCalc.X = econOilData.SW3T_X
                elif well.RoyaltyClassification == 'New Oil':
                    royaltyCalc.K = econOilData.SWNEW_K
                    royaltyCalc.X = econOilData.SWNEW_X
                else:
                    raise AppError('Royalty Classification: ' + well.RoyaltyClassification + ' not known. Royalty not calculated.')
            elif well.Classification == 'Other':
                if well.RoyaltyClassification == 'Third Tier Oil':
                    royaltyCalc.K = econOilData.O3T_K
                    royaltyCalc.X = econOilData.O3T_X
                elif well.RoyaltyClassification == 'New Oil':
                    royaltyCalc.K = econOilData.ONEW_K
                    royaltyCalc.X = econOilData.ONEW_X
                elif well.RoyaltyClassification == 'Old Oil':
                    royaltyCalc.K = econOilData.OOLD_K
                    royaltyCalc.X = econOilData.OOLD_X
                else:
                    raise AppError('Royalty Classification: ' + well.RoyaltyClassification + ' not known. Royalty not calculated.')
            else:
                raise AppError('Product Classification: ' + well.Classification + ' not known. Royalty not calculated.')

            royaltyCalc.CalcRoyaltyRate = royaltyCalc.K - (royaltyCalc.X / mop) - well.SRC
            
        royaltyCalc.CalcRoyaltyRate = round(royaltyCalc.CalcRoyaltyRate,6)
        return

class RoyaltyWorksheet(object):

    def __init__(self):
        self.ws = open('Royalty Worksheet.txt','w')
        self.ws.write ("Hello World - Royalty Worksheet.\n")
        self.count = 0

    def printSaskOilRoyaltyRate(self, monthlyData, well, royalty, lease, royaltyCalc):
        self.count += 1
        self.ws.write ('\n')
        self.ws.write ('Well: {:<3} {:<29} Lease : {}\n'.format(well.WellId,well.UWI,lease.Lease))
        fs = '{:>45} : {}\n'
        self.ws.write (fs.format("Right", royalty.RightsGranted))
        self.ws.write (fs.format("Province", lease.Prov))
        self.ws.write (fs.format("Royalty Base:", royalty.RoyaltyScheme))
        self.ws.write (fs.format("Crown Multiplier:", '{:.2f}'.format(royalty.CrownMultiplier/1)))
        self.ws.write (fs.format("Indian Interest:", well.IndianInterest))
        if royalty.MinRoyalty != None:
            self.ws.write (fs.format("Minimum Royalty:", royalty.MinRoyalty))
        self.ws.write (fs.format("SRC", well.SRC))
        self.ws.write (fs.format("Classification", well.Classification))
        self.ws.write (fs.format("Royalty Classification", well.RoyaltyClassification))
        self.ws.write (fs.format("Valuation Method", royalty.ValuationMethod))
        deductions = ''
        if royalty.TruckingDeducted == 'Y':
            deductions = 'Trucking'
        if royalty.ProcessingDeducted == 'Y':
            if deductions != '':
                deductions += ','
            deductions += 'Processing'
        if deductions != '':
            self.ws.write (fs.format("Deduction", deductions))
        self.ws.write ('\n')

        fsh = '   {:^10} {:^7} {:>5} {:>6} {:>9} {:>11} {:>11} {:>11}\n'
        fsd = '   {:%Y-%m-%d} {}   {:3}    {:3} {:>9,.2f} {:>11,.6f} {:>11,.6f} {:>11,.6f}\n'
        self.ws.write (fsh.format('','','','','Monthly','Sask Def Of','',''))
        self.ws.write (fsh.format('Extract','Prod','Amend','Prod','Prod','Well Head','Trucking','Processing'))
        self.ws.write (fsh.format('Date','Month','No','','Vol','Price','Price','Price'))
        self.ws.write (fsd.format(monthlyData.ExtractMonth,self.yyyy_mm(monthlyData.ProdMonth),monthlyData.AmendNo,
                                  monthlyData.Product,monthlyData.ProdVol,
                                  monthlyData.WellHeadPrice,
                                  monthlyData.TransRate, monthlyData.ProcessingRate))
        self.ws.write ('\n')
        self.ws.write ('   {*** Note: Replace Well Head Price with Petrinex detail when available***}\n')
        self.ws.write ('   {*** Note: Replace Trucking Price with Petrinex detail when available***}\n')
        self.ws.write ('   {*** Note: Replace Processing Price with Petrinex detail when available***}\n')
        self.ws.write ('\n')
        
        #if well.RoyaltyClassification == 'Fourth Tier Oil':
        if royaltyCalc.X > 0:
            self.ws.write('\n')
            self.ws.write('           x            |             {}\n'.format(royaltyCalc.X))
            self.ws.write('   (K - ------ ) - SRC  |  ({} - -------- )  - {} = {:>10,.6f}\n'.format(royaltyCalc.K, well.SRC, royaltyCalc.CalcRoyaltyRate))
            self.ws.write('          MOP           |             {}\n'.format(monthlyData.ProdVol))
            self.ws.write('\n')

        if royaltyCalc.C > 0: # Do not make this an else. Leave this as an if. If for some strange reason bot X and C > 0 this will show it.
            self.ws.write('\n')
            self.ws.write('   (C * MOP) - D   |  ({} * {}) - {} = {}\n'.format(royaltyCalc.C,monthlyData.ProdVol,royaltyCalc.D,royaltyCalc.CalcRoyaltyRate))
            self.ws.write('\n')
        
        # Newer Suff
        
        self.ws.write ('\n')
        self.ws.write ('      CR%    * CMult *   Prod    *   II  *      Val   =     R$\n')
        self.ws.write ('  {:>10,.6f} * {:>5,.2f} * {:>9,.2f} * {:>5.2} * {:>10,.6f} = {:>10,.2f} \n'.format(royaltyCalc.RoyaltyRate, royalty.CrownMultiplier,monthlyData.ProdVol,
                                                                          well.IndianInterest/1, royaltyCalc.Price, royaltyCalc.RoyaltyValuePreDeductions))
        self.ws.write ('\n')
        self.ws.write ('   {***Note: Handle Incentives}\n')
            
        self.ws.write ('\n')
        if royaltyCalc.RoyaltyValuePreDeductions != royaltyCalc.RoyaltyValue:
            self.ws.write ('   Royalty Pre Deductions:             {:>10,.2f}\n'.format(royaltyCalc.RoyaltyValuePreDeductions))
        if royaltyCalc.RoyaltyTransportation > 0:
            self.ws.write ('      Less Transportation{:>10,.2f}\n'.format(royaltyCalc.RoyaltyTransportation))
        if royaltyCalc.RoyaltyProcessing > 0:
            self.ws.write ('      Less Processing    {:>10,.2f}\n'.format(royaltyCalc.RoyaltyProcessing))
        if royaltyCalc.RoyaltyDeductions > 0:
            self.ws.write ('      Total Deductions:  {:>10,.2f}\n'.format(royaltyCalc.RoyaltyDeductions))
        self.ws.write ('   Royalty Amount:                     {:>10,.2f}\n'.format(royaltyCalc.RoyaltyValue))
        self.ws.write ('   {***Note: Handle Previous Paid Amount?}\n')
        self.ws.write ('\n')
        self.ws.write ('\n')
        self.ws.write ('\n')
        
    def yyyy_mm(self,i):
        return str(i)[0:4]+'-'+str(i)[4:6]


    def __del__(self):
        self.ws.write ("*** That's it folks *** Royalties Shown: " + str(self.count) + "\n")
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
