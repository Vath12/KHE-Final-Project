import streamlit as st
from util.verification import isValidSession
from util.request import *

isValidSession()

userInfo = getUserInfo()
classes = getClassList()

st.set_page_config(page_title="homepage", layout="wide")

# ---------- Session State ----------
if "leave_mode" not in st.session_state:
    st.session_state.leave_mode = False
if "selected_classes_to_leave" not in st.session_state:
    st.session_state.selected_classes_to_leave = set()

def toggle_leave_mode():
    st.session_state.leave_mode = not st.session_state.leave_mode
    st.session_state.selected_classes_to_leave.clear()

def confirm_leave():
    for class_id in st.session_state.selected_classes_to_leave:
        removeUserFromClass(class_id)
    st.session_state.leave_mode = False
    st.session_state.selected_classes_to_leave.clear()
    st.rerun()

# ---------- Sidebar ----------
st.sidebar.markdown(
    """
    <style>
        .sidebar-title {
            font-size: 24px;
            font-weight: bold;
            padding-bottom: 20px;
        }
        .sidebar-link {
            font-size: 18px;
            color: #2e86de;
            padding: 10px 0;
            cursor: pointer;
        }
        .sidebar-link:hover {
            color: #1b4f72;
        }
    </style>
    """,
    unsafe_allow_html=True
)

if st.sidebar.button("Profile", use_container_width=True):
    st.switch_page("pages/profile_display.py")
if st.sidebar.button("Notifications", use_container_width=True):
    st.switch_page("pages/notification.py")
if st.sidebar.button("Join Class", use_container_width=True):
    st.switch_page("pages/join_classes.py")

# Show "Leave Classes" under "Join Class" only if user is in non-instructor classes
non_instructor_classes = [
    c for c in classes if not getClassPermissions(c["class_id"]).get("IS_INSTRUCTOR", False)
]

if non_instructor_classes:
    if st.sidebar.button("Leave Classes", use_container_width=True):
        toggle_leave_mode()

# ---------- Page Content ----------
cols = st.columns([4, 1])
with cols[0]:
    subtitle = (
        "<p style='font-size: 18px; color: #555;'>Select the classes you wish to leave</p>"
        if st.session_state.leave_mode else
        "<p style='font-size: 18px; color: #555;'>Click on a course to view details</p>"
    )
    st.markdown(
        f"""
        <div style='font-size: 40px; font-weight: bold; color: #2e86de;'>
            Welcome {userInfo['first_name']} {userInfo['last_name']}
        {subtitle}
        </div>
        """,
        unsafe_allow_html=True
    )
with cols[1]:
    if st.button("Create Class"):
        st.switch_page("pages/create_class.py")

# ---------- Class Display ----------
cols = st.columns(3)

for i, c in enumerate(classes):
    with cols[i % 3]:
        if st.session_state.leave_mode:
            perm = getClassPermissions(c["class_id"])
            if not perm.get("IS_INSTRUCTOR", False):
                checked = c["class_id"] in st.session_state.selected_classes_to_leave
                if st.checkbox(c["name"], key=f"leave_{c['class_id']}", value=checked):
                    st.session_state.selected_classes_to_leave.add(c["class_id"])
                else:
                    st.session_state.selected_classes_to_leave.discard(c["class_id"])
            else:
                st.markdown(f"**{c['name']}** (Instructor)")
        else:
            if st.button(c["name"], key=1888888 + i, use_container_width=True):
                st.session_state.selected_class_id = c['class_id']
                st.switch_page("pages/classes.py")

# ---------- Leave Mode Controls ----------
if st.session_state.leave_mode:
    col1, col2 = st.columns([1, 1])
    with col1:
        if st.button("Confirm Leave"):
            confirm_leave()
    with col2:
        if st.button("Back"):
            toggle_leave_mode()

# ---------- Modify removeUserFromClass function with the fix here -----------
def removeUserFromClass(class_id, user_id=-1) -> bool:
    """
    :param2:
    user_id is optional, if unset will remove current user from the specified class
    :rtype: bool
    :return:
    True if successful
    """
    if (user_id == -1):
        # FIX: pass empty dictionary as second argument to safeDelete
        result = safeDelete(f"{API}/leaveClass/{st.session_state.get('session_key')}/{class_id}", {})
        return result.status_code == 200
    else:
        result = safeDelete(f"{API}/removeUser/{st.session_state.get('session_key')}/{class_id}/{user_id}", {})
        return result.status_code == 200
