from flask import Blueprint
from flask import request
from flask import jsonify
from flask import make_response
from flask import current_app
from backend.db_connection import db as database
from backend.blueprints.util import *

grades = Blueprint('grades', __name__)

@grades.route('/grade/<session_key>/<class_id>/<assignment_id>/<student_id>',methods = ["GET","PUT","POST","DELETE"])
def grade(session_key,class_id,assignment_id,student_id):
    cursor = database.get_db().cursor()

    user_id = userIDFromSessionKey(session_key)

    if (user_id == -1):
        return respond("",CODE_ACCESS_DENIED)
    if (not isClassMember(user_id,class_id)):
        return respond("",CODE_ACCESS_DENIED)
    
    perms = getUserClassPermissions(user_id,class_id)

    if (student_id == -1):
        student_id = user_id
    else:
        if (not isClassMember(student_id,class_id)):
            return respond("",CODE_ACCESS_DENIED)
        if (not perms.get("CAN_GRADE_ASSIGNMENTS",False)):
            return respond("",CODE_ACCESS_DENIED)
        
    if (request.method == "GET"):
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
        cursor.execute(query,(assignment_id,student_id))
        result = cursor.fetchall()
        return respond(jsonify(result),CODE_SUCCESS)
    
    if (not perms.get("CAN_GRADE_ASSIGNMENTS",False)):
        return respond("",CODE_ACCESS_DENIED)

    if (request.method == "DELETE"):
        query = f'''
            DELETE FROM Grades WHERE
            G.student_id = %s AND 
            G.assignment_criterion_id IN
            (SELECT assignment_criterion_id FROM AssignmentCriteria WHERE assignment_id = %s AND class_id = %s)
        '''
        cursor.execute(query,(student_id,assignment_id,class_id))
        database.get_db().commit()
        return respond("",CODE_SUCCESS)
    
    args = request.get_json(Force=True)

    if (args.get("criterion_id") == None):
        return respond("",CODE_INVALID_FORMAT)
    if (args.get("grade") == None):
        return respond("",CODE_INVALID_FORMAT)

    if (request.method == "PUT"):
        exists = False
        query = f'''
            SELECT * FROM Grades WHERE assignment_criterion_id = %s AND student_id = %s
        '''
        cursor.execute(query,(args.get("criterion_id"),student_id))
        exists = len(cursor.fetchall()) > 0
        if (not exists):
            query = f'''
                INSERT INTO Grades Value 
                (%s,%s,%s);
            '''
            cursor.execute(query,(args.get("criterion_id"),student_id,args.get("grade")))
            database.get_db().commit()
        else:
            query = f'''
                UPDATE Grades SET  
                grade = %s WHERE assignment_criterion_id=%s AND student_id = %s;
            '''
            cursor.execute(query,(args.get("grade"),args.get("criterion_id"),student_id))
            database.get_db().commit()
