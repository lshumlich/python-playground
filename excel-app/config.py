#!/bin/env python3
"""
This is the application global object. It stores all relevant information 
for the application. Path to files, database used etc.

For clarity; A database_instance is the connection and all the raw
database commands whereas a database is the interface into all of 
the tables and all of the functionality we require from a database.
"""


import os

from database.apperror import AppError
from database.sqlite_instance import SqliteInstance


class ConfigObject(object):
    """
    A static config class to hold application level data.
    """
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

def get_default_database_name():
    return get_temp_dir() + 'unittest.db'

def get_database_instance(database_name=None):
    if database_name:
        ConfigObject.database_name = database_name
        ConfigObject.database_instance = SqliteInstance(database_name)
    if not ConfigObject.database_instance:
        ConfigObject.database_instance = SqliteInstance(get_default_database_name())
    return ConfigObject.database_instance
    
def get_database_name():
    return ConfigObject.database_name

def get_database():
    raise AppError("*** Code Not Complete **** Larry")
    