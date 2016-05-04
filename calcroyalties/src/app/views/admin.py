from flask import Blueprint, render_template, request, abort, json

import config
from .permission_handler import PermissionHandler
import traceback, sys

admin = Blueprint('admin', __name__)

@admin.route('/admin/users')
def user_list():
    """ display user search form"""
    return render_template('admin/users_search.html')

@admin.route('/api/users', methods=['GET', 'DELETE', 'POST', 'PUT', 'PATCH'])
def user_details():
    """ handles all user-related ajax calls, both for user list and individual users """
    if not request.is_xhr: abort(404)
    db = config.get_database()
    if request.method == 'GET' and not request.args:
        """ get an entire user list """
        results = db.select('Users')
        return render_template('admin/users_search_results.html', users=results)
    elif request.method == 'GET':
        """ get info for a user """
        results = db.select1('Users', ID=request.args.get('ID'))
        return render_template('admin/users_details.html', user=results)
    elif request.method == 'DELETE':
        """ delete user """
        db.delete('Users', int(request.form['ID']))
        return json.dumps({'success': True}), 200, {'ContentType': 'application/json'}
    elif request.method == 'POST':
        """ update info for a user """
        req_data = request.get_json()
        print(req_data)
        user = db.select1('Users', ID=req_data['ID'])
        user.Login = req_data['Login']
        user.Name = req_data['Name']
        user.Email = req_data['Email']
        user.Permissions = req_data['Permissions']
        db.update(user)
        return json.dumps({'success': True}), 200, {'ContentType': 'application/json'}
    elif request.method == 'PATCH':
        """ get an empty form to create a new user """
        return render_template('admin/users_details.html', user=None)
    elif request.method == 'PUT':
        """ create new user """
        class User():
            None
        req_data = request.get_json()
        user = User()
        user._table_name = 'Users'
        user.Login = req_data['Login']
        user.Name = req_data['Name']
        user.Email = req_data['Email']
        user.Permissions = req_data['Permissions']
        db.insert(user)
        return json.dumps({'success': True}), 200, {'ContentType': 'application/json'}
    else:
        abort(400)


# Data Browser below:
from src.database.data_structure import DataStructure

class Shower(object):

    LINK_TABLE = "LinkTab"

    def __init__(self):
        self.dbi = config.get_database_instance()

    def connect(self):
        self.dbi = config.get_database_instance()

    def show_table(self,tableName, attr=None, key=None):
        stmt = 'select * from ' + tableName
        if key:
            ctype = self.column_type(tableName, attr)
            where = ''
            if ctype == 'int':
                where = attr + "=" + key
            elif ctype =='text':
                where = attr + "='" + key + "'"
            else:
                print('***** Type not delt with:', type,tableName,attr)

            stmt = stmt + " where " + where
        elif attr:
            stmt = stmt + " order by " + attr
#         print('SQL:', stmt)
        values = self.dbi.execute(stmt)
        table_rows = []
        for row in values:
            table_rows.append(row)
        return table_rows

    def show_columns(self, tableName):
        stmt = 'pragma table_info(' + tableName + ')'
        values = self.dbi.execute(stmt)
        columns = []
        for row in values:
            columns.append(row[1])
        return (columns)


    def column_type(self, table, column):
        stmt = 'pragma table_info(' + table + ')'
        values = self.dbi.execute(stmt)
        for row in values:
            if row[1] == column:
                return row[2]
        return (None)


class Utils(object):

    def obj_to_dict(self,obj,dic = None):
        """
        This will append or create a dictionary object with property attributes of an object
        The dictionary object is returned for convenience.
        """
        if not dic:
            dic = dict()
        for attr in obj.__dict__:
            if not attr.startswith('_'):
                dic[attr] = obj. __dict__[attr]
        return dic

    def dict_to_obj(self,dic,obj=None):
        if not obj:
            obj = DataStructure()
        for k in dic:
            obj.__dict__[k] = dic[k]

        return obj


    def json_decode(self,req):
        """
        This is used primarly in the browser app.
        Do not remove this method. In the app we could use request.json
        instead of all
        this but... and it's a big but... flask unit testing does not
        suport the request.json method we wrote this.
        """
        reqDataBytes = req.data
        reqDataString = reqDataBytes.decode(encoding='UTF-8')
        return json.loads(reqDataString)


