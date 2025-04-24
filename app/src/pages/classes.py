import streamlit as st
from util.verification import isValidSession
from util.request import getClassInfo, getAssignments, getAnnouncements, getGrade, getAssignmentDetails, getClassPermissions, getClassRoster

isValidSession()

# Get class ID from session state or set a default
if "selected_class_id" not in st.session_state:
    st.session_state.selected_class_id = 1  # Default class ID

# Get class information
class_info = getClassInfo(st.session_state.selected_class_id)

# Get user permissions for this class
permissions = getClassPermissions(st.session_state.selected_class_id)

# Set up page
st.set_page_config(layout="wide", page_title=f"Course: {class_info['name']}")

# Create a row for the header and home button
col_left, col_right = st.columns([6, 1])

with col_left:
    st.markdown(f"<h1 style='color: #7F27FF;'>Course: {class_info['name']}</h1>", unsafe_allow_html=True)

with col_right:
    if st.button("Home", use_container_width=True):
        st.switch_page("pages/home.py")

st.write("")

# Track which section is selected
if "selected_section" not in st.session_state:
    st.session_state.selected_section = "overview"

# Section buttons
st.markdown("### Navigate")

# Determine number of columns based on permissions
nav_buttons = 3  # Default: Assignments, Announcements, Grades
if permissions.get('CAN_MANAGE_ASSIGNMENTS', False):
    nav_buttons += 1  # Manage Assignments
if permissions.get('CAN_GRADE_ASSIGNMENT', False):
    nav_buttons += 1  # Grade Assignments
if permissions.get('CAN_VIEW_ROSTER', False):
    nav_buttons += 1  # Class Roster

# Create columns for navigation buttons
nav_cols = st.columns(min(nav_buttons, 6))  # Max 6 columns to prevent overcrowding

# Standard buttons for all users
button_index = 0
with nav_cols[button_index]:
    if st.button("Assignments"):
        st.session_state.selected_section = "assignments"
    button_index += 1

with nav_cols[button_index]:
    if st.button("Announcements"):
        st.session_state.selected_section = "announcements"
    button_index += 1

with nav_cols[button_index]:
    if st.button("Grades"):
        st.session_state.selected_section = "grades"
    button_index += 1

# Conditional buttons based on permissions
if permissions.get('CAN_MANAGE_ASSIGNMENTS', False) and button_index < len(nav_cols):
    with nav_cols[button_index]:
        if st.button("Manage Assignments"):
            st.session_state.selected_section = "manage_assignments"
        button_index += 1

if permissions.get('CAN_GRADE_ASSIGNMENT', False) and button_index < len(nav_cols):
    with nav_cols[button_index]:
        if st.button("Grade Assignments"):
            st.session_state.selected_section = "grade_assignments"
        button_index += 1

if permissions.get('CAN_VIEW_ROSTER', False) and button_index < len(nav_cols):
    with nav_cols[button_index]:
        if st.button("Class Roster"):
            st.session_state.selected_section = "class_roster"

st.markdown("---")

