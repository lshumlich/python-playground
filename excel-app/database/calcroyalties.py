#!/bin/env python3

from datetime import date
from datetime import datetime
import subprocess
import traceback
import sys
import unittest
import os

from database.apperror import AppError
from database.database import DataBase, DataStructure
from database.royaltyworksheet import RoyaltyWorksheet
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
        self.reference_price = {'Pigeon Lake Indian': 24.04, 'Reserve no.138A': 25.37, 'Sawridge Indian': 25.13, 'Stony Plain Indian': 24.64}


    """
    The place where the calculations begin.
    """
    def process(self, wsName):

        self.db = DataBase(wsName)
        self.ws = RoyaltyWorksheet()

        errorCount = 0
        log = open(config.get_temp_dir() + 'log.txt','w')
        log.write ("Hello World.\n")

        for monthlyData in self.db.monthlyData():
            print('**** Processing ***', monthlyData.WellId)
            try:
                well = self.db.getWell(monthlyData.WellId)
                royalty = self.db.getRoyaltyMaster(well.Lease)
                lease = self.db.getLease(well.Lease)
                #pe =  self.db.getProducingEntity(well.Lease)
                royaltyCalc = self.db.getRoyaltyCalc(monthlyData.ProdMonth,monthlyData.WellId)
                commencement_period = self.db.determineCommencementPeriod(monthlyData.ProdMonth, well.CommencementDate)
                royalty_price = self.db.determineRoyaltyPrice(royalty.ValuationMethod,monthlyData)
                reference_price = {'Pigeon Lake Indian': 24.04, 'Reserve no.138A': 25.37, 'Sawridge Indian': 25.13, 'Stony Plain Indian': 24.64}
#                 log.write('Processing: ' + str(monthlyData.RecordNumber) + 
#                           ' ' + str(monthlyData.ProdMonth) + ' ' +
#                           monthlyData.Product + ' ' + well.RoyaltyClassification + ' ' +
#                           well.Classification + ' ' + str(monthlyData.ProdVol) +
#                           '\n')
# ** call second method **
                if monthlyData.Product == 'Oil' and 'SKProvCrownVar' in royalty.RoyaltyScheme:
                    self.calcSaskOilProvCrown(monthlyData, well, royalty, lease, royaltyCalc)
                elif monthlyData.Product == 'Oil' and 'IOGR1995' in royalty.RoyaltyScheme:
                    self.calcSaskOilIOGR1995(monthlyData, well, royalty, lease, royaltyCalc)
                else:
                    raise AppError('Royalty Scheme not yet developed: ' + lease.Prov + ' ' + monthlyData.Product)


                if monthlyData.Product == 'Oil' and 'GORR' in royalty.RoyaltyScheme:
                    royaltyCalc.GorrRoyaltyRate, royaltyCalc.GorrMessage = self.calcGorrPercent(monthlyData.ProdVol,monthlyData.ProdHours,royalty.Gorr)
                    royaltyCalc.GorrRoyaltyValue = monthlyData.ProdVol * well.IndianInterest * royaltyCalc.GorrRoyaltyRate / 100.0 * royaltyCalc.RoyaltyPrice
                    royaltyCalc.GorrRoyaltyVolume = monthlyData.ProdVol * well.IndianInterest * royaltyCalc.GorrRoyaltyRate / 100.0

                royaltyCalc.RoyaltyValuePreDeductions = (royaltyCalc.ProvCrownRoyaltyValue +
                                                        royaltyCalc.IOGR1995RoyaltyValue +
                                                        royaltyCalc.GorrRoyaltyValue)
                royaltyCalc.RoyaltyValue = royaltyCalc.RoyaltyValuePreDeductions
                
                royaltyCalc.RoyaltyVolume = (royaltyCalc.ProvCrownRoyaltyVolume +
                                                        royaltyCalc.IOGR1995RoyaltyVolume +
                                                        royaltyCalc.GorrRoyaltyVolume)

                if (royalty.TruckingDeducted == 'Y'):
                    royaltyCalc.RoyaltyTransportation = royaltyCalc.RoyaltyVolume * monthlyData.TransRate
                    royaltyCalc.RoyaltyDeductions += royaltyCalc.RoyaltyTransportation
                    royaltyCalc.RoyaltyValue -= royaltyCalc.RoyaltyTransportation

                if (royalty.ProcessingDeducted == 'Y'):
                    royaltyCalc.RoyaltyProcessing = royaltyCalc.RoyaltyVolume * monthlyData.ProcessingRate
                    royaltyCalc.RoyaltyDeductions += royaltyCalc.RoyaltyProcessing
                    royaltyCalc.RoyaltyValue -= royaltyCalc.RoyaltyProcessing
                
                # self.calcSupplementaryRoyaltiesIOGR1995(commencement_period, monthlyData, royalty_price, reference_price['Sawridge Indian'])
                #print(calcSupplementaryRoyaltiesIOGR1995)


                self.ws.printSaskOilRoyaltyRate(monthlyData, well, royalty, lease, royaltyCalc)
