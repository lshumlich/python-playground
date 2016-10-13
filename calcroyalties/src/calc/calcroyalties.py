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
        well_lease_link_array = self.db.select('WellLeaseLink', WellID=well_id)
        if len(well_lease_link_array) == 0:
            raise AppError("There were no well_lease_link records for " + str(well_id) + str(prod_month))
        well_lease_link = well_lease_link_array[0]
        royalty = self.db.select1('Royaltymaster', ID=well_lease_link.LeaseID)
        lease = self.db.select1('Lease', ID=well_lease_link.LeaseID)
        monthly = self.db.select1('Monthly', WellID = well_id, ProdMonth = prod_month, Product = product)
        calc_array = self.db.select('Calc', WellID=well_id, ProdMonth = prod_month)
        if len(calc_array) == 0:
            calc = None
        else:
            calc = calc_array[0]
        calc = self.zero_royalty_calc(prod_month, well_id, product, calc)
        self.calc_royalties(well, royalty, lease, calc, monthly, well_lease_link)
        if len(calc_array) == 0:
            self.db.insert(calc)
        else:
            self.db.update(calc)

    def calc_royalties(self, well, royalty, lease, calc, monthly, well_lease_link):
        # print('    -->',well.WellEvent,monthly)

        if monthly.Product == 'Oil' and 'SKProvCrownVar' in royalty.RoyaltyScheme:
            self.calcSaskOilProvCrown(monthly, well, royalty, lease, calc, well_lease_link)
            calc.RoyaltyValuePreDeductions = calc.ProvCrownRoyaltyValue
            calc.RoyaltyValue = calc.RoyaltyValuePreDeductions

        elif monthly.Product == 'Oil' and 'IOGR1995' in royalty.RoyaltyScheme:
            self.calcSaskOilIOGR1995(well.CommencementDate, royalty.ValuationMethod, royalty.CrownMultiplier,
                                     well_lease_link.PEFNInterest, monthly, calc)
            calc.RoyaltyValuePreDeductions = calc.IOGR1995RoyaltyValue + calc.SupplementaryRoyalties
            calc.RoyaltyValue = calc.RoyaltyValuePreDeductions

        elif monthly.Product == 'Gas' and 'SKProvCrownVar' in royalty.RoyaltyScheme:
            self.calcSaskGasProvCrown(monthly, well, royalty, lease, calc, well_lease_link)
            calc.RoyaltyValuePreDeductions = calc.ProvCrownRoyaltyValue
            calc.RoyaltyValue = calc.RoyaltyValuePreDeductions


        else:
            raise AppError("No calculation for" + str(well.WellEvent) + str(monthly.ProdMonth) + str(monthly.Product) + str(royalty.RoyaltyScheme))


        if monthly.Product == 'Oil' and 'GORR' in royalty.RoyaltyScheme:
            calc.GorrRoyaltyRate, calc.GorrMessage = self.calcGorrPercent(monthly.ProdVol,monthly.ProdHours,royalty.Gorr)
            calc.GorrRoyaltyValue = round(monthly.ProdVol * well_lease_link.PEFNInterest/100 * calc.GorrRoyaltyRate / 100.0 * calc.RoyaltyPrice, 6)
            calc.GorrRoyaltyVolume = round(monthly.ProdVol * well_lease_link.PEFNInterest/100 * calc.GorrRoyaltyRate / 100.0, 2)
            calc.RoyaltyValuePreDeductions = calc.RoyaltyValuePreDeductions + calc.GorrRoyaltyValue
            calc.RoyaltyValue = calc.RoyaltyValuePreDeductions

        calc.RoyaltyVolume = (calc.ProvCrownRoyaltyVolume +
                                                    calc.IOGR1995RoyaltyVolume +
                                                        calc.GorrRoyaltyVolume)


        if (royalty.TruckingDeducted == 'Y'):
            calc.RoyaltyTransportation = calc.RoyaltyVolume * monthly.TransRate
            calc.RoyaltyDeductions += calc.RoyaltyTransportation
            calc.RoyaltyValue -= calc.RoyaltyTransportation

        # if (royalty.TruckingOverride != None):
        #     calc.RoyaltyTransportation = royalty.TruckingOverride

        if (royalty.ProcessingDeducted == 'Y'):
            calc.RoyaltyProcessing = calc.RoyaltyVolume * monthly.ProcessingRate
            calc.RoyaltyDeductions += calc.RoyaltyProcessing
            calc.RoyaltyValue -= calc.RoyaltyProcessing

        if monthly.Product == 'Gas':
            if (royalty.GCADeducted == 'Y'):
                calc.RoyaltyGCA = calc.RoyaltyVolume * monthly.GCARate
                calc.RoyaltyDeductions += calc.RoyaltyGCA
                calc.RoyaltyValue -= calc.RoyaltyGCA

