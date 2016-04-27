#!/bin/env python3

from datetime import date
from datetime import datetime
import subprocess
import traceback
import sys
import unittest
import os

from src.util.apperror import AppError
import config

"""
ToDo:

1) Calculate GORR and put in Worksheet (Done)
2) Save the calculated results in the spreadhseet
    Delete the old results from the calculated results
3) Calucate suplimental royalties
4) Split the worksheet into it's own file
5) Document and write good unit tests

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
        self.reference_price = {'Pigeon Lake Indian': 24.04, 'Reserve no.138A': 25.37, 'Sawridge Indian': 25.13, 'Stony Plain Indian': 24.64, 'Onion Lake': 25}
        self.db = config.get_database()

    """
    Process all the royalties that have monthly data
    """
    def process_all(self):
        errorCount = 0
        log = open(config.get_temp_dir() + 'log.txt', 'w')
        log.write("Hello World.\n")
        for monthlyData in self.db.select('Monthly'):
            try:
                self.process_one(monthlyData.WellID, monthlyData.ProdMonth, monthlyData.Product)

            except AppError as e:
                print(e)
    """
    Process a single royalty
    """
    def process_one(self, well_id, prod_month, product):
        print('**** Processing ***', well_id, prod_month, product)
        errorCount = 0
        log = open(config.get_temp_dir() + 'log.txt','w')
        log.write ("Hello World.\n")
        well = self.db.select1('Well', ID=well_id)
        well_lease_link = self.db.select1('WellLeaseLink', WellEvent=well.WellEvent)
        royalty = self.db.select1('Royaltymaster', ID=well_lease_link.LeaseID)
        lease = self.db.select1('Lease', ID=well_lease_link.LeaseID)
        monthly = self.db.select1('Monthly', WellID = well_id, ProdMonth = prod_month, Product = product)
        calc_array = self.db.select('Calc', WellID=well_id, ProdMonth = prod_month)
        if len(calc_array) == 0:
            calc = None
        else:
            calc = calc_array[0]
        calc = self.zero_royalty_calc(prod_month, well_id, calc)
        self.calc_royalties(well, royalty, lease, calc, monthly, well_lease_link)
        if len(calc_array) == 0:
            self.db.insert(calc)
        else:
            self.db.update(calc)

    def calc_royalties(self, well, royalty, lease, calc, monthly, well_lease_link):
        print('    -->',well.ID,monthly)

        if monthly.Product == 'Oil' and 'SKProvCrownVar' in royalty.RoyaltyScheme:
            self.calcSaskOilProvCrown(monthly, well, royalty, lease, calc, well_lease_link)
            calc.RoyaltyValuePreDeductions = calc.ProvCrownRoyaltyValue
            calc.RoyaltyValue = calc.RoyaltyValuePreDeductions

        elif monthly.Product == 'Oil' and 'IOGR1995' in royalty.RoyaltyScheme:
            self.calcSaskOilIOGR1995(well.CommencementDate, royalty.ValuationMethod, royalty.CrownMultiplier, well_lease_link.PEFNInterest, monthly, calc)
            calc.RoyaltyValuePreDeductions = calc.IOGR1995RoyaltyValue + calc.SupplementaryRoyalties
            calc.RoyaltyValue = calc.RoyaltyValuePreDeductions

        else:
            raise AppError("No calculation for" + str(well.ID) + str(monthly.ProdMonth) + str(monthly.Product) + str(royalty.RoyaltyScheme))


        if monthly.Product == 'Oil' and 'GORR' in royalty.RoyaltyScheme:
            calc.GorrRoyaltyRate, calc.GorrMessage = self.calcGorrPercent(monthly.ProdVol,monthly.ProdHours,royalty.Gorr)
            calc.GorrRoyaltyValue = round(monthly.ProdVol * well_lease_link.PEFNInterest * calc.GorrRoyaltyRate / 100.0 * calc.RoyaltyPrice, 6)
            calc.GorrRoyaltyVolume = round(monthly.ProdVol * well_lease_link.PEFNInterest * calc.GorrRoyaltyRate / 100.0, 2)
            calc.RoyaltyValuePreDeductions = calc.RoyaltyValuePreDeductions + calc.GorrRoyaltyValue
            calc.RoyaltyValue = calc.RoyaltyValuePreDeductions

            calc.RoyaltyVolume = (calc.ProvCrownRoyaltyVolume +
                                                        calc.IOGR1995RoyaltyVolume +
                                                        calc.GorrRoyaltyVolume)


        if (royalty.TruckingDeducted == 'Y'):
            calc.RoyaltyTransportation = calc.RoyaltyVolume * monthly.TransRate
            calc.RoyaltyDeductions += calc.RoyaltyTransportation
            calc.RoyaltyValue -= calc.RoyaltyTransportation

        if (royalty.ProcessingDeducted == 'Y'):
            calc.RoyaltyProcessing = calc.RoyaltyVolume * monthly.ProcessingRate
            calc.RoyaltyDeductions += calc.RoyaltyProcessing
            calc.RoyaltyValue -= calc.RoyaltyProcessing
            print("this is commencement period", calc.CommencementPeriod)

                #calc.SupplementaryRoyalties = self.calcSupplementaryRoyaltiesIOGR1995(calc.CommencementPeriod, monthly.WellHeadPrice, monthly.ProdVol, calc.RoyaltyPrice, self.reference_price['Sawridge Indian'])
                #print(calcSupplementaryRoyaltiesIOGR1995)
                #Royalty Price for Royalty Deduction???
#            self.ws.printSaskOilRoyaltyRate(monthly, well, royalty, lease, calc)
#                 log.write('--- Royalty Calculated: {} {} {} prod: {} Crown Rate: {}\n'.format(monthly.Row, calc.ProdMonth,
#                                                                                              calc.WellId, monthly.ProdVol, calc.RoyaltyRate))
#             self.db.updateRoyaltycalc(calc)

        # except AppError as e:
        #     errorCount +=1
        #     log.write ('Record #: ' + str(monthly.RecordNumber) + ' ' + str(e) + '\n')
        # except Exception as e:
        #     exc_type, exc_value, exc_traceback = sys.exc_info()
        #     errorCount +=1
        #     print('-'*10)
        #     print ('Record #: ' + str(monthly.RecordNumber) + ' ' + str(e))
        #     print(repr(traceback.extract_tb(exc_traceback)))
        #     traceback.print_exc()
        #     print('-'*10)
        #     log.write ('Record #: ' + str(monthly.RecordNumber) + ' ' + str(e) + '\n')


        self.db.commit()
#         log.write ("*** That's it folks " + str(errorCount) + ' errors \n')
#         log.close()
# 
#         del self.ws

# Adrienne - Write this method...
    def calcSaskOilProvCrownRoyaltyRate(self,calc,econOilData,
                wellRoyaltyClassification,wellClassification,mop,src):

    #ADD COMMENCEMENT
     #   econOilData = self.db.getECONOilData(monthly.ProdMonth)
     #   mop = monthly.ProdVol

        if wellRoyaltyClassification == 'Fourth Tier Oil':

            if mop < 25:
                calc.ProvCrownRoyaltyRate = 0
                calc.Message = 'MOP < 25 - RR = 0.' # Needed for worksheet so we can explain why royalty not calculated. Spent a few hours on this one

            elif mop <= 136.2:
                if wellClassification == 'Heavy':
                    calc.C = econOilData.H4T_C
                    calc.D = econOilData.H4T_D
                elif wellClassification == 'Southwest':
                    calc.C = econOilData.SW4T_C
                    calc.D = econOilData.SW4T_D
                elif wellClassification == 'Other':
                    calc.C = econOilData.O4T_C
                    calc.D = econOilData.O4T_D
                else:
                    raise AppError('Royalty Classification: ' + wellRoyaltyClassification + ' not known for ' + wellClassification + ' Royalty not calculated.')
                calc.ProvCrownRoyaltyRate = (calc.C * mop) - calc.D

            else:
                if wellClassification == 'Heavy':
                    calc.K = econOilData.H4T_K
                    calc.X = econOilData.H4T_X
                elif wellClassification == 'Southwest':
                    calc.K = econOilData.SW4T_K
                    calc.X = econOilData.SW4T_X
                elif wellClassification == 'Other':
                    calc.K = econOilData.O4T_K
                    calc.X = econOilData.O4T_X
                else:
                    raise AppError('Royalty Classification: ' + wellRoyaltyClassification + ' not known for ' + wellClassification + ' Royalty not calculated.')
                calc.ProvCrownRoyaltyRate = calc.K - (calc.X / mop)
        else:
            if wellClassification == 'Heavy':
                if wellRoyaltyClassification == 'Third Tier Oil':
                    calc.K = econOilData.H3T_K
                    calc.X = econOilData.H3T_X
                elif wellRoyaltyClassification == 'New Oil':
                    calc.K = econOilData.HNEW_K
                    calc.X = econOilData.HNEW_X
                else:
                    raise AppError('Royalty Classification: ' + wellRoyaltyClassification + ' not known for ' + wellClassification + ' Royalty not calculated.')
            elif wellClassification == 'Southwest':
                if wellRoyaltyClassification == 'Third Tier Oil':
                    calc.K = econOilData.SW3T_K
                    calc.X = econOilData.SW3T_X
                elif wellRoyaltyClassification == 'New Oil':
                    calc.K = econOilData.SWNEW_K
                    calc.X = econOilData.SWNEW_X
                else:
                    raise AppError('Royalty Classification: ' + wellRoyaltyClassification + ' not known for ' + wellClassification + ' Royalty not calculated.')
            elif wellClassification == 'Other':
                if wellRoyaltyClassification == 'Third Tier Oil':
                    calc.K = econOilData.O3T_K
                    calc.X = econOilData.O3T_X
                elif wellRoyaltyClassification == 'New Oil':
                    calc.K = econOilData.ONEW_K
                    calc.X = econOilData.ONEW_X
                elif wellRoyaltyClassification == 'Old Oil':
                    calc.K = econOilData.OOLD_K
                    calc.X = econOilData.OOLD_X
                else:
                    raise AppError('Royalty Classification: ' + wellRoyaltyClassification + ' not known for ' + wellClassification + ' Royalty not calculated.')
            else:
                raise AppError('Product Classification: ' + wellClassification + ' not known. Royalty not calculated.')

            #added if statement because of division by zero error
            if mop == 0:
                calc.ProvCrownRoyaltyRate = 0
            else:
                calc.ProvCrownRoyaltyRate = calc.K - (calc.X / mop) - src

        calc.ProvCrownRoyaltyRate = round(calc.ProvCrownRoyaltyRate, 6)

        return calc.ProvCrownRoyaltyRate


    def calcSaskOilProvCrownRoyaltyVolumeValue(self, m, indian_interest, royalty, calc):
        # Note: If there is no sales. Use last months sales value... Not included in this code

        calc.RoyaltyPrice = self.determineRoyaltyPrice(royalty.ValuationMethod, m)

        calc.ProvCrownUsedRoyaltyRate = calc.ProvCrownRoyaltyRate
        print("THIS IS PROVCROWNUSEDROYALTYRATE", calc.ProvCrownUsedRoyaltyRate)

        if calc.ProvCrownUsedRoyaltyRate < 0:
            calc.ProvCrownUsedRoyaltyRate = 0

        if royalty.MinRoyalty != None:
            if royalty.MinRoyalty > calc.ProvCrownUsedRoyaltyRate:
                calc.ProvCrownUsedRoyaltyRate = royalty.MinRoyalty


        # This was done this way so precision was not lost.

        calc.ProvCrownRoyaltyVolume = round(((calc.ProvCrownUsedRoyaltyRate / 100) *
                                                      royalty.CrownMultiplier *
                                                      m.ProdVol * indian_interest), 2)

        calc.ProvCrownRoyaltyValue = calc.ProvCrownRoyaltyVolume * calc.RoyaltyPrice



    def calcSaskOilIOGR1995(self, commencement_date, valuation_method, crown_multiplier, indian_interest, m, royalty_calc):
        """
        Calculated Based on regulations described: http://laws-lois.justice.gc.ca/eng/regulations/SOR-94-753/page-16.html#h-35
        """
        # Calculate the Comensment Date
        royalty_calc.CommencementPeriod = self.determineCommencementPeriod(m.ProdMonth, commencement_date)
        if royalty_calc.CommencementPeriod < 5:
            royalty_calc.IOGR1995RoyaltyVolume = round(self.calcSaskOilRegulationSubsection2(m.ProdVol),2)
            royalty_calc.RoyaltyRegulation = self.calcSaskOilRegulationSubsection2(m.ProdVol)
        else:
            royalty_calc.IOGR1995RoyaltyVolume = round(self.calcSaskOilRegulationSubsection3(m.ProdVol),2)
            royalty_calc.RoyaltyRegulation = self.calcSaskOilRegulationSubsection3(m.ProdVol)

        
        royalty_calc.RoyaltyPrice = round(self.determineRoyaltyPrice(valuation_method, m), 6)
        
        royalty_calc.IOGR1995RoyaltyValue = round(crown_multiplier *
                                                      royalty_calc.IOGR1995RoyaltyVolume *
                                                      indian_interest *
                                                      royalty_calc.RoyaltyPrice , 2)

        royalty_calc.SupplementaryRoyalties = round(self.calcSupplementaryRoyaltiesIOGR1995(royalty_calc.CommencementPeriod, m.WellHeadPrice, m.ProdVol, royalty_calc.RoyaltyRegulation, self.reference_price['Onion Lake']), 2)
        print("THIS IS SUPP ROYALTIES", royalty_calc.SupplementaryRoyalties)
        return

    def calcSaskOilRegulationSubsection2(self,mop):
        """
