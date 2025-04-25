import streamlit as st
import requests
import json
import hashlib

EXCEPTION_REDIRECT = "Login"
API = "http://api:4000"

def safeGet(URL):
    """
    Tries to get data from the input URL, if the request fails it switches to safe error page specified by
    EXCEPTION_REDIRECT
    """
    try:
        return requests.get(URL)
    except requests.exceptions.HTTPError:
        st.switch_page(EXCEPTION_REDIRECT)
        return None
    

def safePost(URL,jsonData):
    """
    Tries to put data to the input URL, if the request fails it switches to safe error page specified by
    EXCEPTION_REDIRECT
    """
    try:
        return requests.post(URL,json=jsonData)
    except requests.exceptions.HTTPError:
        st.switch_page(EXCEPTION_REDIRECT)
        return None
    
def safePut(URL,jsonData):
    """
    Tries to put data to the input URL, if the request fails it switches to safe error page specified by
    EXCEPTION_REDIRECT
    """
    try:
        return requests.put(URL,json=jsonData)
    except requests.exceptions.HTTPError:
        st.switch_page(EXCEPTION_REDIRECT)
        return None
    
def safeDelete(URL,jsonData):
    """
    Tries to put data to the input URL, if the request fails it switches to safe error page specified by
    EXCEPTION_REDIRECT
    """
    try:
        return requests.delete(URL,json=jsonData)
    except requests.exceptions.HTTPError:
        st.switch_page(EXCEPTION_REDIRECT)
        return None
    

def getUserInfo() -> dict:
    """
    :rtype: dict
    :return:
    {username,first_name,last_name,email,bio}
    """
    result = safeGet(f"{API}/userinfo/{st.session_state.get('session_key')}")
    return result.json()[0] #the query returns an array with one dictionary

def setUserInfo(first_name=None,last_name=None,bio = None,password = None,email = None) -> bool:
    """
    :rtype: bool
    :return:
    True if successful
    """
    data = {
        'first_name' : first_name,
        'last_name' : last_name, 
        'email' : email,
        'bio' : bio,
        'password' : None if password == None else hashlib.sha256(bytes(password,"utf-8")).hexdigest()
    }
    result = safePost(f"{API}/userinfo/{st.session_state.get('session_key')}",data)
    return result.status_code == 200

def getUserProfileLinks() -> list[dict]:
    """
    platform_ids:\n
    0 LINKEDIN\n
    1 SNAPCHAT\n
    2 INSTAGRAM\n
    3 DISCORD\n
    4 GITHUB\n
    5 FACEBOOK\n
    :rtype: list[dict]
    :return:
    [{platform,link}]
    """
    result = safeGet(f"{API}/userProfileLink/{st.session_state.get('session_key')}/-1")
    return result.json()

def addUserProfileLink(platform : int,link : str) -> bool:
    """
    :rtype: bool
    :return:
    True if successful
    """
    data = {
        "link" : link
    }
    result = safePost(f"{API}/userProfileLink/{st.session_state.get('session_key')}/{platform}",data)
    return result.status_code == 200

def setUserProfileLink(platform : int,link : str) -> bool:
    """
    :rtype: bool
    :return:
    True if successful
    """
    data = {
        "link" : link
    }
    result = safePut(f"{API}/userProfileLink/{st.session_state.get('session_key')}/{platform}",data)
    return result.status_code == 200

def removeUserProfileLink(platform : int) -> bool:
    """
    :rtype: bool
    :return:
    True if successful
    """
    result = safeDelete(f"{API}/userProfileLink/{st.session_state.get('session_key')}/{platform}",{})
    return result.status_code == 200

def getClassList() -> list[dict]:
    """
    :rtype: list[dict]
    :return:
    [{class_id,name}]
    """
    result = safeGet(f"{API}/classlist/{st.session_state.get('session_key')}")
    return result.json()

def getClassInfo(class_id : int) -> dict:
    """
    :rtype: dict
    :return:
    {class_id,name,description,organization,<OPTIONAL> join_code}
    join code is None unless user has permission to view it
    """
    result = safeGet(f"{API}/classinfo/{st.session_state.get('session_key')}/{class_id}")
    return result.json()[0]

def getNotifications() -> list[dict]:
    """
    :rtype: list[dict]
    :return:
    {notification_date,assignment_name,class_name,assignment_id}
    """
    result = safeGet(f"{API}/notifications/{st.session_state.get('session_key')}")
    return result.json()

def removeNotifications(toRemove : list[int]) -> bool:
    """
    :rtype: list[dict]
    :return:
    True on success
    """
    data = {
        "removeList" : toRemove
    }
    result = safeDelete(f"{API}/notifications/{st.session_state.get('session_key')}",data)
    return result.json()

