#!/bin/env python3

from datetime import date
from datetime import datetime
import sys
import os
import logging

import config
from src.util.apperror import AppError
from src.util.appdate import prod_month_to_date
from src.database.data_structure import DataStructure
from src.calc.expression import Expression

"""

Big Note: *************
          Putting all this code in one module is very bad programming technique.
          Let me repeat VERY BAD programming technique...

BUT..... Now the justification.....
         Because we are using this code to further our analysis and design, we are
         moving and changing our variable names. It is way easier to work in one file
         for now. Please keep the classes the right size...


This is the royalty calculation class that actually calculates the royalties.
It is a work in progress. Today it uses an SQLite database. This is being done simply
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
        """ """
        self.reference_price = {'Pigeon Lake Indian': 24.04, 'Reserve no.138A': 25.37, 'Sawridge Indian': 25.13,
                                'Stony Plain Indian': 24.64, 'Onion Lake': 25}
        self.db = config.get_database()
        self.expression = Expression()
        """ """

    """
    Process all the royalties that have monthly data
    """

    def process_all(self):
        # errorCount = 0
        for monthlyData in self.db.select('Monthly'):
            try:
                self.process_one(monthlyData.WellID, monthlyData.ProdMonth, monthlyData.Product)

            except AppError as e:
                logging.error(str(e))
            except Exception as e:
                exc_type, exc_obj, exc_tb = sys.exc_info()
                fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
                logging.error(fname + ' ' + str(exc_tb.tb_lineno) + ' ' + str(exc_type) + ' ' + str(e))

                logging.error(sys.exc_info())

    """
    Process a single royalty
    """

    def process_one(self, well_id, prod_month, product):
        # errorCount = 0
        well = self.db.select1('WellRoyaltyMaster', ID=well_id)

        # todo Create a test to ensure there is a RTPInfo for the well. raise an apperror if not
        # todo call the prod_month_to_date in the select and not everytime we use the select.
        # rtp_info_array = self.db.select('RTPInfo', WellEvent=well.WellEvent, Product=product,
        #                                 Date=prod_month_to_date(prod_month))
        # if len(rtp_info_array) == 0:
        #     raise AppError("Well not found in RTPInfo. Well ID: " + str(well_id) + " " + well.WellEvent +
        #                    " Product:" + product)
        #     print('--- Well not found in RTPInfo', well.ID, well.WellEvent)
        # else:
        #     print('--- Well found in RTPInfo Payer:', rtp_info_array[0].Payer)

        monthly_list = self.db.select('Monthly', WellID=well_id, ProdMonth=prod_month, Product=product)
        if len(monthly_list) == 0:
            raise AppError("No monthly data found for WellID: " + str(well_id) + " ProdMonth:" + str(prod_month) +
                           " Product:" + product)

        calc_array = self.db.select('Calc', WellID=well_id, ProdMonth=prod_month, Product=product)
        for calc in calc_array:
            self.db.delete('Calc', calc.ID)

        for monthly in monthly_list:

            well_lease_link_array = self.db.select('WellLeaseLink', WellID=well_id)
            if len(well_lease_link_array) == 0:
                raise AppError("There were no well_lease_link records for Well ID: " + str(well_id) +
                               " Prod Date: " + str(prod_month))

            for well_lease_link in well_lease_link_array:
                logging.info('**** Processing *** {0:06d} {1:06d} {2:04d} {3:}'.
                             format(prod_month, well_id, well_lease_link.LeaseID, product))

                royalty = self.db.select1('LeaseRoyaltymaster', ID=well_lease_link.LeaseID)
                lease = self.db.select1('Lease', ID=well_lease_link.LeaseID)

                calc, calc_specific = self.zero_royalty_calc(prod_month, well_id, product)

                calc.PEFNInterest = well_lease_link.PEFNInterest

                rtp_info = self.db.select1('RTPInfo', WellEvent=well.WellEvent, Product=product, Payer=monthly.RPBA,
                                           Date=prod_month_to_date(prod_month))
                calc.RTPInterest = rtp_info.Percent / 100

                self.calc_royalties(well, royalty, monthly, calc, calc_specific)

                calc.RPBA = monthly.RPBA
                calc.FNReserveID = lease.FNReserveID
                calc.FNBandID = lease.FNBandID
                calc.LeaseID = lease.ID

                self.db.insert(calc)

    def calc_royalties(self, well, royalty, monthly, calc, calc_specific):

        self.determine_royalty_based_on(royalty, monthly, calc)
        calc.SalesPrice = monthly.SalesPrice

        # todo: If there is no sales. Use last months sales value... Not included in this code
        # todo: I think I can get rid of this next line. I do it different now
        self.determine_royalty_price(royalty, monthly, calc, calc_specific)

        self.determine_well_value_for_royalties(royalty, monthly, calc, calc_specific)

        if monthly.Product == 'OIL' and 'SKProvCrownVar' in royalty.RoyaltyScheme:
            self.calc_sask_oil_prov_crown(monthly, well, royalty, calc, calc_specific)

        elif monthly.Product == 'OIL' and 'IOGR1995' in royalty.RoyaltyScheme:
            self.calc_sask_oil_iogr1995(royalty, well.CommencementDate,
                                        monthly, calc, calc_specific)

        elif monthly.Product == 'GAS' and 'IOGR1995' in royalty.RoyaltyScheme:
            self.calc_sask_gas_iogr1995(royalty, monthly, calc, calc_specific)

        elif monthly.Product == 'PEN' and 'IOGR1995' in royalty.RoyaltyScheme:
            self.calc_sask_pen_iogr1995(calc)

        elif monthly.Product == 'SUL' and 'IOGR1995' in royalty.RoyaltyScheme:
            self.calc_sask_sul_iogr1995(calc)

        elif monthly.Product == 'GAS' and 'SKProvCrownVar' in royalty.RoyaltyScheme:
            self.calc_sask_gas_prov_crown(monthly, well, royalty, calc, calc_specific)

        else:
            raise AppError("No calculation for " + str(well.ID) + ' ' + str(monthly.ProdMonth) + ' ' +
                           str(monthly.Product) + ' ' + str(royalty.RoyaltyScheme))

        self.calc_base_net_royalty(calc, calc_specific)

        if 'GORR' in royalty.RoyaltyScheme:
            self.calc_gorr(royalty, monthly, calc, calc_specific)

        calc.RoyaltySpecific = calc_specific.json_dumps()

    @staticmethod
    def determine_royalty_based_on(leaserm, monthly, calc):

        if monthly.Product == "OIL":
            based_on = leaserm.OilRoyaltyBasedOn
        elif monthly.Product == "GAS":
            based_on = leaserm.GasRoyaltyBasedOn
        else:
            based_on = leaserm.ProductsRoyaltyBasedOn

        if based_on == "sales":
            calc.RoyaltyBasedOn = "Sales Vol"
            calc.RoyaltyBasedOnVol = monthly.SalesVol
        elif based_on == "gj":
            calc.RoyaltyBasedOn = "GJs"
            calc.RoyaltyBasedOnVol = monthly.GJ
        else:
            calc.RoyaltyBasedOn = "Prod Vol"
            calc.RoyaltyBasedOnVol = monthly.ProdVol

    # @staticmethod
    def calc_gorr(self, leaserm, monthly, calc, calc_specific):
        """
        For an explanation of the various formats that this can handle please
        see the data dictionary: "General.Gorr"
        """

        calc.GorrMessage = None
        calc.GorrGrossRoyaltyValue = None
        calc_specific.GorrNetRoyaltyMessage = None
        calc.GorrRoyaltyRate = 0.0
        calc_specific.GorrTransValue = 0.0
        calc_specific.GorrGCAValue = 0.0

        if monthly.Product == 'OIL':
            calc.Gorr = leaserm.OilGorr
        elif monthly.Product == 'GAS':
            calc.Gorr = leaserm.GasGorr
        else:
            raise AppError('Can not calculate a GORR for this product: ' + monthly.Product)

        gorr_calc_type, calc.GorrMessage = self.get_gorr_calc_type(monthly, calc.Gorr, calc)

        gross_message_line1 = '$ GORR = '
        gross_message_line2 = gross_message_line1
        gross_message_line3 = gross_message_line1

        if gorr_calc_type[0] == '%':
            calc_specific.GorrValOrPer = '%'
            calc.GorrRoyaltyRate = float(gorr_calc_type[1:])
            calc_specific.GorrBaseRoyalty = round(calc.GorrRoyaltyRate * calc_specific.WellValueForRoyalty, 2)
            calc.GorrMessage += ' for a Royalty Rate of ' + self.fm_percent(calc.GorrRoyaltyRate)
            gross_message_line1 += 'GORR % * Well Value'
            gross_message_line2 += self.fm_percent(calc.GorrRoyaltyRate) + ' * ' + \
                                   self.fm_value(calc_specific.WellValueForRoyalty)

        elif gorr_calc_type[0] == '$':
            calc_specific.GorrValOrPer = '$'
            if gorr_calc_type[1:3] == '=(':
                calc_specific.GorrBaseRoyalty = round(
                    self.expression.evaluate_expression(gorr_calc_type, monthly, calc), 2)
                calc.GorrMessage += ' ' + gorr_calc_type + "; " + \
                                    self.expression.resolve_expression(gorr_calc_type, monthly, calc) + \
                                    "; =" + str(calc_specific.GorrBaseRoyalty) + ';'
            else:
                calc_specific.GorrBaseRoyalty = float(gorr_calc_type[1:])

            gross_message_line1 += 'Base Royalty'
            gross_message_line2 += self.fm_value(calc_specific.GorrBaseRoyalty)

            # Rate may be needed if transportation for GCA is deducted
            calc.GorrRoyaltyRate = round(calc_specific.GorrBaseRoyalty / calc_specific.WellValueForRoyalty, 8)

        gross_message_line1 += ' * PE FN% * RP%;'
        gross_message_line2 += ' * ' + self.fm_percent(calc.PEFNInterest) + ' * ' + \
                               self.fm_percent(calc.RTPInterest) + ';'

        calc.GorrGrossRoyaltyValue = round(calc_specific.GorrBaseRoyalty *
                                                    calc.PEFNInterest *
                                                    calc.RTPInterest, 2)
        gross_message_line3 += self.fm_value(calc.GorrGrossRoyaltyValue)

        calc_specific.GorrRoyaltyGrossMessage = gross_message_line1 + \
                                                gross_message_line2 + \
                                                gross_message_line3

        if monthly.Product == 'OIL':
            calc_specific.GorrTransValue, calc_specific.GorrTransMessage = \
                self.calc_deduction("GORR", "Trans", leaserm.GorrTrans,
                                    'GORR %', calc.GorrRoyaltyRate, calc.GorrGrossRoyaltyValue,
                                    monthly, calc)

        if monthly.Product == 'GAS':
            calc_specific.GorrGCAValue, calc_specific.GorrGCAMessage = \
                self.calc_deduction("GORR", "GCA", leaserm.GorrGCA,
                                    'GORR %', calc.GorrRoyaltyRate, calc.GorrGrossRoyaltyValue,
                                    monthly, calc)

        # Calculate net royalties now
        calc.GorrNetRoyaltyValue = calc.GorrGrossRoyaltyValue

        part1 = 'GORR Net Royalty = GORR Royalty Value'
        part2 = 'GORR Net Royalty = ' + self.fm_value(calc.GorrGrossRoyaltyValue)

        if calc_specific.GorrGCAValue > 0:
            calc.GorrNetRoyaltyValue -= calc_specific.GorrGCAValue
            part1 += ' - GCA'
            part2 += ' - ' + self.fm_value(calc_specific.GorrGCAValue)

        if calc_specific.GorrTransValue > 0:
            calc.GorrNetRoyaltyValue -= calc_specific.GorrTransValue
            part1 += ' - Trans'
            part2 += ' - ' + self.fm_value(calc_specific.GorrTransValue)

        if calc.GorrNetRoyaltyValue == calc.GorrGrossRoyaltyValue:
            calc_specific.GorrNetRoyaltyMessage = ''  # No explanation necessary
        else:
            calc_specific.GorrNetRoyaltyMessage = part1 + ';' + \
                                                  part2 + ';' + \
                                                  'GORR Net Royalty = ' + \
                                                  self.fm_value(calc.GorrNetRoyaltyValue) + ';'

    # @staticmethod
    def get_gorr_calc_type(self, monthly, gorr, calc):
        """ returns the calc type based on the GORR base and an explanation string  """
        if not gorr:
            raise AppError('GORR was expected but none was found.')

        words = gorr.split(",")
        # gorr_percent = 0.0
        gorr_max_vol = 0.0
        last_gorr_max_vol = 0.0
        gorr_explain = ''

        i = 0
        eval_vol = 0
        for s in words:
            i += 1
            if i == 1:
                if s == 'dprod':
                    eval_vol = round(monthly.ProdVol / 30.5, 2)
                    gorr_explain = 'dprod = mprod / 30.5 days; ' + '{:.2f}'.format(eval_vol)
                elif s == 'mprod':
                    eval_vol = monthly.ProdVol
                    gorr_explain = 'mprod = ' + str(eval_vol)
                elif s == 'hprod':
                    eval_vol = round(monthly.ProdVol / monthly.ProdHours, 2)
                    gorr_explain = 'hprod = mprod / hours; ' + '{:.2f}'.format(eval_vol)
                elif s == 'fixed':
                    gorr_explain = 'fixed'
                elif s[:2] == '=(':
                    eval_vol = self.expression.evaluate_expression(s, monthly, calc)
                    gorr_explain = 'Result ' + s + "; " + self.expression.resolve_expression(s, monthly, calc) \
                                   + "; =" + str(eval_vol)
                else:
                    raise AppError('GORR Base is not known: ' + s)
            elif i % 2 == 0:
                last_gorr_max_vol = gorr_max_vol
                gorr_max_vol = float(s)
            else:
                if eval_vol == 0:
                    return s, gorr_explain + ';'
                elif gorr_max_vol == 0:
                    gorr_explain += ' is > ' + str(last_gorr_max_vol)
                    return s, gorr_explain + ';'
                elif eval_vol <= gorr_max_vol:
                    if last_gorr_max_vol == 0:
                        gorr_explain += ' is <= ' + str(gorr_max_vol) + ';'
                    else:
                        gorr_explain += ' is > ' + str(last_gorr_max_vol) + ' and <= ' + str(gorr_max_vol) + ';'
                    return s, gorr_explain
        raise AppError('GORR Logic Error. We should never ever get here: ')

    @staticmethod
    def calc_sask_oil_prov_crown_royalty_rate(calc, econ_oil_data,
                                              well_royalty_classification, well_classification, mop, src):

        if well_royalty_classification == 'Fourth Tier':

            if mop < 25:
                calc.BaseRoyaltyCalcRate = 0
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
                    raise AppError(
                        'Royalty Classification: "' + well_royalty_classification + ' not known for ' +
                        well_classification + ' Royalty not calculated.')
                calc.BaseRoyaltyCalcRate = ((calc.C * mop) - calc.D) / 100

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
                    raise AppError(
                        'Royalty Classification: ' + well_royalty_classification + ' not known for ' +
                        well_classification + ' Royalty not calculated.')
                calc.BaseRoyaltyCalcRate = (calc.K - (calc.X / mop)) / 100
        else:
            if well_classification == 'Heavy':
                if well_royalty_classification == 'Third Tier':
                    calc.K = econ_oil_data.H3T_K
                    calc.X = econ_oil_data.H3T_X
                elif well_royalty_classification == 'New':
                    calc.K = econ_oil_data.HNEW_K
                    calc.X = econ_oil_data.HNEW_X
                else:
                    raise AppError(
                        'Royalty Classification: ' + well_royalty_classification + ' not known for ' +
                        well_classification + ' Royalty not calculated.')
            elif well_classification == 'Southwest':
                if well_royalty_classification == 'Third Tier':
                    calc.K = econ_oil_data.SW3T_K
                    calc.X = econ_oil_data.SW3T_X
                elif well_royalty_classification == 'New':
                    calc.K = econ_oil_data.SWNEW_K
                    calc.X = econ_oil_data.SWNEW_X
                else:
                    raise AppError(
                        'Royalty Classification: "' + well_royalty_classification + '" not known for ' +
                        well_classification + ' Royalty not calculated.')
            elif well_classification == 'Other':
                if well_royalty_classification == 'Third Tier':
                    calc.K = econ_oil_data.O3T_K
                    calc.X = econ_oil_data.O3T_X
                elif well_royalty_classification == 'New':
                    calc.K = econ_oil_data.ONEW_K
                    calc.X = econ_oil_data.ONEW_X
                elif well_royalty_classification == 'Old':
                    calc.K = econ_oil_data.OOLD_K
                    calc.X = econ_oil_data.OOLD_X
                else:
                    raise AppError(
                        'Royalty Classification: "' + well_royalty_classification + '" not known for ' +
                        well_classification + ' Royalty not calculated.')
            else:
                raise AppError('Product Classification: "' + str(well_classification) +
                               '" not known. Royalty not calculated.')

            if mop == 0:
                calc.BaseRoyaltyCalcRate = 0
            else:
                calc.BaseRoyaltyCalcRate = ((calc.K - (calc.X / mop)) / 100) - src

        calc.BaseRoyaltyCalcRate = round(calc.BaseRoyaltyCalcRate, 8)

        return calc.BaseRoyaltyCalcRate

    @staticmethod
    def calc_sask_prov_crown_royalty_volume_value(m, lease_rm, calc, calc_specific):

        calc.BaseRoyaltyRate = calc.BaseRoyaltyCalcRate
        calc_specific.BaseRoyaltyRateDesc = 'CR %'  # SKProvCrownVar calculates an actual Royalty Rate
        calc_specific.CrownMultiplier = lease_rm.CrownMultiplier
        if not calc_specific.CrownMultiplier:
            calc_specific.CrownMultiplier = 1.0

        if calc.BaseRoyaltyRate < 0:
            calc.BaseRoyaltyRate = 0

        if lease_rm.CrownModifier:
            calc.BaseRoyaltyRate += lease_rm.CrownModifier

        if lease_rm.MinRoyaltyRate:
            if lease_rm.MinRoyaltyRate > calc.BaseRoyaltyRate:
                calc.BaseRoyaltyRate = lease_rm.MinRoyaltyRate

        calc.BaseRoyaltyValue = round(calc.BaseRoyaltyRate *
                                      calc_specific.CrownMultiplier *
                                      calc.PEFNInterest *
                                      calc.RTPInterest *
                                      calc_specific.WellValueForRoyalty, 2)

        if lease_rm.MinRoyaltyDollar:
            if lease_rm.MinRoyaltyDollar > calc.BaseRoyaltyValue:
                calc.BaseRoyaltyValue = lease_rm.MinRoyaltyDollar

    def calc_sask_gas_iogr1995(self, lease_rm, monthly, calc, calc_specific):
        """
        1. Royalty Payable = Gross Royalty - (Gross Royalty / Total Value)
        2. Gross Royalty = Basic Gross Royalty + Supplementary Gross Royalty
        3. Basic Gross Royalty = 25% * Gas Volume * Selling Price
        4. Supplementary Gross Royalty = 75% *
            a. Gas: if Selling Price < $10.65: 0
                    if $10.65 > Selling Price < $24.85: 30% * (Selling Price - $10.65)
                    if Selling Price > $24.85: $4.26 + 55% * (Selling Price - $24.85)
            b. Pentanes
            c. Sulphur
            d. Other from gas source
            e. Other from non-gas source
        """
        # New Way basic
        calc.IogrBaseRoyaltyValue = round(0.25 * calc.RoyaltyBasedOnVol * calc.RoyaltyPrice, 2)
        calc_specific.BaseRoyaltyMessage = 'R$ = 0.25 * ' + calc.RoyaltyBasedOn + ' * Price;' + \
            'R$ = 0.25 * ' + self.fm_vol(calc.RoyaltyBasedOnVol) + ' * ' \
                                           + self.fm_rate(calc.RoyaltyPrice) + ';' + \
            'R$ = ' + self.fm_value(calc.IogrBaseRoyaltyValue) + ';'




            # basic
        # basic_gross_royalty = 0.25 * calc.RoyaltyBasedOnVol * calc.SalesPrice

        # supplemental
        if calc.RoyaltyPrice <= 10.65:
            calc.IogrSuppRoyaltyValue = 0
            calc_specific.BaseRoyaltyMessage += ';price < $10.65;' + \
                                                'S = $0.00;'
        elif calc.RoyaltyPrice <= 24.85:
            calc.IogrSuppRoyaltyValue = round(0.75 * calc.RoyaltyBasedOnVol * 0.3 * (calc.RoyaltyPrice - 10.65), 2)
            calc_specific.BaseRoyaltyMessage += ';price <= $10.65);' \
                                                'S = (0.75 * ' + calc.RoyaltyBasedOn + ' * 30% * (price  - $10.65);' + \
                                                'S = (0.75 * ' + self.fm_vol(calc.RoyaltyBasedOnVol) + ' * 30% * (' + \
                                                self.fm_rate(calc.RoyaltyPrice) + ' - $10.65);' + \
                                                'S = ' + self.fm_value(calc.IogrSuppRoyaltyValue) + ';'
        else:
            calc.IogrSuppRoyaltyValue = round(0.75 * calc.RoyaltyBasedOnVol *
                                              (4.26 + 0.55 * (calc.RoyaltyPrice - 24.85)), 2)
            calc_specific.BaseRoyaltyMessage += ';price > $10.65);' \
                                                'S = (0.75 * ' + calc.RoyaltyBasedOn + ' * (4.26 + 0.55 * (price  - $24.85));' + \
                                                'S = (0.75 * ' + self.fm_vol(calc.RoyaltyBasedOnVol) + ' * (4.26 + 0.55 * (' + self.fm_rate(calc.RoyaltyPrice)  + ' - $24.85));' + \
                                                'S = ' + self.fm_value(calc.IogrSuppRoyaltyValue) + ';'

        calc.BaseRoyaltyValue = round((calc.IogrBaseRoyaltyValue + calc.IogrSuppRoyaltyValue) *
                                      calc.PEFNInterest * calc.RTPInterest, 2)

        calc_specific.BaseRoyaltyMessage += ';Royalty = (R$ + S$) * PE FN %	* RP %;' + \
                                            'Royalty = (' + self.fm_value(calc.IogrBaseRoyaltyValue) + \
                                            ' + ' + self.fm_value(calc.IogrSuppRoyaltyValue) + ') * ' + \
                                            self.fm_percent(calc.PEFNInterest) + ' * ' + \
                                            self.fm_percent(calc.RTPInterest) + ';' + \
                                            'Royalty = ' + self.fm_value(calc.BaseRoyaltyValue) + ';'

        calc.BaseRoyaltyRate = round((calc.IogrBaseRoyaltyValue + calc.IogrSuppRoyaltyValue) /
                                     (calc.RoyaltyBasedOnVol * calc.RoyaltyPrice), 8)

        calc.BaseGCAValue, calc_specific.BaseGCAMessage = \
            self.calc_deduction("Base", "GCA", lease_rm.BaseGCA, 'Effective CR %', calc.BaseRoyaltyRate, calc.BaseRoyaltyValue,
                                monthly, calc)

        # calc.IogrSuppRoyaltyValue = round(supplementary_royalty * calc.RTPInterest * calc.PEFNInterest, 2)
        # calc.IogrBaseRoyaltyValue = round(basic_gross_royalty * calc.RTPInterest * calc.PEFNInterest, 2)

        return

    @staticmethod
    def calc_sask_pen_iogr1995(calc):
        # print('processing !!PEN!!')
        """
        1. Royalty Payable = Gross Royalty - (Gross Royalty / Total Value)
        2. Gross Royalty = Basic Gross Royalty + Supplementary Gross Royalty
        3. Basic Gross Royalty = 25% * Gas Volume * Selling Price
        4. Supplementary Gross Royalty = 75% *
            a. Gas: if Selling Price < $10.65: 0
                    if $10.65 > Selling Price < $24.85: 30% * (Selling Price - $10.65)
                    if Selling Price > $24.85: $4.26 + 55% * (Selling Price - $24.85)
            b. Pentanes
            c. Sulphur
            d. Other from gas source
            e. Other from non-gas source
        """

        basic_gross_royalty = 0.25 * calc.RoyaltyBasedOnVol * calc.SalesPrice
        supplementary_royalty = 0
        if calc.SalesPrice > 27.68:
            supplementary_royalty = 0.75 * 0.5 * (calc.SalesPrice - 27.68)

        calc.IogrSuppRoyaltyValue = round(supplementary_royalty, 2)
        calc.IogrBaseRoyaltyValue = round(basic_gross_royalty, 2)
        return

    @staticmethod
    def calc_sask_sul_iogr1995(calc):
        # print('processing !!SUL!!')
        """
        1. Royalty Payable = Gross Royalty - (Gross Royalty / Total Value)
        2. Gross Royalty = Basic Gross Royalty + Supplementary Gross Royalty
        3. Basic Gross Royalty = 25% * Gas Volume * Selling Price
        4. Supplementary Gross Royalty = 75% *
            a. Gas: if Selling Price < $10.65: 0
                    if $10.65 > Selling Price < $24.85: 30% * (Selling Price - $10.65)
                    if Selling Price > $24.85: $4.26 + 55% * (Selling Price - $24.85)
            b. Pentanes
            c. Sulphur
            d. Other from gas source
            e. Other from non-gas source
        """

        basic_gross_royalty = 0.25 * calc.RoyaltyBasedOnVol * calc.SalesPrice
        supplementary_royalty = 0
        if calc.SalesPrice > 39.37:
            supplementary_royalty = 0.75 * 0.5 * (calc.SalesPrice - 39.37)

        calc.IogrSuppRoyaltyValue = round(supplementary_royalty, 2)
        calc.IogrBaseRoyaltyValue = round(basic_gross_royalty, 2)
        return

    def calc_sask_oil_iogr1995(self, royalty, commencement_date,
                               monthly, calc, calc_specific):

        """
        Calculated Based on regulations described:
        http://laws-lois.justice.gc.ca/eng/regulations/sor-94-753/page-8.html#h-35
        """
        # Calculate the Commencement Period
        calc.CommencementPeriod = self.determine_commencement_period(monthly.ProdMonth, commencement_date)
        if calc.CommencementPeriod <= 5:
            self.calc_sask_oil_iogr_subsection2(calc, calc_specific)
        else:
            self.calc_sask_oil_iogr_subsection3(calc, calc_specific)

        calc.IogrBaseRoyaltyValue = round(calc.BaseRoyaltyVolume *
                                          calc.RoyaltyPrice, 2)

        calc_specific.BaseRoyaltyMessage += ';R$ = RVol * RVal;' + \
            'R$ = ' + self.fm_vol(calc.BaseRoyaltyVolume) + ' * ' \
                    + self.fm_rate(calc.RoyaltyPrice) + ';'\
            'R$ = ' + self.fm_value(calc.IogrBaseRoyaltyValue) + ';'

        calc.IogrSuppRoyaltyValue = round(
            self.calc_supplementary_royalties_iogr1995(calc.CommencementPeriod,
                                                       monthly.SalesPrice,
                                                       calc.RoyaltyBasedOnVol,
                                                       calc.BaseRoyaltyVolume,
                                                       self.reference_price['Onion Lake'],
                                                       calc_specific), 2)

        calc.BaseRoyaltyValue = round((calc.IogrBaseRoyaltyValue + calc.IogrSuppRoyaltyValue) *
                                      calc.PEFNInterest * calc.RTPInterest, 2)

        calc_specific.BaseRoyaltyMessage += ';Royalty = (R$ + S$) * PE FN %	* RP %;' + \
                                            'Royalty = (' + self.fm_value(calc.IogrBaseRoyaltyValue) + \
                                            ' + ' + self.fm_value(calc.IogrSuppRoyaltyValue) + ') * ' + \
                                            self.fm_percent(calc.PEFNInterest) + ' * ' + \
                                            self.fm_percent(calc.RTPInterest) + ';' + \
                                            'Royalty = ' + self.fm_value(calc.BaseRoyaltyValue) + ';'

        calc.BaseRoyaltyRate = round((calc.IogrBaseRoyaltyValue + calc.IogrSuppRoyaltyValue) /
                                     (calc.RoyaltyBasedOnVol * monthly.SalesPrice), 8)

        calc.BaseTransValue, calc_specific.BaseTransMessage = \
            self.calc_deduction("Base", "Trans", royalty.BaseTrans,
                                'Effective CR %', calc.BaseRoyaltyRate, calc.BaseRoyaltyValue,
                                monthly, calc)

        return

    # @staticmethod
    def calc_sask_oil_iogr_subsection2(self, calc, calc_specific):
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
        # todo Crap just noticed that RoyaltyBasedOnVol may not be MOP it should also handle sales. Bad Larry.
        if calc.RoyaltyBasedOnVol < 80.0:
            calc.BaseRoyaltyVolume = calc.RoyaltyBasedOnVol * .1
            calc_specific.BaseRoyaltyMessage = 'MOP < 80: RVol = 10% * MOP;' +\
                                               'RVol = 10% * ' + self.fm_vol(calc.RoyaltyBasedOnVol) + ';' +\
                                               'RVol = ' + self.fm_vol(calc.BaseRoyaltyVolume) + ';'
        elif calc.RoyaltyBasedOnVol <= 160.0:
            calc.BaseRoyaltyVolume = 8 + (calc.RoyaltyBasedOnVol - 80) * .2
            calc_specific.BaseRoyaltyMessage = 'MOP 80 to 160: RVol = 8 + (MOP - 80) * 20%;' + \
                'RVol = 8 + (' + self.fm_vol(calc.RoyaltyBasedOnVol) + ' - 80) * 20%;' + \
                'RVol = ' + self.fm_vol(calc.BaseRoyaltyVolume) + ';'
        else:
            calc.BaseRoyaltyVolume = 24 + (calc.RoyaltyBasedOnVol - 160) * .26
            calc_specific.BaseRoyaltyMessage = 'MOP > 160: RVol = 24 + (MOP - 160) * 26%;' + \
                'RVol = 24 + (' + self.fm_vol(calc.RoyaltyBasedOnVol) + ' - 160) * 26%;' + \
                'RVol = ' + self.fm_vol(calc.BaseRoyaltyVolume) + ';'

        calc.BaseRoyaltyVolume = round(calc.BaseRoyaltyVolume, 6)

        return

    # @staticmethod
    def calc_sask_oil_iogr_subsection3(self, calc, calc_specific):
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
        if calc.RoyaltyBasedOnVol < 80.0:
            calc.BaseRoyaltyVolume = calc.RoyaltyBasedOnVol * .1
            calc_specific.BaseRoyaltyMessage = 'MOP < 80: RVol = 10% * MOP;' +\
                                               'RVol = 10% * ' + self.fm_vol(calc.RoyaltyBasedOnVol) + ';' +\
                                               'RVol = ' + self.fm_vol(calc.BaseRoyaltyVolume) + ';'
        elif calc.RoyaltyBasedOnVol <= 160.0:
            calc.BaseRoyaltyVolume = 8 + (calc.RoyaltyBasedOnVol - 80) * .2
            calc_specific.BaseRoyaltyMessage = 'MOP 80 to 160: RVol = 8 + (MOP - 80) * 20%;' +\
                                               'RVol = 8 + (' + self.fm_vol(calc.RoyaltyBasedOnVol) + ' - 80) * 20%;' +\
                                               'RVol = ' + self.fm_vol(calc.BaseRoyaltyVolume) + ';'
        elif calc.RoyaltyBasedOnVol <= 795.0:
            calc.BaseRoyaltyVolume = 24 + (calc.RoyaltyBasedOnVol - 160) * .26
            calc_specific.BaseRoyaltyMessage = 'MOP 160 to 795: RVol = 24 + (MOP - 160) * 26%;' +\
                                               'RVol = 24 + (' + self.fm_vol(calc.RoyaltyBasedOnVol) + ' - 160) * 26%;' +\
                                               'RVol = ' + self.fm_vol(calc.BaseRoyaltyVolume) + ';'
        else:
            calc.BaseRoyaltyVolume = 189 + (calc.RoyaltyBasedOnVol - 795) * .4
            calc_specific.BaseRoyaltyMessage = 'MOP > 795: RVol = 189 + (MOP - 795) * 40%;' +\
                                               'RVol = 189 + (' + self.fm_vol(calc.RoyaltyBasedOnVol) + ' - 795) * 40%;' +\
                                               'RVol = ' + self.fm_vol(calc.BaseRoyaltyVolume) + ';'

        calc.BaseRoyaltyVolume = round(calc.BaseRoyaltyVolume, 6)

        return

    # @staticmethod
    def calc_supplementary_royalties_iogr1995(self, commencement_period, well_head_price, prod_vol, royalty_regulation,
                                              reference_price, calc_specific):
        if commencement_period <= 5:
            supplementary_royalty = round((prod_vol - royalty_regulation) * 0.5 * (well_head_price - reference_price), 2)
            calc_specific.BaseRoyaltyMessage += ';S = (T - B) * 0.50 * (P - R);' + \
                                                'S = (' + self.fm_vol(prod_vol) + ' - ' + self.fm_vol(royalty_regulation) + \
                                                ') * 0.5 * (' + self.fm_rate(well_head_price) + ' - ' + str(reference_price) + ');' + \
                                                'S = ' + self.fm_value(supplementary_royalty) + ';'

        else:
            supplementary_royalty = round((prod_vol - royalty_regulation) *
                                    (0.75 * (well_head_price - reference_price - 12.58) + 6.29), 2)
            calc_specific.BaseRoyaltyMessage += ';S = (T - B) * (0.75 * (P - R - $12.58) + $6.29);' + \
                                                'S = (' + self.fm_vol(prod_vol) + ' - ' + self.fm_vol(royalty_regulation) + \
                                                ') * 0.75 * (' + self.fm_rate(well_head_price) + ' - ' + str(reference_price) + '-12.58) + 6.29);' + \
                                                'S = ' + self.fm_value(supplementary_royalty) + ';'

        return supplementary_royalty

    def determine_royalty_price(self, lease_rm, monthly, calc, calc_specific):

        if monthly.Product == 'OIL':
            calc_specific.PriceBasedOn = lease_rm.OilPriceBasedOn
        elif monthly.Product == 'GAS':
            calc_specific.PriceBasedOn = lease_rm.GasPriceBasedOn
        else:
            calc_specific.PriceBasedOn = lease_rm.ProductsPriceBasedOn

        if calc_specific.PriceBasedOn and calc_specific.PriceBasedOn[:2] == '=(':
            value = round(self.expression.evaluate_expression(calc_specific.PriceBasedOn, monthly), 2)
            explanation = 'Formula ' + calc_specific.PriceBasedOn + " " + \
                          self.expression.resolve_expression(calc_specific.PriceBasedOn, monthly) \
                          + " =" + str(value)
        else:
            value = monthly.SalesPrice
            explanation = None

        calc.RoyaltyPrice = value
        calc.RoyaltyPriceExplanation = explanation

    def determine_well_value_for_royalties(self, lease_rm, monthly, calc, calc_specific):

        if monthly.Product == 'OIL':
            calc_specific.ValueBasedOn = lease_rm.OilValueBasedOn
        elif monthly.Product == 'GAS':
            calc_specific.ValueBasedOn = lease_rm.GasValueBasedOn
        else:
            calc_specific.ValueBasedOn = lease_rm.ProductsValueBasedOn

        if calc_specific.ValueBasedOn:
            if not calc_specific.ValueBasedOn[0:2] == '=(':
                raise AppError('Value based on must be a formula starting with "=(" but found: ' + calc_specific.ValueBasedOn)
            value = round(self.expression.evaluate_expression(calc_specific.ValueBasedOn, monthly), 2)
            explanation = 'Well Value ' + calc_specific.ValueBasedOn + "; Well Value " + \
                          self.expression.resolve_expression(calc_specific.ValueBasedOn, monthly) \
                          + "; Well Value = " + self.fm_value(value) + ';'
        else:
            value = round(monthly.SalesPrice * monthly.SalesVol, 2)
            calc_specific.ValueBasedOn = 'Sales'
            explanation = 'Well Value = Sales Vol * Price;' + \
                          'Well Value = ' + self.fm_vol(monthly.SalesVol) + " * " + self.fm_rate(monthly.SalesPrice) + \
                          '; Well Value = ' + self.fm_value(value) + ';'

        calc_specific.WellValueForRoyalty = value
        calc_specific.WellValueForRoyaltyExplanation = explanation

    @staticmethod
    def ensure_date(d):
        if isinstance(d, datetime):
            return date(d.year, d.month, d.day)
        return d

    def determine_commencement_period(self, prod_month, commencement_date):
        if commencement_date is None:
            return 5

        else:
            cd = self.ensure_date(commencement_date)
            year = int(prod_month / 100)
            month = prod_month - (year * 100)
            prod_date = date(year, month, 1)
            diff = prod_date - cd
            return round(diff.days / 365, 2)

    '''
    Sask Oil Royalty Calculation

    These calculations are fully documented in two documents included in this project
    under the Sask Folder:
      Factor Circulars.pdf
      OilFactors.pdf
    '''

    def calc_sask_oil_prov_crown(self, monthly, well, royalty, calc, calc_specific):
        # calc.CommencementPeriod = self.determine_commencement_period(monthly.ProdMonth, well.CommencementDate)
        econ_oil_data = self.db.select1("ECONOil", ProdMonth=monthly.ProdMonth)

        if royalty.OverrideRoyaltyClassification is not None:
            calc.RoyaltyClassification = royalty.OverrideRoyaltyClassification
        else:
            calc.RoyaltyClassification = well.RoyaltyClassification

        # This seems like a duplicate but on the Worksheet we need these symbols for this royalty type
        if royalty.OilRoyaltyBasedOn == "sales":
            calc_specific.SaskProvBasedOn = "Sales"
        else:
            calc_specific.SaskProvBasedOn = "MOP"

        self.calc_sask_oil_prov_crown_royalty_rate(calc, econ_oil_data, calc.RoyaltyClassification,
                                                   well.Classification, calc.RoyaltyBasedOnVol, well.SRC)

        self.calc_sask_prov_crown_royalty_volume_value(monthly,
                                                       royalty,
                                                       calc,
                                                       calc_specific)

        calc.BaseTransValue, calc_specific.BaseTransMessage = \
            self.calc_deduction("Base", "Trans", royalty.BaseTrans, 'CR %', calc.BaseRoyaltyRate, calc.BaseRoyaltyValue,
                                monthly, calc)

    def calc_sask_gas_prov_crown(self, monthly, well, royalty, calc, calc_specific):

        if royalty.OverrideRoyaltyClassification is not None:
            calc.RoyaltyClassification = royalty.OverrideRoyaltyClassification
        else:
            calc.RoyaltyClassification = well.RoyaltyClassification
        # calc.CommencementPeriod = self.determine_commencement_period(monthly.ProdMonth, well.CommencementDate)
        econ_gas_data = self.db.select1("ECONGas", ProdMonth=monthly.ProdMonth)
        if royalty.OverrideRoyaltyClassification:
            royalty_classification = royalty.OverrideRoyaltyClassification
        else:
            royalty_classification = well.RoyaltyClassification

        # This seems like a duplicate but on the Worksheet we need these symbols for this royalty type
        if royalty.GasRoyaltyBasedOn == "sales":
            calc_specific.SaskProvBasedOn = "Sales"
        elif royalty.GasRoyaltyBasedOn == "gj":
                calc_specific.SaskProvBasedOn = "GJ"
        else:
            calc_specific.SaskProvBasedOn = "MGP"

        self.calc_sask_gas_prov_crown_royalty_rate(calc, econ_gas_data, royalty_classification, calc.RoyaltyBasedOnVol,
                                                   well.SRC, well.WellType)

        self.calc_sask_prov_crown_royalty_volume_value(monthly,
                                                       royalty,
                                                       calc,
                                                       calc_specific)

        calc.BaseGCAValue, calc_specific.BaseGCAMessage = \
            self.calc_deduction("Base", "GCA", royalty.BaseGCA, 'CR %', calc.BaseRoyaltyRate, calc.BaseRoyaltyValue,
                                monthly, calc)

    @staticmethod
    def calc_sask_gas_prov_crown_royalty_rate(calc, econ_gas_data,
                                              well_royalty_classification, mgp, src, well_type):

        if well_royalty_classification == 'Fourth Tier':
            if well_type == 'Gas':
                if mgp <= 25:
                    calc.BaseRoyaltyCalcRate = 0
                    calc.Message = 'MOP <= 25 - RR = 0.'
                elif mgp <= 115.4:
                    calc.C = econ_gas_data.G4T_C
                    calc.D = econ_gas_data.G4T_D
                    calc.BaseRoyaltyCalcRate = (calc.C * mgp) - calc.D
                else:
                    calc.K = econ_gas_data.G4T_K
                    calc.X = econ_gas_data.G4T_X
                    calc.BaseRoyaltyCalcRate = calc.K - (calc.X / mgp)

            elif well_type == 'Oil':
                if mgp <= 64.7:
                    calc.BaseRoyaltyCalcRate = 0
                    calc.Message = 'MOP <= 64.7 - RR = 0.'
                else:
                    calc.K = econ_gas_data.G4T_K
                    calc.X = econ_gas_data.G4T_X
                    calc.BaseRoyaltyCalcRate = calc.K - (calc.X / mgp)

            else:
                raise AppError(
                    'Well Type: "' + well_type + '" not known for "' + well_royalty_classification +
                    '" Royalty not calculated.')

        elif well_royalty_classification == 'Third Tier':
            if mgp < 115.4:
                calc.C = econ_gas_data.G3T_C
                # SRC ?? - ProdDate
                calc.BaseRoyaltyCalcRate = (calc.C * mgp) - src

            else:
                calc.K = econ_gas_data.G3T_K
                calc.X = econ_gas_data.G3T_X
                # SRC ?? - ProdDate
                calc.BaseRoyaltyCalcRate = calc.K - (calc.X / mgp) - src

        elif well_royalty_classification == 'New':
            if mgp < 115.4:
                calc.C = econ_gas_data.GNEW_C
                calc.BaseRoyaltyCalcRate = (calc.C * mgp) - src
                # SRC ?? - ProdDate
            else:
                calc.K = econ_gas_data.GNEW_K
                calc.X = econ_gas_data.GNEW_X
                # SRC ?? - ProdDate
                calc.BaseRoyaltyCalcRate = calc.K - (calc.X / mgp) - src

        elif well_royalty_classification == 'Old':
            if mgp < 115.4:
                calc.C = econ_gas_data.GOLD_C
                calc.BaseRoyaltyCalcRate = (calc.C * mgp) - src
                # SRC ?? - ProdDate
            else:
                calc.K = econ_gas_data.GOLD_K
                calc.X = econ_gas_data.GOLD_X
                # SRC ?? - ProdDate
                calc.BaseRoyaltyCalcRate = calc.K - (calc.X / mgp) - src

        else:
            raise AppError(
                'Royalty Classification: "' + well_royalty_classification + '" not known for "' + well_type +
                '" Royalty not calculated.')

        calc.BaseRoyaltyCalcRate = round(calc.BaseRoyaltyCalcRate / 100, 8)
        return calc.BaseRoyaltyCalcRate

    def calc_base_net_royalty(self, calc, calc_specific):
        calc.BaseNetRoyaltyValue = calc.BaseRoyaltyValue

        part1 = 'Base Net Royalty = Base Royalty Value'
        part2 = 'Base Net Royalty = ' + self.fm_value(calc.BaseNetRoyaltyValue)

        if calc.BaseGCAValue > 0:
            calc.BaseNetRoyaltyValue -= calc.BaseGCAValue
            part1 += ' - GCA'
            part2 += ' - ' + self.fm_value(calc.BaseGCAValue)

        if calc.BaseTransValue > 0:
            calc.BaseNetRoyaltyValue -= calc.BaseTransValue
            part1 += ' - Trans'
            part2 += ' - ' + self.fm_value(calc.BaseTransValue)

        if calc.BaseNetRoyaltyValue == calc.BaseRoyaltyValue:
            calc_specific.BaseNetRoyaltyMessage = ''  # No explanation necessary
        else:
            calc_specific.BaseNetRoyaltyMessage = part1 + ';' + \
                                            part2 + ';' + \
                                            'Base Net Royalty = ' + \
                                            self.fm_value(calc.BaseNetRoyaltyValue) + ';'

    def calc_deduction(self, what, deduction, option, rr_desc, rr, gross_royalty, monthly, calc):

        if not option or option.strip() == '':
            return 0.0, ''

        result_msg = what + ' ' + deduction + ' = '

        msg_1 = result_msg
        msg_2 = result_msg

        options = option.split(',')

        if options[0] == 'sales':
            vol = monthly.SalesVol
            msg_1 += 'Sales Vol'
        elif options[0] == 'prod':
            vol = monthly.ProdVol
            msg_1 += 'Prod Vol'
        else:
            raise AppError(what + ' ' + deduction + ' can not be calculated: ' + '"' + option + '" not understood.')

        # Check to see if the rate is in the option

        msg_1 += ' * ' + deduction + ' Rate'

        rate = 0.0
        if len(options) > 1:
            rate = float(options[1])
        elif deduction == 'GCA':
            rate = monthly.GCARate
        elif deduction == 'Trans':
            rate = monthly.TransRate
        else:
            raise AppError(what + ' ' + deduction + ' can not be calculated: ' + '"' + deduction + '" not understood.')

        if not rate:
            rate = 0
            # raise AppError(what + ' ' + deduction + ' can not be calculated: Rate can not be found.')

        msg_2 += self.fm_vol(vol) + ' * ' + self.fm_rate(rate)

        msg_1 += ' * ' + rr_desc
        msg_2 += ' * ' + self.fm_percent(rr)

        msg_1 += ' * PE FN%'
        msg_2 += ' * ' + self.fm_percent(calc.PEFNInterest)

        msg_1 += ' * RP %'
        msg_2 += ' * ' + self.fm_percent(calc.RTPInterest)

        value = round(vol *
                      rate *
                      rr *
                      calc.PEFNInterest *
                      calc.RTPInterest, 2)

        msg = msg_1 + ';' + msg_2 + ';' + result_msg + self.fm_value(value) + ';'

        gca_msg = ''
        if deduction == 'GCA':
            max_gca = round(gross_royalty * .5, 2)

            if value > max_gca:
                gca_msg += 'GCA > 50% of Royalty therefore GCA = ' + self.fm_value(max_gca) + ';'
                msg = msg_1 + ';' + msg_2 + ';' + result_msg + self.fm_value(value) + ';' + gca_msg
                value = max_gca

        return value, msg

    @staticmethod
    def fm_value(num):
        return '${:0,.2f}'.format(num)

    @staticmethod
    def fm_percent(num):
        return '{:0,.6%}'.format(num)

    @staticmethod
    def fm_rate(num):
        return '{:0,.6f}'.format(num)

    @staticmethod
    def fm_vol(num):
        return '{:0,.2f}'.format(num)

    def zero_royalty_calc(self, month, well_id, product, rc=None):
        if rc is None:
            rc = self.db.get_data_structure('Calc')
            #         rc.ID = 0
        rc.ProdMonth = month
        rc.WellID = well_id
        rc.Product = product

        setattr(rc, 'RTPInterest', 0.0)
        setattr(rc, 'PEFNInterest', 0.0)

        setattr(rc, 'K', 0.0)
        setattr(rc, 'X', 0.0)
        setattr(rc, 'C', 0.0)
        setattr(rc, 'D', 0.0)

        setattr(rc, 'RoyaltyPrice', 0.0)
        setattr(rc, 'RoyaltyVolume', 0.0)

        setattr(rc, 'BaseRoyaltyCalcRate', 0.0)
        setattr(rc, 'BaseRoyaltyRate', 0.0)
        setattr(rc, 'GorrRoyaltyRate', 0.0)

        setattr(rc, 'BaseRoyaltyVolume', 0.0)

        setattr(rc, 'BaseRoyaltyValue', 0.0)
        setattr(rc, 'BaseNetRoyaltyValue', 0.0)
        setattr(rc, 'BaseGCAValue', 0.0)
        setattr(rc, 'IogrBaseRoyaltyValue', 0.0)
        setattr(rc, 'IogrSuppRoyaltyValue', 0.0)
        setattr(rc, 'GorrNetRoyaltyValue', 0.0)
        setattr(rc, 'GorrGrossRoyaltyValue', 0.0)

        setattr(rc, 'BaseTransValue', 0.0)
        setattr(rc, 'GorrTransValue', 0.0)
        setattr(rc, 'ProcessingBaseValue', 0.0)
        setattr(rc, 'ProcessingGorrValue', 0.0)

        setattr(rc, 'RoyaltyGCA', 0.0)

        setattr(rc, 'CommencementPeriod', None)
        setattr(rc, 'Message', None)
        setattr(rc, 'GorrMessage', None)

        calc_specific = DataStructure()

        return rc, calc_specific

# Note: to run the royalties in batch use batch.py
