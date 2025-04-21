from flask import Blueprint
from flask import request
from flask import jsonify
from flask import make_response
from flask import current_app
from backend.db_connection import db as database


# Create a new Blueprint object, which is a collection of routes.
users = Blueprint('users', __name__)

@users.route('/helloWorld', methods=['GET','PUT'])
def hello_world():
    response = make_response("hello world")
    response.status_code = 9999
    return response

@users.route('/trylogin/<username>/<password>', methods=['GET','PUT'])
def try_login(username,password):

    if (len(username) < 64 or len(password)!=64):
        response.status_code = 99
        return ""

    # get a cursor object from the database
    cursor = database.get_db().cursor()

    query = f'''
        SELECT user_id,password
        FROM Users
        WHERE username = '{username}'
    '''

    cursor.execute(query)

    # The cursor will return the data as a Python Dictionary
    theData = cursor.fetchall()

    response = make_response(jsonify(theData))
    # set the proper HTTP Status code of 200 (meaning all good)
    response.status_code = 200
    return response