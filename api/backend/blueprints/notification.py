from flask import Blueprint
from flask import request
from flask import jsonify
from flask import make_response
from flask import current_app
from backend.db_connection import db as database
from backend.blueprints.util import *

notifications = Blueprint('notifications', __name__)

@notifications.route('/notifications/<session_key>')
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
