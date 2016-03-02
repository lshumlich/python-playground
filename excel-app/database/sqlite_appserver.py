#!/bin/env python3

import json
import sys,traceback
from flask import Flask, render_template, request, flash

from database.sqlite_show import Shower
from database.data_structure import DataStructure
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
    @app.route("/data/",methods=['GET','POST'])
    def data():
        try:
            table=request.args.get('table')
            attr=request.args.get('attr')
            key=request.args.get('key')
            links = {}
            links['BAid'] = '?table=BAInfo&attr=BAid&key=' 
            links['WellEvent'] = '?table=WellInfo&attr=Well&key='
            
            tables = AppServer.shower.dbi.get_table_names()
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
    @app.route("/data/link/",methods=['GET','POST']) 
    def link():
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
    @app.route("/data/link.json",methods=['POST']) 
    def link_json():
        print('AppServer.link_json running',request.method)
        data = AppServer.json_decode(request)

        return 'Thats it folks'

    @staticmethod
    @app.route("/data/getLinkRow.json",methods=['POST']) 
    def get_link_row():
        try:
            print('AppServer.get_link_row running',request.method)
            print('Instance:',config.get_database_name(),config.get_environment())
            print('Tables',config.get_database_instance().get_table_names())
            data = AppServer.json_decode(request)
            link = AppServer.db.select("LinkTab", TabName = data['TabName'], AttrName = data['AttrName'])
            print('link',link)
            if not link:
                data['LinkName'] = ''
                data['BaseTab'] = 0
                data['ShowAttrs'] = ''
            else:
                data['LinkName'] = link[0].LinkName
                data['BaseTab'] = link[0].BaseTab
                data['ShowAttrs'] = link[0].ShowAttrs
    
            return json.dumps(data)
        
        except Exception as e:
            print('AppServer.link: ***Error:',e)
            traceback.print_exc(file=sys.stdout)

    @staticmethod
    @app.route("/data/getLinkData.json",methods=['POST']) 
    def get_link_data():
        try:
            print('AppServer.get_link_data running',request.method)
            print('Instance:',config.get_database_name(),config.get_environment())
            print('Tables',config.get_database_instance().get_table_names())
            print('request:', request)
            data = AppServer.json_decode(request)
            print('data', data)
            result_rows = AppServer.db.select("LinkTab", LinkName=data['LinkName'], BaseTab=1)
            print('result:',result_rows)
            print('result.type:',type(result_rows))
                 
            for result in result_rows:
                print('We have a datastructure')
                attrs_to_show = result.ShowAttrs.split(',')
                print('attrs_to_show:',attrs_to_show)
                args = dict()
                args[result.AttrName] = data['KeyValue']
                key_data_rows = AppServer.db.select(result.TabName,**args)
                for keyData in key_data_rows:
                    print('keyData',keyData)
                    print('keyData.__dict__',keyData.__dict__)
                    row = []
                    for a in attrs_to_show:
                        row.append(keyData.__dict__[a])
                    rows = []
                    rows.append(attrs_to_show)
                    rows.append(row)
                    data['BaseData'] = rows
                    
#                 
#             print('link',link)
#             if not link:
#                 data['LinkName'] = ''
#                 data['BaseTab'] = 0
#                 data['ShowAttrs'] = ''
#             else:
#                 data['LinkName'] = link.LinkName
#                 data['BaseTab'] = link.BaseTab
#                 data['ShowAttrs'] = link.ShowAttrs
            print('data at return:',data)
            return json.dumps(data)
#         
        except Exception as e:
            print('AppServer.link: ***Error:',e)
            traceback.print_exc(file=sys.stdout)
    
    @staticmethod
    @app.route("/larry/",methods=['POST']) 
    def larry():
        print('AppServer.larry running',request.method)
        return 'Thats it folks'
    
    @staticmethod
    def reqorblank(reqname):
        a = request.args.get(reqname)
        print('value of a:',a)
        if a:
            return a
        else:
            return ''
        
    @staticmethod
    def json_decode(req):
        """
        Do not remove this method. We could use request.json instead of all
        this but... and it's a big but... flask unit testing does not 
        suport the request.json method we we wrote this.
        """
        reqDataBytes = req.data
        reqDataString = reqDataBytes.decode(encoding='UTF-8')
        return json.loads(reqDataString)
        
    @staticmethod
    def run(dbName):
        print("Starting AppServer.run")
        AppServer.shower.connect()
#         AppServer.db = config.get_database()
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