# Display content based on section
if st.session_state.selected_section == "assignments":
    assignments = getAssignments(st.session_state.selected_class_id)
    
    st.markdown(
        """
        <div style='padding: 1rem; background-color: #FFF6D1; border-left: 8px solid #FFC700; border-radius: 8px;'>
            <h3>Assignments</h3>
        """,
        unsafe_allow_html=True
    )
    
    if not assignments:
        st.markdown("<p>No assignments available for this course.</p>", unsafe_allow_html=True)
    else:
        st.markdown("<ul style='line-height: 2;'>", unsafe_allow_html=True)
        for assignment in assignments:
            assignment_name = assignment.get('name', 'Unnamed Assignment')
            due_date = assignment.get('due_date', 'No due date')
            weight = assignment.get('overall_weight', 0)
            
            # Convert weight to float and then to percentage for display
            try:
                weight_float = float(weight)
                weight_percentage = weight_float * 100
                
                # Format the weight display
                if weight_percentage == int(weight_percentage):
                    weight_display = f"{int(weight_percentage)}%"
                else:
                    weight_display = f"{weight_percentage:.1f}%"
            except:
                weight_display = f"{weight}%"
            
            # Create an expander for each assignment
            with st.expander(f"{assignment_name} - Due: {due_date} (Weight: {weight_display})"):
                assignment_id = assignment.get('assignment_id')
                
                # Get assignment details if available
                try:
                    details = getAssignmentDetails(st.session_state.selected_class_id, assignment_id)
                    if details:
                        st.markdown("#### Components:")
                        for component in details:
                            name = component.get('name', 'Unnamed Component')
                            value = component.get('value', 0)
                            comp_weight = component.get('weight', 0)
                            
                            # Convert component weight to float and then to percentage for display
                            try:
                                comp_weight_float = float(comp_weight)
                                comp_weight_percentage = comp_weight_float * 100
                                
                                # Format the component weight display
                                if comp_weight_percentage == int(comp_weight_percentage):
                                    comp_weight_display = f"{int(comp_weight_percentage)}%"
                                else:
                                    comp_weight_display = f"{comp_weight_percentage:.1f}%"
                            except:
                                comp_weight_display = f"{comp_weight}%"
                            
                            st.markdown(f"- **{name}**: {value} points ({comp_weight_display} of assignment)")
                    else:
                        st.markdown("No detailed components available for this assignment.")
                except Exception as e:
                    st.markdown(f"Error loading assignment details: {str(e)}")
        
        st.markdown("</ul>", unsafe_allow_html=True)
    
    st.markdown("</div>", unsafe_allow_html=True)

elif st.session_state.selected_section == "announcements":
    announcements = getAnnouncements(st.session_state.selected_class_id)
    
    st.markdown(
        """
        <div style='padding: 1rem; background-color: #D9F6FF; border-left: 8px solid #1E90FF; border-radius: 8px;'>
            <h3>Announcements</h3>
        """,
        unsafe_allow_html=True
    )
    
    if not announcements:
        st.markdown("<p>No announcements available for this course.</p>", unsafe_allow_html=True)
    else:
        for announcement in announcements:
            title = announcement.get('title', 'Untitled Announcement')
            message = announcement.get('message', 'No message content')
            date = announcement.get('date_posted', 'Unknown date')
            
            st.markdown(f"""
            <div style='margin-bottom: 1.5rem; padding: 1rem; background-color: white; border-radius: 8px;'>
                <h4>{title}</h4>
                <p style='font-size: 0.9rem; color: #666;'>Posted: {date}</p>
                <p>{message}</p>
            </div>
            """, unsafe_allow_html=True)
    
    st.markdown("</div>", unsafe_allow_html=True)