#                 log.write('--- Royalty Calculated: {} {} {} prod: {} Crown Rate: {}\n'.format(monthlyData.Row, royaltyCalc.ProdMonth,
#                                                                                              royaltyCalc.WellId, monthlyData.ProdVol, royaltyCalc.RoyaltyRate))
                self.db.updateRoyaltyCalc(royaltyCalc)

            except AppError as e:
                errorCount +=1
                log.write ('Record #: ' + str(monthlyData.RecordNumber) + ' ' + str(e) + '\n')
            except Exception as e:
                exc_type, exc_value, exc_traceback = sys.exc_info()
                errorCount +=1
                print('-'*10)
                print ('Record #: ' + str(monthlyData.RecordNumber) + ' ' + str(e))
                print(repr(traceback.extract_tb(exc_traceback)))
                traceback.print_exc()
                print('-'*10)
                log.write ('Record #: ' + str(monthlyData.RecordNumber) + ' ' + str(e) + '\n')
                

        self.db.commit()
        log.write ("*** That's it folks " + str(errorCount) + ' errors \n')
        log.close()

        del self.ws

# Adrienne - Write this method...
    def calcSaskOilProvCrownRoyaltyRate(self,royaltyCalc,econOilData,
                wellRoyaltyClassification,wellClassification,mop,src):

     #   econOilData = self.db.getECONOilData(monthlyData.ProdMonth)
     #   mop = monthlyData.ProdVol

        if wellRoyaltyClassification == 'Fourth Tier Oil':

            if mop < 25:
                royaltyCalc.ProvCrownRoyaltyRate = 0
                royaltyCalc.Message = 'MOP < 25 - RR = 0.' # Needed for worksheet so we can explain why royalty not calculated. Spent a few hours on this one

            elif mop <= 136.2:
                if wellClassification == 'Heavy':
                    royaltyCalc.C = econOilData.H4T_C
                    royaltyCalc.D = econOilData.H4T_D
                elif wellClassification == 'Southwest':
                    royaltyCalc.C = econOilData.SW4T_C
                    royaltyCalc.D = econOilData.SW4T_D
                elif wellClassification == 'Other':
                    royaltyCalc.C = econOilData.O4T_C
                    royaltyCalc.D = econOilData.O4T_D
                else:
                    raise AppError('Royalty Classification: ' + wellRoyaltyClassification + ' not known for ' + wellClassification + ' Royalty not calculated.')
                royaltyCalc.ProvCrownRoyaltyRate = (royaltyCalc.C * mop) - royaltyCalc.D

            else:
                if wellClassification == 'Heavy':
                    royaltyCalc.K = econOilData.H4T_K
                    royaltyCalc.X = econOilData.H4T_X
                elif wellClassification == 'Southwest':
                    royaltyCalc.K = econOilData.SW4T_K
                    royaltyCalc.X = econOilData.SW4T_X
                elif wellClassification == 'Other':
                    royaltyCalc.K = econOilData.O4T_K
                    royaltyCalc.X = econOilData.O4T_X
                else:
                    raise AppError('Royalty Classification: ' + wellRoyaltyClassification + ' not known for ' + wellClassification + ' Royalty not calculated.')
                royaltyCalc.ProvCrownRoyaltyRate = royaltyCalc.K - (royaltyCalc.X / mop)
        else:
            if wellClassification == 'Heavy':
                if wellRoyaltyClassification == 'Third Tier Oil':
                    royaltyCalc.K = econOilData.H3T_K
                    royaltyCalc.X = econOilData.H3T_X
                elif wellRoyaltyClassification == 'New Oil':
                    royaltyCalc.K = econOilData.HNEW_K
                    royaltyCalc.X = econOilData.HNEW_X
                else:
                    raise AppError('Royalty Classification: ' + wellRoyaltyClassification + ' not known for ' + wellClassification + ' Royalty not calculated.')
            elif wellClassification == 'Southwest':
                if wellRoyaltyClassification == 'Third Tier Oil':
                    royaltyCalc.K = econOilData.SW3T_K
                    royaltyCalc.X = econOilData.SW3T_X
                elif wellRoyaltyClassification == 'New Oil':
                    royaltyCalc.K = econOilData.SWNEW_K
                    royaltyCalc.X = econOilData.SWNEW_X
                else:
                    raise AppError('Royalty Classification: ' + wellRoyaltyClassification + ' not known for ' + wellClassification + ' Royalty not calculated.')
            elif wellClassification == 'Other':
                if wellRoyaltyClassification == 'Third Tier Oil':
                    royaltyCalc.K = econOilData.O3T_K
                    royaltyCalc.X = econOilData.O3T_X
                elif wellRoyaltyClassification == 'New Oil':
                    royaltyCalc.K = econOilData.ONEW_K
                    royaltyCalc.X = econOilData.ONEW_X
                elif wellRoyaltyClassification == 'Old Oil':
                    royaltyCalc.K = econOilData.OOLD_K
                    royaltyCalc.X = econOilData.OOLD_X
                else:
                    raise AppError('Royalty Classification: ' + wellRoyaltyClassification + ' not known for ' + wellClassification + ' Royalty not calculated.')
            else:
                raise AppError('Product Classification: ' + wellClassification + ' not known. Royalty not calculated.')

            #added if statement because of division by zero error
            if mop == 0:
                royaltyCalc.ProvCrownRoyaltyRate = 0
            else:
                royaltyCalc.ProvCrownRoyaltyRate = royaltyCalc.K - (royaltyCalc.X / mop) - src

        royaltyCalc.ProvCrownRoyaltyRate = round(royaltyCalc.ProvCrownRoyaltyRate, 6)

        return royaltyCalc.ProvCrownRoyaltyRate


    def calcSaskOilProvCrownRoyaltyVolumeValue(self, ProvCrownUsedRoyaltyRate, mop, indianInterest, MinRoyalty, crownMultiplier, RoyaltyPrice):
        # Note: If there is no sales. Use last months sales value... Not included in this code

        #royaltyCalc.RoyaltyPrice = self.determineRoyaltyprice(royalty.ValuationMethod, econOilData)

  #      ProvCrownUsedRoyaltyRate = royaltyCalc.ProvCrownRoyaltyRate

        if ProvCrownUsedRoyaltyRate < 0:
            ProvCrownUsedRoyaltyRate = 0

        if MinRoyalty != None:
            if MinRoyalty > ProvCrownUsedRoyaltyRate:
                ProvCrownUsedRoyaltyRate = MinRoyalty
        #
        # This was done this way so precision was not lost.
        #
        ProvCrownRoyaltyVolume = ((ProvCrownUsedRoyaltyRate / 100) *
                                                      crownMultiplier *
                                                      mop * indianInterest)

        ProvCrownRoyaltyValue = round((ProvCrownUsedRoyaltyRate / 100) *
                                               crownMultiplier *
                                               mop * indianInterest *
                                               RoyaltyPrice , 2)

        return ProvCrownRoyaltyVolume, ProvCrownRoyaltyValue


    def calcSaskOilIOGR1995(self, commencement_date, valuation_method, crown_multiplier, indian_interest, m, royalty_calc):
        """
        Calculated Based on regulations described: http://laws-lois.justice.gc.ca/eng/regulations/SOR-94-753/page-16.html#h-35

        """
        # Calculate the Comensment Date
        royalty_calc.CommencementPeriod = self.determineCommencementPeriod(m.ProdMonth, commencement_date)
        if royalty_calc.CommencementPeriod < 5:
            royalty_calc.IOGR1995RoyaltyVolume = self.calcSaskOilRegulationSubsection2(m.ProdVol)
        else:
            royalty_calc.IOGR1995RoyaltyVolume = self.calcSaskOilRegulationSubsection3(m.ProdVol)


        royalty_calc.RoyaltyPrice = self.determineRoyaltyPrice(valuation_method, m)

        royalty_calc.IOGR1995RoyaltyValue = round(crown_multiplier *
                                                      royalty_calc.IOGR1995RoyaltyVolume *
                                                      indian_interest *
                                                      royalty_calc.RoyaltyPrice , 2)

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

    def determineRoyaltyPrice(self,method,monthlyData):

        royaltyPrice = 0.0
        if method == 'ActSales':
            royaltyPrice = monthlyData.WellHeadPrice + monthlyData.TransRate + monthlyData.ProcessingRate
        else:
            royaltyPrice = monthlyData.WellHeadPrice

        return royaltyPrice


    def determineCommencementPeriod(self,prodMonth,commencementDate):
        if commencementDate == None:
            raise AppError('Commencement Date must be set for this Royalty Type.')
        cd = self.ensureDate(commencementDate)
        year = int(prodMonth / 100)
        month = prodMonth - (year * 100)
        prodDate = date(year,month,1)
        diff = prodDate - cd
        return round(diff.days/365,2)

    # called well head price the selling price
    def calcSupplementaryRoyaltiesIOGR1995(self, commencement_period, well_head_price, prod_vol, royalty_regulation, reference_price):
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
                    evalVol = vol / hours
                    gorrExplain = 'dprod = ' + '{:.6f}'.format(evalVol) + ' = ' + str(vol) + ' / ' + str(hours)
                elif s == 'mprod':
                    evalVol = vol
                    gorrExplain = 'mprod = ' + str(evalVol)
                elif s == 'fixed':
                    gorrExplain = 'fixed'
                else:
                    raise AppError('GORR Base is not known: ' + s)
