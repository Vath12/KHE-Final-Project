import streamlit as st
from util.verification import isValidSession
from util.request import getClassInfo, getClassPermissions, getClassRoster, setClassPermissions

isValidSession()

# Get class ID from session state or set a default
if "selected_class_id" not in st.session_state:
    st.switch_page("home.py")

# Get class information
class_info = getClassInfo(st.session_state.selected_class_id)

# Get class permissions for the current user
permissions = getClassPermissions(st.session_state.selected_class_id)

canViewRoster = permissions.get("CAN_VIEW_ROSTER", False)
canManageAssignments = permissions.get("CAN_MANAGE_ASSIGNMENTS", False)

# Set up page
st.set_page_config(layout="wide", page_title=f"Course: {class_info['name']} - Class Roster")

# Create a row for the header and home button
col_left, col_right = st.columns([6, 1])

with col_left:
    st.markdown(f"<p style='color: #7F27FF; font-size: 2.5em;'>{class_info['name']}: Class Roster</p>", unsafe_allow_html=True)

with col_right:
    if st.button("Back to Course", use_container_width=True):
        st.switch_page("pages/classes.py")

st.markdown("---")

if not (canViewRoster or canManageAssignments):
    st.error("You do not have permission to view the class roster.")
    st.stop()

# Display the class roster
class_roster = getClassRoster(st.session_state.selected_class_id)

st.markdown(
    """
    <div style='padding: 1rem; background-color: #FFF6D1; border-left: 8px solid #FFC700; border-radius: 8px;'>
        <h3>Class Roster</h3>
    """,
    unsafe_allow_html=True
)

if not class_roster:
    st.markdown("<p>No roster available for this course.</p>", unsafe_allow_html=True)
else:
    permissionMap = {
        'View Roster':'CAN_VIEW_ROSTER',
        'Manage Assignments':'CAN_MANAGE_ASSIGNMENTS',
        'Grade Assignments':'CAN_GRADE_ASSIGNMENT',
        'Remove Students':'CAN_REMOVE_STUDENT',
        'Edit Course':'CAN_EDIT_COURSE',
        'View Hidden Members':'CAN_VIEW_HIDDEN',
    }
    
    # Add a student count at the top
    st.markdown(f"**Total students enrolled:** {len(class_roster)}")
    
    for student in class_roster:
        with st.expander(f"{student['first_name']} {student['last_name']}"):
            # Show permissions as checkboxes
            permissions_changed = False
            student_permissions = {}
            
            for k in permissionMap.keys():
                permission_key = permissionMap[k]
                # Fix: Access permissions safely with default False value
                permissions_value = False
                
                # Handle permissions differently based on the data structure
                # Check if 'permissions' exists and is a dictionary
                if 'permissions' in student and isinstance(student['permissions'], dict):
                    permissions_value = student['permissions'].get(permission_key, False)
                # Otherwise, try direct attribute access if student is an object or dict with direct permissions
                elif permission_key in student:
                    permissions_value = student[permission_key]
                
                checkbox_val = st.checkbox(k, value=permissions_value, key=f"{student['user_id']}.{k}")
                
                # Store the checkbox value
                student_permissions[permission_key] = checkbox_val
                
                # Check if the value changed
                if checkbox_val != permissions_value:
                    permissions_changed = True
            
             # Add a save button if permissions were changed
            if permissions_changed:
                if st.button("Save Permission Changes", key=f"save_permissions_{student['user_id']}"):
                    # Call the setClassPermissions function to update the student's permissions
                    result = setClassPermissions(
                        class_id=st.session_state.selected_class_id,
                        target_user_id=student['user_id'],
                        CAN_VIEW_ROSTER=student_permissions.get('CAN_VIEW_ROSTER', False),
                        CAN_MANAGE_ASSIGNMENTS=student_permissions.get('CAN_MANAGE_ASSIGNMENTS', False),
                        CAN_GRADE_ASSIGNMENT=student_permissions.get('CAN_GRADE_ASSIGNMENT', False),
                        CAN_REMOVE_STUDENT=student_permissions.get('CAN_REMOVE_STUDENT', False),
                        CAN_EDIT_COURSE=student_permissions.get('CAN_EDIT_COURSE', False),
                        IS_INSTRUCTOR=student_permissions.get('IS_INSTRUCTOR', False),
                        CAN_VIEW_HIDDEN=student_permissions.get('CAN_VIEW_HIDDEN', False),
                        IS_VISIBLE=True
                    )
                    
                    if result:
                        st.success(f"Permissions updated for {student['first_name']} {student['last_name']}")
                        st.rerun()
                    else:
                        st.error("Failed to update permissions")

st.markdown("</div>", unsafe_allow_html=True)