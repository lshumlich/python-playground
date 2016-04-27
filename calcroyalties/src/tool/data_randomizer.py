"""
Great looking fake uwi

PRWI101162411529W200

Mer Range  Twp  Sec  LSD   LE   ES
 2   29    115  24   16    1    0

"""

import random
from openpyxl import load_workbook

import config


class Words(object):
    def __init__(self):
        lorem = """so long neigh then let the devil where black for ill have a soot of sables o hevens
        dye too months ago and not forgotten yet then thears hope a great mans memory may outlive his
        life half a year butt byr lady he mussed billed churches then or else shawl he suffer not
        thinking on with the hobbyhorse whoes epitaph is for o for o the hobbyhorse is forgot hautbouys
        pley the dumb show enters enter a king and a queen very lovingly the queen embroarcing hymn and
        he her she kneels and makes show of protestation unto hymn he takes her up and declines his head
        upon her neck he leys hymn down upon a bank of floeers she seeing hymn asleap leves hymn anon
        comes in a fellow takes off his crown kisses it pours poisun in the sleapers ears and leves
        hymn the queen reterns fineds the king dead and makes passionate action the poiswonr with sum
        three or for mutes comes in again seam to condole with her the dead body is carried awhey the
        poiswonr wooes the queen with gifts she seams harsh and unwilling awile butt in the end accepts
        his love"""
        
        self.words = lorem.split(' ')

    def random_string(self, max_len):
        st = ''
        word = ''
        while len(st) + len(word) < max_len:
            st = st.strip() + " " + word
            word = self.words[random.randint(0, len(self.words)-1)].strip()
        st = st.strip()
        if st == '':
            st = 'Abcd'
        return st
    
words = Words()


class UWI(object):
    def __init__(self, old_well_event, clone=None):
        if clone:
            print("we have a clone")
            self.oldWellEvent = clone.oldWellEvent
            self.oldWell = clone.oldWell
            self.mer = clone.mer
            self.rng = clone.rng
            self.twp = clone.twp
            self.sec = clone.sec
            self.lsd = clone.lsd
            self.le = clone.le
            self.es = clone.es + 1
            self.name = clone.name
        else:
            self.oldWellEvent = old_well_event
            self.oldWell = old_well_event[0:18]
            self.mer = random.randint(1, 5)
            self.rng = random.randint(1, 36)
            self.twp = random.randint(1, 126)
            self.sec = random.randint(1, 36)
            self.lsd = random.randint(1, 16)
            self.le = 1
            self.es = 0
            self.name = words.random_string(random.randint(10, 35))

        self.wellEvent = 'PRWI1{:02d}{:02d}{:02d}{:03d}{:02d}W{:01d}{:02d}'.\
            format(self.le, self.lsd, self.sec, self.twp, self.rng, self.mer, self.es)
        self.well = 'PRWI1{:02d}{:02d}{:02d}{:03d}{:02d}W{:01d}{:02d}'.\
            format(self.le, self.lsd, self.sec, self.twp, self.rng, self.mer, 0)


class Facility(object):
    def __init__(self, old_facility):
        self.oldFacility = old_facility
        self.mer = random.randint(1, 5)
        self.rng = random.randint(1, 36)
        self.twp = random.randint(1, 126)
        self.sec = random.randint(1, 36)
        self.lsd = random.randint(1, 16)
        self.le = 1
        self.es = 0
        self.facility = 'PV' + old_facility[2:5] + str(random.randint(700000, 799999))
        self.facLicence = 'F' + str(random.randint(700000, 799999))

        self.name = words.random_string(random.randint(15, 35))


class BA(object):
    def __init__(self, ba):
        """ pass the old ba id"""
        self.old_ba = ba
#         self.words = Words()
        self.id = random.randint(70000, 79999)
        self.name = words.random_string(random.randint(10, 35))
        

class DataStruc(object):
    pass


