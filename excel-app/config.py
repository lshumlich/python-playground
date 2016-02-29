#!/bin/env python3
"""
This is the application global object. It stores all relevant information 
for the application. Path to files, database used etc.

For clarity; A database_instance is the connection and all the raw
database commands whereas a database is the interface into all of 
the tables and all of the functionality we require from a database.
"""


import os,json

from database.sqlite_instance import SqliteInstance
from database.sqlite_database import Database


class ConfigObject(object):
    """
    A static config class to hold application level data.
    """
    CONFIG_FILE = 'config.json'
    environment = None
    database_name = None
    database_instance = None
    database = None
    
def where_am_i():
    BASE_DIR = os.path.dirname(__file__)
    print('From appinfo:',BASE_DIR)
    
def get_file_dir():
    return os.path.join(os.path.dirname(__file__), "files/")
    
def get_temp_dir():
    return os.path.join(os.path.dirname(__file__), "tempfiles/")

def reset():
    """ only used in test situations """
    ConfigObject.environment = None
    ConfigObject.database_name = None
    ConfigObject.database_instance = None
    ConfigObject.database = None

def set_enviornment(environment):
    """ only used in test situations, valid values are unittest, test, qa, prod """
    reset()
    ConfigObject.environment = environment
    
def set_database_name(name):
    reset()
    ConfigObject.database_name = name
    
def setup_environment():
    if not ConfigObject.database_name and not ConfigObject.environment:
        configFile = get_temp_dir() + ConfigObject.CONFIG_FILE
        if not os.path.exists(configFile):
            ConfigObject.environment = 'unittest'
        else :
            with open(configFile) as json_file:
                json_data = json.load(json_file)
                if 'environment' in json_data:
                    ConfigObject.environment = json_data['environment']
                if 'databasename' in json_data:
                    ConfigObject.database_name = get_temp_dir() + json_data['databasename']
                
    if ConfigObject.database_name and not ConfigObject.environment:
        ConfigObject.environment = "????"
                
    if not ConfigObject.database_name and not ConfigObject.environment:
        ConfigObject.environment = "unittest"

    if not ConfigObject.database_name and ConfigObject.environment:
        ConfigObject.database_name = ":memory:"
#         ConfigObject.database_name = get_temp_dir() + ConfigObject.environment + '.db'
        
    print("Setting Environment to:",ConfigObject.environment,ConfigObject.database_name)
        
    ConfigObject.database_instance = SqliteInstance(ConfigObject.database_name)
    ConfigObject.database = Database()
    
def get_environment():
    if not ConfigObject.environment:
        setup_environment()
    return ConfigObject.environment
    
def get_database_name():
    if not ConfigObject.database_name:
        setup_environment()
    return ConfigObject.database_name
    
def get_database_instance():
    if not ConfigObject.database_instance:
        setup_environment()
    return ConfigObject.database_instance

def get_database():
    if not ConfigObject.database:
        setup_environment()
    return ConfigObject.database
    