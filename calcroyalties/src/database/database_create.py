#!/bin/env python3

"""
This is the system's only database creation script.

To Update, do the following:

1) Update the database version #
2) Make whatever updates you need

Database Change Log: Must be maintained so we can keep the database in sink:

2016-10-07
- WellLeaseLink change WellEvent to WellID
- Monthly change WellEvent to WellID
- Calc change WellEvent to WellID
2016-10-13
- Rename RoyaltyMaster.MinRoyalty to MinRoyaltyDollar
- move MinRoyaltyDollar to the min section of RoyaltyMaster
- remove well PEFNInterest, Lease, LeaseType
2016-10-16
- Rename Well to WellRoyaltyMaster
- Rename RoyaltyMaster to LeaseRoyaltyMaster
2016-10-25
- Rename Monthly.WellHeadPrice to SalesPrice
- Remove Monthly.TransPrice
2016-11-03
- Add LeaseRoyaltyMaster.CrownModifier
- Remove Lease.LessorID
2016-11-04
- Add Monthly.Oper
- Add Monthly.OperVol
2016-11-08
- Remove Calc.RoyaltyRegulation
- Add Calc.IOGR1995WellRoyaltyVolume
- Add Calc.RoyaltyClassification
2016-11-09
- Add Calc.Oper
- Add Calc.FNBandID
- Add Calc.FNReserveID (Note: Add logic to pick the correct one
- Add WellRoyaltyMaster.PrimaryReserve
2016-11-14
- Rename Calc.Oper to RPBA
- Rename Monthly.Oper to RPBA
- Rename Monthly.OperVol to RPVol
- Rename DataDictionary.Table to TableName
2016-11-21
- Rename LeaseRoyaltyMaster.TruckingDeducted to TransDeducted
- Remove Calc.RoyaltyTransportation
- Add Calc.TransBaseValue
- Add Calc.TransGorrValue
- Remove Calc.RoyaltyProcessing
- Add Calc.ProcessingBaseValue
- Add Calc.ProcessingGorrValue
- Rename Calc.RoyaltyValuePreDeductions to GrossRoyaltyValue
- Rename Calc.RoyaltyValue to NetRoyaltyValue
- Add Table RTPInfo
- Add RTPInfo.ID
- Rename calc.ProvCrownUsedRoyaltyRate to BaseRoyaltyRate
- Rename calc.ProvCrownRoyaltyRate to BaseRoyaltyCalcRate
- Rename calc.ProvCrownRoyaltyValue to BaseRoyaltyValue
- Rename calc.ProvCrownRoyaltyVolume to BaseRoyaltyVolume
2016-11-22
- Remove Calc tab from sample.xlsx (The create database creates a blank one and the process creates updated ones.
- Rename Calc.IOGR1995RoyaltyVolume to BaseRoyaltyVolume
- Rename Calc.IOGR1995RoyaltyValue to BaseRoyaltyValue
- Rename Calc.SupplementaryRoyalties to SuppRoyaltyValue
- Delete Calc.IOGR1995RoyaltyRate
- Delete Calc.IOGR1995WellRoyaltyVolume
- Delete Calc.IOGR1995RoyaltyVolume
- Delete Calc.IOGR1995RoyaltyValue
- Delete Calc.GorrRoyaltyVolume
2017-02-19
- Add calc.RoyaltySpecific
- Add monthly.SalesVol
2017-03-15
- Add LeaseRoyatlyMaster.OilBasedOn
  Add LeaseRoyatlyMaster.GasBasedOn
  Add LeaseRoyatlyMaster.ProductsBasedOn
  Add Monthly.GJ
  Add Lookups table
2017-03-19
  Add Calc.RTPInterest
  Add Calc.PEFNInterest
  Add Calc.LeaseID
  Add Calc.RoyaltyBasedOn
  Add Calc.RoyaltyBasedOnVol
  Reorder Calc Table
2017-03-21
  add Calc.RoyaltyPriceExplanation
2017-03-23
  add Monthly.Heat
2017-03-23
  Change DataDictionary.Order to SortOrder
2017-04-07
  Change LeaseRoyaltyMaster.ValuationMethod --> OilPriceBasedOn
  Add LeaseRoyaltyMaster.GasPriceBasedOn
  Add LeaseRoyaltyMaster.ProductsPriceBasedOn
  Add LeaseRoyaltyMaster.GasValueBasedOn
  Add LeaseRoyaltyMaster.OilValueBasedOn
  Add LeaseRoyaltyMaster.ProductsValueBasedOn
"""

import datetime

import config


