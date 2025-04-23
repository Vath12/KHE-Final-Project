import streamlit as st
import requests

EXCEPTION_REDIRECT = "Login"
API = "http://api:4000"

def safeRequest(URL):
    """
    Tries to get data from the input URL, if the request fails it switches to safe error page specified by
    EXCEPTION_REDIRECT
    """
    try:
        return requests.get(URL)
    except requests.exceptions.HTTPError:
        st.switch_page(EXCEPTION_REDIRECT)
        return None
    

def getUserInfo() -> dict:
    """
    :rtype: dict
    :return:
    {username,first_name,last_name,email,bio}
    """
    result = safeRequest(f"{API}/userinfo/{st.session_state.get('session_key')}")
    return result.json()[0] #the query returns an array with one dictionary

def getClassList() -> list[dict]:
    """
    :rtype: list[dict]
    :return:
    [{class_id,name}]
    """
    result = safeRequest(f"{API}/classlist/{st.session_state.get('session_key')}")
    return result.json()

def getClassInfo(class_id : int) -> dict:
    """
    :rtype: dict
    :return:
    {class_id,name,description,organization,<OPTIONAL> join_code}
    join code is None unless user has permission to view it
    """
    result = safeRequest(f"{API}/classinfo/{st.session_state.get('session_key')}/{class_id}")
    return result.json()[0]

def getNotifications() -> list[dict]:
    """
    :rtype: list[dict]
    :return:
    {notification_date,assignment_name,class_name}
    """
    result = safeRequest(f"{API}/notifications/{st.session_state.get('session_key')}")
    return result.json()

def getAnnouncements(class_id : int) -> list[dict]:
    """
    :rtype: list[dict]
    :return:
    [{author_id,title,message,date_posted}]
    """
    result = safeRequest(f"{API}/announcements/{st.session_state.get('session_key')}/{class_id}")
    return result.json()

def getAssignments(class_id : int) -> list[dict]:
    """
    :rtype: list[dict]
    :return:
    [{assignment_id,due_date,name,overall_weight}]
    """
    result = safeRequest(f"{API}/assignments/{st.session_state.get('session_key')}/{class_id}")
    return result.json()

def getAssignmentDetails(class_id : int,assignment_id : int) -> list[dict]:
    """
    :rtype: list[dict]
    :return:
    [{name,value,weight}]
    """
    result = safeRequest(f"{API}/assignmentDetails/{st.session_state.get('session_key')}/{class_id}/{assignment_id}")
    return result.json()

def getGrade(class_id : int,assignment_id : int) -> list[dict]:
    """
    :rtype: list[dict]
    :return:
    [{name,grade,value,weight}]
    """
    result = safeRequest(f"{API}/grade/{st.session_state.get('session_key')}/{class_id}/{assignment_id}")
    return result.json()

def getClassPermissions(class_id : int) -> dict:
    """
    :rtype: dict
    :return:
    {
        CAN_VIEW_ROSTER,
        CAN_MANAGE_ASSIGNMENTS,
        CAN_GRADE_ASSIGNMENT,
        CAN_REMOVE_STUDENT,
        CAN_EDIT_COURSE,
        IS_INSTRUCTOR,
        CAN_VIEW_HIDDEN
    }
    """
    result = safeRequest(f"{API}classPermissions/{st.session_state.get('session_key')}/{class_id}")
    return result.json()

def getClassRoster(class_id : int) -> list[dict]:
    """
    :rtype: list[dict]
    :return:
    [{first_name,last_name}]
    """
    result = safeRequest(f"{API}/classRoster/{st.session_state.get('session_key')}/{class_id}")
    return result.json()

def getComments(class_id,assignment_id) -> list[dict]:
    """
    :rtype: int
    :return:
    [{message,author_first_name,author_last_name,created_on}]
    """
    pass

def removeUserFromClass(class_id,user_id=-1) -> bool:
    """
    :param2:
    user_id is optional, if unset will remove current user from the specified class
    :rtype: bool
    :return:
    True if successful
    """
    if (user_id == -1):
        result = safeRequest(f"{API}/leaveClass/{st.session_state.get('session_key')}/{class_id}")
        return result.status_code == 200
    else:
        result = safeRequest(f"{API}/removeUser/{st.session_state.get('session_key')}/{class_id}/{user_id}")
        return result.status_code == 200

def joinClass(class_code) -> bool:
    """
    :rtype: bool
    :return:
    True if successful
    """
    result = safeRequest(f"{API}/joinClass/{st.session_state.get('session_key')}/{class_code}")
    return result.status_code == 200

def createClass(class_name,class_description,organization) -> int:
    """
    :rtype: int
    :return:
    class_id
    """
    result = safeRequest(f"{API}/createClass/{st.session_state.get('session_key')}/{class_name}/{class_description}/{organization}")
    return int(result.content)

def createAssignment():
    pass
    
def gradeAssignment():
    pass

def createComment():
    pass

