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


class ConfigObject(object):
    """
    A static config class to hold application level data.
    """
    database_name = None
    database_instance = None
    database = None
    
    
class DatabaseInstance (object):
    """
    Has all the base database commands. This is to remove
    any knowladge of which database we are using from
    the problem solving code.
    """
    _instanceCount = 0
    
    def __init__(self,databaseName):
        
        DatabaseInstance._instanceCount += 1
        if DatabaseInstance._instanceCount > 1:
            raise AppError('Only one instance of DatabaseInstance is allowed. A second one was requested')
        
    

def where_am_i():
    BASE_DIR = os.path.dirname(__file__)
    print('From appinfo:',BASE_DIR)
    
def get_file_dir():
    return os.path.join(os.path.dirname(__file__), "files/")
    
def get_temp_dir():
    return os.path.join(os.path.dirname(__file__), "tempfiles/")

def set_default_database_name():
    """ 
    *** VERY IMPORTANT *** this database will be delete in most of 
    the test.... This can never be changed to test qa or prod database...
    """
    ConfigObject.database = get_default_database_name()

def get_default_database_name():
    return 'testdb.db'
    
def get_database_name():
    raise AppError("*** Code Not Complete **** Larry")
#     return ConfigObject.database_name
    
def get_database_instance():
    raise AppError("*** Code Not Complete **** Larry")
#     if not ConfigObject.database_instance:
#         if not ConfigObject.database_name:
#             set_default_database_name()
            
            

def get_database():
    raise AppError("*** Code Not Complete **** Larry")
    if not ConfigObject.database:
        set_default_database_name # This Must Change()
    
    return ConfigObject.database
    
def set_database_name(name):
    raise AppError("*** Code Not Complete **** Larry")
    if ConfigObject.database:
        raise AppError('config.get_database has already been called. config.set_database can not. ' + name)
    ConfigObject.database = name
    
    