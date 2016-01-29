import os
import sys
import datetime
import traceback
import sqlite3
from sqlite3 import OperationalError
from flask import Flask, render_template, url_for, request, flash

from openpyxl import load_workbook
from openpyxl import Workbook
from sqlalchemy.sql.base import ColumnSet


class Loader(object):

    def connect(self,dbName):
        self.conn = sqlite3.connect(dbName)
        self.cursor = self.conn.cursor()
        
    def execute(self,statement):
        # Create table
        return self.cursor.execute(statement)

    def commit(self):
        # Save (commit) the changes
        self.conn.commit()
        
        # We can also close the connection if we are done with it.
        # Just be sure any changes have been committed or they will be lost.
    def close(self):
        self.conn.close()

    def openExcel(self, workbookName):
        self.wb = load_workbook(workbookName)
        
    def loadAllSheets(self):
        sheets = self.wb.get_sheet_names()
        for sheet in sheets:
            print ('loading:', sheet)
            self.LoadWorksheet(sheet)

    def LoadWorksheet(self,tabName):
        try:
            
            ws = self.wb[tabName]
            tableName = tabName.replace(' ', '')
            if len(ws.rows) > 1:
                recordNo = 0;
                headerRow = None
                for row in ws.rows:
                    if not headerRow:
                        headerRow = row
                        self.createTable(tableName,headerRow, ws.rows[1])
                    else:
                        recordNo = recordNo +1
                        self.insertData(tableName,row, headerRow)
                self.commit()
            else:
                print('*** No data to load for tab:', tabName)
        except Exception as e:
            raise e
                
    def createTable(self,tableName,headerRow, dataRow):

        self.deleteTable(tableName)
       
        tableCreate = 'CREATE TABLE ' + tableName + '('
        cols = ""
        i = 0
        for cell in headerRow:
            name = cell.value.replace('#','')
            if type(dataRow[i].value) is str:
                cols = cols + name + ' text, '
            elif type(dataRow[i].value) is int:
                cols = cols + str(name) + ' int, '
            elif type(dataRow[i].value) is float:
                cols = cols + str(name) + ' float, '
            elif type(dataRow[i].value) is datetime.datetime:
                cols = cols + str(name) + ' date, '
            else:
                cols = cols + name + ' text, '
                print('*** Null first line so defaulting to str',cell.value,type(dataRow[i].value))
            i += 1
            
        cols = cols + ')'
        cols = cols.replace(', )', ')')
        
        tableCreate = tableCreate + cols
    
        
        print(tableCreate)
        self.execute(tableCreate)
        self.commit()

    def deleteTable(self,tableName):
        
        try:
            self.execute('drop table ' + tableName)
        except sqlite3.OperationalError:
            print("Table did not exist so not deleted:", tableName)

        
    def insertData(self,tableName,row, headerRow):
        insert = 'INSERT INTO ' + tableName + ' VALUES ('
        data = ""
        i = 0
        
        for h in headerRow:
            cell = row[i]
            if type(cell.value) is str:
                data = data + "'" + cell.value + "',"
            elif type(cell.value) is int:
                data = data +  str(cell.value) + ","
            elif type(cell.value) is float:
                data = data +  str(cell.value) + ","
            elif type(cell.value) is datetime.datetime:
                data = data +  "'" + str(cell.value) + "',"
#                 data = data +  str(cell.value.strftime("%Y/%m/%d")) + ","
            elif cell.value is None:
                data = data +  " Null,"
            else:
                print('*** Not Loaded',cell.value, type(cell.value))
            i += 1

            
        data = data + ')'
        data = data.replace(',)', ')')
        
        insert = insert + data
            
        print(insert)
        self.execute(insert)
        
            
class Shower(object):
    
    def __init__(self):
        print('Shower.__init__', self)

    def connect(self,dbName):
        print('Shower opening connection to:', dbName)
        self.conn = sqlite3.connect(dbName)
        self.cursor = self.conn.cursor()
        
    def insertLink(self,tab,att,lnk):
        stmt = 'insert into linktab values("' + tab + '", "' + att + '", "' + lnk + '")'
        self.cursor.execute(stmt)
        self.conn.commit()
        
    def execute(self,statement):
        return self.cursor.execute(statement)
    
    def commit(self):
        self.conn.commit()

    def close(self):
        self.conn.close()

    def showTable(self,tableName,attr=None,key=None):
        stmt = 'select * from ' + tableName
        if key:
            type = self.columnType(tableName, attr)
            where = ''
            if type == 'int':
                where = attr + "=" + key
            elif type =='text':
                where = attr + "='" + key + "'"
            else:
                print('***** Type not delt with:', type,tableName,attr)
            
            stmt = stmt + " where " + where
        elif attr:
            stmt = stmt + " order by " + attr
        print('SQL:', stmt)
        values = self.execute(stmt)
        return values;
        
    def showTables(self):
        stmt = 'select tbl_name from sqlite_master'
        values = self.execute(stmt)
        tables = []
        for row in values:
            tables.append(row[0])
        return(tables)

    def showColumns(self,tableName):
        stmt = 'pragma table_info(' + tableName + ')'
        values = self.execute(stmt)
        columns = []
        for row in values:
            columns.append(row[1])
        return(columns)
    
    def columnType(self,table,column):
        stmt = 'pragma table_info(' + table + ')'
        values = self.execute(stmt)
        for row in values:
            if row[1] == column:
                return row[2]
        return(None)
        
    
            
