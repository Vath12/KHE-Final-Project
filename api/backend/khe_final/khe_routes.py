from flask import Blueprint
from flask import request
from flask import jsonify
from flask import make_response
from flask import current_app
from backend.db_connection import db as database
import os

CODE_SUCCESS = 200
CODE_ACCESS_DENIED = 401
CODE_INVALID_FORMAT = 403

def respond(content,code):
    response = make_response(content)
    response.status_code = code
    return response

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
        return respond("",CODE_INVALID_FORMAT)

    # get a cursor object from the database
    cursor = database.get_db().cursor()

    query = f'''
        SELECT user_id
        FROM Users
        WHERE username = '{username}' AND password = 0x{password} 
    ''' #this is hilariously bad but works for our purposes
    cursor.execute(query)
    # The cursor will return the data as a Python Dictionary
    user = cursor.fetchall()
    if (len(user) != 1):
        return respond("",CODE_ACCESS_DENIED)
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

    database.get_db().commit()

    return respond(str(session_key[0]["session_key"]),CODE_SUCCESS)
    

#trylogin/hamburger/5E884898DA28047151D0E56F8DC6292773603D0D6AABBDD62A11EF721D1542D8

@users.route('/userinfo/<session_key>', methods=['GET'])
def get_user_info(session_key):
    cursor = database.get_db().cursor()

    user_id = userIDFromSessionKey(session_key)
    if (user_id == -1):
        return respond("",CODE_ACCESS_DENIED)
    query = f'''
        SELECT username,first_name,last_name,bio,email FROM Users WHERE user_id = {user_id}
    '''
    success = cursor.execute(query)
    result = cursor.fetchall()
    return respond(jsonify(result),CODE_SUCCESS)


@users.route('/isValidSession/<session_key>', methods=['GET'])
def get_valid_session(session_key):
    return respond("",200 if (userIDFromSessionKey(session_key) != -1) else 401)

@users.route('/classlist/<session_key>', methods=['GET'])
def get_class_list(session_key):
    cursor = database.get_db().cursor()

    user_id = userIDFromSessionKey(session_key)
    if (user_id == -1):
        return respond("",CODE_ACCESS_DENIED)
    query = f'''
        SELECT class_id,name FROM Classes WHERE class_id in (SELECT class_id FROM Memberships WHERE user_id = {user_id})
    '''
    success = cursor.execute(query)
    result = cursor.fetchall()
    return respond(jsonify(result),CODE_SUCCESS)

@users.route('/classinfo/<session_key>/<class_id>')
def getClassInfo(session_key,class_id):
    cursor = database.get_db().cursor()

    user_id = userIDFromSessionKey(session_key)

    if (user_id == -1):
        return respond("",CODE_ACCESS_DENIED)
    query = f'''
        SELECT class_id,name,description,organization FROM Classes WHERE 
        class_id = {class_id} AND class_id in 
        (SELECT class_id FROM Memberships WHERE user_id = {user_id})
    '''
    success = cursor.execute(query)
    result = cursor.fetchall()
    return respond(jsonify(result),CODE_SUCCESS)

@users.route('/notifications/<session_key>')
def getNotifications(session_key):
    cursor = database.get_db().cursor()

    user_id = userIDFromSessionKey(session_key)

    if (user_id == -1):
        return respond("",CODE_ACCESS_DENIED)
    
    query = f'''
        SELECT N.notification_date,A.name as assignment_name,C.name as class_name FROM 
        (Assignments as A JOIN Notifications as N) JOIN Classes as C WHERE student_id = {user_id}
    '''
    success = cursor.execute(query)
    result = cursor.fetchall()
    return respond(jsonify(result),CODE_SUCCESS)

