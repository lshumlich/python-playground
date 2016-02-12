"""

This is the application global object. It stores all relevant information 
for the application. Path to files, database used etc.

"""

import os

def wheresAreYou():
    BASE_DIR = os.path.dirname(__file__)
    print('From appinfo:',BASE_DIR)
    
def getFileDir():
    return os.path.dirname(__file__) +  "\\files\\"

