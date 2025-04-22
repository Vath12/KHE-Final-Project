import streamlit as st

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

st.sidebar.markdown("<div class='sidebar-title'>📘 GradeBook</div>", unsafe_allow_html=True)
st.sidebar.markdown("<div class='sidebar-link'>🔔 Notifications</div>", unsafe_allow_html=True)
st.sidebar.markdown("<div class='sidebar-link'>📚 Courses</div>", unsafe_allow_html=True)
st.sidebar.markdown("<div class='sidebar-link'>👨‍🏫 Instructors</div>", unsafe_allow_html=True)
st.sidebar.markdown("<div class='sidebar-link'>🙍 Profile</div>", unsafe_allow_html=True)

# ---------- Page Title ----------
st.markdown(
    """
    <h1 style='color: #2e86de;'>Welcome to Your Dashboard</h1>
    <p style='font-size: 18px; color: #555;'>Click on course to view details</p>
    """,
    unsafe_allow_html=True
)

# ---------- Class Cards Layout ----------
cols = st.columns(3)

for i in range(6):  # 2 rows of 3 cards
    with cols[i % 3]:
        if st.button("Class",key = 1888888+i):
            st.switch_page("pages/classes.py")
        #st.markdown(
        #    f"""
        #    <div style='
        #        background-color: #e8f0fe;
        #        border-radius: 12px;
        #        padding: 20px;
        #        margin: 15px 0;
        #        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.08);
        #        transition: 0.3s;
        #        cursor: pointer;
        #    'onmouseover="this.style.backgroundColor='#d0e3fd'" onmouseout="this.style.backgroundColor='#e8f0fe'">
        #        <h4 style='margin: 0; color: #1b4f72;'>Class Name</h4>
        #        <p style='margin: 5px 0 0; color: #34495e;'>Instructor Name</p>
        #    </div>
        #    """,
        #    unsafe_allow_html=True
        #)