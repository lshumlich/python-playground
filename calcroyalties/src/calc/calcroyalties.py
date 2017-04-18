#!/bin/env python3

from datetime import date
from datetime import datetime
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

    """
    Process a single royalty
    """

    def process_one(self, well_id, prod_month, product):
        logging.info('**** Processing *** {0:6d} {1:6d} {2:}'.format(well_id, prod_month, product))
        # errorCount = 0
        well = self.db.select1('WellRoyaltyMaster', ID=well_id)
        well_lease_link_array = self.db.select('WellLeaseLink', WellID=well_id)
        if len(well_lease_link_array) == 0:
            raise AppError("There were no well_lease_link records for Well ID: " + str(well_id) +
                           " Prod Date: " + str(prod_month))
        well_lease_link = well_lease_link_array[0]
        royalty = self.db.select1('LeaseRoyaltymaster', ID=well_lease_link.LeaseID)
        lease = self.db.select1('Lease', ID=well_lease_link.LeaseID)

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
            self.calc_sask_gas_iogr1995(calc)

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

        # if monthly.Product == 'OIL' and 'GORR' in royalty.RoyaltyScheme:
        if 'GORR' in royalty.RoyaltyScheme:
            self.calc_gorr(royalty, monthly, calc, calc_specific)

        # todo replace this, i don't think we want to mix base and gorr royalties together

        # calc.GrossRoyaltyValue = calc.BaseRoyaltyValue + calc.SuppRoyaltyValue + calc.GorrRoyaltyValue
        # calc.NetRoyaltyValue = calc.GrossRoyaltyValue - calc.TransBaseValue - calc.TransGorrValue

        # calc.RoyaltyVolume = (calc.BaseRoyaltyVolume +
        #                       calc.GorrRoyaltyVolume)

        # if royalty.TruckingDeducted == 'Y':
        #     calc.RoyaltyTransportation = round(calc.RoyaltyVolume * monthly.TransRate, 2)
        #     calc.RoyaltyDeductions += calc.RoyaltyTransportation
        #     calc.NetRoyaltyValue -= calc.RoyaltyTransportation

        # if (royalty.TruckingOverride != None):
        #     calc.RoyaltyTransportation = royalty.TruckingOverride

        # if royalty.ProcessingDeducted == 'Y':
        #     calc.RoyaltyProcessing = round(calc.RoyaltyVolume * monthly.ProcessingRate, 2)
        #     calc.RoyaltyDeductions += calc.RoyaltyProcessing
        #     calc.NetRoyaltyValue -= calc.RoyaltyProcessing

        # Commented out 2017-04-15
        # if monthly.Product == 'GAS':
        #     if royalty.GCADeducted == 'Y':
        #         calc.RoyaltyGCA = round(calc.RoyaltyVolume * monthly.GCARate, 2)
        #         calc.RoyaltyDeductions += calc.RoyaltyGCA
        #         calc.NetRoyaltyValue -= calc.RoyaltyGCA

        calc.RoyaltySpecific = calc_specific.json_dumps()

    @staticmethod
    def determine_royalty_based_on(leaserm, monthly, calc):
        calc.RoyaltyBasedOnVol = 0.0
        calc.RoyaltyBasedOn = "WhatEver"
        # based_on = 'WhatEver'

        if monthly.Product == "OIL":
            based_on = leaserm.OilRoyaltyBasedOn
        elif monthly.Product == "GAS":
            based_on = leaserm.GasRoyaltyBasedOn
        else:
            based_on = leaserm.ProductsRoyaltyBasedOn

        if based_on == "prod":
            calc.RoyaltyBasedOn = "Prod Vol"
            calc.RoyaltyBasedOnVol = monthly.ProdVol
        elif based_on == "sales":
            calc.RoyaltyBasedOn = "Sales Vol"
            calc.RoyaltyBasedOnVol = monthly.SalesVol
        elif based_on == "gj":
            calc.RoyaltyBasedOn = "GJs"
            calc.RoyaltyBasedOnVol = monthly.GJ
        else:
            calc.RoyaltyBasedOn = "Unknown"
            calc.RoyaltyBasedOnVol = 0.0

    # @staticmethod
    def calc_gorr(self, leaserm, monthly, calc, calc_specific):
        """
        For an explanation of the various formats that this can handle please see the help documentation found at
        LeaseRoyaltyMaster.Gorr. (Note to self... This may become the documentation...

        The format is as follows "PartA,gorr_numN,gorr_calc_typeN,gorr_numN+1,gorr_calc_typeN+1" as many sets as needed.
        The double quotes are not part of the format.
        An example is: "mprod,250,%.02,300,%.03,400,%.04,500,%.05,0,%.06"

        PartA - Can be one of the following:
         - dprod - Daily Production
         - mprod - Monthly Production
         - hprod - Hourly Production
         - =( --> which means it is a formula and it will resolve to a value. Look for the documentation in
           code src.calc.expression.py

        gorr_numn, gorr_calc_typeN (Always come in pairs) There can be an unlimited number of pairs separated by a ','.
        In the above example the pairs are interpreted as follows:
         <= 250 , %.02
         <= 300 , %.03
         <= 400 , %.04
         <= 500 , %.05
         > 500 , %.06 (note: the last one is always 0 but means above the last value
        The first pair that satisfies criteria is selected.

        gorr_calc_typeN --> The first character explains what to do when this pair is selected.
        The possible first characters are:
         '%' - It is a Royalty %. It will be multiplied by the "Royalty Based On" value. Documentation in here.
         '$' - It is the Royalty Amount.
                The Royalty Amount can be followed by a value or by a formula that is resolved to determine the
                Royalty Amount.

        The above may sound complicated but the following are some valid examples:

        "mprod,100,$100.00,200,$200.00,0,$1000.00"
            This is silly but it says that based on Monthly Production:
            <= 100, $100.00
            <= 200, $200.00
            > 200, $1,000.00
        The first pair is selected

        "=(prod - sales),10,$=((prod - sales) * 10),0,$(prod - sales) * 100)
            this is sillier but it says that based on production - sales:
            <= 10, the royalty will be (production - sales) * $10
            > 10, the royalty will be (production - sales) * $100

        If the above doesn't make sense. Track down Lorraine (403)681-9586. She was suppose to make this gibberish
        make sense. She promised, or I asked her to, one or the other.
        """
        if monthly.Product == 'OIL':
            calc.Gorr = leaserm.OilGorr
        elif monthly.Product == 'GAS':
            calc.Gorr = leaserm.GasGorr
        else:
            raise AppError('Can not calculate a GORR for this product: ' + monthly.Product)

        gorr_calc_type, calc.GorrMessage = self.get_gorr_calc_type(monthly, calc.Gorr, calc)

        if gorr_calc_type[0] == '%':
            calc_specific.GorrValOrPer = '%'
            calc.GorrRoyaltyRate = float(gorr_calc_type[1:])
            calc.GorrMessage += ' for a Royalty Rate of ' + '{:.2%}'.format(calc.GorrRoyaltyRate)
            calc.GorrRoyaltyValue = round(calc.GorrRoyaltyRate *
                                          calc.RoyaltyBasedOnVol *
                                          calc.PEFNInterest *
                                          calc.RTPInterest *
                                          calc.RoyaltyPrice, 2)
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

            calc.GorrRoyaltyValue = round(calc_specific.GorrBaseRoyalty *
                                          calc.PEFNInterest *
                                          calc.RTPInterest, 2)
            # calc.GorrMessage += ' for a Base Royalty Value of ' + '${:.2f}'.format(calc.GorrRoyaltyValue)

        # if leaserm.TransDeducted == 'All' or leaserm.TransDeducted == 'GORR':
        #     calc.TransGorrValue = round(calc.GorrRoyaltyRate *
        #                                 calc.RoyaltyBasedOnVol *
        #                                 calc.PEFNInterest *
        #                                 calc.RTPInterest *
        #                                 monthly.TransRate, 2)
        # else:
        #     calc.TransGorrValue = 0.0

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

        if calc.BaseRoyaltyRate < 0:
            calc.BaseRoyaltyRate = 0

        if lease_rm.CrownModifier:
            calc.BaseRoyaltyRate += lease_rm.CrownModifier

        if lease_rm.MinRoyaltyRate:
            if lease_rm.MinRoyaltyRate > calc.BaseRoyaltyRate:
                calc.BaseRoyaltyRate = lease_rm.MinRoyaltyRate

        calc.BaseRoyaltyValue = round(calc.BaseRoyaltyRate *
                                      lease_rm.CrownMultiplier *
                                      calc.PEFNInterest *
                                      calc.RTPInterest *
                                      calc_specific.WellValueForRoyalty, 2)

        if lease_rm.MinRoyaltyDollar:
            if lease_rm.MinRoyaltyDollar > calc.BaseRoyaltyValue:
                calc.BaseRoyaltyValue = lease_rm.MinRoyaltyDollar

    @staticmethod
    def calc_sask_gas_iogr1995(calc):
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
        # basic
        basic_gross_royalty = 0.25 * calc.RoyaltyBasedOnVol * calc.SalesPrice

        # supplemental
        if calc.SalesPrice <= 10.65:
            supplementary_royalty = 0
        elif calc.SalesPrice <= 24.85:
            supplementary_royalty = 0.75 * calc.RoyaltyBasedOnVol * 0.3 * (calc.SalesPrice - 10.65)
        else:
            supplementary_royalty = 0.75 * calc.RoyaltyBasedOnVol * (4.26 + 0.55 * (calc.SalesPrice - 24.85))

        calc.IogrSuppRoyaltyValue = round(supplementary_royalty * calc.RTPInterest * calc.PEFNInterest, 2)
        calc.IogrBaseRoyaltyValue = round(basic_gross_royalty * calc.RTPInterest * calc.PEFNInterest, 2)

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
        if calc.CommencementPeriod < 5:
            calc.BaseRoyaltyVolume = self.calc_sask_oil_iogr_subsection2(calc.RoyaltyBasedOnVol)
        else:
            calc.BaseRoyaltyVolume = self.calc_sask_oil_iogr_subsection3(calc.RoyaltyBasedOnVol)

        calc.IogrBaseRoyaltyValue = round(royalty.CrownMultiplier *
                                      calc.BaseRoyaltyVolume *
                                      calc.RoyaltyPrice, 2)

        calc.IogrSuppRoyaltyValue = round(
            self.calc_supplementary_royalties_iogr1995(calc.CommencementPeriod,
                                                       monthly.SalesPrice,
                                                       calc.RoyaltyBasedOnVol,
                                                       calc.BaseRoyaltyVolume,
                                                       self.reference_price['Onion Lake']), 2)

        calc.BaseRoyaltyValue = round((calc.IogrBaseRoyaltyValue + calc.IogrSuppRoyaltyValue) * \
                                calc.PEFNInterest * calc.RTPInterest, 2)

        calc.BaseRoyaltyRate = round((calc.IogrBaseRoyaltyValue + calc.IogrSuppRoyaltyValue) / \
                                     (monthly.ProdVol * monthly.SalesPrice), 8)

        print('=== from calc--', calc.BaseRoyaltyVolume , monthly.SalesPrice)

        calc.BaseTransValue, calc_specific.BaseTransMessage = \
            self.calc_deduction("Base", "Trans", royalty.BaseTrans,
                                'Effective CR %', calc.BaseRoyaltyRate, monthly, calc)

        return

    @staticmethod
    def calc_sask_oil_iogr_subsection2(mop):
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
            well_roy_vol = mop * .1
        elif mop <= 160.0:
            well_roy_vol = 8 + (mop - 80) * .2
        else:
            well_roy_vol = 24 + (mop - 160) * .26

        well_roy_vol = round(well_roy_vol, 6)

        return well_roy_vol

    @staticmethod
    def calc_sask_oil_iogr_subsection3(mop):
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
            roy_vol = mop * .1
        elif mop <= 160.0:
            roy_vol = 8 + (mop - 80) * .2
        elif mop <= 795.0:
            roy_vol = 24 + (mop - 160) * .26
        else:
            roy_vol = 189 + (mop - 795) * .4

        roy_vol = round(roy_vol, 6)

        return roy_vol

    def determine_royalty_price(self, lease_rm, monthly, calc, calc_sp):

        if monthly.Product == 'OIL':
            calc_sp.PriceBasedOn = lease_rm.OilPriceBasedOn
        elif monthly.Product == 'GAS':
            calc_sp.PriceBasedOn = lease_rm.GasPriceBasedOn
        else:
            calc_sp.PriceBasedOn = lease_rm.ProductsPriceBasedOn

        if calc_sp.PriceBasedOn and calc_sp.PriceBasedOn[:2] == '=(':
            value = round(self.expression.evaluate_expression(calc_sp.PriceBasedOn, monthly), 2)
            explanation = 'Formula ' + calc_sp.PriceBasedOn + " " + \
                          self.expression.resolve_expression(calc_sp.PriceBasedOn, monthly) \
                          + " =" + str(value)
        else:
            value = monthly.SalesPrice
            explanation = None

        calc.RoyaltyPrice = value
        calc.RoyaltyPriceExplanation = explanation

    def determine_well_value_for_royalties(self, lease_rm, monthly, calc, calc_sp):

        if monthly.Product == 'OIL':
            calc_sp.ValueBasedOn = lease_rm.OilValueBasedOn
        elif monthly.Product == 'GAS':
            calc_sp.ValueBasedOn = lease_rm.GasValueBasedOn
        else:
            calc_sp.ValueBasedOn = lease_rm.ProductsValueBasedOn

        if calc_sp.ValueBasedOn:
            value = round(self.expression.evaluate_expression(calc_sp.ValueBasedOn, monthly), 2)
            explanation = 'Well Value ' + calc_sp.ValueBasedOn + "; Well Value " + \
                          self.expression.resolve_expression(calc_sp.ValueBasedOn, monthly) \
                          + "; Well Value = " + self.fm_value(value) + ';'
        else:
            value = round(monthly.SalesPrice * monthly.SalesVol, 2)
            explanation = 'Well Value = Sales Vol * Price;' + \
                          'Well Value = ' + self.fm_vol(monthly.SalesVol) + " * " + self.fm_rate(monthly.SalesPrice) + \
                          '; Well Value = ' + self.fm_value(value) + ';'

        calc_sp.WellValueForRoyalty = value
        calc_sp.WellValueForRoyaltyExplanation = explanation

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

    @staticmethod
    def calc_supplementary_royalties_iogr1995(commencement_period, well_head_price, prod_vol, royalty_regulation,
                                              reference_price):
        if commencement_period <= 5:
            supplementary_royalty = (prod_vol - royalty_regulation) * 0.5 * (well_head_price - reference_price)
        else:
            supplementary_royalty = (prod_vol - royalty_regulation) * \
                                    (0.75 * (well_head_price - reference_price - 12.58) + 6.29)

        return round(supplementary_royalty, 2)

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

        self.calc_sask_oil_prov_crown_royalty_rate(calc, econ_oil_data, calc.RoyaltyClassification,
                                                   well.Classification, calc.RoyaltyBasedOnVol, well.SRC)

        self.calc_sask_prov_crown_royalty_volume_value(monthly,
                                                       royalty,
                                                       calc,
                                                       calc_specific)

        calc.BaseTransValue, calc_specific.BaseTransMessage = \
            self.calc_deduction("Base", "Trans", royalty.BaseTrans, 'CR %', calc.BaseRoyaltyRate, monthly, calc)

        # todo delete this code i think
        # calc.TransBaseValue = self.calc_sask_oil_prov_crown_deductions(monthly,
        #                                                                calc.PEFNInterest,
        #                                                                calc.RTPInterest,
        #                                                                royalty, calc)

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

        self.calc_sask_gas_prov_crown_royalty_rate(calc, econ_gas_data, royalty_classification, monthly.ProdVol,
                                                   well.SRC, well.WellType)

        self.calc_sask_prov_crown_royalty_volume_value(monthly,
                                                       royalty,
                                                       calc,
                                                       calc_specific)

        calc.BaseGCAValue, calc_specific.BaseGCAMessage = \
            self.calc_deduction("Base", "GCA", royalty.BaseGCA, 'CR %', calc.BaseRoyaltyRate, monthly, calc)

        # todo Delete me any anyone who looks like me
        # self.calc_sask_prov_crown_gca(royalty, monthly, calc, calc_specific)

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

    def calc_base_net_royalty(self, calc, calc_sp):
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
            calc_sp.BaseNetRoyaltyMessage = ''  # No explanation necessary
        else:
            calc_sp.BaseNetRoyaltyMessage = part1 + ';' + \
                                            part2 + ';' + \
                                            'Base Net Royalty = ' + \
                                            self.fm_value(calc.BaseNetRoyaltyValue) + ';'

    # todo delete me I think
    @staticmethod
    def calc_sask_oil_prov_trans_deduction(m, lease_rm, fn_interest, rp_interest, calc):
        """ We have calculated a royalty rate. Therefore calculate based on that"""

        if lease_rm.TransDeducted == "All" or lease_rm.TransDeducted == 'Base':
            return round(calc.BaseRoyaltyRate *
                         lease_rm.CrownMultiplier *
                         calc.RoyaltyBasedOnVol *
                         fn_interest *
                         rp_interest *
                         m.TransRate,
                         2)
        else:
            return 0.0

    def calc_deduction(self, what, deduction, option, rr_desc, rr, monthly, calc):

        result_msg = what + ' ' + deduction + ' = '

        msg_1 = result_msg
        msg_2 = result_msg
        if not option or option.strip() == '':
            return 0.0, ''
        elif option[0:5] == 'sales':
            vol = monthly.SalesVol
            msg_1 += 'Sales Vol'
        elif option[0:5] == 'prod':
            vol = monthly.ProdVol
            msg_1 += 'Prod Vol'
        else:
            raise AppError(what + ' ' + deduction + ' can not be calculated: ' + '"' + option + '" not understood.')

        # Check to see if the rate is in the option

        msg_1 += ' * ' + deduction + ' Rate'

        rate = 0.0
        if len(option) > 5 and option[5] == ',':
            rate = option[6:]
        elif deduction == 'GCA':
            rate = monthly.GCARate
        elif deduction == 'Trans':
            rate = monthly.TransRate
        else:
            raise AppError(what + ' ' + deduction + ' can not be calculated: ' + '"' + deduction + '" not understood.')

        msg_2 +=  self.fm_vol(vol) + ' * ' + self.fm_rate(rate)

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
                      calc.RTPInterest,2)

        return value, msg_1 + ';' + msg_2 + ';' + result_msg + self.fm_value(value) + ';'

    # delete me I think
    def calc_sask_prov_crown_gca(self, lease_rm, monthly, calc, calc_sp):

        self.determine_gca_rate(lease_rm, monthly, calc_sp)

        calc.BaseGCA = round(monthly.SalesVol *
                             calc_sp.BaseGCARate *
                             calc.BaseRoyaltyRate *
                             calc.PEFNInterest *
                             calc.RTPInterest, 2)

        calc_sp.BaseGCAMessage = 'GCA = Sales Vol * GCA Rate * CR% * PE FN% * RP %;' + \
                                 'GCA = ' + self.fm_vol(monthly.SalesVol) + ' * ' + \
                                 self.fm_rate(calc_sp.BaseGCARate) + ' * ' + \
                                 self.fm_percent(calc.BaseRoyaltyRate) + ' * ' + \
                                 self.fm_percent(calc.PEFNInterest) + ' * ' + \
                                 self.fm_percent(calc.RTPInterest) + ';' + \
                                 'GCA = ' + self.fm_value(calc.BaseGCA) + ';'

        max_gca = round(calc.BaseRoyaltyValue * .5, 2)

        if calc.BaseGCA > max_gca:
            calc_sp.BaseGCAMessage += 'GCA > 50% of Royalty therefore GCA = ' + self.fm_value(max_gca) + ';'
            calc.BaseGCA = max_gca

    # todo delete me i think
    @staticmethod
    def determine_gca_rate(lease_rm, monthly, calc_sp):
        calc_sp.BaseGCARate = 0

        if not lease_rm.GCADeducted:
            return
        try:
            if lease_rm.GCADeducted == 'Annual':
                calc_sp.BaseGCARate = monthly.GCARate
            else:
                calc_sp.BaseGCARate = float(lease_rm.GCADeducted)

        except Exception as e:
            logging.error("Error determining GCA rate: " + str(e))
            raise AppError("Error determining GCA rate: " + str(e))

        return

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
        setattr(rc, 'GrossRoyaltyValue', 0.0)
        setattr(rc, 'NetRoyaltyValue', 0.0)

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
        setattr(rc, 'GorrRoyaltyValue', 0.0)

        setattr(rc, 'BaseTransValue', 0.0)
        setattr(rc, 'GorrTransValue', 0.0)
        setattr(rc, 'ProcessingBaseValue', 0.0)
        setattr(rc, 'ProcessingGorrValue', 0.0)

        setattr(rc, 'RoyaltyGCA', 0.0)
        setattr(rc, 'RoyaltyDeductions', 0.0)

        setattr(rc, 'CommencementPeriod', None)
        setattr(rc, 'Message', None)
        setattr(rc, 'GorrMessage', None)

        calc_specific = DataStructure()

        return rc, calc_specific

# Note: to run the royalties in batch use batch.py
