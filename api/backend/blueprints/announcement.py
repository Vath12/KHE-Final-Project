from flask import Blueprint
from flask import request
from flask import jsonify
from flask import make_response
from flask import current_app
from backend.db_connection import db as database
from backend.blueprints.util import *

announcements = Blueprint('announcements', __name__)

@announcements.route('/announcements/<session_key>/<class_id>',methods = ["GET","POST","PUT","DELETE"])
def get_announcements(session_key,class_id):
    cursor = database.get_db().cursor()

    user_id = userIDFromSessionKey(session_key)

    if (user_id == -1):
        return respond("",CODE_ACCESS_DENIED)
    if (not isClassMember(user_id,class_id)):
        return respond("",CODE_ACCESS_DENIED)
    
    if (request.method == "GET"):
        query = '''
            SELECT author_id,title,message,date_posted FROM Announcements WHERE class_id = %s
        '''
        cursor.execute(query,(class_id))
        result = cursor.fetchall()
        return respond(jsonify(result),CODE_SUCCESS)
    
    args = request.get_json(force = True)
    perms = getUserClassPermissions(user_id,class_id)

    if (not perms.get("IS_INSTRUCTOR")):
        return respond("",CODE_ACCESS_DENIED)

    if (request.method == "POST"):
        query = '''
            INSERT INTO Announcements (class_id,author_id,title,message) VALUE
            (%s,%s,%s,%s)
        '''
        cursor.execute(query,(class_id,user_id,args.get("title","Untitled"),args.get("message","")))
        database.get_db().commit()
        return respond("",CODE_SUCCESS)
    if (request.method == "PUT"):
        query = '''
            UPDATE Announcements SET title = %s,message = %s WHERE
            class_id = %s AND author_id = %s AND announcement_id = %s
        '''
        cursor.execute(query,(args.get("title","Untitled"),args.get("message",""),class_id,user_id,args.get("announcement_id",-1)))
        database.get_db().commit()
        return respond("",CODE_SUCCESS)
    if (request.method == "DELETE"):
        query = '''
            DELETE FROM Announcements WHERE
            class_id = %s AND author_id = %s AND announcement_id = %s
        '''
        cursor.execute(query,(class_id,user_id,args.get("announcement_id",-1)))
        database.get_db().commit()
        return respond("",CODE_SUCCESS)