@admin.route("/admin/data/", methods=['GET', 'POST'])
def data():
    html = ""
    try:
        db_instance = config.get_database_instance()
        shower = Shower()

        table = request.args.get('table')
        attr = request.args.get('attr')
        key = request.args.get('key')
        links = {}
        links['BAid'] = '?table=BAInfo&attr=BAid&key='
        links['WellEvent'] = '?table=WellInfo&attr=Well&key='

        tables = db_instance.get_table_names()
        header = None
        rows = None
        print('Table:', table)
        if table:
            header = shower.show_columns(table)
            rows = shower.show_table(table, attr, key)
        html = render_template('admin/data.html', table=table, tables=tables, header=header, rows=rows, links=links)
    except Exception as e:
        print('views.data: ***Error:', e)
        traceback.print_exc(file=sys.stdout)
    return html

@admin.route("/admin/data/updateLinkRow.json", methods=['POST'])
def update_link_row():
    utils = Utils()
    db = config.get_database()
    return_data = dict()
    try:
        print('AppServer.update_link_row running', request.method)
        data = utils.json_decode(request)
        print('data:', data)
        linktab = db.get_data_structure('LinkTab')
        utils.dict_to_obj(data, linktab)
        print('just before if data:', data)
        print('just before if data:', data['ID'])
        if data['ID'] == '0':
            db.insert(linktab)
        else:
            db.update(linktab)

        return_data['StatusCode'] = 0
        return json.dumps(return_data)
    except Exception as e:
        print('AppServer.link: ***Error:', e)
        traceback.print_exc(file=sys.stdout)
        return_data['StatusCode'] = -1
        return_data['Message'] = str(e)
        return json.dumps(return_data)

@admin.route("/admin/data/getLinkRow.json", methods=['POST'])
def get_link_row():
    utils = Utils()
    db = config.get_database()
    try:
        print('AppServer.get_link_row running', request.method)
        print('Instance:', config.get_database_name(), config.get_environment())
        print('Tables', config.get_database_instance().get_table_names())
        data = utils.json_decode(request)
        link = db.select("LinkTab", TabName=data['TabName'], AttrName=data['AttrName'])
        print('link', link)
        if not link:
            data['ID'] = 0
            data['LinkName'] = ''
            data['BaseTab'] = 0
            data['ShowAttrs'] = ''
        else:
            data['ID'] = link[0].ID
            data['LinkName'] = link[0].LinkName
            data['BaseTab'] = link[0].BaseTab
            data['ShowAttrs'] = link[0].ShowAttrs

        return json.dumps(data)

    except Exception as e:
        print('AppServer.link: ***Error:', e)
        traceback.print_exc(file=sys.stdout)

@admin.route("/admin/data/getLinkData.json", methods=['POST'])
def get_link_data():
    utils = Utils()
    db = config.get_database()
    try:
        data = utils.json_decode(request)
        #             print('data', data)
        link = db.select("LinkTab", TabName=data['TabName'], AttrName=data['AttrName'])
        #             print('link',link)
        if len(link) > 0:
            result_rows = db.select("LinkTab", LinkName=link[0].LinkName, BaseTab=1)
            #                 print('result:',result_rows)
            #                 print('result.type:',type(result_rows))

            # Get the base table
            for result in result_rows:
                print('We have a base table')
                attrs_to_show = result.ShowAttrs.split(',')
                args = dict()
                args[result.AttrName] = data['AttrValue']
                key_data_rows = db.select(result.TabName, **args)
                rows = []
                for keyData in key_data_rows:
                    row = []
                    for a in attrs_to_show:
                        row.append(keyData.__dict__[a])
                    rows.append(attrs_to_show)
                    rows.append(row)
                data['BaseData'] = rows

            # Get all the tables that the link uses
            result_rows = db.select("LinkTab", LinkName=link[0].LinkName)

            rows = []
            for result in result_rows:
                row = []
                row.append(result.TabName)
                row.append(result.AttrName)
                rows.append(row)
            data['Links'] = rows

        else:
            data["Message"] = data['AttrName'] + " has not been linked."
        return json.dumps(data)
        #
    except Exception as e:
        print('AppServer.link: ***Error:', e)
        traceback.print_exc(file=sys.stdout)

    print("hello")