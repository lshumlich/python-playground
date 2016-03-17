#!/bin/env python3

"""
This is the system's only database creation script. 

To Update, do the following:

1) Update the database version #
2) Make whatever updates you need

"""
import datetime

import config

class DatabaseCreate(object):
    
    DATABASE_VERSION = 1

    def __init__(self):
        self.dbi = config.get_database_instance()
        
    def create_all(self):
        tables = self.dbi.get_table_names()
        if not 'Config' in tables:
            self.config()
        if not 'Well' in tables:
            self.well()
        if not 'RoyaltyMaster' in tables:
            self.royaltymaster()
        if not 'Lease' in tables:
            self.lease()
        if not 'Monthly' in tables:
            self.monthly()
        if not 'Calc' in tables:
            self.calc()
        if not 'ECONData' in tables:
            self.econdata()
        if not 'LinkTab' in tables:
            self.linktab()
        
    def config(self):
        statement = """
            CREATE TABLE Config ('ID' integer primary key autoincrement, 
            'Version' int, CreateDate timestamp);
        """
        self.dbi.execute_statement(statement)
        
        insertStatement = "insert into Config (Version, CreateDate) values(" + str(DatabaseCreate.DATABASE_VERSION) + ",'" + str(datetime.datetime.now()) + "');"
        self.dbi.execute(insertStatement)

    def well(self):
        statement = """
            CREATE TABLE Well ('ID' integer primary key autoincrement, 
            'UWI' text, 'Prov' text, 'WellType' text, 'LeaseType' text, 
            'LeaseID' int, 'RoyaltyClassification' text, 
            'Classification' text, 'SRC' int, 'IndianInterest' float, 
            'CommencementDate' timestamp, 'ReferencePrice' int);
        """
        self.dbi.execute_statement(statement)
        
    def royaltymaster(self):
        statement = """
            CREATE TABLE RoyaltyMaster ('ID' integer primary key autoincrement, 
            "LeaseType" text, "RightsGranted" text, "RoyaltyScheme" text, 
            "CrownMultiplier" float, "MinRoyalty" int, "ValuationMethod" text,
            "TruckingDeducted" text, "ProcessingDeducted" text, "Gorr" text,
             "Notes" text);
        """
        self.dbi.execute_statement(statement)
        
    def lease(self):
        statement = """
            CREATE TABLE Lease ('ID' integer primary key autoincrement, 
            "LeaseType" text, "Prov" text, "FNReserve" int, "Lessor" int, 
            "Notes" text);
        """
        self.dbi.execute_statement(statement)
        
    def monthly(self):
        statement = """
            CREATE TABLE Monthly ('ID' integer primary key autoincrement, 
            "ExtractMonth" timestamp, "ProdMonth" int, "WellID" int, "Product" text,
            "AmendNo" int, "ProdHours" int, "ProdVol" int, "TransPrice" float, 
            "WellHeadPrice" float, "TransRate" float, "ProcessingRate" float);
        """
        self.dbi.execute_statement(statement)
        
    def calc(self):
        statement = """
            CREATE TABLE Calc ('ID' integer primary key autoincrement, 
            "ProdMonth" int, "WellID" int, 
            "K" int, "X" int, "C" int, "D" int, 
            "RoyaltyPrice" float, "RoyaltyVolume" int, "ProvCrownRoyaltyRate" int, 
            "ProvCrownUsedRoyaltyRate" int, "IOGR1995RoyaltyRate" int, 
            "GorrRoyaltyRate" int, "ProvCrownRoyaltyVolume" int, 
            "GorrRoyaltyVolume" int, "IOGR1995RoyaltyVolume" int, 
            "ProvCrownRoyaltyValue" int, "IOGR1995RoyaltyValue" float, 
            "GorrRoyaltyValue" float, "RoyaltyValuePreDeductions" float, 
            "RoyaltyTransportation" int, "RoyaltyProcessing" int, 
            "RoyaltyDeductions" int, "RoyaltyValue" float, 
            "CommencementPeriod" float, "Message" text, "GorrMessage" text);
        """
        self.dbi.execute_statement(statement)
        
    def econdata(self):
        statement = """
            CREATE TABLE ECONData ('ID' integer primary key autoincrement,
            "CharMonth" text, "ProdMonth" int, 
            "HOP" int, "SOP" int, "NOP" int, 
            "H4T_C" float, "H4T_D" float, "H4T_K" float, "H4T_X" int, 
            "H3T_K" float, "H3T_X" int, 
            "HNEW_K" float, "HNEW_X" int, 
            "SW4T_C" float, "SW4T_D" float, "SW4T_K" float, "SW4T_X" int, "
            SW3T_K" float, "SW3T_X" int, 
            "SWNEW_K" float, "SWNEW_X" int, 
            "O4T_C" float, "O4T_D" float, "O4T_K" float, "O4T_X" int, 
            "O3T_K" float, "O3T_X" int, 
            "ONEW_K" float, "ONEW_X" int, 
            "OOLD_K" float, "OOLD_X" int);
        """
        self.dbi.execute_statement(statement)

    def linktab(self):        
        statement = """
            create table LinkTab ('ID' integer primary key autoincrement,
            TabName text, AttrName text, LinkName text, BaseTab boolean, ShowAttrs text);
        """
        self.dbi.execute_statement(statement)
