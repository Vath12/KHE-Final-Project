from flask import Blueprint
from flask import request
from flask import jsonify
from flask import make_response
from flask import current_app
from backend.db_connection import db as database
import os
import random

CODE_SUCCESS = 200
CODE_ACCESS_DENIED = 401
CODE_INVALID_FORMAT = 403

FLAG_CAN_VIEW_ROSTER = 0
FLAG_CAN_MANAGE_ASSIGNMENTS = 1
FLAG_CAN_GRADE_ASSIGNMENT = 2
FLAG_CAN_REMOVE_STUDENT = 4
FLAG_CAN_EDIT_COURSE = 5
FLAG_IS_INSTRUCTOR = 6
FLAG_CAN_VIEW_HIDDEN = 7

def getFlag(flags,index):
    return (flags >> index) & 0b1
def setFlag(flags,index,value):
    return (flags & ~(0b00000000 | 0b1 << index)) | (0b1 if (value) else 0b0 << index)

def respond(content,code):
    response = make_response(content)
    response.status_code = code
    return response

# Create a new Blueprint object, which is a collection of routes.
users = Blueprint('users', __name__)

@users.route('/debug')
def debug():
    cursor = database.get_db().cursor()

    query = f'''
        SELECT * FROM LoginSessions
    '''
    success = cursor.execute(query)
    result = cursor.fetchall()
    return respond(jsonify(result),CODE_SUCCESS)

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



@users.route('/trylogin/<username>/<password>', methods=['GET','PUT'])
def try_login(username,password):
    if (len(username) > 64 or len(password)!=64):
        return respond("",CODE_INVALID_FORMAT)

    # get a cursor object from the database
    cursor = database.get_db().cursor()

    query = '''
        SELECT user_id
        FROM Users
        WHERE username = %s AND password = %s
    ''' #this is probably bad but works for our purposes

    cursor.execute(query,(username,bytes.fromhex(password)))
    # The cursor will return the data as a Python Dictionary
    user = cursor.fetchall()
    if (len(user) != 1):
        return respond("",CODE_ACCESS_DENIED)
    user = user[0]["user_id"]
    query = '''
        SELECT user_id,session_key,expiration_time FROM LoginSessions WHERE user_id=%s
    '''
    cursor.execute(query,(user))
    session_key = cursor.fetchall()
    if (len(session_key) == 0):
        query = '''
            INSERT INTO LoginSessions (user_id,expiration_time) VALUES
            (%s, ADDTIME(CURRENT_TIMESTAMP, '23:59:59'))
        '''
        result=cursor.execute(query,(user))

    query = '''
        SELECT session_key FROM LoginSessions WHERE user_id=%s
    '''
    cursor.execute(query,(user))
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
    query = '''
        SELECT username,first_name,last_name,bio,email FROM Users WHERE user_id = %s
    '''
    success = cursor.execute(query,(user_id))
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
    query = '''
        SELECT class_id,name FROM Classes WHERE class_id in (SELECT class_id FROM Memberships WHERE user_id = %s)
    '''
    success = cursor.execute(query,(user_id))
    result = cursor.fetchall()
    return respond(jsonify(result),CODE_SUCCESS)

@users.route('/classinfo/<session_key>/<class_id>')
def getClassInfo(session_key,class_id):
    cursor = database.get_db().cursor()

    user_id = userIDFromSessionKey(session_key)

    if (user_id == -1):
        return respond("",CODE_ACCESS_DENIED)
    if (not isClassMember(user_id,class_id)):
        return respond("",CODE_ACCESS_DENIED)
    query = '''
        SELECT class_id,name,description,organization FROM Classes WHERE 
        class_id = %s
    '''
    success = cursor.execute(query,(class_id))
    result = cursor.fetchall()
    return respond(jsonify(result),CODE_SUCCESS)

@users.route('/notifications/<session_key>')
def getNotifications(session_key):
    cursor = database.get_db().cursor()

    user_id = userIDFromSessionKey(session_key)

    if (user_id == -1):
        return respond("",CODE_ACCESS_DENIED)
    
    query = '''
        SELECT N.notification_date,A.name as assignment_name,C.name as class_name FROM 
        (Assignments as A JOIN Notifications as N) JOIN Classes as C WHERE student_id = %s
    '''
    success = cursor.execute(query,(user_id))
    result = cursor.fetchall()
    return respond(jsonify(result),CODE_SUCCESS)

