import streamlit as st
from util.verification import isValidSession
from util.request import *

isValidSession()

st.set_page_config(page_title="homepage", layout="wide")

# ---------- Session State ----------
if "leave_mode" not in st.session_state:
    st.session_state.leave_mode = False
if "selected_classes_to_leave" not in st.session_state:
    st.session_state.selected_classes_to_leave = set()

# ---------- Toggle Handlers ----------
def toggle_leave_mode():
    st.session_state.leave_mode = not st.session_state.leave_mode
    st.session_state.selected_classes_to_leave.clear()
    st.rerun()  # <- Updated from experimental_rerun

def confirm_leave():
    for class_id in st.session_state.selected_classes_to_leave:
        removeUserFromClass(class_id)
    st.session_state.leave_mode = False
    st.session_state.selected_classes_to_leave.clear()
    st.rerun()  # <- Updated from experimental_rerun

# ---------- Get User Info & Class List ----------
userInfo = getUserInfo()
classes = getClassList()

# ---------- Sidebar ----------
st.sidebar.markdown(
    """
    <style>
        .sidebar-title {
            font-size: 24px; font-weight: bold;
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
if st.sidebar.button("Leave Classes", use_container_width=True):
    toggle_leave_mode()

# ---------- Page Header ----------
cols = st.columns([4, 1])
with cols[0]:
    st.markdown(
        f"""
        <div style='font-size: 40px; font-weight: bold; color: #2e86de;'>
            Welcome {userInfo['first_name']} {userInfo['last_name']}
        <p style='font-size: 18px; color: #555;'>Click on a course to view details</p>
        """,
        unsafe_allow_html=True
    )
with cols[1]:
    if st.button("Create Class"):
        st.switch_page("pages/create_class.py")

# ---------- Leave Mode Buttons ----------
if st.session_state.leave_mode:
    leave_cols = st.columns([1, 1])
    with leave_cols[0]:
        if st.button("Back"):
            toggle_leave_mode()
    with leave_cols[1]:
        if st.button("Confirm Leave"):
            confirm_leave()

# ---------- Class Cards or Checkboxes ----------
cols = st.columns(3)

for i, c in enumerate(classes):
    with cols[i % 3]:
        if st.session_state.leave_mode:
            checked = st.checkbox(c["name"], key=f"leave_{c['class_id']}")
            if checked:
                st.session_state.selected_classes_to_leave.add(c["class_id"])
            else:
                st.session_state.selected_classes_to_leave.discard(c["class_id"])
        else:
            if st.button(c["name"], key=1888888 + i, use_container_width=True):
                st.session_state.selected_class_id = c["class_id"]
                st.switch_page("pages/classes.py")