elif st.session_state.selected_section == "grades":
    assignments = getAssignments(st.session_state.selected_class_id)
    
    st.markdown(
        """
        <div style='padding: 1rem; background-color: #E6FFE6; border-left: 8px solid #00CC66; border-radius: 8px;'>
            <h3>Grades</h3>
        """,
        unsafe_allow_html=True
    )
    
    if not assignments:
        st.markdown("<p>No graded assignments available for this course.</p>", unsafe_allow_html=True)
    else:
        for assignment in assignments:
            assignment_id = assignment.get('assignment_id')
            assignment_name = assignment.get('name', 'Unnamed Assignment')
            
            # Get grade data for this assignment
            try:
                grades = getGrade(st.session_state.selected_class_id, assignment_id)
                
                with st.expander(f"{assignment_name}"):
                    if not grades:
                        st.markdown("No grade information available yet.")
                    else:
                        total_points = 0
                        earned_points = 0
                        
                        for component in grades:
                            name = component.get('name', 'Unnamed Component')
                            grade = component.get('grade', 'Not graded')
                            value = component.get('value', 0)
                            weight = component.get('weight', 0)
                            
                            # Convert weight to float and then to percentage for display
                            try:
                                weight_float = float(weight)
                                weight_percentage = weight_float * 100
                                
                                # Format the weight display
                                if weight_percentage == int(weight_percentage):
                                    weight_display = f"{int(weight_percentage)}%"
                                else:
                                    weight_display = f"{weight_percentage:.1f}%"
                            except:
                                weight_display = f"{weight}%"
                            
                            st.markdown(f"**{name}** ({weight_display}): {grade}/{value}")
                            
                            if grade != 'Not graded':
                                try:
                                    # Convert to float for calculation
                                    grade_float = float(grade)
                                    value_float = float(value)
                                    weight_float = float(weight)
                                    
                                    # Use the weight as is (already in decimal form) for calculations
                                    earned_points += grade_float * weight_float
                                    total_points += value_float * weight_float
                                except Exception as e:
                                    st.markdown(f"Error in calculation: {str(e)}")
                        
                        if total_points > 0:
                            percentage = (earned_points / total_points) * 100
                            st.markdown(f"**Total Score: {earned_points:.2f}/{total_points:.2f} ({percentage:.2f}%)**")
            except Exception as e:
                st.markdown(f"Error loading grades for {assignment_name}: {str(e)}")
    
    st.markdown("</div>", unsafe_allow_html=True)

# MANAGE ASSIGNMENTS SECTION
elif st.session_state.selected_section == "manage_assignments" and permissions.get('CAN_MANAGE_ASSIGNMENTS', False):
    st.markdown(
        """
        <div style='padding: 1rem; background-color: #F0E6FF; border-left: 8px solid #9C4DFF; border-radius: 8px;'>
            <h3>Manage Assignments</h3>
        """,
        unsafe_allow_html=True
    )
    
    # Create New Assignment Button
    if st.button("➕ Create New Assignment", type="primary"):
        st.session_state.show_assignment_form = True
    
    # Show assignment creation form
    if st.session_state.get("show_assignment_form", False):
        with st.form("new_assignment_form"):
            st.subheader("Create New Assignment")
            
            assignment_name = st.text_input("Assignment Name", placeholder="Enter a descriptive name")
            due_date = st.date_input("Due Date")
            weight = st.number_input("Overall Weight (%)", min_value=0.0, max_value=100.0, step=5.0, value=10.0) / 100
            
            st.markdown("### Assignment Components")
            
            # Default to 1 component, allow adding more
            if "component_count" not in st.session_state:
                st.session_state.component_count = 1
            
            components = []
            
            for i in range(st.session_state.component_count):
                st.markdown(f"#### Component {i+1}")
                col1, col2 = st.columns(2)
                with col1:
                    comp_name = st.text_input("Name", key=f"comp_name_{i}", placeholder="e.g., Written Response")
                with col2:
                    comp_value = st.number_input("Max Points", key=f"comp_value_{i}", min_value=0, value=10)
                
                comp_weight = st.slider("Component Weight (%)", key=f"comp_weight_{i}", min_value=0, max_value=100, value=100 if i == 0 else 0)
                
                components.append({
                    "name": comp_name,
                    "value": comp_value,
                    "weight": comp_weight / 100  # Convert to decimal
                })
            
            # Button to add more components
            if st.form_submit_button("Add Another Component"):
                st.session_state.component_count += 1
                st.rerun()
            
            # Make sure weights sum to 100%
            total_weight = sum(c["weight"] * 100 for c in components)
            if total_weight != 100:
                st.warning(f"Total component weight is {total_weight}%. It should equal 100%.")
            
            # Form submission
            col1, col2 = st.columns(2)
            with col1:
                submit = st.form_submit_button("Create Assignment", type="primary", use_container_width=True)
            with col2:
                cancel = st.form_submit_button("Cancel", use_container_width=True)
            
            if submit:
                if not assignment_name:
                    st.error("Assignment name is required")
                elif total_weight != 100:
                    st.error("Component weights must sum to 100%")
                else:
                    # Here you would make an API call to create the assignment
                    # For demonstration, just show success message
                    st.success(f"Assignment '{assignment_name}' created successfully!")
                    st.session_state.show_assignment_form = False
                    st.rerun()
            
            if cancel:
                st.session_state.show_assignment_form = False
                st.rerun()
    
    # Edit/Delete Existing Assignments
    st.markdown("### Existing Assignments")
    
    assignments = getAssignments(st.session_state.selected_class_id)
    
    if not assignments:
        st.info("No assignments created yet")
    else:
        for assignment in assignments:
            assignment_name = assignment.get('name', 'Unnamed Assignment')
            assignment_id = assignment.get('assignment_id')
            due_date = assignment.get('due_date', 'No due date')
            
            with st.expander(f"{assignment_name} - Due: {due_date}"):
                col1, col2, col3 = st.columns([3, 1, 1])
                with col1:
                    st.markdown(f"**Assignment ID:** {assignment_id}")
                with col2:
                    if st.button("Edit", key=f"edit_{assignment_id}", use_container_width=True):
                        # Here you would implement edit functionality
                        st.info("Edit functionality would go here")
                with col3:
                    if st.button("Delete", key=f"delete_{assignment_id}", use_container_width=True):
                        # Confirm deletion
                        st.warning(f"Are you sure you want to delete '{assignment_name}'?")
                        col1, col2 = st.columns(2)
                        with col1:
                            if st.button("Yes, Delete", key=f"confirm_delete_{assignment_id}", use_container_width=True):
                                # Here you would make an API call to delete the assignment
                                st.success(f"Assignment '{assignment_name}' deleted successfully!")
                                st.rerun()
                        with col2:
                            if st.button("Cancel", key=f"cancel_delete_{assignment_id}", use_container_width=True):
                                st.rerun()
    
    st.markdown("</div>", unsafe_allow_html=True)

