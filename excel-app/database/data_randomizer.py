"""
Great looking fake uwi

PRWI101162411529W200

Mer Range  Twp  Sec  LSD   LE   ES
 2   29    115  24   16    1    0

"""

import random
from openpyxl import load_workbook

class Words(object):
    def __init__(self):
        loremx = """Lorem ipsum dolor sit amet consectetur adipiscing elit Aenean pulvinar condimentum blandit Vivamus lacus metus consectetur et elementum a convallis non lectus Etiam at erat aliquet tristique enim eget finibus purus Curabitur facilisis venenatis justo in pretium Quisque lacus orci tincidunt at dui vel auctor porta enim Etiam ac leo condimentum cursus felis et porttitor ante In elementum faucibus augue et tristique arcu porta eget Duis vel risus nunc Praesent elementum porta massa sed facilisis augue eleifend nec Donec ultricies placerat pulvinar In tempus libero ut tortor ultricies ac lacinia erat lacinia Integer ut magna cursus interdum metus a placerat metus Maecenas sodales velit vel aliquam convallis Aliquam in nisi ut ligula ornare euismod Curabitur nec maximus purus vitae molestie enim Morbi venenatis est justo ac iaculis arcu imperdiet ornare Aenean pulvinar ultricies nulla quis mattis velit Quisque non orci est Etiam a nunc in massa egestas bibendum In commodo orci sed dictum blandit Aenean lorem enim luctus sed nisl non luctus euismod metus Cras molestie imperdiet lacus eget lacinia In vel tellus ac lacus gravida ultrices Integer congue blandit porta In posuere dui a metus malesuada ullamcorper quis id turpis Etiam eu massa id leo accumsan ornare non eget nulla Morbi tincidunt mollis suscipit Maecenas condimentum faucibus diam quis accumsan tortor sollicitudin nec Quisque cursus ipsum rhoncus mollis posuere Pellentesque eget felis tincidunt malesuada sapien posuere dapibus turpis Praesent blandit nibh in ex lacinia non tincidunt mauris porttitor Vestibulum at quam nunc Pellentesque at lectus mollis rhoncus sem at accumsan velit Nunc malesuada lorem eu tristique ultricies enim erat commodo ante ut euismod urna tortor quis urna Donec cursus nisl lacinia mi iaculis pellentesque Mauris ultrices nisi vitae suscipit accumsan Pellentesque placerat orci vel auctor rutrum nunc enim scelerisque mauris sit amet sollicitudin quam ligula a felis Maecenas non velit odio Cras eros felis viverra pellentesque commodo ultrices bibendum ornare enim In pulvinar dictum quam Morbi at purus at dolor vulputate mollis vel sed nulla In metus felis eleifend eget convallis vitae tempor quis lacus Suspendisse lectus ex egestas ut mi sed blandit cursus dolor Aliquam sagittis efficitur erat ut cursus dolor imperdiet egestas Suspendisse mollis risus in rhoncus aliquam erat dolor molestie enim ut aliquet ex odio quis nisl Nullam convallis est mattis malesuada rutrum nibh dolor egestas nisi vitae scelerisque justo felis non lectus Nunc sapien augue finibus ut libero eget hendrerit consequat libero"""
        lorem = """so long neigh then let the devil where black for ill have a soot of sables o hevens dye too months ago and not forgotten yet then thears hope a great mans memory may outlive his life half a year butt byr lady he mussed billed churches then or else shawl he suffer not thinking on with the hobbyhorse whoes epitaph is for o for o the hobbyhorse is forgot hautbouys pley the dumb show enters enter a king and a queen very lovingly the queen embroarcing hymn and he her she kneels and makes show of protestation unto hymn he takes her up and declines his head upon her neck he leys hymn down upon a bank of floeers she seeing hymn asleap leves hymn anon comes in a fellow takes off his crown kisses it pours poisun in the sleapers ears and leves hymn the queen reterns fineds the king dead and makes passionate action the poiswonr with sum three or for mutes comes in again seam to condole with her the dead body is carried awhey the poiswonr wooes the queen with gifts she seams harsh and unwilling awile butt in the end accepts his love"""       
        
        self.words = lorem.split(' ')

    def randomString(self, maxLen):
        st = ''
        word =  ''
        while len(st) + len(word) < maxLen:
            st = st.strip() + " " + word
            word = self.words[random.randint(0,len(self.words)-1)].strip()
        st = st.strip()
        if st == '':
            st = 'Abcd'
        return st
    