def getAnnouncements(class_id : int) -> list[dict]:
    """
    :rtype: list[dict]
    :return:
    [{author_id,title,message,date_posted}]
    """
    result = safeGet(f"{API}/announcements/{st.session_state.get('session_key')}/{class_id}")
    return result.json()

def getAssignments(class_id : int) -> list[dict]:
    """
    :rtype: list[dict]
    :return:
    [{assignment_id,due_date,name,overall_weight}]
    """
    result = safeGet(f"{API}/assignments/{st.session_state.get('session_key')}/{class_id}")
    return result.json()

def getAssignmentDetails(class_id : int,assignment_id : int) -> list[dict]:
    """
    :rtype: list[dict]
    :return:
    [{criterion_id,name,value,weight}]
    """
    result = safeGet(f"{API}/assignmentDetails/{st.session_state.get('session_key')}/{class_id}/{assignment_id}")
    return result.json()

def getGrade(class_id : int,assignment_id : int,student_id : int = -1) -> list[dict]:
    """
    :param3:
    student_id is optional, by default it returns the grade for the logged in user
    :rtype: list[dict]
    :return:
    [{name,grade,value,weight}]
    """
    result = safeGet(f"{API}/grade/{st.session_state.get('session_key')}/{class_id}/{assignment_id}/{student_id}")
    return result.json()

def setGrade(class_id : int,assignment_id : int,criterion_id : int,student_id : int,grade : float) -> bool:
    """
    :rtype: list[dict]
    :return:
    True if successful
    """
    data = {
        "criterion_id" : criterion_id,
        "grade" : grade
    }
    result = safePut(f"{API}/grade/{st.session_state.get('session_key')}/{class_id}/{assignment_id}/{student_id}",data)
    return result.json()

def deleteGrade(class_id : int,assignment_id : int,student_id : int) -> bool:
    """
    :rtype: list[dict]
    :return:
    True on success
    """
    result = safeGet(f"{API}/grade/{st.session_state.get('session_key')}/{class_id}/{assignment_id}/{student_id}")
    return result.status_code == 200

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
    result = safeGet(f"{API}/classPermissions/{st.session_state.get('session_key')}/{class_id}")
    return result.json()

def setClassPermissions(
        class_id : int,
        target_user_id : int,
        CAN_VIEW_ROSTER : bool,
        CAN_MANAGE_ASSIGNMENTS : bool,
        CAN_GRADE_ASSIGNMENT : bool,
        CAN_REMOVE_STUDENT : bool,
        CAN_EDIT_COURSE : bool,
        IS_INSTRUCTOR : bool,
        CAN_VIEW_HIDDEN : bool,
        IS_VISIBLE : bool
) -> bool:
    """
    :rtype: bool
    :return:
    True on success
    """
    data = {
        'user_id' : target_user_id,
        'CAN_VIEW_ROSTER' : CAN_VIEW_ROSTER,
        'CAN_MANAGE_ASSIGNMENTS' : CAN_MANAGE_ASSIGNMENTS,
        'CAN_GRADE_ASSIGNMENT' : CAN_GRADE_ASSIGNMENT,
        'CAN_REMOVE_STUDENT' : CAN_REMOVE_STUDENT,
        'CAN_EDIT_COURSE' : CAN_EDIT_COURSE,
        'IS_INSTRUCTOR' : IS_INSTRUCTOR,
        'CAN_VIEW_HIDDEN' : CAN_VIEW_HIDDEN,
        'IS_VISIBLE' : IS_VISIBLE,
    }
    result = safePost(f"{API}/classPermissions/{st.session_state.get('session_key')}",data)
    return result.status_code == 200

def getClassRoster(class_id : int) -> list[dict]:
    """
    :rtype: list[dict]
    :return:
    [{user_id,first_name,last_name,permissions}]
    """
    result = safeGet(f"{API}/classRoster/{st.session_state.get('session_key')}/{class_id}")
    return result.json()

def removeUserFromClass(class_id,user_id=-1) -> bool:
    """
    :param2:
    user_id is optional, if unset will remove current user from the specified class
    :rtype: bool
    :return:
    True if successful
    """
    if (user_id == -1):
        result = safeDelete(f"{API}/leaveClass/{st.session_state.get('session_key')}/{class_id}", {})
        return result.status_code == 200
    else:
        result = safeDelete(f"{API}/removeUser/{st.session_state.get('session_key')}/{class_id}/{user_id}", {})
        return result.status_code == 200

def joinClass(class_code) -> bool:
    """
    :rtype: bool
    :return:
    True if successful
    """
    result = safeGet(f"{API}/joinClass/{st.session_state.get('session_key')}/{class_code}")
    return result.status_code == 200