(2) During the five year period beginning on the date determined by the Executive Director
    to be the date of commencement of production of oil from a contract area, the basic royalty
    is the part of the oil that is obtained from, or attributable to, each well during each month
    of that period calculated in accordance with the table to this subsection

                Column I            Column II
        Item    Monthly Production  Royalty per Month
                (m3)
        1.      Less than 80        10% of the number of cubic metres
        2.      80 to 160           8 m3 plus 20% of the number of cubic metres in excess of 80
        3.      More than 160       24 m3 plus 26% of the number of cubic metres in excess of 160
        """
        if mop < 80.0:
            royVol = mop *.1
        elif mop <= 160.0:
            royVol = 8 + (mop - 80) * .2
        else:
            royVol = 24 + (mop - 160) * .26

        return royVol

    def calcSaskOilRegulationSubsection3(self, mop):
        """
(3) Commencing immediately after the period referred to in subsection (2), the basic royalty is the
    part of the oil that is obtained from, or attributable to, each well in a contract area during
    each month thereafter calculated in accordance with the table to this subsection.

                Column I            Column II
        Item    Monthly             Production
                (m3)

        1.      Less than 80        10% of the number of cubic metres
        2.      80 to 160           8 m3 plus 20% of the number of cubic metres in excess of 80
        3.      160 to 795          24 m3 plus 26% of the number of cubic metres in excess of 160
        4.      More than 795       189 m3 plus 40% of the number of cubic metres in excess of 795
        """
        if mop < 80.0:
            royVol = mop *.1
        elif mop <= 160.0:
            royVol = 8 + (mop - 80) * .2
        elif mop <= 795.0:
            royVol = 24 + (mop - 160) * .26
        else:
            royVol = 189 + (mop - 795) * .4

        return royVol

    def determineRoyaltyPrice(self,method,monthly):

        royaltyPrice = 0.0
        if method == 'ActSales':
            royaltyPrice = monthly.WellHeadPrice + monthly.TransRate + monthly.ProcessingRate
        else:
            royaltyPrice = monthly.WellHeadPrice

        return royaltyPrice

    def ensureDate(self,d):
        if isinstance(d,datetime):
            return date(d.year, d.month, d.day)
        return d

    def determineCommencementPeriod(self,prodMonth,commencementDate):
        if commencementDate == None:
            return 5

        else:
            cd = self.ensureDate(commencementDate)
            year = int(prodMonth / 100)
            month = prodMonth - (year * 100)
            prodDate = date(year,month,1)
            diff = prodDate - cd
            return round(diff.days/365,2)

    def calcSupplementaryRoyaltiesIOGR1995(self, commencement_period, well_head_price, prod_vol, royalty_regulation, reference_price):
        print("This is the commencement_period", commencement_period)
        if commencement_period <= 5:
            supplementary_royalty = (prod_vol - royalty_regulation)*0.5*(well_head_price - reference_price)
        else:
            supplementary_royalty = (prod_vol - royalty_regulation)*(0.75*(well_head_price - reference_price - 12.58) + 6.29)

        return round(supplementary_royalty, 2)

    def calcGorrPercent(self,vol,hours,gorr):
        """ returns the rr% based on the GORR base and an explination string  """
        words = gorr.split(",")
        gorrPercent = 0.0
        gorrMaxVol = 0.0
        lastGorrMaxVol = 0.0
        gorrExplain = ''

        i = 0
        evalVol = 0
        for s in words:
            i += 1
            if i == 1:
                if s == 'dprod':
                    evalVol = round(vol / 30.5, 2)
                    gorrExplain = 'dprod = mprod / 30.5 days; ' + '{:.2f}'.format(evalVol)
                elif s == 'mprod':
                    evalVol = vol
                    gorrExplain = 'mprod = ' + str(evalVol)
                elif s =='hprod':
                    evalVol = round(vol / hours, 2)
                    gorrExplain = 'hprod = mprod / hours; ' + '{:.2f}'.format(evalVol)
                elif s == 'fixed':
                    gorrExplain = 'fixed'
                else:
                    raise AppError('GORR Base is not known: ' + s)
            elif i % 2 == 0:
                lastGorrMaxVol = gorrMaxVol
                gorrMaxVol = float(s)
            else:
                gorrPercent = float(s)
                if evalVol == 0:
                    gorrExplain += ' for a RoyRate of ' + str(gorrPercent) +'%'
                    return round(gorrPercent, 6), gorrExplain
                elif gorrMaxVol == 0:
                    gorrExplain += ' is > ' + str(lastGorrMaxVol) + ' for a RoyRate of ' + str(gorrPercent) +'%'
                    return round(gorrPercent, 6), gorrExplain
                elif evalVol <= gorrMaxVol:
                    gorrExplain += ' is > ' + str(lastGorrMaxVol) + ' and <= ' + str(gorrMaxVol) + ' for a RoyRate of ' + str(gorrPercent) +'%'
                    return round(gorrPercent, 6), gorrExplain
        raise AppError('GORR Logic Error. We should never ever get here: ')


    '''
    Sask Oil Royalty Calculation

    These calculations are fully documented in two documents included in this project
    under the Sask Folder:
      Factor Circulars.pdf
      OilFactors.pdf
    '''
    def calcSaskOilProvCrown(self, monthly, well, royalty, lease, calc, well_lease_link):
        calc.CommencementPeriod = self.determineCommencementPeriod(monthly.ProdMonth, well.CommencementDate)
        econOilData = self.db.select1("ECONData",ProdMonth = monthly.ProdMonth)
        self.calcSaskOilProvCrownRoyaltyRate(calc,econOilData, well.RoyaltyClassification,
                                             well.Classification, monthly.ProdVol, well.SRC)

        # Note: If there is no sales. Use last months sales value... Not included in this code
        calc.RoyaltyPrice = self.determineRoyaltyPrice(royalty.ValuationMethod, monthly)

        self.calcSaskOilProvCrownRoyaltyVolumeValue(monthly, well_lease_link.PEFNInterest, royalty, calc)

    '''
    Royalty Calculation
    '''

    def zero_royalty_calc(self, month, wellID, rc):
        if rc == None:
            rc = self.db.get_data_structure('Calc')
            #         rc.ID = 0
        rc.ProdMonth = month
        rc.WellID = wellID

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
        setattr(rc, 'SupplementaryRoyalties', 0.0)
        setattr(rc, 'RoyaltyRegulation', 0.0)

        setattr(rc, 'CommencementPeriod', None)
        setattr(rc, 'Message', None)
        setattr(rc, 'GorrMessage', None)

        return rc


     
if __name__ == '__main__':
    pr = ProcessRoyalties()
#     pr.process('iogcdatabase.xlsx')
    pr.process('database.xlsx')
    print('os name is:',os.name)
    if os.name != "posix":
        subprocess.call(['notepad.exe', 'Royalty Worksheet.txt'])
        subprocess.call(['notepad.exe', 'log.txt'])

"""
if __name__ == '__main__':
    unittest.main()

"""
