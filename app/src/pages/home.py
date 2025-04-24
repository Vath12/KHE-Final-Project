import streamlit as st
from util.verification import isValidSession
from util.request import *

isValidSession()

userInfo = getUserInfo()
classes = getClassList()

st.set_page_config(page_title="homepage", layout="wide")

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

if st.sidebar.button("Profile",use_container_width=True):
    st.switch_page("pages/profile_display.py")
if st.sidebar.button("Notifications",use_container_width=True):
    st.switch_page("pages/notification.py")
if st.sidebar.button("Manage Classes",use_container_width=True):
    st.switch_page("pages/manage_classes.py")



cols = st.columns([4,1])
with cols[0]:
    # ---------- Page Title ----------
    st.markdown(
        f"""
        <div style='font-size: 40px; font-weight: bold; color: #2e86de;'>
            Welcome {userInfo['first_name']} {userInfo['last_name']}
        <p style='font-size: 18px; color: #555;'>Click on a course to view details</p>
        """,
        unsafe_allow_html=True
    )
with cols[1]:
    # ---------- Create Class Button ----------
    if st.button("Create Class"):
        st.switch_page("pages/create_classes.py")

# ---------- Class Cards Layout ----------
cols = st.columns(3)

for i in range(len(classes)):
    with cols[i % 3]:
        if st.button(classes[i]["name"], key=1888888 + i, use_container_width=True):
            st.switch_page("pages/classes.py")