# GRADE ASSIGNMENTS SECTION
elif st.session_state.selected_section == "grade_assignments" and permissions.get('CAN_GRADE_ASSIGNMENT', False):
    st.markdown(
        """
        <div style='padding: 1rem; background-color: #FFE6E6; border-left: 8px solid #FF5757; border-radius: 8px;'>
            <h3>Grade Assignments</h3>
        """,
        unsafe_allow_html=True
    )
    
    # Get the class roster
    try:
        roster = getClassRoster(st.session_state.selected_class_id)
    except Exception as e:
        st.error(f"Error loading class roster: {str(e)}")
        roster = []
    
    # Get assignments
    assignments = getAssignments(st.session_state.selected_class_id)
    
    if not assignments:
        st.info("No assignments available to grade")
    else:
        # Initialize session state variables if they don't exist
        if "selected_assignment_id" not in st.session_state:
            st.session_state.selected_assignment_id = None
        if "selected_student_index" not in st.session_state:
            st.session_state.selected_student_index = None
        
        # Assignment selector
        assignment_options = {a.get('assignment_id'): a.get('name', 'Unnamed Assignment') for a in assignments}
        assignment_selected = st.selectbox(
            "Select Assignment to Grade", 
            options=list(assignment_options.keys()),
            format_func=lambda x: assignment_options.get(x),
            index=None if st.session_state.selected_assignment_id is None else 
                  list(assignment_options.keys()).index(st.session_state.selected_assignment_id)
        )
        
        if assignment_selected:
            st.session_state.selected_assignment_id = assignment_selected
            
            # Get assignment details
            selected_assignment = next((a for a in assignments if a.get('assignment_id') == assignment_selected), None)
            
            if selected_assignment:
                # Display assignment info
                st.markdown(f"### Grading: {selected_assignment.get('name')}")
                st.markdown(f"**Due Date:** {selected_assignment.get('due_date', 'No due date')}")
                
                # Get assignment components
                try:
                    components = getAssignmentDetails(st.session_state.selected_class_id, assignment_selected)
                    if not components:
                        st.warning("This assignment has no grading components defined")
                except Exception as e:
                    st.error(f"Error loading assignment details: {str(e)}")
                    components = []
                
                # Student selector
                if roster:
                    student_options = [f"{s.get('first_name', '')} {s.get('last_name', '')}" for s in roster]
                    student_index = st.selectbox(
                        "Select Student", 
                        options=range(len(student_options)),
                        format_func=lambda i: student_options[i],
                        index=st.session_state.selected_student_index
                    )
                    
                    if student_index is not None:
                        st.session_state.selected_student_index = student_index
                        selected_student = roster[student_index]
                        
                        # Display grading form
                        with st.form("grading_form"):
                            st.subheader(f"Grade for: {student_options[student_index]}")
                            
                            grades = []
                            feedback = ""
                            
                            if components:
                                for component in components:
                                    comp_name = component.get('name', 'Unnamed Component')
                                    comp_value = component.get('value', 0)
                                    
                                    # Get current grade if exists
                                    current_grade = "Not graded"  # You would get this from an API
                                    
                                    # Grade input
                                    grade = st.number_input(
                                        f"{comp_name} (max: {comp_value})",
                                        min_value=0.0,
                                        max_value=float(comp_value),
                                        value=float(current_grade) if current_grade != "Not graded" else 0.0,
                                        step=0.5
                                    )
                                    
                                    grades.append({
                                        "component_id": component.get('component_id', 1),  # Assuming component IDs
                                        "grade": grade
                                    })
                            
                            # Feedback section
                            st.markdown("### Feedback")
                            feedback = st.text_area("Add feedback for the student", height=150)
                            
                            # Submit button
                            submit_grade = st.form_submit_button("Submit Grade", type="primary")
                            
                            if submit_grade:
                                # Here you would make an API call to submit the grades
                                # Example data structure:
                                grade_data = {
                                    "assignment_id": assignment_selected,
                                    "student_id": selected_student.get('student_id', 1),  # Assuming student IDs
                                    "grades": grades,
                                    "feedback": feedback
                                }
                                
                                # For demonstration just show success
                                st.success("Grades submitted successfully!")
                else:
                    st.warning("No students enrolled in this class")
        
    st.markdown("</div>", unsafe_allow_html=True)