words = Words()

class UWI(object):
    def __init__(self,oldWellEvent, clone = None):
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
            self.oldWellEvent = oldWellEvent
            self.oldWell = oldWellEvent[0:18]
            self.mer = random.randint(1,5)
            self.rng = random.randint(1,36)
            self.twp = random.randint(1,126)
            self.sec = random.randint(1,36)
            self.lsd = random.randint(1,16)
            self.le = 1
            self.es = 0
            self.name = words.randomString(random.randint(10,35))

        self.wellEvent = 'PRWI1{:02d}{:02d}{:02d}{:03d}{:02d}W{:01d}{:02d}'.format(self.le,self.lsd,self.sec,self.twp,self.rng,self.mer,self.es)
        self.well = 'PRWI1{:02d}{:02d}{:02d}{:03d}{:02d}W{:01d}{:02d}'.format(self.le,self.lsd,self.sec,self.twp,self.rng,self.mer,0)


class Facility(object):
    def __init__(self,oldFacility):
        self.oldFacility = oldFacility
        self.mer = random.randint(1,5)
        self.rng = random.randint(1,36)
        self.twp = random.randint(1,126)
        self.sec = random.randint(1,36)
        self.lsd = random.randint(1,16)
        self.le = 1
        self.es = 0
        self.facility = 'PV' + oldFacility[2:5] + str(random.randint(700000,799999))
        self.facLicence = 'F' + str(random.randint(700000,799999))

        self.name = words.randomString(random.randint(15,35))

class BA(object):
    def __init__(self,ba):
        self.old_ba = ba
#         self.words = Words()
        self.id = random.randint(70000,79999)
        self.name = words.randomString(random.randint(10,35))
        

class DataStruc(object):
    None

