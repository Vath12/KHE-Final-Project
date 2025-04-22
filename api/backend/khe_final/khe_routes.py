from flask import Blueprint
from flask import request
from flask import jsonify
from flask import make_response
from flask import current_app
from backend.db_connection import db as database
import os


# Create a new Blueprint object, which is a collection of routes.
users = Blueprint('users', __name__)

def log(message):
    os.write(1,bytes(message+"\n","utf-8"))

def userIDFromSessionKey(session_key):
    cursor = database.get_db().cursor()
    query = f'''
        SELECT * FROM LoginSessions
    '''
    success = cursor.execute(query)
    result = cursor.fetchall()
    log(f"sessions {result}")
    query = f'''
        SELECT user_id FROM LoginSessions WHERE session_key={session_key}
    '''
    success = cursor.execute(query)
    result = cursor.fetchall()
    if (len(result) == 0):
        return -1
    return result[0]["user_id"]


@users.route('/trylogin/<username>/<password>', methods=['GET','PUT'])
def try_login(username,password):
    if (len(username) > 64 or len(password)!=64):
        response.status_code = 400#incorrect format
        return ""

    # get a cursor object from the database
    cursor = database.get_db().cursor()
    #username = hamburger
    #password = password
    #hash = 5E884898DA28047151D0E56F8DC6292773603D0D6AABBDD62A11EF721D1542D8
    query = f'''
        SELECT user_id
        FROM Users
        WHERE username = '{username}' AND password = 0x{password} 
    ''' #this is hilariously bad but works for our purposes
    cursor.execute(query)
    # The cursor will return the data as a Python Dictionary
    user = cursor.fetchall()
    if (len(user) != 1):
        response.status_code = 401 #incorrect credentials
        return ""
    user = user[0]["user_id"]
    log(f"user: {user}\n")
    query = f'''
        SELECT user_id,session_key,expiration_time FROM LoginSessions WHERE user_id={user}
    '''
    cursor.execute(query)
    session_key = cursor.fetchall()
    log(f"session_key {str(session_key)}")
    if (len(session_key) == 0):
        query = f'''
            INSERT INTO LoginSessions (user_id,expiration_time) VALUES
            ({user}, ADDTIME(CURRENT_TIMESTAMP, '23:59:59'))
        '''
        result=cursor.execute(query)
        log(f"insertion result: {result}")

    query = f'''
        SELECT session_key FROM LoginSessions WHERE user_id={user}
    '''
    cursor.execute(query)
    session_key = cursor.fetchall()
    response = make_response(str(session_key[0]["session_key"]))
    # set the proper HTTP Status code of 200 (meaning all good)
    response.status_code = 200

    database.get_db().commit()
    return response

#trylogin/hamburger/5E884898DA28047151D0E56F8DC6292773603D0D6AABBDD62A11EF721D1542D8

@users.route('/userinfo/<session_key>', methods=['GET'])
def get_user_info(session_key):
    cursor = database.get_db().cursor()

    user_id = userIDFromSessionKey(session_key)
    if (user_id == -1):
        response = make_response("")
        response.status_code = 401 #incorrect credentials
        return response
    query = f'''
        SELECT username,first_name,last_name,bio,email FROM Users WHERE user_id = {user_id}
    '''
    success = cursor.execute(query)
    result = cursor.fetchall()
    response = make_response(jsonify(result))
    response.status_code = 200
    return response