class DatabaseCreate(object):
    
    DATABASE_VERSION = 1.1

    def __init__(self):
        self.dbi = config.get_database_instance()
        
    def create_all(self):
        tables = self.dbi.get_table_names()
        if 'Config' not in tables:
            self.config()
        if 'WellRoyaltyMaster' not in tables:
            self.well_royalty_master()
        if 'LeaseRoyaltyMaster' not in tables:
            self.lease_royalty_master()
        if 'Lease' not in tables:
            self.lease()
        if 'WellLeaseLink' not in tables:
            self.well_lease_link()
        if 'Monthly' not in tables:
            self.monthly()
        if 'Lookups' not in tables:
            self.lookups()
        if 'Calc' not in tables:
            self.calc()
        if 'ECONData' not in tables:
            self.econ_oil()
        if 'LinkTab' not in tables:
            self.linktab()
        if 'Users' not in tables:
            self.users()
        if 'RTPInfo' not in tables:
            self.rtp_info()
        if 'DataDictionary' not in tables:
            self.data_dictionary()

        self.dbi.commit()

    def config(self):
        statement = """
            CREATE TABLE Config ('ID' integer primary key autoincrement, 
            'Version' int, CreateDate timestamp);
        """
        self.dbi.execute_statement(statement)
        
        insert_statement = "insert into Config (Version, CreateDate) values(" + str(DatabaseCreate.DATABASE_VERSION) \
                           + ",'" + str(datetime.datetime.now()) + "');"
        self.dbi.execute(insert_statement)

    def well_royalty_master(self):
        statement = """
            CREATE TABLE WellRoyaltyMaster ('ID' integer primary key autoincrement,
             "StartDate" timestamp,
             "EndDate" timestamp,
             'WellEvent' text,
             'Prov' text,
             'WellType' text,
             "PrimaryReserve" text,
             'RoyaltyClassification' text,
             'Classification' text,
             'SRC' int,
             'CommencementDate' timestamp,
             'ReferencePrice' int,
             "FinishDrillDate" timestamp,
             "HorizontalDrilllnd" text,
             "Notes" text);
        """
        self.dbi.execute_statement(statement)
        
    def lease_royalty_master(self):
        statement = """
            CREATE TABLE LeaseRoyaltyMaster ('ID' integer primary key autoincrement,
             "StartDate" timestamp,
             "EndDate" timestamp,
             "RightsGranted" text,
             "RoyaltyScheme" text,
             "CrownMultiplier" float,
             "CrownModifier" float,
             "OilPriceBasedOn" text,
             "GasPriceBasedOn" text,
             "ProductsPriceBasedOn" text,
             "OilValueBasedOn" text,
             "GasValueBasedOn" text,
             "ProductsValueBasedOn" text,
             "OilBasedOn" text,
             "GasBasedOn" text,
             "ProductsBasedOn" text,
             "TransDeducted" text,
             "ProcessingDeducted" text,
             "GCADeducted" text,
             "Gorr" text,
             "OverrideRoyaltyClassification" text,
             "MinRoyaltyRate" float,
             "MaxRoyaltyRate" float,
             "MinRoyaltyDollar" float,
             "Notes" text);
        """
        self.dbi.execute_statement(statement)
        
    def lease(self):
        statement = """
            CREATE TABLE Lease ('ID' integer primary key autoincrement,
             "StartDate" timestamp,
             "EndDate" timestamp,
             "LeaseType" text,
             "Prov" text,
             "FNReserveID" int,
             "FNBandID" int,
             "Notes" text);
        """
        self.dbi.execute_statement(statement)
        
    def well_lease_link(self):
        statement = """
            CREATE TABLE WellLeaseLink ('ID' integer primary key autoincrement,
             "StartDate" timestamp,
             "EndDate" timestamp,
             "WellID" int,
             "LeaseID" int,
             "PEFNInterest" float);
        """
        self.dbi.execute_statement(statement)

    def monthly(self):
        statement = """
            CREATE TABLE Monthly ('ID' integer primary key autoincrement, 
            "ExtractMonth" timestamp,
            "ProdMonth" int,
            "WellID" int,
            "Product" text,
            "AmendNo" int,
            "ProdHours" int,
            "ProdVol" int,
            "SalesVol" int,
            "Heat" int,
            "GJ" int,
            "RPBA" text,
            "RPVol" float,
            "SalesPrice" float,
            "TransRate" float,
            "ProcessingRate" float,
            "GCARate" float);
        """
        self.dbi.execute_statement(statement)

    def lookups(self):
        statement = """
            CREATE TABLE Lookups ('ID' integer primary key autoincrement,
            "Name" text,
            "ProdMonth" int,
            "Value" int);
        """
        self.dbi.execute_statement(statement)

    def calc(self):
        statement = """
            CREATE TABLE Calc ('ID' integer primary key autoincrement,
            "ProdMonth" int,
            "WellID" int,
            "Product" text,
            "RPBA" text,
            "FNBandID" text,
            "FNReserveID" text,
            "LeaseID" int,
            "RoyaltyBasedOn" text,
            "RoyaltyBasedOnVol" float,
            "SalesPrice" float,
            "RTPInterest" int,
            "PEFNInterest" float,
            "NetRoyaltyValue" float,
            "GrossRoyaltyValue" float,
            "K" int,
            "X" int,
            "C" int,
            "D" int,
            "RoyaltyClassification" text,
            "RoyaltyPrice" float,
            "RoyaltyPriceExplanation" text,
            "RoyaltyVolume" int,
            "BaseRoyaltyCalcRate" int,
            "BaseRoyaltyRate" int,
            "GorrRoyaltyRate" int,
            "BaseRoyaltyVolume" int,
            "BaseRoyaltyValue" float,
            "SuppRoyaltyValue" int,
            "GorrRoyaltyValue" float,
            "TransBaseValue" float,
            "TransGorrValue" float,
            "ProcessingBaseValue" float,
            "ProcessingGorrValue" float,
            "RoyaltyGCA" float,
            "RoyaltyDeductions" int,
            "CommencementPeriod" float,
            "Message" text,
            "GorrMessage" text,
            "RoyaltySpecific" text);
        """
        self.dbi.execute_statement(statement)
        
    def econ_oil(self):
        statement = """
            CREATE TABLE ECONOil ('ID' integer primary key autoincrement,
            "CharMonth" text,
            "ProdMonth" int,
            "HOP" int,
            "SOP" int,
            "NOP" int,
            "H4T_C" float, "H4T_D" float, "H4T_K" float, "H4T_X" int, 
            "H3T_K" float, "H3T_X" int, 
            "HNEW_K" float, "HNEW_X" int, 
            "SW4T_C" float, "SW4T_D" float, "SW4T_K" float, "SW4T_X" int,
            "SW3T_K" float, "SW3T_X" int,
            "SWNEW_K" float, "SWNEW_X" int, 
            "O4T_C" float, "O4T_D" float, "O4T_K" float, "O4T_X" int, 
            "O3T_K" float, "O3T_X" int, 
            "ONEW_K" float, "ONEW_X" int, 
            "OOLD_K" float, "OOLD_X" int);
        """
        self.dbi.execute_statement(statement)

    def econ_gas(self):
        statement = """
            CREATE TABLE ECONGas ('ID' integer primary key autoincrement,
            "CharMonth" text, "ProdMonth" int,
            "G4T_C" int, "G4T_D" int, "G4T_K" int,
            "G4T_X" float, "G3T_C" float, "G3T_K" float, "G3T_X" int,
            "GNEW_C" float, "GNEW_K" int,
            "GNEW_X" float, "GOLD_C" int,
            "GOLD_K" float, "GOLD_X" float);
        """
        self.dbi.execute_statement(statement)

    def linktab(self):
        statement = """
            create table LinkTab ('ID' integer primary key autoincrement,
            TabName text, AttrName text, LinkName text, BaseTab boolean, ShowAttrs text);
        """
        self.dbi.execute_statement(statement)

    def users(self):
        statement = """
            CREATE TABLE Users (
                "ID"	INTEGER PRIMARY KEY AUTOINCREMENT,
                "Login"	TEXT,
                "Name"	TEXT,
                "Email"	TEXT,
                "ProdMonth"	INTEGER,
                "Permissions"	TEXT)
        """
        self.dbi.execute_statement(statement)

        insert_statement = "insert into Users values(1,'admin','Admin Admin','info@leanminds.com',201609, \
                           ' ,well_view,well_edit,wellevent_view,wellevent_edit,facility_view,lease_view,lease_edit," \
                           "welllease_view,welllease_edit,data_view,data_edit,users_view,users_edit');"
        self.dbi.execute(insert_statement)

    def rtp_info(self):
        statement = """
            CREATE TABLE RTPInfo (
                "ID"	    INTEGER PRIMARY KEY AUTOINCREMENT,
                "WellEvent"	TEXT,
                "Product"	TEXT,
                "StartDate" timestamp,
                "EndDate"   timestamp,
                "Payer"	    TEXT,
                "MineralOwnershipType"	TEXT,
                "Percent"	Float)
        """
        self.dbi.execute_statement(statement)

    def data_dictionary(self):
        statement = """
            CREATE TABLE DataDictionary (
                "ID"	        INTEGER PRIMARY KEY AUTOINCREMENT,
                "TableName"	    TEXT,
                "SortOrder"	    int,
                "Attribute"	    TEXT,
                "Documentation"	TEXT)
        """
        self.dbi.execute_statement(statement)
