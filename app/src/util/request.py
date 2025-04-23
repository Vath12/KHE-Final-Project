import streamlit as st
import requests

EXCEPTION_REDIRECT = "Login"

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
    result = safeRequest(f"http://api:4000/userinfo/{st.session_state.get('session_key')}")
    return result.json()[0] #the query returns an array with one dictionary

def getClassList() -> list[dict]:
    """
    :rtype: list[dict]
    :return:
    [{class_id,name}]
    """
    result = safeRequest(f"http://api:4000/classlist/{st.session_state.get('session_key')}")
    return result.json()

def getClassInfo(class_id : int) -> dict:
    """
    :rtype: dict
    :return:
    {class_id,name,description,organization}
    """
    result = safeRequest(f"http://api:4000/classinfo/{st.session_state.get('session_key')}/{class_id}")
    return result.json()[0]

def getNotifications() -> list[dict]:
    """
    :rtype: list[dict]
    :return:
    {notification_date,assignment_name,class_name}
    """
    result = safeRequest(f"http://api:4000/notifications/{st.session_state.get('session_key')}")
    return result.json()

def getAnnouncements(class_id : int) -> list[dict]:
    """
    :rtype: list[dict]
    :return:
    [{author_id,title,message,date_posted}]
    """
    result = safeRequest(f"http://api:4000/announcements/{st.session_state.get('session_key')}/{class_id}")
    return result.json()

def getAssignments(class_id : int) -> list[dict]:
    """
    :rtype: list[dict]
    :return:
    [{assignment_id,due_date,name,overall_weight}]
    """
    result = safeRequest(f"http://api:4000/assignments/{st.session_state.get('session_key')}/{class_id}")
    return result.json()

def getAssignmentDetails(class_id : int,assignment_id : int) -> list[dict]:
    """
    :rtype: list[dict]
    :return:
    [{name,value,weight}]
    """
    result = safeRequest(f"http://api:4000/assignmentDetails/{st.session_state.get('session_key')}/{class_id}/{assignment_id}")
    return result.json()

def getGrade(class_id : int,assignment_id : int) -> list[dict]:
    """
    :rtype: list[dict]
    :return:
    [{name,grade,value,weight}]
    """
    result = safeRequest(f"http://api:4000/grade/{st.session_state.get('session_key')}/{class_id}/{assignment_id}")
    return result.json()

