import streamlit as st
from util.verification import isValidSession
from util.request import getClassInfo, getClassPermissions

isValidSession()

# Get class ID from session state or set a default
if "selected_class_id" not in st.session_state:
    st.switch_page("home.py")

# Get class information
class_info = getClassInfo(st.session_state.selected_class_id)

# Get class permissions for the current user
permissions = getClassPermissions(st.session_state.selected_class_id)

# Set up page
st.set_page_config(layout="wide", page_title=f"Course: {class_info['name']}")

# Create a row for the header and home button
col_left, col_right = st.columns([6, 1])

with col_left:
    st.markdown(f"<p style='font-size: 1em;'>{class_info['organization']}</p>", unsafe_allow_html=True)
    st.markdown(f"<p style='color: #7F27FF; font-size: 2.5em;'>{class_info['name']}</p>", unsafe_allow_html=True)
    st.markdown(f"<p style='font-size: 1em;'>{class_info['description']}</p>", unsafe_allow_html=True)

with col_right:
    if st.button("Home", use_container_width=True):
        st.switch_page("pages/home.py")

st.write("")

if class_info.get("join_code") is not None:
    st.markdown(f"<p style='color: #0066FF;'>Join Code: {class_info['join_code']}</p>", unsafe_allow_html=True)

canViewRoster = permissions.get("CAN_VIEW_ROSTER", False)
canManageAssignments = permissions.get("CAN_MANAGE_ASSIGNMENTS", False)
canGradeAssignments = permissions.get("CAN_GRADE_ASSIGNMENT", False)

# Create a list of navigation buttons to display
nav_buttons = []

# Add standard buttons for all users
nav_buttons.append({"label": "Assignments", "path": "pages/assignments.py"})

# Add Create button if user has permission
if canManageAssignments:
    nav_buttons.append({"label": "Create Assignments", "path": "pages/create_assignment.py"})

# Add other standard buttons
nav_buttons.append({"label": "Announcements", "path": "pages/announcements.py"})
nav_buttons.append({"label": "Grades", "path": "pages/grades.py"})

# Add Grade Assignments button if user has permission
if canGradeAssignments:
    nav_buttons.append({"label": "Manage Assignments", "path": "pages/edit_assignments.py"})

# Add View Class Roster button if user has permission
if canViewRoster or canManageAssignments:
    nav_buttons.append({"label": "Class Roster", "path": "pages/class_roster.py"})

# Create columns based on number of buttons
cols = st.columns(len(nav_buttons))

# Display buttons in columns
for i, btn in enumerate(nav_buttons):
    with cols[i]:
        if st.button(btn["label"], key=f"nav_{i}", use_container_width=True):
            st.switch_page(btn["path"])

st.markdown("---")

# Overview section shown by default
st.markdown(
    f"""
    <div style='padding: 2rem; background-color: #F0EFFF; border-left: 8px solid #9C4DFF; border-radius: 8px;'>
        <h3>Welcome to {class_info['name']}</h3>
        <p>Organization: {class_info.get('organization', 'N/A')}</p>
        <p>This is your course dashboard. Select a section above to begin.</p>
    </div>
    """,
    unsafe_allow_html=True
)