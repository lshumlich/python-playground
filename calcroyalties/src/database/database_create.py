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
        if 'Calc' not in tables:
            self.calc()
        if 'ECONData' not in tables:
            self.econ_data()
        if 'LinkTab' not in tables:
            self.linktab()
        if 'Users' not in tables:
            self.users()

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
             "ValuationMethod" text,
             "TruckingDeducted" text,
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
            "Oper" text,
            "OperVol" float,
            "SalesPrice" float,
            "TransRate" float,
            "ProcessingRate" float,
            "GCARate" float);
        """
        self.dbi.execute_statement(statement)
        
    def calc(self):
        statement = """
            CREATE TABLE Calc ('ID' integer primary key autoincrement,
            "ProdMonth" int,
            "WellID" id,
            "Product" text,
            "Oper" text,
            "FNBandID" text,
            "FNReserveID" text,
            "K" int,
            "X" int,
            "C" int,
            "D" int,
            "RoyaltyPrice" float,
            "RoyaltyVolume" int,
            "ProvCrownRoyaltyRate" int,
            "ProvCrownUsedRoyaltyRate" int,
            "RoyaltyClassification" text,
            "IOGR1995RoyaltyRate" int,
            "GorrRoyaltyRate" int,
            "ProvCrownRoyaltyVolume" int,
            "GorrRoyaltyVolume" int,
            "IOGR1995WellRoyaltyVolume" float,
            "IOGR1995RoyaltyVolume" float,
            "ProvCrownRoyaltyValue" float,
            "IOGR1995RoyaltyValue" float,
            "GorrRoyaltyValue" float,
            "RoyaltyValuePreDeductions" float,
            "RoyaltyTransportation" int,
            "RoyaltyProcessing" int,
            "RoyaltyGCA" int,
            "SupplementaryRoyalties" int,
            "RoyaltyDeductions" int,
            "RoyaltyValue" float,
            "CommencementPeriod" float,
            "Message" text,
            "GorrMessage" text);
        """
        self.dbi.execute_statement(statement)
        
    def econ_data(self):
        statement = """
            CREATE TABLE ECONData ('ID' integer primary key autoincrement,
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

    def econ_gas_data(self):
        statement = """
            CREATE TABLE ECONGasData ('ID' integer primary key autoincrement,
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

        insert_statement = "insert into Users values(1,'admin','Admin Admin','info@thesolutionstack.com',201604, \
                           ' ,well_view,well_edit,wellevent_view,wellevent_edit,facility_view,lease_view,lease_edit," \
                           "welllease_view,welllease_edit,data_view,data_edit,users_view,users_edit');"
        self.dbi.execute(insert_statement)
