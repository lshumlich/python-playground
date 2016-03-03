#!/bin/env python3

import json
import sys,traceback
from flask import Flask, render_template, request, flash

from database.sqlite_show import Shower
from database.data_structure import DataStructure
from database.utils import Utils
import config


class AppServer(object):
    
    print('we are running a class level in AppServer')
    app = Flask(__name__) 
#     appinfo.debug = True
    shower = Shower()
    db = config.get_database()
    
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
    @app.route("/data/linkxxx/",methods=['GET','POST']) 
    def xxx_link():
        print('AppServer.link2 running',request.method)
        tablename = None
        attrname = None
        linkname = None
        try:
            if request.method == 'POST':
                print('  It was a post')
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
                    AppServer.shower.insert_link(tablename, attrname, linkname,0,'id')
                    return render_template('closeme.html')
            else:   
                print('  It was a get')
                tablename = AppServer.reqorblank('tablename')
                attrname = AppServer.reqorblank('attrname')
                linkname = AppServer.reqorblank('linkname')
            
            html = render_template('link.html',tablename=tablename,attrname=attrname,linkname=linkname)
            
        except Exception as e:
            print('AppServer.link: ***Error:',e)
            traceback.print_exc(file=sys.stdout)
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
        AppServer.shower.connect()
#         AppServer.db = config.get_database()
        print('starting the run method of AppServer')
        AppServer.app.secret_key = 'secret'
        AppServer.app.run()
        print('after the run in run in AppServer')
    