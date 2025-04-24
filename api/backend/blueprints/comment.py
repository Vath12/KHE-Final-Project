from flask import Blueprint
from flask import request
from flask import jsonify
from flask import make_response
from flask import current_app
from backend.db_connection import db as database
from backend.blueprints.util import *

comments = Blueprint('comments', __name__)

@comments.route("/comment/<session_key>/<class_id>/<assignment_id>/<student_id>",methods=["GET","POST","PUT","DELETE"])
def comment(session_key,class_id,assignment_id,student_id):
    cursor = database.get_db().cursor()

    user_id = userIDFromSessionKey(session_key)
    
    if (user_id == -1):
        return respond("",CODE_ACCESS_DENIED)
    if (not isClassMember(user_id,class_id)):
        return respond("",CODE_ACCESS_DENIED)
    
    perms = getUserClassPermissions(user_id,class_id)

    if (not perms.get("CAN_GRADE_ASSIGNMENTS",False)):
        return respond("",CODE_ACCESS_DENIED)
    
    args = request.get_json(force=True)
    if (request.method == "GET"):
        query = """
        SELECT 
        C.comment_id as comment_id,
        C.message as message, 
        C.created_on as created_on,
        A.first_name AS author_first_name, 
        A.last_name AS author_last_name 
        FROM 
        (
        SELECT * FROM Comments WHERE 
        class_id = %s AND
        assignment_id = %s AND
        student_id = %s
        ) as C
        JOIN Users as A ON A.user_id = C.author_id
        """
        cursor.execute(query,(class_id,assignment_id,student_id))
        result = cursor.fetchall()
        return respond(jsonify(result),CODE_SUCCESS)

    if (request.method == "POST"):
        query = '''
        INSERT INTO Comments (class_id,name,due_date,overall_weight) VALUES
        (%s,%s,%s,%s)
        '''
        cursor.execute(query,(
            class_id,
            args.get("name","Untitled"),
            args.get("due_date","ADDTIME(CURRENT_TIMESTAMP, '1:00:00:00')"),
            args.get("overall_weight",1)
        ))

        database.get_db().commit()
        return respond("",CODE_SUCCESS)
    if (request.method == "PUT"):
        return respond("",CODE_SUCCESS)
    if (request.method == "DELETE"):
        return respond("",CODE_SUCCESS)
