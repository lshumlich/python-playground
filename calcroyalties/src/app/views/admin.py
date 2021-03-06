from flask import Blueprint
from flask import render_template
from flask import request
from flask import abort
from flask import json

# from .permission_handler import PermissionHandler
import traceback
import sys

from src.util.data_dictionary import resolve_lookups_in_description
import config
from src.database.data_structure import DataStructure

admin = Blueprint('admin', __name__)

@admin.route('/admin/users')
def user_list():
    """ display user search form"""
    return render_template('admin/users_search.html')

@admin.route('/api/users', methods=['GET', 'DELETE', 'POST', 'PUT', 'PATCH'])
def user_details():
    """ handles all user-related ajax calls, both for user list and individual users """
    if not request.is_xhr:
        abort(404)
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
        class User:
            pass
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


@admin.route('/admin/datadictionary/show')
def data_dictionary():
    """ display search form """
    return render_template('admin/data_dictionary_search.html')


@admin.route('/admin/datadictionary/get')
def data_dictionary_get():
    db = config.get_database()
    print("--- args", request.args)
    print("---> subject", request.args.get('Subject'))
    # print("---> ID", request.args.get('ID'))
    print("---> Resolve", request.args.get('Resolve'))
    print("---> Print", request.args.get('Print'))

    if request.args:
        if request.args.get('Subject'):
            # results = db.select('DataDictionary', TableName=request.args.get('Subject'))
            results = db.select_sql("SELECT * from DataDictionary where TableName = \'{}\' order by SortOrder".format
                                    (request.args.get('Subject')))
            if request.args.get('Resolve') == 'true':
                resolve_lookups(results)
            return render_template('admin/data_dictionary_search_results.html',
                                   datadic=results,
                                   subject=request.args.get('Subject'),
                                   print=request.args.get('Print'))
        elif request.args.get('ID'):
            _id = request.args.get('ID')
            if _id == '0':
                return render_template('admin/data_dictionary_details.html', datadic=None)
            else:
                results = db.select1('DataDictionary', ID=request.args.get('ID'))
                return render_template('admin/data_dictionary_details.html', datadic=results)

    """ get an entire dictionary list """
    # results = db.select('DataDictionary')
    results = db.select_sql("SELECT * from DataDictionary order by TableName,SortOrder")

    if request.args.get('Resolve') == 'true':
        resolve_lookups(results)

    return render_template('admin/data_dictionary_search_results.html',
                           datadic=results,
                           subject=request.args.get('Subject'),
                           print=request.args.get('Print'))


def resolve_lookups(results):
    for r in results:
        s = resolve_lookups_in_description(r.Documentation)
        r.Documentation = s


# @admin.route('/admin/datadictionary/save',  methods=['GET', 'POST', 'PUT'])
@admin.route('/admin/datadictionary/save', methods=['POST'])
def data_dictionary_save():

    req_data = request.get_json()
    db = config.get_database()
    _id = req_data['ID']
    if _id:  # This means there is an id so it is an update
        datadic = db.select1('DataDictionary', ID=int(req_data['ID']))
    else:
        class DataDic:
            pass
        req_data = request.get_json()
        datadic = DataDic()
        datadic._table_name = 'DataDictionary'

    # Add or Update do the move
    datadic.TableName = req_data['Subject']
    datadic.SortOrder = int(req_data['Order'])
    datadic.Attribute = req_data['Attribute']
    datadic.Documentation = req_data['Description']
    print('--->', req_data)
    print('---ID:', _id)
    if _id:
        db.update(datadic)
    else:
        db.insert(datadic)

    return "ok from datadic"


@admin.route('/admin/datadictionary/delete')
def data_dictionary_delete():
    db = config.get_database()

    db.delete('DataDictionary', int(request.args.get('ID')))

    return "ok from data_dictionary_delete"


# Data Browser below:

