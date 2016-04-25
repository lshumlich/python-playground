from flask import Blueprint, render_template, request, abort, json

import config
from .permission_handler import PermissionHandler

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