class Obfuscator(object):

    def __init__(self,ws_name):
        self.ws_name = ws_name
        self.newWorksheetName = 'new.xlsx'
        self.wb = load_workbook(ws_name)
        self.bas = dict()
        self.wells = dict()
        self.wellEvents = dict()
        self.pools = dict()
        self.wellLicences = dict()
        self.facilities = dict()
        self.facLicences = dict()
        self.words = Words()

    def process(self):
        self.processTab('BA Info',self.processBAInfoRow)
        self.processTab('WellEvent Info',self.processWellEventRow)
        self.processTab('RTA Header',self.processRTAHeaderRow)
        self.processTab('RTA Mineral Ownership',self.processRTAMineralOwnershipRow)
        self.processTab('WellEvent Status',self.processWellEventStatusRow)
        self.processTab('Well Info',self.processWellInfoRow)
        self.processTab('Well Licence',self.processWellLicenceRow)
        self.processTab('RTA Wells in PE',self.processRTAWellsInPERow)
        self.processTab('Facility Info',self.processFacilityInfoRow)
        self.processTab('Facility Licence',self.processFacilityLicenceRow)
        self.processTab('Facility Operator',self.processFacilityOperatorRow)
        self.processTab('Facility Status',self.processFacilityStatusRow)
        self.processTab('Well Facility link',self.processWellFacilityLinkRow)
        self.processTab('RTP Info',self.processRTPInfoRow)
        self.processTab('Volumetric Info',self.processVolumetricInfoRow)
        self.processTab('Proration Factor',self.processProrationFactorRow)
        self.processTab('OVRTP Facility',self.processOVRTPFacilityRow)
        self.processTab('OVRTP Unit',self.processOVRTPUnitRow)

        self.wb.save(self.newWorksheetName)

    def processTab(self, ws_name, func):
        ws = self.wb[ws_name]
        recordNo = 0
        self.headerRow = None
        for row in ws.rows:
            if self.headerRow == None:
                self.headerRow = row
            else:
                recordNo = recordNo +1
                func(row)
    
    def getIndex(self,colName):
        i = 0
        for cell in self.headerRow:
            if cell.value == colName:
                return i
            i += 1
        
        raise Exception(colName + " was not found in the header:")
    
    def processBAInfoRow(self,row):

        i = self.getIndex("BAid")
        v = row[i].value
        ba = None
        if not v in self.bas:
            ba = BA(v)
            self.bas[v] = ba
        else:
            ba = self.bas[v]
        row[i].value = ba.id
        row[self.getIndex("CorpLegalName")].value = ba.name
        row[self.getIndex("CorpShortName")].value = ba.name
        row[self.getIndex("CorpSortName")].value = ba.name
        row[self.getIndex("CorpAddrKey")].value = 1234
        row[self.getIndex("CorpPhoneCountryCode")].value = 12345
        row[self.getIndex("CorpPhone")].value = 123456
        row[self.getIndex("CorpPhoneExtension")].value = 1234567
        row[self.getIndex("CorpFaxCountryCode")].value = 12345678
        row[self.getIndex("S003CorpFax")].value = 123456789
        row[self.getIndex("CorpPhoneCountryCode")].value = 123
        row[self.getIndex("S003CorpFax")].value = 1023456789
        row[self.getIndex("CorpFaxExtension")].value = ""
        row[self.getIndex("CorpEmail")].value = "you@me.com"
        row[self.getIndex("ContactPersonKey")].value = "1234"
        row[self.getIndex("CareOfBAID")].value = ""
        row[self.getIndex("GSTRegistrationNumber")].value = ""
        row[self.getIndex("TradeNamePartnershipNumber")].value = ""
            
   
    def processWellEventRow(self,row):

        i = self.getIndex("Well")
        v = row[i].value
        new_event = None
        if v in self.wells:
            print("*** Dup Well ***: ", v)
            new_event = UWI('x',self.wells[v])
        else:
            new_event = UWI(v)
        self.wells[v] = new_event
        
        row[i].value = new_event.well
        
        i = self.getIndex("WellEvent")
        v = row[i].value
        self.wellEvents[v] = new_event
        row[i].value = new_event.wellEvent

        row[self.getIndex("Meridian")].value = new_event.mer
        row[self.getIndex("Range")].value = new_event.rng
        row[self.getIndex("Township")].value = new_event.twp
        row[self.getIndex("Section")].value = new_event.sec
        row[self.getIndex("LSD")].value = new_event.lsd
        row[self.getIndex("LE")].value = new_event.le
        row[self.getIndex("ES")].value = new_event.es

        i = self.getIndex("HorizonPool")
        v = row[i].value
        pool = None
        if not v in self.pools:
            pool = DataStruc()
            pool.id = random.randint(700000,799999)
            pool.name = self.words.randomString(random.randint(5,25))
            self.pools[v] = pool
        else:
            pool = self.pools[v]
        row[i].value = pool.id
        row[self.getIndex("PoolName")].value = pool.name

   
    def processRTAHeaderRow(self,row):

        i = self.getIndex("WellEvent")
        v = row[i].value
        new_event = None
        if v in self.wellEvents:
            new_event = self.wellEvents[v]
        else:
            new_event = UWI(v)
            self.wellEvents[v] = new_event
            
        row[i].value = new_event.wellEvent
        row[self.getIndex("Name")].value = new_event.name
        
        i = self.getIndex("RTPOperator")
        v = row[i].value
        
        if not v in self.bas:
            ba = BA(v)
            self.bas[v] = ba
        else:
            ba = self.bas[v]
        
        row[i].value = ba.id
   
    def processRTAMineralOwnershipRow(self,row):

        i = self.getIndex("WellEvent")
        v = row[i].value
        new_event = None
        if v in self.wellEvents:
            new_event = self.wellEvents[v]
        else:
            new_event = UWI(v)
            self.wellEvents[v] = new_event
            
        row[i].value = new_event.wellEvent
        
   
    def processWellEventStatusRow(self,row):

        i = self.getIndex("WellEvent")
        v = row[i].value
        new_event = None
        if v in self.wellEvents:
            new_event = self.wellEvents[v]
        else:
            new_event = UWI(v)
            self.wellEvents[v] = new_event
            
        row[i].value = new_event.wellEvent

    def processWellInfoRow(self,row):

        i = self.getIndex("Well")
        v = row[i].value
        well = None
        if v in self.wells:
            well = self.wells[v]
        else:
            well = UWI(v)
            self.wells[v] = well
            
        row[i].value = well.well
        row[self.getIndex("WellName")].value = well.name
        
        wellLicence = 'W' + str(random.randint(70000,79999))
        well.wellLicence = wellLicence
        
        i = self.getIndex("WellLicence")
        v = row[i].value

        self.wellLicences[v] = well
        row[i].value = wellLicence
        
        row[self.getIndex("RangeAlt")].value = ''
        row[self.getIndex("TownshipAlt")].value = ''
        row[self.getIndex("SectionAlt")].value = ''

    def processWellLicenceRow(self,row):
        
        i = self.getIndex("WellLicence")
        v = row[i].value
        well = None
        if v in self.wellLicences:
            well = self.wellLicences[v]
        else:
            well = UWI('x')
            well.wellLicence = 'W??????'
            
        row[i].value = well.wellLicence
        
        i = self.getIndex("Licensee")
        v = row[i].value
        
        if not v in self.bas:
            ba = BA(v)
            self.bas[v] = ba
        else:
            ba = self.bas[v]
        
        row[i].value = ba.id


        row[self.getIndex("Meridian")].value = well.mer
        row[self.getIndex("Range")].value = well.rng
        row[self.getIndex("Township")].value = well.twp
        row[self.getIndex("Section")].value = well.sec
        row[self.getIndex("LSD")].value = well.lsd
        row[self.getIndex("LE")].value = well.le
        row[self.getIndex("ES")].value = well.es
        
        row[self.getIndex("ProjectedFormation")].value = ''
        row[self.getIndex("ProjectedFormationName")].value = ''
        row[self.getIndex("TerminatingFormation")].value = ''
        row[self.getIndex("TerminatingFormationName")].value = ''
        
        row[self.getIndex("RangeAlt")].value = ''
        row[self.getIndex("TownshipAlt")].value = ''
        row[self.getIndex("SectionAlt")].value = ''
   
    def processRTAWellsInPERow(self,row):

        i = self.getIndex("WellEvent")
        v = row[i].value
        well_event = None
        if v in self.wellEvents:
            well_event = self.wellEvents[v]
        else:
            well_event = UWI(v)
            self.wellEvents[v] = well_event
            
        row[i].value = well_event.wellEvent
        
        pe = 'W' + str(random.randint(7000000,7999999))
        row[self.getIndex("PE")].value = pe
        
   
    def processFacilityInfoRow(self,row):

        i = self.getIndex("Facility")
        v = row[i].value

        f = Facility(v)
        
        self.facilities[v] = f
        
        row[i].value = f.facility

        i = self.getIndex("FacLicence")
        v = row[i].value
        self.facLicences[v] = f
        row[i].value = f.facLicence

        row[self.getIndex("Name")].value = f.name

        row[self.getIndex("Meridian")].value = f.mer
        row[self.getIndex("Range")].value = f.rng
        row[self.getIndex("Township")].value = f.twp
        row[self.getIndex("Section")].value = f.sec
        row[self.getIndex("LSD")].value = f.lsd
        row[self.getIndex("LE")].value = f.le
        row[self.getIndex("ES")].value = f.es

        row[self.getIndex("RangeAlt")].value = ''
        row[self.getIndex("TownshipAlt")].value = ''
        row[self.getIndex("SectionAlt")].value = ''
        row[self.getIndex("ProvinceState")].value = 'PV'

        
    def processFacilityLicenceRow(self,row):

        i = self.getIndex("FacLicence")
        v = row[i].value
        
        if not v in self.facLicences:
            f = Facility(v)
            self.facLicences[v] = f
        else:
            f = self.facLicences[v]
        
        row[i].value = f.facLicence

        i = self.getIndex("Licensee")
        v = row[i].value
        
        if not v in self.bas:
            ba = BA(v)
            self.bas[v] = ba
        else:
            ba = self.bas[v]
        
        row[i].value = ba.id

        row[self.getIndex("Meridian")].value = f.mer
        row[self.getIndex("Range")].value = f.rng
        row[self.getIndex("Township")].value = f.twp
        row[self.getIndex("Section")].value = f.sec
        row[self.getIndex("LSD")].value = f.lsd
        row[self.getIndex("LE")].value = f.le
        row[self.getIndex("ES")].value = f.es

        row[self.getIndex("ProjectedFormation")].value = ''
        row[self.getIndex("TerminatingFormation")].value = ''

        row[self.getIndex("RangeAlt")].value = ''
        row[self.getIndex("TownshipAlt")].value = ''
        row[self.getIndex("SectionAlt")].value = ''
        
    def processFacilityOperatorRow(self,row):

        i = self.getIndex("Facility")
        v = row[i].value
        
        if not v in self.facilities:
            f = Facility(v)
            self.facLicences[v] = f
        else:
            f = self.facilities[v]
        
        row[i].value = f.facility

        i = self.getIndex("Operator")
        v = row[i].value
        
        if not v in self.bas:
            ba = BA(v)
            self.bas[v] = ba
        else:
            ba = self.bas[v]
        
        row[i].value = ba.id
        
    def processFacilityStatusRow(self,row):

        i = self.getIndex("Facility")
        v = row[i].value
        
        if not v in self.facilities:
            f = Facility(v)
            self.facLicences[v] = f
        else:
            f = self.facilities[v]
        
        row[i].value = f.facility
        
    def processWellFacilityLinkRow(self,row):

        i = self.getIndex("Facility")
        v = row[i].value
        
        if not v in self.facilities:
            f = Facility(v)
            self.facLicences[v] = f
        else:
            f = self.facilities[v]
        
        row[i].value = f.facility

        i = self.getIndex("WellEvent")
        v = row[i].value
        well_event = None
        if v in self.wellEvents:
            well_event = self.wellEvents[v]
        else:
            well_event = UWI(v)
            self.wellEvents[v] = well_event
            
        row[i].value = well_event.wellEvent

        
    def processRTPInfoRow(self,row):

        i = self.getIndex("WellEvent")
        v = row[i].value
        well_event = None
        if v in self.wellEvents:
            well_event = self.wellEvents[v]
        else:
            well_event = UWI(v)
            self.wellEvents[v] = well_event
            
        row[i].value = well_event.wellEvent

        i = self.getIndex("Payer")
        v = row[i].value
        
        if not v in self.bas:
            ba = BA(v)
            self.bas[v] = ba
        else:
            ba = self.bas[v]
        
        row[i].value = ba.id

        
    def processVolumetricInfoRow(self,row):

        i = self.getIndex("Facility")
        v = row[i].value
        
        if not v in self.facilities:
            f = Facility(v)
            self.facLicences[v] = f
        else:
            f = self.facilities[v]
        
        row[i].value = f.facility
        
        i = self.getIndex("FromTo")
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

    def processProrationFactorRow(self,row):

        i = self.getIndex("Facility")
        v = row[i].value
        
        if not v in self.facilities:
            f = Facility(v)
            self.facLicences[v] = f
        else:
            f = self.facilities[v]
        
        row[i].value = f.facility
            
        
    def processOVRTPFacilityRow(self,row):

        i = self.getIndex("RTPBA")
        v = row[i].value
        
        if not v in self.bas:
            ba = BA(v)
            self.bas[v] = ba
        else:
            ba = self.bas[v]
        
        row[i].value = ba.id
        
        i = self.getIndex("Facility")
        v = row[i].value
        
        if not v in self.facilities:
            f = Facility(v)
            self.facLicences[v] = f
        else:
            f = self.facilities[v]
        
        row[i].value = f.facility

        row[self.getIndex("DelFacility")].value = ''
            
        i = self.getIndex("RecFacility")
        v = row[i].value
        
        if not v in self.facilities:
            f = Facility(v)
            self.facLicences[v] = f
        else:
            f = self.facilities[v]
        
        row[i].value = f.facility

            
        i = self.getIndex("CTPFacility")
        v = row[i].value
        
        if not v in self.facilities:
            f = Facility(v)
            self.facLicences[v] = f
        else:
            f = self.facilities[v]
        
        row[i].value = f.facility


        i = self.getIndex("PurchaserBA")
        v = row[i].value
        
        if not v in self.bas:
            ba = BA(v)
            self.bas[v] = ba
        else:
            ba = self.bas[v]
        
        row[i].value = ba.id
        

        i = self.getIndex("GrossPrice")
        v = row[i].value
        
        rand = random.randint(1222,2222) / 1000        
        row[i].value = round(v*rand,2)

        i = self.getIndex("COTCharge")
        v = row[i].value
        
        rand = random.randint(1222,2222) / 1000        
        row[i].value = round(v*rand,2)
        
    def processOVRTPUnitRow(self,row):
        
        print("No Logic to handle processOVRRTPUnit")
        
        

"""
        self.processTab('Proration Factor',self.processProrationFactorRow)
        self.processTab('OVRTP Facility',self.processOVRTPFacilityRow)
"""


print('Hello World!')
o = Obfuscator('sample.xlsx')
o.process()
print('Catch you on the flip side!')