class Shower(object):

    LINK_TABLE = "LinkTab"

    def __init__(self):
        self.dbi = config.get_database_instance()

    def connect(self):
        self.dbi = config.get_database_instance()

    def show_table(self, table_name, attr=None, key=None):
        stmt = 'select * from ' + table_name
        if key:
            ctype = self.column_type(table_name, attr)
            where = ''
            if ctype == 'int':
                where = attr + "=" + key
            elif ctype == 'text':
                where = attr + "='" + key + "'"
            else:
                print('***** Type not delt with:', type, table_name, attr)

            stmt = stmt + " where " + where
        elif attr:
            stmt = stmt + " order by " + attr
#         print('SQL:', stmt)
        values = self.dbi.execute(stmt)
        table_rows = []
        for row in values:
            table_rows.append(row)
        return table_rows

    def show_columns(self, table_name):
        stmt = 'pragma table_info(' + table_name + ')'
        values = self.dbi.execute(stmt)
        columns = []
        for row in values:
            columns.append(row[1])
        return columns

    def column_type(self, table, column):
        stmt = 'pragma table_info(' + table + ')'
        values = self.dbi.execute(stmt)
        for row in values:
            if row[1] == column:
                return row[2]
        return None


class Utils(object):

    @staticmethod
    def obj_to_dict(obj, dic=None):
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

    @staticmethod
    def dict_to_obj(dic, obj=None):
        if not obj:
            obj = DataStructure()
        for k in dic:
            obj.__dict__[k] = dic[k]

        return obj

    @staticmethod
    def json_decode(req):
        """
        This is used primarly in the browser app.
        Do not remove this method. In the app we could use request.json
        instead of all
        this but... and it's a big but... flask unit testing does not
        suport the request.json method we wrote this.
        """
        req_data_bytes = req.data
        req_data_string = req_data_bytes.decode(encoding='UTF-8')
        return json.loads(req_data_string)


@admin.route("/admin/data/", methods=['GET', 'POST'])
def data():
    html = ""
    try:
        db_instance = config.get_database_instance()
        shower = Shower()

        table = request.args.get('table')
        attr = request.args.get('attr')
        key = request.args.get('key')
        links = dict()
        links['BAid'] = '?table=BAInfo&attr=BAid&key='
        links['WellEvent'] = '?table=WellInfo&attr=Well&key='

        tables = db_instance.get_table_names()
        header = None
        rows = None
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
        # print('AppServer.update_link_row running', request.method)
        _data = utils.json_decode(request)
        # print('data:', data)
        linktab = db.get_data_structure('LinkTab')
        utils.dict_to_obj(_data, linktab)
        print('just before if data:', _data)
        print('just before if data:', _data['ID'])
        if _data['ID'] == '0':
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
        _data = utils.json_decode(request)
        link = db.select("LinkTab", TabName=_data['TabName'], AttrName=_data['AttrName'])
        print('link', link)
        if not link:
            _data['ID'] = 0
            _data['LinkName'] = ''
            _data['BaseTab'] = 0
            _data['ShowAttrs'] = ''
        else:
            _data['ID'] = link[0].ID
            _data['LinkName'] = link[0].LinkName
            _data['BaseTab'] = link[0].BaseTab
            _data['ShowAttrs'] = link[0].ShowAttrs

        return json.dumps(_data)

    except Exception as e:
        print('AppServer.link: ***Error:', e)
        traceback.print_exc(file=sys.stdout)


@admin.route("/admin/data/getLinkData.json", methods=['POST'])
def get_link_data():
    utils = Utils()
    db = config.get_database()
    try:
        _data = utils.json_decode(request)
        #             print('data', data)
        link = db.select("LinkTab", TabName=_data['TabName'], AttrName=_data['AttrName'])
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
                args[result.AttrName] = _data['AttrValue']
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
                row = [result.TabName, result.AttrName]
                rows.append(row)
            _data['Links'] = rows

        else:
            _data["Message"] = _data['AttrName'] + " has not been linked."
        return json.dumps(_data)
        #
    except Exception as e:
        print('AppServer.link: ***Error:', e)
        traceback.print_exc(file=sys.stdout)
