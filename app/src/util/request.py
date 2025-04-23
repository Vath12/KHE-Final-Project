import streamlit as st
import requests

def getUserInfo():
    """
    Returns a dictionary with the following keys
    {username,first_name,last_name,email,bio}
    """
    result = requests.get(f"http://api:4000/userinfo/{st.session_state.get('session_key')}")
    return result.json()[0] #the query returns an array with one dictionary

def getClassList():
    """
    Returns a list of dictionaries with the following keys
    {class_id,name}
    """
    result = requests.get(f"http://api:4000/classlist/{st.session_state.get('session_key')}")
    return result.json()

def getClassInfo(class_id):
    """
    Returns a dictionary with the following keys
    {class_id,name,description,organization}
    """
    result = requests.get(f"http://api:4000/classinfo/{st.session_state.get('session_key')}/{class_id}")
    return result.json()[0]

def getNotifications():
    """
    Returns a list of dictionaries with the following keys
    {notification_date,assignment_name,class_name}
    """
    result = requests.get(f"http://api:4000/notifications/{st.session_state.get('session_key')}")
    return result.json()

def getAnnouncements(class_id):
    """
    Returns a list of dictionaries with the following keys
    {}
    """
    result = requests.get(f"http://api:4000/announcements/{st.session_state.get('session_key')}/{class_id}")
    return result.json()

def getAssignments(class_id):
    """
    Returns a list of dictionaries with the following keys
    {}
    """
    result = requests.get(f"http://api:4000/assignments/{st.session_state.get('session_key')}")
    return result.json()

def getAssignmentDetails(class_id,assignment_id):
    """
    Returns a list of dictionaries with the following keys
    {}
    """
    result = requests.get(f"http://api:4000/assignmentDetails/{st.session_state.get('session_key')}/{class_id}/{assignment_id}")
    return result.json()

def getGrade(class_id,assignment_id):
    """
    Returns a list of dictionaries with the following keys
    {}
    """
    result = requests.get(f"http://api:4000/grade/{st.session_state.get('session_key')}/{class_id}/{assignment_id}")
    return result.json()

