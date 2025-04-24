from flask import Blueprint
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



@users.route('/trylogin/<username>/<password>', methods=['GET'])
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

@users.route('/userinfo/<session_key>', methods=['GET','POST'])
def get_user_info(session_key):
    cursor = database.get_db().cursor()

    user_id = userIDFromSessionKey(session_key)
    if (user_id == -1):
        return respond("",CODE_ACCESS_DENIED)
    
    if (request.method == "GET"):
        query = '''
            SELECT username,first_name,last_name,bio,email FROM Users WHERE user_id = %s
        '''
        success = cursor.execute(query,(user_id))
        result = cursor.fetchall()
        return respond(jsonify(result),CODE_SUCCESS)
    
    if (request.method == "POST"):
        fields = ['first_name','last_name','bio','email','password']

        args = request.get_json(force=True)

        data = []
        set_clause = ""

        for field in fields:
            if args.get(field) is not None:
                set_clause += f"{field} = %s,"
                if (field == "password"):
                    data.append(bytes.fromhex(args[field]))
                else:
                    data.append(args[field])

        set_clause = set_clause.rstrip(', ')
        
        if (set_clause != ""):
            query = f'''
                UPDATE Users 
                SET {set_clause} 
                WHERE user_id = {user_id}
            '''
            log(query)
            cursor.execute(query,data)
            database.get_db().commit()
        
        return respond("",CODE_SUCCESS)

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

@users.route('/classPermissions/<session_key>/<class_id>')
def get_class_permissions(session_key,class_id):
    user_id = userIDFromSessionKey(session_key)

    if (user_id == -1 or not isClassMember(user_id,class_id)):
        return respond("",CODE_ACCESS_DENIED)
   
    return respond(jsonify(getUserClassPermissions(user_id,class_id)),CODE_SUCCESS)

@users.route('/classinfo/<session_key>/<class_id>')
def getClassInfo(session_key,class_id):
    cursor = database.get_db().cursor()

    user_id = userIDFromSessionKey(session_key)

    if (user_id == -1):
        return respond("",CODE_ACCESS_DENIED)
    if (not isClassMember(user_id,class_id)):
        return respond("",CODE_ACCESS_DENIED)
    
    canViewCode = getUserClassPermissions(user_id,class_id).get('IS_INSTRUCTOR')

    query = f'''
        SELECT class_id,name,description,organization{',join_code' if canViewCode else ''} FROM Classes WHERE 
        class_id = %s
    '''
    success = cursor.execute(query,(class_id))
    result = cursor.fetchall()
    return respond(jsonify(result),CODE_SUCCESS)

@users.route('/classRoster/<session_key>/<class_id>')
def get_class_roster(session_key,class_id):

    cursor = database.get_db().cursor()

    user_id = userIDFromSessionKey(session_key)

    if (user_id == -1 or not isClassMember(user_id,class_id)):
        return respond("",CODE_ACCESS_DENIED)
    
    perms = getUserClassPermissions(user_id,class_id)

    if (not perms["CAN_VIEW_ROSTER"]):
        return respond("",CODE_ACCESS_DENIED)
    
    query = f'''
        SELECT first_name, last_name, M.permission_level FROM
        (
            SELECT user_id as member_id, permission_level FROM Memberships 
            WHERE class_id = %s {"" if (Permissions.CAN_VIEW_HIDDEN in perms) else "AND visibility = 1"}
        ) AS M 
        JOIN Users ON M.member_id = user_id
    '''
    cursor.execute(query,(class_id))
    result = cursor.fetchall()
    return (jsonify(result))

@users.route('/notifications/<session_key>')
def get_notifications(session_key):
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
def get_announcements(session_key,class_id):
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
def get_assignments(session_key,class_id):
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
def get_assignment_details(session_key,class_id,assignment_id):
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
def get_grade(session_key,class_id,assignment_id):
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

@users.route("/joinClass/<session_key>/<class_code>")
def join_class(session_key,class_code):
    cursor = database.get_db().cursor()

    user_id = userIDFromSessionKey(session_key)

    if (user_id == -1):
        return respond("",CODE_ACCESS_DENIED)
    if (len(class_code) != 8):
        return respond("",CODE_INVALID_FORMAT)
    
    query = """
    SELECT class_id FROM Classes WHERE join_code = %s
    """
    cursor.execute(query,(class_code))
    match = cursor.fetchall()
    if (len(match) == 0):
        return respond("",CODE_ACCESS_DENIED)
    class_id = match[0].class_id

    query = '''
        INSERT INTO Memberships (user_id,class_id,permission_level,visibility) VALUES
        (%s,%s,%s,%s)
    '''

    cursor.execute(query,(user_id,class_id,0,1))

    database.get_db().commit()

    return respond("",200)

def removeUserFromClass(class_id,user_id):
    cursor = database.get_db().cursor()
    query  = '''
    DELETE FROM Memberships WHERE class_id = %s AND user_id = %s
    '''
    cursor.execute(query,(class_id,user_id))
    database.get_db().commit()

@users.route("/leaveClass/<session_key>/<class_id>",methods = ["DELETE"])
def leave_class(session_key,class_id):
    user_id = userIDFromSessionKey(session_key)

    if (user_id == -1):
        return respond("",CODE_ACCESS_DENIED)
    if (not isClassMember(user_id,class_id)):
        return respond("",CODE_ACCESS_DENIED)
    
    removeUserFromClass(class_id,user_id)
    return respond("",CODE_SUCCESS)

@users.route("/removeUser/<session_key>/<class_id>/<user_id>",methods = ["DELETE"])
def force_leave_class(session_key,class_id,target_id):
    user_id = userIDFromSessionKey(session_key)

    if (user_id == -1):
        return respond("",CODE_ACCESS_DENIED)
    if (not isClassMember(user_id,class_id)):
        return respond("",CODE_ACCESS_DENIED)
    
    perms = getUserClassPermissions(user_id,class_id)

    if (not perms.CAN_REMOVE_STUDENT):
        return respond("",CODE_ACCESS_DENIED)
    
    removeUserFromClass(class_id,target_id)
    return respond("",CODE_SUCCESS)

@users.route("/createClass/<session_key>",methods=["POST"])
def create_class(session_key):
    data = request.form

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

    cursor.execute(query,(data.class_name,data.class_description,data.organization,join_code))

    cursor.execute('SELECT LAST_INSERT_ID()')
    class_id = cursor.fetchall()[0]["LAST_INSERT_ID()"]

    query = '''
        INSERT INTO Memberships (user_id,class_id,permission_level,visibility) VALUES
        (%s,%s,%s,%s)
    '''

    cursor.execute(query,(user_id,class_id,16,1))

    database.get_db().commit()

    return respond(str(class_id),200)



