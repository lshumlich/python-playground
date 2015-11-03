
import subprocess
from datetime import date
from FetchData import *

"""

The royalty calculation class that actually calculates the royalties.
This is a work in progress. Today it uses an Excel Worksheet that must
be formated just so... to simulate a database. This is being done simpley 
for agility purposes.

Now all you real good programmers out there. This is written so we can
show real smart people that are not programmers and have them verify our
process. Please do not be to harsh when I have used some real procedural
code rather than good OO code.

The intent to to have test data that test 100% of the code as tested
by code coverage.
    
"""
class ProcessRoyalties(object):

    def __init__(self):
        None

    """
    The place where the calculations begin.
    """
    def process(self, wsName):

        self.fetch = FetchData(wsName)

        errorCount = 0
        log = open('log.txt','w')
        log.write ("Hello World.\n")

        firstTime = True

        for monthlyData in self.fetch.monthlyData():
            try:
                crownRoyaltyRate = 0 # The goal of this is to calculate this number.
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
    # These calculations are fully document in two documents included in this project
    # under the Sask Folder:
    #   Factor Circulars.pdf
    #   OilFactors.pdf
    #
    def saskOilRoyaltyRate(self, monthlyData, well, royalty, lease, pe):
        econOilData = self.fetch.getECONOilData(monthlyData.ProdYear, monthlyData.ProdMonth)
        mop = monthlyData.ProdVol
        crownRoyaltyRate = 0
        freeholdProdTaxRate = 0

        if well.TaxClassification == 'Fourth Tier Oil':

            if mop < 25:
                crownRoyaltyRate = 0

            elif mop <= 136.2:
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
            if well.ProductClassification == 'Heavy':
                if well.TaxClassification == 'Third Tier Oil':
                    k = econOilData.H3T_K
                    x = econOilData.H3T_X
                elif well.TaxClassification == 'New Oil':
                    k = econOilData.HNEW_K
                    x = econOilData.HNEW_X
                else:
                    raise AppError('Tax Classification: ' + well.TaxClassification + ' not known. Royalty not calculated.')
            elif well.ProductClassification == 'Southwest':
                if well.TaxClassification == 'Third Tier Oil':
                    k = econOilData.SW3T_K
                    x = econOilData.SW3T_X
                elif well.TaxClassification == 'New Oil':
                    k = econOilData.SWNEW_K
                    x = econOilData.SWNEW_X
                else:
                    raise AppError('Tax Classification: ' + well.TaxClassification + ' not known. Royalty not calculated.')
            elif well.ProductClassification == 'Other':
                if well.TaxClassification == 'Third Tier Oil':
                    k = econOilData.O3T_K
                    x = econOilData.O3T_X
                elif well.TaxClassification == 'New Oil':
                    k = econOilData.ONEW_K
                    x = econOilData.ONEW_X
                elif well.TaxClassification == 'Old Oil':
                    k = econOilData.OOLD_K
                    x = econOilData.OOLD_X
                else:
                    raise AppError('Tax Classification: ' + well.TaxClassification + ' not known. Royalty not calculated.')
            else:
                raise AppError('Product Classification: ' + well.ProductClassification + ' not known. Royalty not calculated.')

            #TODO Calculate src correctly
            
            src = 1
            crownRoyaltyRate = k - (x / mop) - src

        return crownRoyaltyRate

    def newProcess(self):
        print('whatever')


    """
    Accourding to the Sask Factor Circulars:
    2) SRC = Saskatchewan Resource Credit of:
    (a) 2.5 percentage points for all oil produced prior to April 2013 from vertical oil
        wells or gas wells drilled on or after February 9, 1998 and before October 1, 2002.
        Also for all incremental oil produced prior to April 2013 from new or expanded
        waterfloods implemented on or after February 9, 1998 and before October 1, 2002;
    (b) 2.25 percentage points for all oil produced on or after April 1, 2013 from
        vertical oil wells or gas wells drilled on or after February 9, 1998 and before
        October 1, 2002. Also for all incremental oil produced on or after April 1, 2013
        from new or expanded waterfloods implemented on or after February 9, 1998 and
        before October 1, 2002;
    (c) 1.0 percentage point for all other “old oil”, “new oil” and “third tier oil”
        produced prior to April 2013; and
    (d) 0.75 percentage points for all other “old oil”, “new oil” and “third tier oil”
        produced after April 1, 2013.
    """


    def newProcess2(self):
        print('whatever')

    def saskOilSrcCalc(self, prodYear, prodMonth, verticalHorizontal, drillDate, wellType, taxClass ):
        src = 0
        prodYearMonth = (prodYear * 100) + prodMonth
        if (prodYearMonth <= 201304 and wellType == 'Oil' and verticalHorizontal == 'V'):
            src = 2.5
        elif (wellType == 'Gas' and drillDate >= date(1998, 2, 9) and drillDate <= date(2002, 10, 1)):
            src = 2.5
        return src

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
subprocess.call(['notepad.exe', 'log.txt'])

"""
if __name__ == '__main__':
    unittest.main()

"""
