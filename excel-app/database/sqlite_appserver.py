#!/bin/env python3

import sys
from flask import Flask, render_template, request, flash

from database.sqlite_show import Shower
import config


class AppServer(object):
    
    print('we are running a class level in AppServer')
    app = Flask(__name__) 
#     appinfo.debug = True
    shower = Shower()
    
    def __init__(self):
#         AppServer.appinfo = Flask(__name__)
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
            
            tables = AppServer.shower.show_tables()
            header = None
            rows = None
            print('Table:',table)
            if table:
                header = AppServer.shower.show_columns(table)
                rows = AppServer.shower.show_table(table,attr,key)
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
    
def helloMsg():
    print('Hello World from ' + sys.argv[0])
    
def goodbyMsg():
    print("*** Done ***")

def sampleCode():
    print('we are in sample code')
    print('what do we do now')
    
def appServer():
#     appinfo = AppServer()
#     appinfo.run()
    AppServer.run(config.get_temp_dir() + 'browser.db')

if __name__ == '__main__':
    helloMsg()
    print('v2')
    appServer()
    # showTable(database,'well')
    goodbyMsg()