def createClass(class_name,class_description,organization) -> int:
    """
    :rtype: int
    :return:
    class_id
    """
    data = {
     'class_name' : class_name,
     'class_description' : class_description,
     'organization' : organization
    }
    result = safePost(f"{API}/createClass/{st.session_state.get('session_key')}",data)
    return result.json().get('class_id')

def createAssignment(class_id,name,due,weight):
    """
    :rtype: bool
    :return:
    assignment_id on Success, None on Failure
    """
    data = {
     'name' : name,
     'due_date' : due,
     'overall_weight' : weight
    }
    result = safePost(f"{API}/modifyAssignment/{st.session_state.get('session_key')}/{class_id}/-1",data)
    return result.json().get('assignment_id')

def updateAssignmnet(class_id,assignment_id,name,due,weight):
    """
    :rtype: bool
    :return:
    True on success
    """
    data = {
     'name' : name,
     'due_date' : due,
     'overall_weight' : weight
    }
    result = safePut(f"{API}/modifyAssignment/{st.session_state.get('session_key')}/{class_id}/{assignment_id}",data)
    return result.status_code == 200

def deleteAssignment(class_id,assignment_id):
    """
    :rtype: bool
    :return:
    True on success
    """
    result = safeDelete(f"{API}/modifyAssignment/{st.session_state.get('session_key')}/{class_id}/{assignment_id}")
    return result.status_code == 200

def getAssignmentCriterion(class_id : int, assignment_id : int,criterion_id : int) -> dict:
    """
    :rtype: dict
    :return:
    {name,value,weight}
    """
    result = safeGet(f"{API}/assignmentCriteria/{st.session_state.get('session_key')}/{class_id}/{assignment_id}/{criterion_id}")
    return result.json().get(0,None)


def createAssignmentCriterion(class_id : int, assignment_id : int ,name : str,value : int,weight : float) -> int:
    """
    :rtype: bool
    :return:
    criterion_id on Success, None on Failure
    """
    data = {
     'name' : name,
     'value' : value,
     'weight' : weight
    }
    result = safePost(f"{API}/assignmentCriteria/{st.session_state.get('session_key')}/{class_id}/{assignment_id}/-1",data)
    return result.json().get('criterion_id')

def updateAssignmentCriterion(class_id : int, assignment_id : int, criterion_id : int, name : str,value : int,weight : float) -> bool:
    """
    :rtype: bool
    :return:
    True on success
    """
    data = {
     'name' : name,
     'value' : value,
     'weight' : weight
    }
    result = safePut(f"{API}/assignmentCriteria/{st.session_state.get('session_key')}/{class_id}/{assignment_id}",data)
    return result.status_code == 200

def deleteAssignmentCriterion(class_id: int,assignment_id : int,criterion_id : int) -> bool:
    """
    :rtype: bool
    :return:
    True on success
    """
    result = safeDelete(f"{API}/assignmentCriteria/{st.session_state.get('session_key')}/{class_id}/{assignment_id}/{criterion_id}")
    return result.status_code == 200
    

def gradeAssignment(class_id,criterion_id,student_id,grade):
    """
    TODO: IMPLEMENT
    :rtype: bool
    :return:
    True if successful
    """
    pass

def createComment(class_id : int,assignment_id : int,student_id : int,message : str) -> bool:
    """
    :rtype: bool
    :return:
    True if successful
    """
    data = {
        'message' : message
    }
    result = safePost(f"{API}/comment/{st.session_state.get('session_key')}/{class_id}/{assignment_id}/{student_id}",data)
    return result.status_code == 200

def updateComment(class_id : int,assignment_id : int,student_id : int,comment_id : int, message : str):
    """
    :rtype: bool
    :return:
    True if successful
    """
    data = {
        'comment_id' : comment_id,
        'message' : message
    }
    result = safePut(f"{API}/comment/{st.session_state.get('session_key')}/{class_id}/{assignment_id}/{student_id}",data)
    return result.status_code == 200

def deleteComment(class_id : int,assignment_id : int,student_id : int,comment_id : int):
    """
    :rtype: bool
    :return:
    True if successful
    """
    data = {
        'comment_id' : comment_id,
    }
    result = safePut(f"{API}/comment/{st.session_state.get('session_key')}/{class_id}/{assignment_id}/{student_id}",data)
    return result.status_code == 200

def getComments(class_id,assignment_id,student_id) -> list[dict]:
    """
    :rtype: list[dict]
    :return:
    
    [{message,author_first_name,author_last_name,created_on}]
    """
    result = safeGet(f"{API}/comment/{st.session_state.get('session_key')}/{class_id}/{assignment_id}/{student_id}")
    return result.status_code == 200