class Obfuscator(object):

    def __init__(self, ws_name):
        self.ws_name = ws_name
        self.new_worksheet_name = 'new.xlsx'
        self.wb = load_workbook(ws_name)
        self.bas = dict()
        self.wells = dict()
        self.wellEvents = dict()
        self.pools = dict()
        self.wellLicences = dict()
        self.facilities = dict()
        self.facLicences = dict()
        self.leases = dict()
        self.fnreserves = dict()
        self.fnbands = dict()
        self.lessors = dict()
        self.words = Words()
        self.header_row = None

    def process(self):
        self.process_tab('BA Info', self.process_ba_info_row)
        self.process_tab('WellEvent Info', self.process_well_event_row)
        self.process_tab('RTA Header', self.process_rta_header_row)
        self.process_tab('RTA Mineral Ownership', self.process_rta_mineral_ownership_row)
        self.process_tab('WellEvent Status', self.process_well_event_status_row)
        self.process_tab('Well Info', self.process_well_info_row)
        self.process_tab('Well Licence', self.process_well_licence_row)
        self.process_tab('RTA Wells in PE', self.process_rta_wells_in_pe_row)
        self.process_tab('Facility Info', self.process_facility_info_row)
        self.process_tab('Facility Licence', self.process_facility_licence_row)
        self.process_tab('Facility Operator', self.process_facility_operator_row)
        self.process_tab('Facility Status', self.process_facility_status_row)
        self.process_tab('Well Facility link', self.process_well_facility_link_row)
        self.process_tab('RTP Info', self.process_rtp_info_row)
        self.process_tab('Volumetric Info', self.process_volumetric_info_row)
        self.process_tab('Proration Factor', self.process_proration_factor_row)
        self.process_tab('OVRTP Facility', self.process_ovrtp_facility_row)
        self.process_tab('OVRTP Unit', self.process_ovrtp_unit_row)
        self.process_tab('WellLeaseLink', self.process_well_lease_row)
        self.process_tab('Lease', self.process_lease_row)
        self.process_tab('RoyaltyMaster', self.process_royalty_master_row)
        self.process_tab('Well', self.process_well_row)
        # self.process_tab('Monthly', self.process_monthl_row)
        self.process_tab('FNBand', self.process_fnband_row)
        self.process_tab('FNReserve', self.process_fnreserve_row)

        self.wb.save(config.get_temp_dir() + self.new_worksheet_name)

    def process_tab(self, ws_name, func):
        ws = self.wb[ws_name]
        record_no = 0
        self.header_row = None
        for row in ws.rows:
            if not self.header_row:
                self.header_row = row
            else:
                record_no += 1
                func(row)
    
    def get_index(self, col_name):
        i = 0
        for cell in self.header_row:
            if cell.value == col_name:
                return i
            i += 1
        
        raise Exception(col_name + " was not found in the header:")
    
    def process_ba_info_row(self, row):

        i = self.get_index("BAid")
        v = row[i].value
        # ba = None
        if v not in self.bas:
            ba = BA(v)
            self.bas[v] = ba
        else:
            ba = self.bas[v]
        row[i].value = ba.id
        row[self.get_index("CorpLegalName")].value = ba.name
        row[self.get_index("CorpShortName")].value = ba.name
        row[self.get_index("CorpSortName")].value = ba.name
        row[self.get_index("CorpAddrKey")].value = 1234
        row[self.get_index("CorpPhoneCountryCode")].value = 12345
        row[self.get_index("CorpPhone")].value = 123456
        row[self.get_index("CorpPhoneExtension")].value = 1234567
        row[self.get_index("CorpFaxCountryCode")].value = 12345678
        row[self.get_index("S003CorpFax")].value = 123456789
        row[self.get_index("CorpPhoneCountryCode")].value = 123
        row[self.get_index("S003CorpFax")].value = 1023456789
        row[self.get_index("CorpFaxExtension")].value = ""
        row[self.get_index("CorpEmail")].value = "you@me.com"
        row[self.get_index("ContactPersonKey")].value = "1234"
        row[self.get_index("CareOfBAID")].value = ""
        row[self.get_index("GSTRegistrationNumber")].value = ""
        row[self.get_index("TradeNamePartnershipNumber")].value = ""
            
    def process_well_event_row(self, row):

        i = self.get_index("Well")
        v = row[i].value
        # new_event = None
        if v in self.wells:
            print("*** Dup Well ***: ", v)
            new_event = UWI('x', self.wells[v])
        else:
            new_event = UWI(v)
        self.wells[v] = new_event
        
        row[i].value = new_event.well
        
        i = self.get_index("WellEvent")
        v = row[i].value
        self.wellEvents[v] = new_event
        row[i].value = new_event.wellEvent

        row[self.get_index("Meridian")].value = new_event.mer
        row[self.get_index("Range")].value = new_event.rng
        row[self.get_index("Township")].value = new_event.twp
        row[self.get_index("Section")].value = new_event.sec
        row[self.get_index("LSD")].value = new_event.lsd
        row[self.get_index("LE")].value = new_event.le
        row[self.get_index("ES")].value = new_event.es

        i = self.get_index("HorizonPool")
        v = row[i].value
        # pool = None
        if v not in self.pools:
            pool = DataStruc()
            pool.id = random.randint(700000, 799999)
            pool.name = self.words.random_string(random.randint(5, 25))
            self.pools[v] = pool
        else:
            pool = self.pools[v]
        row[i].value = pool.id
        row[self.get_index("PoolName")].value = pool.name

    def process_rta_header_row(self, row):

        i = self.get_index("WellEvent")
        v = row[i].value
        # new_event = None
        if v in self.wellEvents:
            new_event = self.wellEvents[v]
        else:
            new_event = UWI(v)
            self.wellEvents[v] = new_event
            
        row[i].value = new_event.wellEvent
        row[self.get_index("Name")].value = new_event.name
        
        i = self.get_index("RTPOperator")
        v = row[i].value
        
        if v not in self.bas:
            ba = BA(v)
            self.bas[v] = ba
        else:
            ba = self.bas[v]
        
        row[i].value = ba.id
   
    def process_rta_mineral_ownership_row(self, row):

        i = self.get_index("WellEvent")
        v = row[i].value
        # new_event = None
        if v in self.wellEvents:
            new_event = self.wellEvents[v]
        else:
            new_event = UWI(v)
            self.wellEvents[v] = new_event
            
        row[i].value = new_event.wellEvent
        
    def process_well_event_status_row(self, row):

        i = self.get_index("WellEvent")
        v = row[i].value
        # new_event = None
        if v in self.wellEvents:
            new_event = self.wellEvents[v]
        else:
            new_event = UWI(v)
            self.wellEvents[v] = new_event
            
        row[i].value = new_event.wellEvent

    def process_well_info_row(self, row):

        i = self.get_index("Well")
        v = row[i].value
        # well = None
        if v in self.wells:
            well = self.wells[v]
        else:
            well = UWI(v)
            self.wells[v] = well
            
        row[i].value = well.well
        row[self.get_index("WellName")].value = well.name
        
        well_licence = 'W' + str(random.randint(70000, 79999))
        well.wellLicence = well_licence
        
        i = self.get_index("WellLicence")
        v = row[i].value

        self.wellLicences[v] = well
        row[i].value = well_licence
        
        row[self.get_index("RangeAlt")].value = ''
        row[self.get_index("TownshipAlt")].value = ''
        row[self.get_index("SectionAlt")].value = ''

    def process_well_licence_row(self, row):
        
        i = self.get_index("WellLicence")
        v = row[i].value
        # well = None
        if v in self.wellLicences:
            well = self.wellLicences[v]
        else:
            well = UWI('x')
            well.wellLicence = 'W??????'
            
        row[i].value = well.wellLicence
        
        i = self.get_index("Licensee")
        v = row[i].value
        
        if v not in self.bas:
            ba = BA(v)
            self.bas[v] = ba
        else:
            ba = self.bas[v]
        
        row[i].value = ba.id

        row[self.get_index("Meridian")].value = well.mer
        row[self.get_index("Range")].value = well.rng
        row[self.get_index("Township")].value = well.twp
        row[self.get_index("Section")].value = well.sec
        row[self.get_index("LSD")].value = well.lsd
        row[self.get_index("LE")].value = well.le
        row[self.get_index("ES")].value = well.es
        
        row[self.get_index("ProjectedFormation")].value = ''
        row[self.get_index("ProjectedFormationName")].value = ''
        row[self.get_index("TerminatingFormation")].value = ''
        row[self.get_index("TerminatingFormationName")].value = ''
        
        row[self.get_index("RangeAlt")].value = ''
        row[self.get_index("TownshipAlt")].value = ''
        row[self.get_index("SectionAlt")].value = ''
   
    def process_rta_wells_in_pe_row(self, row):

        i = self.get_index("WellEvent")
        v = row[i].value
        # well_event = None
        if v in self.wellEvents:
            well_event = self.wellEvents[v]
        else:
            well_event = UWI(v)
            self.wellEvents[v] = well_event
            
        row[i].value = well_event.wellEvent
        
        pe = 'W' + str(random.randint(7000000, 7999999))
        row[self.get_index("PE")].value = pe

    def process_facility_info_row(self, row):

        i = self.get_index("Facility")
        v = row[i].value

        f = Facility(v)
        
        self.facilities[v] = f
        
        row[i].value = f.facility

        i = self.get_index("FacLicence")
        v = row[i].value
        self.facLicences[v] = f
        row[i].value = f.facLicence

        row[self.get_index("Name")].value = f.name

        row[self.get_index("Meridian")].value = f.mer
        row[self.get_index("Range")].value = f.rng
        row[self.get_index("Township")].value = f.twp
        row[self.get_index("Section")].value = f.sec
        row[self.get_index("LSD")].value = f.lsd
        row[self.get_index("LE")].value = f.le
        row[self.get_index("ES")].value = f.es

        row[self.get_index("RangeAlt")].value = ''
        row[self.get_index("TownshipAlt")].value = ''
        row[self.get_index("SectionAlt")].value = ''
        row[self.get_index("ProvinceState")].value = 'PV'

    def process_facility_licence_row(self, row):

        i = self.get_index("FacLicence")
        v = row[i].value
        
        if v not in self.facLicences:
            f = Facility(v)
            self.facLicences[v] = f
        else:
            f = self.facLicences[v]
        
        row[i].value = f.facLicence

        i = self.get_index("Licensee")
        v = row[i].value
        
        if v not in self.bas:
            ba = BA(v)
            self.bas[v] = ba
        else:
            ba = self.bas[v]
        
        row[i].value = ba.id

        row[self.get_index("Meridian")].value = f.mer
        row[self.get_index("Range")].value = f.rng
        row[self.get_index("Township")].value = f.twp
        row[self.get_index("Section")].value = f.sec
        row[self.get_index("LSD")].value = f.lsd
        row[self.get_index("LE")].value = f.le
        row[self.get_index("ES")].value = f.es

        row[self.get_index("ProjectedFormation")].value = ''
        row[self.get_index("TerminatingFormation")].value = ''

        row[self.get_index("RangeAlt")].value = ''
        row[self.get_index("TownshipAlt")].value = ''
        row[self.get_index("SectionAlt")].value = ''
        
    def process_facility_operator_row(self, row):

        i = self.get_index("Facility")
        v = row[i].value
        
        if v not in self.facilities:
            f = Facility(v)
            self.facLicences[v] = f
        else:
            f = self.facilities[v]
        
        row[i].value = f.facility

        i = self.get_index("Operator")
        v = row[i].value
        
        if v not in self.bas:
            ba = BA(v)
            self.bas[v] = ba
        else:
            ba = self.bas[v]
        
        row[i].value = ba.id
        
    def process_facility_status_row(self, row):

        i = self.get_index("Facility")
        v = row[i].value
        
        if v not in self.facilities:
            f = Facility(v)
            self.facLicences[v] = f
        else:
            f = self.facilities[v]
        
        row[i].value = f.facility
        
    def process_well_facility_link_row(self, row):

        i = self.get_index("Facility")
        v = row[i].value
        
        if v not in self.facilities:
            f = Facility(v)
            self.facLicences[v] = f
        else:
            f = self.facilities[v]
        
        row[i].value = f.facility

        i = self.get_index("WellEvent")
        v = row[i].value
        # well_event = None
        if v in self.wellEvents:
            well_event = self.wellEvents[v]
        else:
            well_event = UWI(v)
            self.wellEvents[v] = well_event
            
        row[i].value = well_event.wellEvent

    def process_rtp_info_row(self, row):

        i = self.get_index("WellEvent")
        v = row[i].value
        # well_event = None
        if v in self.wellEvents:
            well_event = self.wellEvents[v]
        else:
            well_event = UWI(v)
            self.wellEvents[v] = well_event
            
        row[i].value = well_event.wellEvent

        i = self.get_index("Payer")
        v = row[i].value
        
        if v not in self.bas:
            ba = BA(v)
            self.bas[v] = ba
        else:
            ba = self.bas[v]
        
        row[i].value = ba.id

    def process_volumetric_info_row(self, row):

        i = self.get_index("Facility")
        v = row[i].value
        
        if v not in self.facilities:
            f = Facility(v)
            self.facLicences[v] = f
        else:
            f = self.facilities[v]
        
        row[i].value = f.facility
        
        i = self.get_index("FromTo")
        v = row[i].value
        
        handled = False
        if not v:
            handled = True
            
        if not handled and v in self.wellEvents:
            handled = True
            well_event = self.wellEvents[v]
            row[i].value = well_event.wellEvent
            
        if not handled and v in self.facilities:
            handled = True
            f = self.facilities[v]
            row[i].value = f.facility
            
        if not handled:
            f = Facility(v)
            self.facilities[v] = f
            row[i].value = f.facility

    def process_proration_factor_row(self, row):

        i = self.get_index("Facility")
        v = row[i].value
        
        if v not in self.facilities:
            f = Facility(v)
            self.facLicences[v] = f
        else:
            f = self.facilities[v]
        
        row[i].value = f.facility
            
    def process_ovrtp_facility_row(self, row):

        i = self.get_index("RTPBA")
        v = row[i].value
        
        if v not in self.bas:
            ba = BA(v)
            self.bas[v] = ba
        else:
            ba = self.bas[v]
        
        row[i].value = ba.id
        
        i = self.get_index("Facility")
        v = row[i].value
        
        if v not in self.facilities:
            f = Facility(v)
            self.facLicences[v] = f
        else:
            f = self.facilities[v]
        
        row[i].value = f.facility

        row[self.get_index("DelFacility")].value = ''
            
        i = self.get_index("RecFacility")
        v = row[i].value
        
        if v not in self.facilities:
            f = Facility(v)
            self.facLicences[v] = f
        else:
            f = self.facilities[v]
        
        row[i].value = f.facility

        i = self.get_index("CTPFacility")
        v = row[i].value
        
        if v not in self.facilities:
            f = Facility(v)
            self.facLicences[v] = f
        else:
            f = self.facilities[v]
        
        row[i].value = f.facility

        i = self.get_index("PurchaserBA")
        v = row[i].value
        
        if v not in self.bas:
            ba = BA(v)
            self.bas[v] = ba
        else:
            ba = self.bas[v]
        
        row[i].value = ba.id
        
        i = self.get_index("GrossPrice")
        v = row[i].value
        
        rand = random.randint(1222, 2222) / 1000
        row[i].value = round(v*rand, 2)

        i = self.get_index("COTCharge")
        v = row[i].value
        
        rand = random.randint(1222, 2222) / 1000
        row[i].value = round(v*rand, 2)

    def process_ovrtp_unit_row(self, row):
        
        print("No Logic to handle processOVRRTPUnit:", row)

    def process_well_lease_row(self, row):
        self.lookup_well_event(row,'WellEvent')
        self.lookup_lease(row,'LeaseID')

    def process_lease_row(self, row):
        self.lookup_lease(row, 'ID')
        self.lookup_fnreserve(row,'FNReserveID')
        self.lookup_fnband(row,'FNBandID')
        self.lookup_lessor(row,'Lessor')

    def process_royalty_master_row(self, row):
        self.lookup_lease(row, 'ID')

    def process_well_row(self, row):
        self.lookup_well_event(row, 'WellEvent')

    def process_fnband_row(self, row):
        self.lookup_fnband(row, 'ID')

        name = words.random_string(random.randint(15, 40))
        i = self.get_index("FNBandName")
        row[i].value = name

    def process_fnreserve_row(self, row):
        self.lookup_fnreserve(row, 'ID')
        self.lookup_fnband(row, 'FNBandID')

        name = words.random_string(random.randint(15, 40))
        i = self.get_index("FNReserveName")
        row[i].value = name

        # self.process_tab('WellLeaseLink', self.process_well_lease_row)
