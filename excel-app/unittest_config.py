#!/bin/env python3
"""
This is the application global object for unit testing. It stores 
all relevent unit test information 
for the application. 

For clarity; A database_instance is the connection and all the raw
database commands whereas a database is the interface into all of 
the tables and all of the functionality we require from a database.
"""


from database.apperror import AppError
from database.sqlite_instance import SqliteInstance
import config


class UnittestConfigObject(object):
    """
    A static config class to hold application level data.
    """
    database_name = None
    database_instance = None
    database = None
    
def get_default_database_name():
    return config.get_temp_dir() + 'unittest.db'

def get_database_instance(database_name=None):
    if database_name:
        UnittestConfigObject.database_name = database_name
        UnittestConfigObject.database_instance = SqliteInstance(database_name)
    if not UnittestConfigObject.database_instance:
        UnittestConfigObject.database_instance = SqliteInstance(get_default_database_name())
    return UnittestConfigObject.database_instance
    
def get_database_name():
    return UnittestConfigObject.database_name

def database_reset():
    """ Should only be used for unit testing """
    UnittestConfigObject.database_name = None
    UnittestConfigObject.database_instance = None
    UnittestConfigObject.database = None

def get_database():
    raise AppError("*** Code Not Complete **** Larry")
    