class AppServer(object):
    
    print('we are running a class level in AppServer')
    app = Flask(__name__) 
#     app.debug = True
    shower = Shower()
    
    def __init__(self):
#         AppServer.app = Flask(__name__)
        print("in init of AppServer")
        
    @staticmethod
    @app.route("/")
    def hello():
        print('should be at root')
        return "hello World! v4"
    
    @staticmethod
    @app.route("/hello/<username>")
    def helloab(username):
        print('should be at /ab/')
        return "hello World/hello/" + username
    
    @staticmethod
    @app.route("/data/")
    def data():
        try:
            table=request.args.get('table')
            attr=request.args.get('attr')
            key=request.args.get('key')
            links = {}
            links['BAid'] = '?table=BAInfo&attr=BAid&key=' 
            links['WellEvent'] = '?table=WellInfo&attr=Well&key='
            
            tables = AppServer.shower.showTables()
            header = None
            rows = None
            print('Table:',table)
            if table:
                header = AppServer.shower.showColumns(table)
                rows = AppServer.shower.showTable(table,attr,key)
            html = render_template('data.html',table=table,tables=tables,header=header,rows=rows,links=links)
        except Exception as e:
            print('AppServer.data: ***Error:',e)

        return html
    
    @staticmethod
    @app.route("/link/",methods=['GET','POST']) 
    def link():
        tablename = None
        attrname = None
        linkname = None
        try:
            print('AppServer.link running')
            if request.method == 'POST':
                tablename = request.form['tablename']
                attrname = request.form['attrname']
                linkname = request.form['linkname']
            
                error = False
                if tablename == '':
                    error = True
                    flash('Table name must be entered.')
                if attrname == '':
                    error = True
                    flash('Attribute name must be entered.')
                if linkname == '':
                    error = True
                    flash('Link name must be entered.')
                    
                if not error:
                    AppServer.shower.insertLink(tablename, attrname, linkname)
                    return render_template('closeme.html')
            else:   
                tablename = AppServer.reqorblank('tablename')
                attrname = AppServer.reqorblank('attrname')
                linkname = AppServer.reqorblank('linkname')
            
            html = render_template('link.html',tablename=tablename,attrname=attrname,linkname=linkname)
            
        except Exception as e:
            print('AppServer.link: ***Error:',e)
        return html
    
    @staticmethod
    def reqorblank(reqname):
        a = request.args.get(reqname)
        print('value of a:',a)
        if a:
            return a
        else:
            return ''

    @staticmethod
    def run(dbName):
        print("Starting AppServer.run")
        AppServer.shower.connect(dbName)
        print('starting the run method of AppServer')
        AppServer.app.secret_key = 'secret'
        AppServer.app.run()
        print('after the run in run in AppServer')
    

database = 'testload.db'
def helloMsg():
    print('Hello World from ' + sys.argv[0])
    

def loadExcelToDb():
    loader = Loader()
    loader.connect(database)
    loader.openExcel(r'd:/$temp/Onion Lake SK wells.xlsx')
    loader.loadAllSheets()
    loader.loadExcel("database.xlsx")
    loader.close()
    
def showStuff():
    loader = Loader()
    loader.LoadWorksheet('Well')
    loader.showTables()
    loader.showTable('well')
    loader.showTables()
    loader.showColumns('well')
    loader.close()

def goodbyMsg():
    print("*** Done ***")

def sampleCode():
    print('we are in sample code')
    print('what do we do now')
    
def appServer():
#     app = AppServer()
#     app.run()
    AppServer.run(database)

def showTables(dbName):
    shower = Shower()
    shower.connect(dbName)
    value = shower.showTables()
    print(type(value))
    print(value)

def showTable(dbName, tableName):
    shower = Shower()
    shower.connect(dbName)
    header = shower.showColumns(tableName)
    print(header)
    rows = shower.showTable(tableName,'Prov','SK')
    for row in rows:
        print(row)

helloMsg()
print('v2')
appServer()
# showTable(database,'well')
goodbyMsg()
