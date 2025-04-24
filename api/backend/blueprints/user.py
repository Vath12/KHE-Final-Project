from flask import Blueprint
from flask import request
from flask import jsonify
from flask import make_response
from flask import current_app
from backend.db_connection import db as database
from backend.blueprints.util import *

users = Blueprint('users', __name__)

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
            cursor.execute(query,data)
            database.get_db().commit()
        
        return respond("",CODE_SUCCESS)

@users.route('/isValidSession/<session_key>', methods=['GET'])
def get_valid_session(session_key):
    return respond("",200 if (userIDFromSessionKey(session_key) != -1) else 401)

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
    class_id = match[0]["class_id"]

    query = '''
        INSERT INTO Memberships (user_id,class_id,permission_level,visibility) VALUES
        (%s,%s,%s,%s)
    '''

    cursor.execute(query,(user_id,class_id,0,1))

    database.get_db().commit()

    return respond("",200)

@users.route("/leaveClass/<session_key>/<class_id>",methods = ["DELETE"])
def leave_class(session_key,class_id):
    user_id = userIDFromSessionKey(session_key)

    if (user_id == -1):
        return respond("",CODE_ACCESS_DENIED)
    if (not isClassMember(user_id,class_id)):
        return respond("",CODE_ACCESS_DENIED)
    
    removeUserFromClass(class_id,user_id)
    return respond("",CODE_SUCCESS)

profileLinks = Blueprint('profileLinks', __name__)
@profileLinks.route("/userProfileLink/<session_key>/<platform_id>",methods=["GET","POST","PUT","DELETE"])
def crud_profile_links(session_key,platform_id):
    cursor = database.get_db().cursor()

    user_id = userIDFromSessionKey(session_key)

    if (user_id == -1):
        return respond("",CODE_ACCESS_DENIED)
    
    args = request.get_json(force = True)

    if (request.method == "GET"):
        query = '''
            SELECT platform,link FROM UserProfileLinks WHERE user_id = %s
        '''
        cursor.execute(query,(user_id))
        result = cursor.fetchall()
        return respond(jsonify(result),CODE_SUCCESS)
    if (request.method == "POST"):
        query = '''
            INSERT INTO UserProfileLinks (user_id,platform,link) Value
            (%s,%s,%s)
        '''
        cursor.execute(query,(
            user_id,
            platform_id,
            args.get("link","")
        ))
        database.get_db().commit()

        return respond("",CODE_SUCCESS)

    if (request.method == "PUT"):
        query = '''
            UPDATE UserProfileLinks SET 
            link = %s
            WHERE 
            platform = %s AND user_id = %s
        '''
        cursor.execute(query,(
            args.get("link",""),
            platform_id,
            user_id
        ))
        database.get_db().commit()
        return respond("",CODE_SUCCESS)
    if (request.method == "DELETE"):
        query = '''
            DELETE FROM UserProfileLinks WHERE user_id = %s AND platform = %s
        '''
        cursor.execute(query,(user_id,platform_id))
        database.get_db().commit()
        return respond("",CODE_SUCCESS)