
import subprocess
from FetchData import *

class ProcessRoyalties(object):

    def __init__(self):
        None

    def process(self, wsName):

        self.fetch = FetchData(wsName)

        errorCount = 0
        log = open('log.txt','w')
        log.write ("Hello World.\n")

        firstTime = True

        for monthlyData in self.fetch.monthlyData():
            try:
                crownRoyaltyRate = 0
                well = self.fetch.getWell(monthlyData.WellId)
                royalty = self.fetch.getRoyaltyMaster(monthlyData.LeaseType, monthlyData.LeaseNumber)
                lease = self.fetch.getLease(monthlyData.LeaseType, monthlyData.LeaseNumber)
                pe =  self.fetch.getProducingEntity(monthlyData.LeaseType, monthlyData.LeaseNumber)

                log.write('Processing: ' + str(monthlyData.RecordNumber) + ' ' + str(monthlyData.ProdYear) +
                          ' ' + str(monthlyData.ProdMonth) + ' ' + monthlyData.LeaseNumber + ' ' +
                          monthlyData.Product + ' ' + well.TaxClassification + ' ' +
                          well.ProductClassification + ' ' + str(monthlyData.ProdVol) +
                          '\n')

                if(lease.Prov == 'SK' and monthlyData.Product == 'Oil'):
                    crownRoyaltyRate = self.saskOilRoyaltyRate(monthlyData, well, royalty, lease, pe)
                else:
                    raise AppError('Royalty Scheme not yet developed: ' + lease.Prov + ' ' + monthlyData.Product)
                
                crownRoyaltyRate = round(crownRoyaltyRate,6)
                log.write ("   Royalty Rate calculated as: " + str(crownRoyaltyRate) + ".\n")

            except AppError as e:
                errorCount +=1
                log.write ('Record #: ' + str(monthlyData.RecordNumber) + ' ' + str(e) + '\n')
                None

        log.write ("*** That's it folks " + str(errorCount) + ' errors \n')
        log.close()

    #
    # Sask Oil Royalty Calculation... Finally we are here...
    # 
    def saskOilRoyaltyRate(self, monthlyData, well, royalty, lease, pe):
        econOilData = self.fetch.getECONOilData(monthlyData.ProdYear, monthlyData.ProdMonth)
        #
        # Transform from internal datastructure names to ECON's variable names as defined in the "Crude Oil Royalty/Tax Formulas"
        #
        mop = monthlyData.ProdVol
        crownRoyaltyRate = 0
        freeholdProdTaxRate = 0
        if well.TaxClassification == 'Fourth Tier Oil':
            if mop < 25:
                crownRoyaltyRate = 0
            elif mop <= 136.2:
                c = 0
                d = 0
                if well.ProductClassification == 'Heavy':
                    c = econOilData.H4T_C
                    d = econOilData.H4T_D
                elif well.ProductClassification == 'Southwest':
                    c = econOilData.SW4T_C
                    d = econOilData.SW4T_D
                elif well.ProductClassification == 'Other':
                    c = econOilData.O4T_C
                    d = econOilData.O4T_D
                else:
                    raise AppError('Product Classification: ' + well.ProductClassification + ' not known. Royalty not calculated.')
                crownRoyaltyRate = (c * mop) - d
            else:
                if well.ProductClassification == 'Heavy':
                    k = econOilData.H4T_K
                    x = econOilData.H4T_X
                elif well.ProductClassification == 'Southwest':
                    k = econOilData.SW4T_K
                    x = econOilData.SW4T_X
                elif well.ProductClassification == 'Other':
                    k = econOilData.O4T_K
                    x = econOilData.O4T_X
                else:
                    raise AppError('Product Classification: ' + well.ProductClassification + ' not known. Royalty not calculated.')
                crownRoyaltyRate = k - (x / mop)
        else:
            raise AppError('Tax Classification: ' + well.TaxClassification + ' not known. Royalty not calculated.')

        return crownRoyaltyRate

pr = ProcessRoyalties()
pr.process('database.xlsx')
subprocess.call(['notepad.exe', 'log.txt'])
