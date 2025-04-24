from flask import Blueprint
from flask import request
from flask import jsonify
from flask import make_response
from flask import current_app
from backend.db_connection import db as database
from backend.blueprints.util import *

assignments = Blueprint('assignments', __name__)

@assignments.route('/assignments/<session_key>/<class_id>')
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

@assignments.route('/assignmentDetails/<session_key>/<class_id>/<assignment_id>')
def get_assignment_details(session_key,class_id,assignment_id):
    cursor = database.get_db().cursor()

    user_id = userIDFromSessionKey(session_key)

    if (user_id == -1):
        return respond("",CODE_ACCESS_DENIED)
    if (not isClassMember(user_id,class_id)):
        return respond("",CODE_ACCESS_DENIED)
    query = '''
        SELECT criterion_id,name,value,weight FROM AssignmentCriteria WHERE class_id = %s AND assignment_id = %s
    '''
    success = cursor.execute(query,(class_id,assignment_id))
    result = cursor.fetchall()
    return respond(jsonify(result),CODE_SUCCESS)

@assignments.route("/modifyAssignment/<session_key>/<class_id>/<assignment_id>",methods=["POST","PUT","DELETE"])
def create_update_delete_assignment(session_key,class_id,assignment_id):
    cursor = database.get_db().cursor()

    user_id = userIDFromSessionKey(session_key)

    if (user_id == -1):
        return respond("",CODE_ACCESS_DENIED)
    if (not isClassMember(user_id,class_id)):
        return respond("",CODE_ACCESS_DENIED)
    
    perms = getUserClassPermissions(user_id,class_id)

    if (not perms.get("CAN_MANAGE_ASSIGNMENTS",False)):
        return respond("",CODE_ACCESS_DENIED)
    
    args = request.get_json(force = True)

    if (request.method == "POST"):
        query = '''
        INSERT INTO Assignments (class_id,name,due_date,overall_weight) VALUES
        (%s,%s,%s,%s)
        '''
        cursor.execute(query,(
            class_id,
            args.get("name","Untitled"),
            args.get("due_date","ADDTIME(CURRENT_TIMESTAMP, '1:00:00:00')"),
            args.get("overall_weight",1)
        ))

        database.get_db().commit()

        cursor.execute('SELECT LAST_INSERT_ID()')
        id = cursor.fetchall()[0]["LAST_INSERT_ID()"]

        return respond(jsonify({'assignment_id':id}),CODE_SUCCESS)
    
    if (request.method == "PUT"):
        query = '''
        UPDATE Assignments SET
        name=%s,
        due_date=%s,
        overall_weight=%s WHERE assignment_id = %s
        '''
        cursor.execute(query,(
            class_id,
            args.get("name","Untitled"),
            args.get("due_date","ADDTIME(CURRENT_TIMESTAMP, '1:00:00:00')"),
            args.get("overall_weight",1),
            assignment_id
        ))

        database.get_db().commit()
        return respond("",CODE_SUCCESS)

    if (request.method == "DELETE"):
        query = '''
        DELETE Assignments WHERE assignment_id = %s
        '''
        cursor.execute(query,(assignment_id))

        database.get_db().commit()
        return respond("",CODE_SUCCESS)

assignmentCriteria = Blueprint('assignmentCriteria', __name__)

@assignmentCriteria.route("/assignmentCriteria/<session_key>/<class_id>/<assignment_id>/<criterion_id>",methods=["GET","POST","PUT","DELETE"])
def crud_assignment_criterion(session_key,class_id,assignment_id,criterion_id):
    cursor = database.get_db().cursor()

    user_id = userIDFromSessionKey(session_key)

    if (user_id == -1):
        return respond("",CODE_ACCESS_DENIED)
    if (not isClassMember(user_id,class_id)):
        return respond("",CODE_ACCESS_DENIED)
    
    perms = getUserClassPermissions(user_id,class_id)

    if (not perms.get("CAN_MANAGE_ASSIGNMENTS",False)):
        return respond("",CODE_ACCESS_DENIED)
    
    args = request.get_json(force = True)

    if (request.method == "GET"):
        query = '''
            SELECT name,value,weight FROM AssignmentCriteria WHERE criterion_id = %s
        '''
        cursor.execute(query,(criterion_id))
        result = cursor.fetchall()
        return respond(jsonify(result),CODE_SUCCESS)
    if (request.method == "POST"):
        query = '''
            INSERT INTO AssignmentCriteria (class_id,assignment_id,name,value,weight) Value
            (%s,%s,%s,%s,%s)
        '''
        cursor.execute(query,(
            class_id,
            assignment_id,
            args.get("name","Untitled"),
            args.get("value",0),
            args.get("weight",1.0)
        ))
        database.get_db().commit()

        cursor.execute('SELECT LAST_INSERT_ID()')
        id = cursor.fetchall()[0]["LAST_INSERT_ID()"]

        return respond(jsonify({'criterion_id':id}),CODE_SUCCESS)
    #the class_id seems redundant but it prevents people from just randomly updating criterion_ids from
    #classes they don't belong to
    if (request.method == "PUT"):
        query = '''
            UPDATE AssignmentCriteria SET 
            name = %s,
            value = %s,
            weight = %s
            WHERE 
            criterion_id = %s AND class_id = %s
        '''
        cursor.execute(query,(
            args.get("name","Untitled"),
            args.get("value",0),
            args.get("weight",1.0),
            criterion_id,
            class_id
        ))
        database.get_db().commit()
        return respond("",CODE_SUCCESS)
    if (request.method == "DELETE"):
        query = '''
            DELETE FROM AssignmentCriteria WHERE criterion_id = %s AND class_id = %s
        '''
        cursor.execute(query,(criterion_id,class_id))
        database.get_db().commit()
        return respond("",CODE_SUCCESS)