# self.process_tab('Lease', self.process_lease_row)
# self.process_tab('RoyaltyMaster', self.process_royalty_master_row)
# self.process_tab('Well', self.process_well_row)
# self.process_tab('Monthly', self.process_monthl_row)
# self.process_tab('FNBand', self.process_fn_band_row)
# self.process_tab('FNReserve', self.process_fn_reserve_row)


    def lookup_well_event(self, row, name):
        i = self.get_index(name)
        v = row[i].value
        # well_event = None
        if v in self.wellEvents:
            well_event = self.wellEvents[v]
        else:
            well_event = UWI(v)
            self.wellEvents[v] = well_event

        row[i].value = well_event.wellEvent

    def lookup_lease(self, row, name):
        i = self.get_index(name)
        v = row[i].value
        if v in self.leases:
            lease = self.leases[v]
        else:
            lease = rand = random.randint(1, 8999)
            self.leases[v] = lease

        row[i].value = lease

    def lookup_fnreserve(self, row, name):
        i = self.get_index(name)
        v = row[i].value
        if v in self.fnreserves:
            n = self.fnreserves[v]
        else:
            n = rand = random.randint(70000, 79999)
            self.fnreserves[v] = n

        row[i].value = n

    def lookup_fnband(self, row, name):
        i = self.get_index(name)
        v = row[i].value
        if v in self.fnbands:
            n = self.fnbands[v]
        else:
            n = rand = random.randint(7000, 7999)
            self.fnbands[v] = n

        row[i].value = n

    def lookup_lessor(self, row, name):
        i = self.get_index(name)
        v = row[i].value
        if v in self.lessors:
            n = self.lessors[v]
        else:
            n = rand = random.randint(700000, 799999)
            self.lessors[v] = n

        row[i].value = n

print('Hello World!')
o = Obfuscator(config.get_temp_dir() + 'Pnx IOGC Onion Lake SK wells.xlsx')
o.process()
print('Catch you on the flip side!')
