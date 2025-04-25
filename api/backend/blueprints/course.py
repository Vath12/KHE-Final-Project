from flask import Blueprint
from flask import request
from flask import jsonify
from flask import make_response
from flask import current_app
from backend.db_connection import db as database
from backend.blueprints.util import *

classes = Blueprint('classes', __name__)


@classes.route("/createClass/<session_key>",methods=["POST"])
def create_class(session_key):
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

    args = request.get_json(force=True)

    if (args.get('class_name',None) == None or args.get('class_description',None) == None or args.get('organization',None) == None):
        return respond("",CODE_INVALID_FORMAT)
    
    cursor.execute(query,(args['class_name'],args['class_description'],args['organization'],join_code))

    cursor.execute('SELECT LAST_INSERT_ID();')
    class_id = cursor.fetchall()[0]['LAST_INSERT_ID()']

    query = '''
        INSERT INTO Memberships (user_id,class_id,permission_level,visibility) VALUES
        (%s,%s,%s,%s)
    '''

    cursor.execute(query,(user_id,class_id,0b1111111111111111,1))

    database.get_db().commit()

    return respond(jsonify({'class_id':class_id}),200)

@classes.route('/classlist/<session_key>', methods=['GET'])
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

@classes.route('/classPermissions/<session_key>/<class_id>/<target_id>',methods = ["GET","POST"])
def class_permissions(session_key,class_id,target_id):
    cursor = database.get_db().cursor()
    user_id = userIDFromSessionKey(session_key)
    
    if (user_id == -1 or not isClassMember(user_id,class_id)):
        return respond("",CODE_ACCESS_DENIED)
    
    if (int(target_id) == -1):
        target_id = user_id
    
    if (request.method == "GET"):
        return respond(jsonify(getUserClassPermissions(target_id,class_id)),CODE_SUCCESS)
    
    if (request.method == "POST"):

        perms  = getUserClassPermissions(user_id,class_id)

        if (not perms.get('CAN_EDIT_COURSE')):
            return respond("",CODE_ACCESS_DENIED)
            
        args = request.get_json(force=True)

        flags = Permissions(0)

        target_id = args.get("user_id")
        if (target_id == None):
            return respond("",CODE_INVALID_FORMAT)
        
        if (args.get('CAN_VIEW_ROSTER')):
            flags |= Permissions.CAN_VIEW_ROSTER
        if (args.get('CAN_MANAGE_ASSIGNMENTS')):
            flags |= Permissions.CAN_MANAGE_ASSIGNMENTS
        if (args.get('CAN_GRADE_ASSIGNMENT')):
            flags |= Permissions.CAN_GRADE_ASSIGNMENT
        if (args.get('CAN_REMOVE_STUDENT')):
            flags |= Permissions.CAN_REMOVE_STUDENT
        if (args.get('CAN_EDIT_COURSE')):
            flags |= Permissions.CAN_EDIT_COURSE
        if (args.get('IS_INSTRUCTOR')):
            flags |= Permissions.IS_INSTRUCTOR
        if (args.get('CAN_VIEW_HIDDEN')):
            flags |= Permissions.CAN_VIEW_HIDDEN
        
        query = f'''
            UPDATE Memberships
            SET permission_level = {int(flags)}, visibility = {1 if args.get('IS_VISIBLE') == True else 0}
            WHERE user_id = {target_id}
        '''
        log(query)
        cursor.execute(query)
        database.get_db().commit()

        return respond("",CODE_SUCCESS)

@classes.route('/classinfo/<session_key>/<class_id>',methods = ["GET"])
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

@classes.route('/classRoster/<session_key>/<class_id>',methods = ["GET"])
def get_class_roster(session_key,class_id):
    cursor = database.get_db().cursor()

    user_id = userIDFromSessionKey(session_key)

    if (user_id == -1 or not isClassMember(user_id,class_id)):
        return respond("",CODE_ACCESS_DENIED)
    
    perms = getUserClassPermissions(user_id,class_id)

    if (not perms["CAN_VIEW_ROSTER"]):
        return respond("",CODE_ACCESS_DENIED)
    
    query = f'''
        SELECT user_id,first_name, last_name, M.permission_level as permissions FROM
        (
            SELECT user_id as member_id, permission_level FROM Memberships 
            WHERE class_id = %s {"" if (Permissions.CAN_VIEW_HIDDEN in perms) else "AND visibility = 1"}
        ) AS M 
        JOIN Users ON M.member_id = user_id
    '''
    cursor.execute(query,(class_id))
    result = cursor.fetchall()
    return (jsonify(result))

@classes.route("/removeUser/<session_key>/<class_id>/<user_id>",methods = ["DELETE"])
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
