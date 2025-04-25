import streamlit as st
from util.verification import isValidSession
from util.request import getClassInfo, getClassPermissions, getClassRoster, setClassPermissions, removeUserFromClass

# Ensure the user has a valid session
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
canRemoveStudent = permissions.get("CAN_REMOVE_STUDENT", False)

# Set up page
st.set_page_config(layout="wide", page_title=f"Course: {class_info['name']} - Class Roster")

# Create a row for the header and home button
col_left, col_right = st.columns([6, 1])

with col_left:
    st.markdown(f"<p style='color: #7F27FF; font-size: 2.5em;'>{class_info['name']} - Class Roster</p>", unsafe_allow_html=True)

with col_right:
    if st.button("Back to Course", use_container_width=True):
        st.switch_page("pages/classes.py")

st.markdown("---")

# Check if user has permission to view the roster or manage assignments
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
        'View Roster': 'CAN_VIEW_ROSTER',
        'Manage Assignments': 'CAN_MANAGE_ASSIGNMENTS',
        'Grade Assignments': 'CAN_GRADE_ASSIGNMENT',
        'Remove Students': 'CAN_REMOVE_STUDENT',
        'Edit Course': 'CAN_EDIT_COURSE',
        'View Hidden Members': 'CAN_VIEW_HIDDEN',
    }

    st.markdown(f"**Total students enrolled:** {len(class_roster)}")

    for student in class_roster:
        with st.expander(f"{student['first_name']} {student['last_name']}"):
            permissions_changed = False
            student_permissions = getClassPermissions(st.session_state.selected_class_id,student['user_id'])

            # Loop over permission map to create checkboxes
            for label, key in permissionMap.items():
                # Fetch the current permission value for the student
                permissions_value = student_permissions.get(key, False)

                # Set the checkbox value to match the student's current permission
                checkbox_val = st.checkbox(label, value=permissions_value, key=f"{student['user_id']}.{label}")
                student_permissions[key] = checkbox_val
                # Check if the permission value has changed
                if checkbox_val != permissions_value:
                    permissions_changed = True

            # New checkbox: Visible to All
            visible_key = f"{student['user_id']}.VISIBLE_TO_ALL"
            is_visible = student.get("IS_VISIBLE", True)  # Default to True if not provided
            visible_to_all = st.checkbox("Visible to All", value=is_visible, key=visible_key)
            student_permissions["IS_VISIBLE"] = visible_to_all

            # Add a "Kick" button next to the student's name if the user has permission to remove students
            if canRemoveStudent:
                if st.button(f"Kick {student['first_name']} {student['last_name']}", key=f"kick_{student['user_id']}"):
                    # Call the removeUserFromClass function when the button is clicked
                    result = removeUserFromClass(
                        class_id=st.session_state.selected_class_id,
                        user_id=student['user_id']
                    )
                    if result:
                        st.success(f"{student['first_name']} {student['last_name']} has been removed from the class.")
                        st.rerun()  # Reload the page to update the roster
                    else:
                        st.error(f"Failed to remove {student['first_name']} {student['last_name']} from the class.")

            # Optional: Save button only if permissions changed
            if permissions_changed:
                if st.button("Save Permission Changes", key=f"save_permissions_{student['user_id']}"):
                    result = setClassPermissions(
                        class_id=st.session_state.selected_class_id,
                        target_user_id=student['user_id'],
                        CAN_VIEW_ROSTER=student_permissions.get('CAN_VIEW_ROSTER', False),
                        CAN_MANAGE_ASSIGNMENTS=student_permissions.get('CAN_MANAGE_ASSIGNMENTS', False),
                        CAN_GRADE_ASSIGNMENT=student_permissions.get('CAN_GRADE_ASSIGNMENT', False),
                        CAN_REMOVE_STUDENT=student_permissions.get('CAN_REMOVE_STUDENT', False),
                        CAN_EDIT_COURSE=student_permissions.get('CAN_EDIT_COURSE', False),
                        CAN_VIEW_HIDDEN=student_permissions.get('CAN_VIEW_HIDDEN', False),
                        IS_VISIBLE=student_permissions.get("IS_VISIBLE", True),
                        IS_INSTRUCTOR=student_permissions.get("IS_INSTRUCTOR", False)  # <- Added IS_INSTRUCTOR
                    )

                    # Since result is a bool, check if it's True (success) or False (failure)
                    if result:
                        st.success(f"Permissions updated for {student['first_name']} {student['last_name']}")
                        st.rerun()
                    else:
                        st.error(f"Failed to update permissions for {student['first_name']} {student['last_name']}.")

st.markdown("</div>", unsafe_allow_html=True)