@users.route('/announcements/<session_key>/<class_id>')
def getAnnouncements(session_key,class_id):
    cursor = database.get_db().cursor()

    user_id = userIDFromSessionKey(session_key)

    if (user_id == -1):
        return respond("",CODE_ACCESS_DENIED)
    if (not isClassMember(user_id,class_id)):
        return respond("",CODE_ACCESS_DENIED)
    query = '''
        SELECT author_id,title,message,date_posted FROM Announcements WHERE class_id = %s
    '''
    success = cursor.execute(query,(class_id))
    result = cursor.fetchall()
    return respond(jsonify(result),CODE_SUCCESS)

@users.route('/assignments/<session_key>/<class_id>')
def getAssignments(session_key,class_id):
    cursor = database.get_db().cursor()

    user_id = userIDFromSessionKey(session_key)

    if (user_id == -1):
        return respond("",CODE_ACCESS_DENIED)
    if (not isClassMember(user_id,class_id)):
        return respond("",CODE_ACCESS_DENIED)
    query = '''
        SELECT assignment_id,due_date,name,overall_weight FROM Assignments WHERE class_id = %s
    '''
    success = cursor.execute(query,(class_id))
    result = cursor.fetchall()
    return respond(jsonify(result),CODE_SUCCESS)

@users.route('/assignmentDetails/<session_key>/<class_id>/<assignment_id>')
def getAssignmentDetails(session_key,class_id,assignment_id):
    cursor = database.get_db().cursor()

    user_id = userIDFromSessionKey(session_key)

    if (user_id == -1):
        return respond("",CODE_ACCESS_DENIED)
    if (not isClassMember(user_id,class_id)):
        return respond("",CODE_ACCESS_DENIED)
    query = '''
        SELECT name,value,weight FROM AssignmentCriteria WHERE class_id = %s AND assignment_id = %s
    '''
    success = cursor.execute(query,(class_id,assignment_id))
    result = cursor.fetchall()
    return respond(jsonify(result),CODE_SUCCESS)

@users.route('/grade/<session_key>/<class_id>/<assignment_id>')
def getGrade(session_key,class_id,assignment_id):
    cursor = database.get_db().cursor()

    user_id = userIDFromSessionKey(session_key)

    if (user_id == -1):
        return respond("",CODE_ACCESS_DENIED)
    if (not isClassMember(user_id,class_id)):
        return respond("",CODE_ACCESS_DENIED)
    query = f'''
        SELECT 
        AC.name,
        G.grade,
        AC.value,
        AC.weight
        FROM Grades as G JOIN 
        (SELECT * FROM AssignmentCriteria WHERE assignment_id = %s) as AC ON AC.criterion_id = G.assignment_criterion_id
        WHERE G.student_id = %s
    '''
    success = cursor.execute(query,(assignment_id,user_id))
    result = cursor.fetchall()
    return respond(jsonify(result),CODE_SUCCESS)

values = list("qwertyuiopasdfghjklzxcvbnmQWERTYUIOPASDFGHJKLZXCVBNM1234567890")
def intToJoinCode(number):
    code = ""
    for i in range(8):
        number,remainder = divmod(number,62)
        code+=values[remainder]
    return code

#Creation Queries
@users.route("/createClass/<session_key>/<class_name>/<class_description>/<organization>")
def createClass(session_key,class_name,class_description,organization):
    cursor = database.get_db().cursor()

    user_id = userIDFromSessionKey(session_key)

    if (user_id == -1):
        return respond("",CODE_ACCESS_DENIED)
    
    while (True):
        #8 characters, only latin letters and numbers 0-9
        join_code = intToJoinCode(random.randint(0,62**8))

        query = '''
        SELECT class_id FROM Classes WHERE join_code = %s
        '''
        cursor.execute(query,(join_code))
        if (len(cursor.fetchall()) == 0):
            break
    
    query = '''
        INSERT INTO Classes (name,description,organization,join_code) VALUES
        (%s,%s,%s,%s);
    '''

    cursor.execute(query,(class_name,class_description,organization,join_code))

    cursor.execute('SELECT LAST_INSERT_ID()')
    class_id = cursor.fetchall()[0]["LAST_INSERT_ID()"]

    query = '''
        INSERT INTO Memberships (user_id,class_id,permission_level,visibility) VALUES
        (%s,%s,%s,%s)
    '''

    cursor.execute(query,(user_id,class_id,16,1))

    database.get_db().commit()

    return respond(str(class_id),200)