# #            self.ws.printSaskOilRoyaltyRate(monthly, well, royalty, lease, calc)
# #                 log.write('--- Royalty Calculated: {} {} {} prod: {} Crown Rate: {}\n'.format(monthly.Row, calc.ProdMonth,
# #                                                                                              calc.WellId, monthly.ProdVol, calc.RoyaltyRate))
# #             self.db.updateRoyaltycalc(calc)
#
#         # except AppError as e:
#         #     errorCount +=1
#         #     log.write ('Record #: ' + str(monthly.RecordNumber) + ' ' + str(e) + '\n')
#         # except Exception as e:
#         #     exc_type, exc_value, exc_traceback = sys.exc_info()
#         #     errorCount +=1
#         #     print('-'*10)
#         #     print ('Record #: ' + str(monthly.RecordNumber) + ' ' + str(e))
#         #     print(repr(traceback.extract_tb(exc_traceback)))
#         #     traceback.print_exc()
#         #     print('-'*10)
#         #     log.write ('Record #: ' + str(monthly.RecordNumber) + ' ' + str(e) + '\n')
#
#
#         self.db.commit()
# #         log.write ("*** That's it folks " + str(errorCount) + ' errors \n')
# #         log.close()
# #
# #         del self.ws

    def calcSaskGasProvCrownRoyaltyRate(self,calc,econ_gas_data,
                well_royalty_classification,mgp,src,well_type):

        if well_royalty_classification == 'Fourth Tier Gas':
            if well_type == 'GasWells':
                if mgp <= 25:
                    calc.ProvCrownRoyaltyRate = 0
                    calc.Message = 'MOP <= 25 - RR = 0.'
                elif mgp <= 115.4:
                    calc.C = econ_gas_data.G4T_C
                    calc.D = econ_gas_data.G4T_D
                    calc.ProvCrownRoyaltyRate = (calc.C * mgp) - calc.D
                else:
                    calc.K = econ_gas_data.G4T_K
                    calc.X = econ_gas_data.G4T_X
                    calc.ProvCrownRoyaltyRate = calc.K - (calc.X / mgp)

            elif well_type == 'OilWells':
                if mgp <= 64.7:
                    calc.ProvCrownRoyaltyRate = 0
                    calc.Message = 'MOP <= 64.7 - RR = 0.'
                else:
                    calc.K = econ_gas_data.G4T_K
                    calc.X = econ_gas_data.G4T_X
                    calc.ProvCrownRoyaltyRate = calc.K - (calc.X / mgp)

            else:
                raise AppError('Well Type: ' + well_type + ' not known for ' + well_royalty_classification + ' Royalty not calculated.')

        elif well_royalty_classification == 'Third Tier Gas':
            if mgp < 115.4:
                calc.C = econ_gas_data.G3T_C
                #SRC ?? - ProdDate
                calc.ProvCrownRoyaltyRate = (calc.C * mgp) - src

            else:
                calc.K = econ_gas_data.G3T_K
                calc.X = econ_gas_data.G3T_X
                #SRC ?? - ProdDate
                calc.ProvCrownRoyaltyRate = calc.K - (calc.X / mgp) - src

        elif well_royalty_classification == 'New Gas':
            if mgp < 115.4:
                calc.C = econ_gas_data.GNEW_C
                calc.ProvCrownRoyaltyRate = (calc.C * mgp) - src
                #SRC ?? - ProdDate
            else:
                calc.K = econ_gas_data.GNEW_K
                calc.X = econ_gas_data.GNEW_X
                #SRC ?? - ProdDate
                calc.ProvCrownRoyaltyRate = calc.K - (calc.X / mgp) - src

        elif well_royalty_classification == 'Old Gas':
            if mgp < 115.4:
                calc.C = econ_gas_data.GOLD_C
                calc.ProvCrownRoyaltyRate = (calc.C * mgp) - src
                #SRC ?? - ProdDate
            else:
                calc.K = econ_gas_data.GOLD_K
                calc.X = econ_gas_data.GOLD_X
                #SRC ?? - ProdDate
                calc.ProvCrownRoyaltyRate = calc.K - (calc.X / mgp) - src

        else:
            raise AppError('Royalty Classification: ' + well_royalty_classification + ' not known for ' + well_type + ' Royalty not calculated.')

        calc.ProvCrownRoyaltyRate = round(calc.ProvCrownRoyaltyRate, 6)
        return calc.ProvCrownRoyaltyRate


    def calcSaskOilProvCrownRoyaltyRate(self,calc,econ_oil_data,
                well_royalty_classification,well_classification,mop,src):

        if well_royalty_classification == 'Fourth Tier Oil':

            if mop < 25:
                calc.ProvCrownRoyaltyRate = 0
                calc.Message = 'MOP < 25 - RR = 0.'

            elif mop <= 136.2:
                if well_classification == 'Heavy':
                    calc.C = econ_oil_data.H4T_C
                    calc.D = econ_oil_data.H4T_D
                elif well_classification == 'Southwest':
                    calc.C = econ_oil_data.SW4T_C
                    calc.D = econ_oil_data.SW4T_D
                elif well_classification == 'Other':
                    calc.C = econ_oil_data.O4T_C
                    calc.D = econ_oil_data.O4T_D
                else:
                    raise AppError('Royalty Classification: ' + well_royalty_classification + ' not known for ' + well_classification + ' Royalty not calculated.')
                calc.ProvCrownRoyaltyRate = (calc.C * mop) - calc.D

            else:
                if well_classification == 'Heavy':
                    calc.K = econ_oil_data.H4T_K
                    calc.X = econ_oil_data.H4T_X
                elif well_classification == 'Southwest':
                    calc.K = econ_oil_data.SW4T_K
                    calc.X = econ_oil_data.SW4T_X
                elif well_classification == 'Other':
                    calc.K = econ_oil_data.O4T_K
                    calc.X = econ_oil_data.O4T_X
                else:
                    raise AppError('Royalty Classification: ' + well_royalty_classification + ' not known for ' + well_classification + ' Royalty not calculated.')
                calc.ProvCrownRoyaltyRate = calc.K - (calc.X / mop)
        else:
            if well_classification == 'Heavy':
                if well_royalty_classification == 'Third Tier Oil':
                    calc.K = econ_oil_data.H3T_K
                    calc.X = econ_oil_data.H3T_X
                elif well_royalty_classification == 'New Oil':
                    calc.K = econ_oil_data.HNEW_K
                    calc.X = econ_oil_data.HNEW_X
                else:
                    raise AppError('Royalty Classification: ' + well_royalty_classification + ' not known for ' + well_classification + ' Royalty not calculated.')
            elif well_classification == 'Southwest':
                if well_royalty_classification == 'Third Tier Oil':
                    calc.K = econ_oil_data.SW3T_K
                    calc.X = econ_oil_data.SW3T_X
                elif well_royalty_classification == 'New Oil':
                    calc.K = econ_oil_data.SWNEW_K
                    calc.X = econ_oil_data.SWNEW_X
                else:
                    raise AppError('Royalty Classification: ' + well_royalty_classification + ' not known for ' + well_classification + ' Royalty not calculated.')
            elif well_classification == 'Other':
                if well_royalty_classification == 'Third Tier Oil':
                    calc.K = econ_oil_data.O3T_K
                    calc.X = econ_oil_data.O3T_X
                elif well_royalty_classification == 'New Oil':
                    calc.K = econ_oil_data.ONEW_K
                    calc.X = econ_oil_data.ONEW_X
                elif well_royalty_classification == 'Old Oil':
                    calc.K = econ_oil_data.OOLD_K
                    calc.X = econ_oil_data.OOLD_X
                else:
                    raise AppError('Royalty Classification: ' + well_royalty_classification + ' not known for ' + well_classification + ' Royalty not calculated.')
            else:
                raise AppError('Product Classification: ' + well_classification + ' not known. Royalty not calculated.')

            if mop == 0:
                calc.ProvCrownRoyaltyRate = 0
            else:
                calc.ProvCrownRoyaltyRate = calc.K - (calc.X / mop) - src

        calc.ProvCrownRoyaltyRate = round(calc.ProvCrownRoyaltyRate, 6)

        return calc.ProvCrownRoyaltyRate


    def calcSaskOilProvCrownRoyaltyVolumeValue(self, m, fn_interest, royalty, calc):
        # Note: If there is no sales. Use last months sales value... Not included in this code

        calc.RoyaltyPrice = self.determineRoyaltyPrice(royalty.ValuationMethod, m)

        calc.ProvCrownUsedRoyaltyRate = calc.ProvCrownRoyaltyRate

        if calc.ProvCrownUsedRoyaltyRate < 0:
            calc.ProvCrownUsedRoyaltyRate = 0

        if royalty.MinRoyalty != None:
            if royalty.MinRoyalty > calc.ProvCrownUsedRoyaltyRate:
                calc.ProvCrownUsedRoyaltyRate = royalty.MinRoyalty

        calc.ProvCrownRoyaltyVolume = round(((calc.ProvCrownUsedRoyaltyRate / 100) *
                                                      royalty.CrownMultiplier *
                                                      m.ProdVol * fn_interest), 2)

        calc.ProvCrownRoyaltyValue = calc.ProvCrownRoyaltyVolume * calc.RoyaltyPrice

    def calcSaskOilIOGR1995(self, commencement_date, valuation_method, crown_multiplier, fn_interest, m, calc):
        """
        Calculated Based on regulations described: http://laws-lois.justice.gc.ca/eng/regulations/SOR-94-753/page-16.html#h-35
        """
        # Calculate the Comensment Date
        calc.CommencementPeriod = self.determineCommencementPeriod(m.ProdMonth, commencement_date)
        if calc.CommencementPeriod < 5:
            calc.RoyaltyRegulation = self.calcSaskOilRegulationSubsection2(m.ProdVol)
            calc.IOGR1995RoyaltyVolume = round(calc.RoyaltyRegulation,2)
        else:
            calc.RoyaltyRegulation = self.calcSaskOilRegulationSubsection3(m.ProdVol)
            calc.IOGR1995RoyaltyVolume = round(calc.RoyaltyRegulation,2)
        
        calc.RoyaltyPrice = round(self.determineRoyaltyPrice(valuation_method, m), 6)
        
        calc.IOGR1995RoyaltyValue = round(crown_multiplier *
                                                      calc.IOGR1995RoyaltyVolume *
                                                      fn_interest *
                                                      calc.RoyaltyPrice , 2)

        calc.SupplementaryRoyalties = round(self.calcSupplementaryRoyaltiesIOGR1995(calc.CommencementPeriod, m.WellHeadPrice, m.ProdVol, calc.RoyaltyRegulation, self.reference_price['Onion Lake']), 2)
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
        econ_oil_data = self.db.select1("ECONData",ProdMonth = monthly.ProdMonth)
        if royalty.OverrideRoyaltyClassification != None:
            RoyaltyClassification = royalty.OverrideRoyaltyClassification
        else:
            RoyaltyClassification = well.RoyaltyClassification
        self.calcSaskOilProvCrownRoyaltyRate(calc,econ_oil_data, RoyaltyClassification,
                                             well.Classification, monthly.ProdVol, well.SRC)
        self.calcSaskOilProvCrownRoyaltyVolumeValue(monthly, well_lease_link.PEFNInterest, royalty, calc)


    def calcSaskGasProvCrown(self, monthly, well, royalty, lease, calc, well_lease_link):
        calc.CommencementPeriod = self.determineCommencementPeriod(monthly.ProdMonth, well.CommencementDate)
        econ_gas_data = self.db.select1("ECONGasData",ProdMonth = monthly.ProdMonth)
        if royalty.OverrideRoyaltyClassification != None:
            RoyaltyClassification = royalty.OverrideRoyaltyClassification
        else:
            RoyaltyClassification = well.RoyaltyClassification
        #We need econ oil data
        # Note: If there is no sales. Use last months sales value... Not included in this code
        calc.RoyaltyPrice = self.determineRoyaltyPrice(royalty.ValuationMethod, monthly)
        self.calcSaskOilProvCrownRoyaltyRate(calc,econ_gas_data, well.RoyaltyClassification, monthly.ProdVol,
                                             well.SRC, well.Classification)
    '''
    Royalty Calculation
    '''

    def zero_royalty_calc(self, month, well_id, product, rc):
        if rc == None:
            rc = self.db.get_data_structure('Calc')
            #         rc.ID = 0
        rc.ProdMonth = month
        rc.WellID = well_id
        rc.Product = product

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
        setattr(rc, 'RoyaltyGCA', 0.0)
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
