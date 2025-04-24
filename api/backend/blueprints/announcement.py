from flask import Blueprint
from flask import request
from flask import jsonify
from flask import make_response
from flask import current_app
from backend.db_connection import db as database
from backend.blueprints.util import *

announcements = Blueprint('announcements', __name__)

@announcements.route('/announcements/<session_key>/<class_id>')
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