#                 print (s,evalVol)
            elif i % 2 == 0:
                lastGorrMaxVol = gorrMaxVol
                gorrMaxVol = float(s)
#                 print('gorrMaxVol:', gorrMaxVol)
            else:
                gorrPercent = float(s)
#                 print('gorrPercent:', gorrPercent)
                if evalVol == 0:
                    gorrExplain += ' for an RR of ' + str(gorrPercent) +'%'
                    return gorrPercent, gorrExplain
                elif gorrMaxVol == 0:
                    gorrExplain += ' is greater than ' + str(lastGorrMaxVol) + ' for an RR of ' + str(gorrPercent) +'%'
                    return gorrPercent, gorrExplain
                elif evalVol <= gorrMaxVol:
                    gorrExplain += ' is greater than ' + str(lastGorrMaxVol) + ' and less than or equal to ' + str(gorrMaxVol) + ' for an RR of ' + str(gorrPercent) +'%'
                    return gorrPercent, gorrExplain


    #
    # Sask Oil Royalty Calculation... Finally we are here...
    #
    # These calculations are fully documented in two documents included in this project
    # under the Sask Folder:
    #   Factor Circulars.pdf
    #   OilFactors.pdf


    """
# Where is lease used in this method? - Adrienne
    def calcSaskOilProvCrown(self, monthlyData, well, royalty, lease, royaltyCalc):
        
        econOilData = self.db.getECONOilData(monthlyData.ProdMonth)
        # mop = monthlyData.ProdVol

        self.calcSaskOilProvCrownRoyaltyRate(royaltyCalc,econOilData, well.RoyaltyClassification, well.Classification, monthlyData.ProdVol, well.SRC)




        if well.RoyaltyClassification == 'Fourth Tier Oil':

            if mop < 25:
                royaltyCalc.ProvCrownRoyaltyRate = 0
                royaltyCalc.Message = 'MOP < 25 - RR = 0.' # Needed for worksheet so we can explain why royalty not calculated. Spent a few hours on this one

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
                    raise AppError('Royalty Classification: ' + well.RoyaltyClassification + ' not known for ' + well.Classification + ' Royalty not calculated.')
                royaltyCalc.ProvCrownRoyaltyRate = (royaltyCalc.C * mop) - royaltyCalc.D

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
                    raise AppError('Royalty Classification: ' + well.RoyaltyClassification + ' not known for ' + well.Classification + ' Royalty not calculated.')
                royaltyCalc.ProvCrownRoyaltyRate = royaltyCalc.K - (royaltyCalc.X / mop)
        else:
            if well.Classification == 'Heavy':
                if well.RoyaltyClassification == 'Third Tier Oil':
                    royaltyCalc.K = econOilData.H3T_K
                    royaltyCalc.X = econOilData.H3T_X
                elif well.RoyaltyClassification == 'New Oil':
                    royaltyCalc.K = econOilData.HNEW_K
                    royaltyCalc.X = econOilData.HNEW_X
                else:
                    raise AppError('Royalty Classification: ' + well.RoyaltyClassification + ' not known for ' + well.Classification + ' Royalty not calculated.')
            elif well.Classification == 'Southwest':
                if well.RoyaltyClassification == 'Third Tier Oil':
                    royaltyCalc.K = econOilData.SW3T_K
                    royaltyCalc.X = econOilData.SW3T_X
                elif well.RoyaltyClassification == 'New Oil':
                    royaltyCalc.K = econOilData.SWNEW_K
                    royaltyCalc.X = econOilData.SWNEW_X
                else:
                    raise AppError('Royalty Classification: ' + well.RoyaltyClassification + ' not known for ' + well.Classification + ' Royalty not calculated.')
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
                    raise AppError('Royalty Classification: ' + well.RoyaltyClassification + ' not known for ' + well.Classification + ' Royalty not calculated.')
            else:
                raise AppError('Product Classification: ' + well.Classification + ' not known. Royalty not calculated.')

            royaltyCalc.ProvCrownRoyaltyRate = royaltyCalc.K - (royaltyCalc.X / mop) - well.SRC
            
        royaltyCalc.ProvCrownRoyaltyRate = round(royaltyCalc.ProvCrownRoyaltyRate, 6)



        # Note: If there is no sales. Use last months sales value... Not included in this code

        royaltyCalc.RoyaltyPrice = self.determineRoyaltyprice(royalty.ValuationMethod, monthlyData)

        royaltyCalc.ProvCrownUsedRoyaltyRate = royaltyCalc.ProvCrownRoyaltyRate

        if royaltyCalc.ProvCrownUsedRoyaltyRate < 0:
            royaltyCalc.ProvCrownUsedRoyaltyRate = 0

        if royalty.MinRoyalty != None:
            if royalty.MinRoyalty > royaltyCalc.ProvCrownUsedRoyaltyRate:
                royaltyCalc.ProvCrownUsedRoyaltyRate = royalty.MinRoyalty
        #
        # This was done this way so precision was not lost.
        #
        royaltyCalc.ProvCrownRoyaltyVolume = ((royaltyCalc.ProvCrownUsedRoyaltyRate / 100) *
                                                      royalty.CrownMultiplier *
                                                      monthlyData.ProdVol *
                                                      well.IndianInterest)

        royaltyCalc.ProvCrownRoyaltyValue = round((royaltyCalc.ProvCrownUsedRoyaltyRate / 100) *
                                               royalty.CrownMultiplier *
                                               monthlyData.ProdVol *
                                               well.IndianInterest *
                                               royaltyCalc.RoyaltyPrice , 2)

        return


    def calcSaskOilIOGR1995(self, monthlyData, well, royalty, lease, royaltyCalc):

        #Calculated Based on regulations described: http://laws-lois.justice.gc.ca/eng/regulations/SOR-94-753/page-16.html#h-35


        Calculate the Comensment Date
        royaltyCalc.CommencementPeriod = self.determineCommencementPeriod(monthlyData.ProdMonth,well.CommencementDate)
        if royaltyCalc.CommencementPeriod < 5:
            royaltyCalc.IOGR1995RoyaltyVolume = self.calcSaskOilRegulationSubsection2(monthlyData.ProdVol)
        else:
            royaltyCalc.IOGR1995RoyaltyVolume = self.calcSaskOilRegulationSubsection3(monthlyData.ProdVol)
        

        royaltyCalc.RoyaltyPrice = self.determineRoyaltyprice(royalty.ValuationMethod, monthlyData)
        
        royaltyCalc.IOGR1995RoyaltyValue = round(royalty.CrownMultiplier * 
                                                      royaltyCalc.IOGR1995RoyaltyVolume * 
                                                      well.IndianInterest * 
                                                      royaltyCalc.RoyaltyPrice , 2)
        
        return
    
    def calcSaskOilRegulationSubsection2(self,mop):

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

        if mop < 80.0:
            royVol = mop *.1
        elif mop <= 160.0:
            royVol = 8 + (mop - 80) * .2
        else:
            royVol = 24 + (mop - 160) * .26

        return royVol
    
    def calcSaskOilRegulationSubsection3(self,mop):

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

        if mop < 80.0:
            royVol = mop *.1
        elif mop <= 160.0:
            royVol = 8 + (mop - 80) * .2
        elif mop <= 795.0:
            royVol = 24 + (mop - 160) * .26
        else:
            royVol = 189 + (mop - 795) * .4

        return royVol
    
    def determineRoyaltyprice(self,method,monthlyData):

        royaltyPrice = 0.0
        if method == 'ActSales':
            royaltyPrice = monthlyData.WellHeadPrice + monthlyData.TransRate + monthlyData.ProcessingRate
        else:
            royaltyPrice = monthlyData.WellHeadPrice
        
        return royaltyPrice
    
    def determineCommencementPeriod(self,prodMonth,commencementDate):
        if commencementDate == None:
            raise AppError('Commencement Date must be set for this Royalty Type.')
        cd = self.ensureDate(commencementDate)
        year = int(prodMonth / 100)
        month = prodMonth - (year * 100)
        prodDate = date(year,month,1)
        diff = prodDate - cd
        return round(diff.days/365,2)



    def calcGorrPercent(self,vol,hours,gorr):
         returns the rr% and an explination string
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
                    evalVol = vol / hours
                    gorrExplain = 'dprod = ' + '{:.6f}'.format(evalVol) + ' = ' + str(vol) + ' / ' + str(hours)
                elif s == 'mprod':
                    evalVol = vol
                    gorrExplain = 'mprod = ' + str(evalVol)
                elif s == 'fixed':
                    gorrExplain = 'fixed'
                else:
                    raise AppError('GORR Base is not known: ' + s)
#                 print (s,evalVol)
            elif i % 2 == 0:
                lastGorrMaxVol = gorrMaxVol
                gorrMaxVol = float(s)
#                 print('gorrMaxVol:', gorrMaxVol)
            else:
                gorrPercent = float(s)
#                 print('gorrPercent:', gorrPercent)
                if evalVol == 0:
                    gorrExplain += ' for a RR of ' + str(gorrPercent) +'%' 
                    return gorrPercent, gorrExplain
                elif gorrMaxVol == 0:
                    gorrExplain += ' is greater than ' + str(lastGorrMaxVol) + ' for a RR of ' + str(gorrPercent) +'%' 
                    return gorrPercent, gorrExplain
                elif evalVol <= gorrMaxVol:
                    gorrExplain += ' is between ' + str(lastGorrMaxVol) + ' - ' + str(gorrMaxVol) + ' for a RR of ' + str(gorrPercent) +'%' 
                    return gorrPercent, gorrExplain
        
        raise AppError('GORR Logic Error. We should never ever get here: ')

    """

    def ensureDate(self,d):
        if isinstance(d,datetime):
            return date(d.year, d.month, d.day)
        return d

     
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
