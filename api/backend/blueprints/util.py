from flask import request
from flask import jsonify
from flask import make_response
from flask import current_app
from backend.db_connection import db as database
import os
import random
from enum import IntFlag


CODE_SUCCESS = 200
CODE_ACCESS_DENIED = 401
CODE_INVALID_FORMAT = 403


class Permissions(IntFlag):
    CAN_VIEW_ROSTER = 1
    CAN_MANAGE_ASSIGNMENTS = 2
    CAN_GRADE_ASSIGNMENT = 4
    CAN_REMOVE_STUDENT = 8
    CAN_EDIT_COURSE = 16
    IS_INSTRUCTOR = 32
    CAN_VIEW_HIDDEN = 64

PROFILE_LINK_PLATFORMS = {
    "LINKEDIN" : 0,
    "SNAPCHAT" : 1,
    "INSTAGRAM" : 2,
    "DISCORD" : 3,
    "GITHUB" : 4,
    "FACEBOOK" : 5
}



def respond(content,code):
    response = make_response(content)
    response.status_code = code
    return response

def log(message):
    os.write(1,bytes(message+"\n","utf-8"))

def userIDFromSessionKey(session_key):
    cursor = database.get_db().cursor()
    query = f'''
        SELECT * FROM LoginSessions
    '''
    success = cursor.execute(query)
    result = cursor.fetchall()
    query = '''
        SELECT user_id FROM LoginSessions WHERE session_key = %s
    '''
    success = cursor.execute(query,(session_key))
    result = cursor.fetchall()
    if (len(result) == 0):
        return -1
    return result[0]["user_id"]

def isClassMember(user_id,class_id):
    cursor = database.get_db().cursor()
    query = '''
        SELECT * FROM Memberships WHERE user_id = %s AND class_id = %s
    '''
    success = cursor.execute(query,(user_id,class_id))
    return len(cursor.fetchall()) > 0

def getUserClassPermissions(user_id,class_id):
    cursor = database.get_db().cursor()
    query = '''
        SELECT * FROM Memberships WHERE user_id = %s AND class_id = %s
    '''
    cursor.execute(query,(user_id,class_id))
    result = cursor.fetchall()
    perms = 0
    if (len(result) > 0):
        perms = Permissions(result[0]["permission_level"])

    result = {
        'CAN_VIEW_ROSTER' : Permissions.CAN_VIEW_ROSTER in perms,
        'CAN_MANAGE_ASSIGNMENTS' : Permissions.CAN_MANAGE_ASSIGNMENTS in perms,
        'CAN_GRADE_ASSIGNMENT' : Permissions.CAN_GRADE_ASSIGNMENT in perms,
        'CAN_REMOVE_STUDENT' : Permissions.CAN_REMOVE_STUDENT in perms,
        'CAN_EDIT_COURSE' : Permissions.CAN_EDIT_COURSE in perms,
        'IS_INSTRUCTOR' : Permissions.IS_INSTRUCTOR in perms,
        'CAN_VIEW_HIDDEN' : Permissions.CAN_VIEW_HIDDEN in perms
    }
    return result

values = list("qwertyuiopasdfghjklzxcvbnmQWERTYUIOPASDFGHJKLZXCVBNM1234567890")
def intToJoinCode(number):
    code = ""
    for i in range(8):
        number,remainder = divmod(number,62)
        code+=values[remainder]
    return code

def removeUserFromClass(class_id,user_id):
    cursor = database.get_db().cursor()
    query  = '''
    DELETE FROM Memberships WHERE class_id = %s AND user_id = %s
    '''
    cursor.execute(query,(class_id,user_id))
    database.get_db().commit()

