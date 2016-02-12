from datetime import date
from datetime import datetime
from database.database import DataBase
import appinfo

class RoyaltyWorksheet(object):

    def __init__(self):
        self.ws = open('Royalty Worksheet.txt','w')
        self.ws.write ("Hello World - Royalty Worksheet.\n")
        self.count = 0
        
    def printWithWellProdDate(self,wellId,prodDate,product):
        db = DataBase(appinfo.getFileDir() + 'database.xlsx')
        md = db.getMonthlyDataByWellProdMonthProduct(wellId,prodDate,product)
        print(md)
        well = db.getWell(wellId)
        print(well)
        royalty = db.getRoyaltyMaster(well.Lease)
        print(royalty)
        lease = db.getLease(well.Lease)
        print(lease)
        calc = db.getCalcDataByWellProdMonthProduct(wellId,prodDate,product)
        print(calc)

        ws = RoyaltyWorksheet()
        ws.printSaskOilRoyaltyRate(md,well,royalty,lease,calc)
        
        
    def printSaskOilRoyaltyRate(self, monthlyData, well, royalty, lease, royaltyCalc):
#         print('Well:',well.WellId,lease.Lease,royaltyCalc)
        self.count += 1
        self.ws.write ('\n')
        self.ws.write ('Well: {:<33} Lease: {}\n'.format(well.WellId,lease.Lease))
        fs = '{:>45}: {}\n'
        self.ws.write (fs.format("Right", royalty.RightsGranted))
        self.ws.write (fs.format("Province", well.Prov))
        self.ws.write (fs.format("Royalty Base:", royalty.RoyaltyScheme))
        if royalty.Gorr != None:
            self.ws.write (fs.format("GORR", royalty.Gorr))
        self.ws.write (fs.format("Crown Multiplier", '{:.2f}'.format(royalty.CrownMultiplier/1)))
        self.ws.write (fs.format("Indian Interest", '{:.2f}'.format(well.IndianInterest/1)))
        if royalty.MinRoyalty != None:
            self.ws.write (fs.format("Minimum Royalty", royalty.MinRoyalty))
        if well.SRC != None:
            self.ws.write (fs.format("SRC", well.SRC))
        if well.Classification != None:
            self.ws.write (fs.format("Classification", well.Classification))
        if well.RoyaltyClassification != None:
            self.ws.write (fs.format("Royalty Classification", well.RoyaltyClassification))
        self.ws.write (fs.format("Valuation Method", royalty.ValuationMethod))
        if well.CommencementDate != None:
            self.ws.write (fs.format("Commencement Date", self.ensureDate(well.CommencementDate)))
        if royaltyCalc.CommencementPeriod != None:
            self.ws.write (fs.format("Commencement Period", royaltyCalc.CommencementPeriod))
        
        deductions = ""
        if royalty.TruckingDeducted == 'Y':
            deductions = 'Trucking'
        if royalty.ProcessingDeducted == 'Y':
            if deductions != "":
                deductions += ','
            deductions += 'Processing'
        if deductions != "":
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
        
        #if well.RoyaltyClassification == 'Fourth Tier Oil':
        if royaltyCalc.X > 0:
            self.ws.write('\n')
            self.ws.write('           x            |             {}\n'.format(royaltyCalc.X))
            self.ws.write('   (K - ------ ) - SRC  |  ({} - -------- )  - {} = {:>10,.6f}%\n'.format(royaltyCalc.K, well.SRC, royaltyCalc.ProvCrownRoyaltyRate))
            self.ws.write('          MOP           |             {}\n'.format(monthlyData.ProdVol))

        if royaltyCalc.C > 0: # Do not make this an else. Leave this as an if. If for some strange reason bot X and C > 0 this will show it.
            self.ws.write('\n')
            self.ws.write('   (C * MOP) - D   |  ({} * {}) - {} = {:>10,.6f}%\n'.format(royaltyCalc.C,monthlyData.ProdVol,royaltyCalc.D,royaltyCalc.ProvCrownRoyaltyRate))

        if royaltyCalc.Message != None:
            self.ws.write('\n')
            self.ws.write('   ' + royaltyCalc.Message + '\n')


            
        if royaltyCalc.CommencementPeriod != None:
            self.ws.write('\n')
            if royaltyCalc.CommencementPeriod < 5:
                self.ws.write('   IOGR1995 - Commencement Period < 5 Years: {}:\n'.format(royaltyCalc.CommencementPeriod))
            else:
                self.ws.write('   IOGR1995 - Commencement Period >= 5 Years: {}:\n'.format(royaltyCalc.CommencementPeriod))
                
            volDisplay = ' = {:,.2f}\n'.format(royaltyCalc.IOGR1995RoyaltyVolume)
            if monthlyData.ProdVol < 80:
                self.ws.write('      MOP < 80    ->  RVol = 10% * MOP' + volDisplay)
            elif monthlyData.ProdVol < 160:
                self.ws.write('      MOP 80 to 160 ->  RVol = 8 + 20% * (MOP - 80)' + volDisplay)
            elif royaltyCalc.CommencementPeriod < 5:
                self.ws.write('      MOP > 160   ->  RVol = 24 + 26% * (MOP - 160)' + volDisplay)
            elif monthlyData.ProdVol < 795:
                self.ws.write('      MOP 160 to 795 -> RVol = 24 + 26% * (mop - 160)' + volDisplay)
            else:
                self.ws.write('      MOP > 795   -> RVol = 189 + 40% * (mop - 795)' + volDisplay)
            self.ws.write ('\n')
            
        if monthlyData.Product == 'Oil' and 'SKProvCrownVar' in royalty.RoyaltyScheme:                            
            self.ws.write ('\n')
            self.ws.write ('      CR%    * CMult *   Prod    *   II  *      Val   =     R$     =     Rvol\n')
            self.ws.write ('  {:>10,.6f} * {:>5,.2f} * {:>9,.2f} * {:>5.2} * {:>10,.6f} = {:>10,.2f} = {:>10,.3f}\n'.format(royaltyCalc.ProvCrownUsedRoyaltyRate, royalty.CrownMultiplier,monthlyData.ProdVol,
                                                                              well.IndianInterest/1, royaltyCalc.RoyaltyPrice, royaltyCalc.ProvCrownRoyaltyValue, royaltyCalc.ProvCrownRoyaltyVolume))
            self.ws.write ('\n')

        if monthlyData.Product == 'Oil' and 'IOGR1995' in royalty.RoyaltyScheme:
            self.ws.write ('\n')
            self.ws.write ('       CMult *   RoyVol  *    II *      Val   =     R$     =     Rvol\n')
            self.ws.write ('      {:>5,.2f}  * {:>9,.2f} * {:>5.2} * {:>10,.6f} = {:>10,.2f} = {:>10,.3f}\n'.format(royalty.CrownMultiplier,royaltyCalc.IOGR1995RoyaltyVolume,
                                                                              well.IndianInterest/1, royaltyCalc.RoyaltyPrice, royaltyCalc.IOGR1995RoyaltyValue, royaltyCalc.IOGR1995RoyaltyVolume))
        
            
        if 'GORR' in royalty.RoyaltyScheme:
            self.ws.write('\n')
            self.ws.write('   GORR: ' + royaltyCalc.GorrMessage + '\n')
            self.ws.write ('         GORR%    *   Prod    *   II  *      Val   =     R$     =     Rvol\n')
            self.ws.write('      {:>10,.2f}  * {:>9,.2f} * {:>5.2f} * {:>10,.6f} = {:>10,.2f} = {:>10,.3f}\n'.format(
                          royaltyCalc.GorrRoyaltyRate,
                          monthlyData.ProdVol,
                          well.IndianInterest,
                          royaltyCalc.RoyaltyPrice,
                          royaltyCalc.GorrRoyaltyValue,
                          royaltyCalc.GorrRoyaltyVolume))

        self.ws.write ('\n')
        self.ws.write ('   {***Note: Handle Incentives}\n')
            
        self.ws.write ('\n')
        if royaltyCalc.RoyaltyValuePreDeductions != royaltyCalc.RoyaltyValue:
            self.ws.write ('   Royalty Pre Deductions:                                      {:>10,.2f}\n'.format(royaltyCalc.RoyaltyValuePreDeductions))
        if royaltyCalc.RoyaltyTransportation > 0:
            self.ws.write ('      Less Transportation {:>9,.3f} * {:>10,.6f} = {:>10,.2f}\n'.format(royaltyCalc.RoyaltyVolume,monthlyData.TransRate,royaltyCalc.RoyaltyTransportation))
        if royaltyCalc.RoyaltyProcessing > 0:
            self.ws.write ('      Less Processing     {:>9,.3f} * {:>10,.6f} = {:>10,.2f}\n'.format(royaltyCalc.RoyaltyVolume,monthlyData.ProcessingRate,royaltyCalc.RoyaltyProcessing))
        if royaltyCalc.RoyaltyDeductions > 0:
            self.ws.write ('      Total Deductions:                            {:>10,.2f}\n'.format(royaltyCalc.RoyaltyDeductions))
        self.ws.write ('   Royalty Amount:                                              {:>10,.2f}\n'.format(royaltyCalc.RoyaltyValue))
        self.ws.write ('\n')
        self.ws.write ('   {***Note: Handle Previous Paid Amount?}\n')
        self.ws.write ('\n')
        self.ws.write ('\n')
        self.ws.write ('\n')
        
    def yyyy_mm(self,i):
        return str(i)[0:4]+'-'+str(i)[4:6]

    def ensureDate(self,d):
        if isinstance(d,datetime):
            return date(d.year, d.month, d.day)
        return d

    def __del__(self):
        self.ws.write ("*** That's it folks *** Royalties Shown: " + str(self.count) + "\n")
        self.ws.close()

    