# CLASS ROSTER SECTION
elif st.session_state.selected_section == "class_roster" and permissions.get('CAN_VIEW_ROSTER', False):
    st.markdown(
        """
        <div style='padding: 1rem; background-color: #E6FFFA; border-left: 8px solid #00C9A7; border-radius: 8px;'>
            <h3>Class Roster</h3>
        """,
        unsafe_allow_html=True
    )
    
    # Get the class roster
    try:
        roster = getClassRoster(st.session_state.selected_class_id)
    except Exception as e:
        st.error(f"Error loading class roster: {str(e)}")
        roster = []
    
    if not roster:
        st.info("No students enrolled in this class")
    else:
        # Display the roster
        st.markdown("### Enrolled Students")
        
        for i, student in enumerate(roster):
            first_name = student.get('first_name', '')
            last_name = student.get('last_name', '')
            
            st.markdown(f"**{i+1}.** {first_name} {last_name}")
        
        st.markdown(f"**Total students:** {len(roster)}")
    
    st.markdown("</div>", unsafe_allow_html=True)

else:
    st.markdown(
        f"""
        <div style='padding: 2rem; background-color: #F0EFFF; border-left: 8px solid #9C4DFF; border-radius: 8px;'>
            <h3>Welcome to {class_info['name']}</h3>
            <p>{class_info.get('description', 'No description available.')}</p>
            <p>Organization: {class_info.get('organization', 'N/A')}</p>
            <p>This is your course dashboard. Select a section above to begin.</p>
        </div>
        """,
        unsafe_allow_html=True
    )