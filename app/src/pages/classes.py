import streamlit as st
import requests
import time
from util.verification import isValidSession
from util.request import (getClassInfo, getAssignments, getAnnouncements, getGrade, 
                          getAssignmentDetails, getClassPermissions, getClassRoster, 
                          setGrade, deleteAssignment, updateAssignmnet, 
                          createAssignmentCriterion, updateAssignmentCriterion, 
                          safeDelete, API, safePut, getComments, createComment)

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

# Track which section is selected
if "selected_section" not in st.session_state:
    st.session_state.selected_section = "overview"

if class_info.get("join_code") is not None:
    st.markdown(f"<p style='color: #0066FF;'>Join Code: {class_info['join_code']}</p>", unsafe_allow_html=True)

canViewRoster = permissions.get("CAN_VIEW_ROSTER", False)
canManageAssignments = permissions.get("CAN_MANAGE_ASSIGNMENTS", False)
canGradeAssignments = permissions.get("CAN_GRADE_ASSIGNMENT", False)

# Create a list of navigation buttons to display
nav_buttons = []

# Add standard buttons for all users
nav_buttons.append({"label": "Assignments", "section": "assignments"})

# Add Create button if user has permission
if canManageAssignments:
    nav_buttons.append({"label": "Create", "action": "switch_page", "target": "pages/assignments.py"})

# Add other standard buttons
nav_buttons.append({"label": "Announcements", "section": "announcements"})
nav_buttons.append({"label": "Grades", "section": "grades"})

# Add Grade Assignments button if user has permission
if canGradeAssignments:
    nav_buttons.append({"label": "Manage Assignments", "section": "grade_assignments"})

# Add View Class Roster button if user has permission
if canViewRoster or canManageAssignments:
    nav_buttons.append({"label": "View Class Roster", "section": "roster"})

# Create columns based on number of buttons
cols = st.columns(len(nav_buttons))

# Display buttons in columns
for i, btn in enumerate(nav_buttons):
    with cols[i]:
        if "action" in btn and btn["action"] == "switch_page":
            # Button switches to another page
            if st.button(btn["label"], key=f"nav_{i}", use_container_width=True):
                st.switch_page(btn["target"])
        else:
            # Button changes section
            if st.button(btn["label"], key=f"nav_{i}", use_container_width=True):
                st.session_state.selected_section = btn["section"]

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
            weight_float = float(weight)
            weight_percentage = weight_float * 100
            
            # Format the weight display
            if weight_percentage == int(weight_percentage):
                weight_display = f"{int(weight_percentage)}%"
            else:
                weight_display = f"{weight_percentage:.1f}%"
            
            # Create an expander for each assignment
            with st.expander(f"{assignment_name} - Due: {due_date} (Weight: {weight_display})"):
                assignment_id = assignment.get('assignment_id')
                
                # Get assignment details if available
                details = getAssignmentDetails(st.session_state.selected_class_id, assignment_id)
                if details:
                    st.markdown("#### Components:")
                    for component in details:
                        name = component.get('name', 'Unnamed Component')
                        value = component.get('value', 0)
                        comp_weight = component.get('weight', 0)
                        
                        # Convert component weight to float and then to percentage for display
                        comp_weight_float = float(comp_weight)
                        comp_weight_percentage = comp_weight_float * 100
                        
                        # Format the component weight display
                        if comp_weight_percentage == int(comp_weight_percentage):
                            comp_weight_display = f"{int(comp_weight_percentage)}%"
                        else:
                            comp_weight_display = f"{comp_weight_percentage:.1f}%"
                        
                        st.markdown(f"- **{name}**: {value} points ({comp_weight_display} of assignment)")
                else:
                    st.markdown("No detailed components available for this assignment.")
                
                # Get and display comments for the assignment
                try:
                    comments = getComments(st.session_state.selected_class_id, assignment_id)
                    
                    if comments and len(comments) > 0:
                        st.markdown("#### Comments:")
                        for comment in comments:
                            author = f"{comment.get('author_first_name', 'Unknown')} {comment.get('author_last_name', 'User')}"
                            message = comment.get('message', 'No content')
                            created_on = comment.get('created_on', 'Unknown date')
                            
                            st.markdown(f"""
                            <div style='margin-bottom: 1rem; padding: 0.75rem; background-color: #f5f5f5; border-radius: 6px;'>
                                <p style='font-size: 0.9rem; color: #666; margin-bottom: 0.25rem;'><b>{author}</b> • {created_on}</p>
                                <p style='margin: 0;'>{message}</p>
                            </div>
                            """, unsafe_allow_html=True)
                except:
                    pass
        
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
            
            # Force reload grades on each render to ensure up-to-date data
            st.session_state.force_reload_grades = True
            
            # Get grade data for this assignment using the student_id parameter
            try:
                # Use -1 to indicate current user (as per the getGrade docstring)
                grades = getGrade(st.session_state.selected_class_id, assignment_id)
            except requests.exceptions.JSONDecodeError:
                grades = []  # If we can't decode JSON, assume no grades
            except Exception as e:
                st.error(f"Error fetching grades: {str(e)}")
                grades = []
            
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
                        weight_float = float(weight)
                        weight_percentage = weight_float * 100
                        
                        # Format the weight display
                        if weight_percentage == int(weight_percentage):
                            weight_display = f"{int(weight_percentage)}%"
                        else:
                            weight_display = f"{weight_percentage:.1f}%"
                        
                        st.markdown(f"**{name}** ({weight_display}): {grade}/{value}")
                        
                        if grade != 'Not graded':
                            # Convert to float for calculation
                            try:
                                grade_float = float(grade)
                                value_float = float(value)
                                weight_float = float(weight)
                                
                                # Use the weight as is (already in decimal form) for calculations
                                earned_points += grade_float * weight_float
                                total_points += value_float * weight_float
                            except ValueError:
                                st.warning(f"Could not calculate grade for {name}: invalid grade '{grade}'")
                    
                    if total_points > 0:
                        percentage = (earned_points / total_points) * 100
                        st.markdown(f"**Grade**: {earned_points:.2f}/{total_points:.2f} = {percentage:.2f}%")
                    else:
                        st.markdown("**Grade**: Not graded")
                
                # Get and display comments for this assignment
                try:
                    comments = getComments(st.session_state.selected_class_id, assignment_id)
                    
                    if comments and len(comments) > 0:
                        st.markdown("#### Instructor Feedback:")
                        for comment in comments:
                            author = f"{comment.get('author_first_name', 'Unknown')} {comment.get('author_last_name', 'User')}"
                            message = comment.get('message', 'No content')
                            created_on = comment.get('created_on', 'Unknown date')
                            
                            st.markdown(f"""
                            <div style='margin-top: 0.5rem; padding: 0.75rem; background-color: #F0FFF0; border-left: 3px solid #00CC66; border-radius: 6px;'>
                                <p style='font-size: 0.9rem; color: #666; margin-bottom: 0.25rem;'><b>{author}</b> • {created_on}</p>
                                <p style='margin: 0;'>{message}</p>
                            </div>
                            """, unsafe_allow_html=True)
                except:
                    pass
    
    st.markdown("</div>", unsafe_allow_html=True)

elif st.session_state.selected_section == "grade_assignments" and canGradeAssignments:
    st.markdown(
        """
        <div style='padding: 1rem; background-color: #FFE6E6; border-left: 8px solid #FF5757; border-radius: 8px;'>
            <h3>Manage Assignments</h3>
        """,
        unsafe_allow_html=True
    )
    
    # Get assignments
    assignments = getAssignments(st.session_state.selected_class_id)
    
    if not assignments:
        st.info("No assignments available to manage")
    else:
        # Action selector
        action = st.selectbox(
            "What would you like to do?", 
            options=["Grade Assignments", "Edit Assignment"]
        )
        
        # Assignment selector
        assignment_options = {str(a.get('assignment_id')): a.get('name', 'Unnamed Assignment') for a in assignments}
        assignment_selected = st.selectbox(
            "Select Assignment", 
            options=list(assignment_options.keys()),
            format_func=lambda x: assignment_options.get(x)
        )
        
        if assignment_selected:
            selected_assignment_id = int(assignment_selected)
            
            # Get assignment details
            selected_assignment = next((a for a in assignments if a.get('assignment_id') == selected_assignment_id), None)
            
            if selected_assignment:
                assignment_details = getAssignmentDetails(st.session_state.selected_class_id, selected_assignment_id)
                
                # Display assignment info
                st.markdown(f"### Selected: {selected_assignment.get('name')}")
                st.markdown(f"**Due Date:** {selected_assignment.get('due_date', 'No due date')}")
                
                if action == "Grade Assignments":
                    # GRADING SECTION
                    # Get class roster
                    roster = getClassRoster(st.session_state.selected_class_id)
                    
                    if roster:
                        # Student selector
                        student_options = {str(s.get('user_id')): f"{s.get('first_name', '')} {s.get('last_name', '')}" for s in roster}
                        student_selected = st.selectbox(
                            "Select Student", 
                            options=list(student_options.keys()),
                            format_func=lambda x: student_options.get(x)
                        )
                        
                        if student_selected:
                            selected_student_id = int(student_selected)
                            selected_student = next((s for s in roster if s.get('user_id') == selected_student_id), None)
                            
                            if selected_student:
                                # Get current grades and comments if they exist
                                try:
                                    current_grades = getGrade(
                                        st.session_state.selected_class_id, 
                                        selected_assignment_id, 
                                        selected_student_id
                                    )
                                except requests.exceptions.JSONDecodeError:
                                    current_grades = []  # No grades yet
                                except Exception as e:
                                    st.error(f"Error fetching grades: {str(e)}")
                                    current_grades = []
                                
                                # Get existing comments/feedback
                                try:
                                    current_comments = getComments(
                                        st.session_state.selected_class_id,
                                        selected_assignment_id
                                    )
                                except:
                                    current_comments = []
                                
                                # Create a dictionary to easily look up grades by criterion
                                current_grades_dict = {}
                                for grade in current_grades:
                                    criterion_name = grade.get('name')
                                    if criterion_name:
                                        current_grades_dict[criterion_name] = grade
                                
                                # Display grading form
                                with st.form("grading_form"):
                                    st.subheader(f"Grade for: {student_options.get(student_selected)}")
                                    
                                    # Initialize variables for grade calculation
                                    total_earned = 0
                                    total_possible = 0  # This will hold the total max points
                                    grades_to_submit = []
                                    
                                    # Grade inputs for each criterion
                                    if assignment_details:
                                        for criterion in assignment_details:
                                            criterion_id = criterion.get('criterion_id')
                                            criterion_name = criterion.get('name', 'Unnamed Criterion')
                                            criterion_value = float(criterion.get('value', 0))
                                            criterion_weight = float(criterion.get('weight', 0))
                                            
                                            # Get current grade if it exists
                                            current_grade = "Not graded"
                                            if criterion_name in current_grades_dict:
                                                current_grade = current_grades_dict[criterion_name].get('grade', "Not graded")
                                            
                                            try:
                                                current_grade_float = float(current_grade) if current_grade != "Not graded" else 0.0
                                            except:
                                                current_grade_float = 0.0
                                            
                                            # Create column layout for each criterion
                                            col1, col2 = st.columns([3, 1])
                                            
                                            with col1:
                                                st.markdown(f"**{criterion_name}** (Max: {criterion_value} points, Weight: {criterion_weight*100:.1f}%)")
                                            
                                            with col2:
                                                # Grade input - use a unique key based on criterion_id to avoid duplicates
                                                grade_value = st.number_input(
                                                    f"Grade for {criterion_name}",
                                                    min_value=0.0,
                                                    max_value=criterion_value,
                                                    value=min(current_grade_float, criterion_value),
                                                    step=0.5,
                                                    key=f"grade_input_{criterion_id}",
                                                    label_visibility="collapsed"
                                                )
                                            
                                            # For raw point calculation
                                            total_earned += grade_value  # Actual points earned
                                            total_possible += criterion_value  # Maximum possible points
                                            
                                            # Add to grades to submit
                                            grades_to_submit.append({
                                                "criterion_id": criterion_id,
                                                "grade": grade_value
                                            })
                                            
                                            st.markdown("---")
                                    
                                    # Show total points and percentage
                                    if total_possible > 0:
                                        percentage = (total_earned / total_possible) * 100
                                        st.markdown(f"**Total Score: {total_earned:.2f}/{total_possible:.2f} ({percentage:.2f}%)**")
                                    else:
                                        st.warning("Cannot calculate final grade: total possible points is 0")
                                    
                                    # Feedback/Comments section
                                    st.markdown("### Feedback / Comments")
                                    
                                    # Show existing comments/feedback
                                    if current_comments:
                                        st.markdown("#### Existing Feedback:")
                                        for comment in current_comments:
                                            author = f"{comment.get('author_first_name', 'Unknown')} {comment.get('author_last_name', 'User')}"
                                            message = comment.get('message', 'No content')
                                            created_on = comment.get('created_on', 'Unknown date')
                                            
                                            st.markdown(f"""
                                            <div style='margin-bottom: 1rem; padding: 0.75rem; background-color: #f5f5f5; border-radius: 6px;'>
                                                <p style='font-size: 0.9rem; color: #666; margin-bottom: 0.25rem;'><b>{author}</b> • {created_on}</p>
                                                <p style='margin: 0;'>{message}</p>
                                            </div>
                                            """, unsafe_allow_html=True)
                                    
                                    # New feedback input
                                    new_feedback = st.text_area(
                                        "Add or update feedback for the student",
                                        height=150
                                    )
                                    
                                    # Submit button
                                    submit_grade = st.form_submit_button("Submit Grades & Feedback", type="primary")
                                    
                                    if submit_grade:
                                        # Add a placeholder for status messages
                                        status_placeholder = st.empty()
                                        status_placeholder.info("Submitting grades and feedback...")
                                        
                                        # Submit grades one by one with status updates
                                        success_count = 0
                                        failed_criteria = []
                                        
                                        for grade_item in grades_to_submit:
                                            criterion_id = grade_item["criterion_id"]
                                            grade_value = grade_item["grade"]
                                            
                                            status_placeholder.info(f"Submitting grade for criterion {criterion_id}...")
                                            
                                            # Use the setGrade function from request.py
                                            try:
                                                result = setGrade(
                                                    class_id=st.session_state.selected_class_id,
                                                    assignment_id=selected_assignment_id,
                                                    criterion_id=criterion_id,
                                                    student_id=selected_student_id,
                                                    grade=grade_value
                                                )
                                                
                                                if result:
                                                    success_count += 1
                                                    status_placeholder.success(f"Grade for criterion {criterion_id} submitted successfully")
                                                else:
                                                    status_placeholder.error(f"Failed to submit grade for criterion {criterion_id}")
                                                    failed_criteria.append(criterion_id)
                                            except requests.exceptions.JSONDecodeError:
                                                # If there's a JSON decode error but the request went through,
                                                # still consider it a success since the API might not return JSON
                                                success_count += 1
                                                status_placeholder.success(f"Grade for criterion {criterion_id} submitted successfully")
                                            except Exception as e:
                                                status_placeholder.error(f"Error setting grade for criterion {criterion_id}: {str(e)}")
                                                failed_criteria.append(criterion_id)
                                        
                                        # Submit feedback/comment if provided
                                        if new_feedback:
                                            status_placeholder.info("Submitting feedback...")
                                            try:
                                                # Use the createComment function to submit feedback
                                                feedback_result = createComment(
                                                    st.session_state.selected_class_id,
                                                    selected_assignment_id,
                                                    selected_student_id,
                                                    new_feedback
                                                )
                                                
                                                if feedback_result:
                                                    status_placeholder.success("Feedback submitted successfully")
                                                else:
                                                    status_placeholder.error("Failed to submit feedback")
                                            except Exception as e:
                                                status_placeholder.error(f"Error submitting feedback: {str(e)}")
                                        
                                        # Show final status
                                        if success_count == len(grades_to_submit) and (not new_feedback or feedback_result):
                                            status_placeholder.success(f"All grades and feedback successfully submitted for {student_options.get(student_selected)}")
                                            # Force a refresh after a brief delay
                                            time.sleep(1)
                                            st.rerun()
                                        else:
                                            status_placeholder.warning(f"Submitted {success_count} out of {len(grades_to_submit)} grades successfully. Failed criteria: {failed_criteria}")
                            else:
                                st.error("Could not find selected student in the roster")
                        else:
                            st.info("Please select a student to grade")
                    else:
                        st.warning("No students enrolled in this class")
                
                else:  # Edit Assignment section
                    # EDIT ASSIGNMENT SECTION
                    # Add a Delete Assignment button at the top
                    delete_col1, delete_col2 = st.columns([3, 1])
                    with delete_col2:
                        if st.button("Delete Assignment", type="primary", use_container_width=True):
                            st.warning(f"Are you sure you want to delete '{selected_assignment.get('name')}'? This cannot be undone.")
                            confirm_col1, confirm_col2 = st.columns(2)
                            with confirm_col1:
                                if st.button("Yes, Delete", key="confirm_delete", use_container_width=True):
                                    # Call the deleteAssignment function
                                    success = deleteAssignment(st.session_state.selected_class_id, selected_assignment_id)
                                    if success:
                                        st.success(f"Assignment '{selected_assignment.get('name')}' deleted successfully")
                                        st.rerun()
                            with confirm_col2:
                                if st.button("Cancel", key="cancel_delete", use_container_width=True):
                                    st.rerun()

                    # Store criteria in session state to allow adding/removing
                    if "criteria" not in st.session_state:
                        # Initialize from existing criteria
                        if assignment_details:
                            st.session_state.criteria = assignment_details.copy()
                        else:
                            st.session_state.criteria = []

                    # Add New Criterion button
                    if st.button("Add New Criterion", use_container_width=True):
                        new_criterion = {
                            "criterion_id": -1,  # Indicates a new criterion
                            "name": "New Criterion",
                            "value": 10.0,
                            "weight": 0.0
                        }
                        st.session_state.criteria.append(new_criterion)
                        st.rerun()

                    # Display criteria for deletion outside the form
                    st.markdown("### Manage Criteria")
                    if len(st.session_state.criteria) > 0:
                        criterion_options = [f"{i+1}. {c.get('name', 'Unnamed')}" for i, c in enumerate(st.session_state.criteria)]
                        selected_idx = st.selectbox(
                            "Select criterion to delete",
                            options=["None"] + criterion_options,
                            index=0
                        )
                        
                        if selected_idx != "None" and st.button("🗑️ Delete Selected Criterion", type="primary", use_container_width=True):
                            index_to_remove = int(selected_idx.split('.')[0]) - 1
                            criterion_to_remove = st.session_state.criteria[index_to_remove]
                            
                            # If this is an existing criterion (has a valid criterion_id), delete it from database
                            if criterion_to_remove.get('criterion_id', -1) > 0:
                                # Use deleteAssignmentCriterion function
                                success = deleteAssignmentCriterion(
                                    st.session_state.selected_class_id, 
                                    selected_assignment_id, 
                                    criterion_to_remove['criterion_id']
                                )
                                
                                if success:
                                    st.success(f"Criterion '{criterion_to_remove.get('name')}' deleted successfully")
                            
                            # Remove from session state
                            st.session_state.criteria.pop(index_to_remove)
                            st.rerun()

                    # Now create the form for editing assignment details
                    with st.form("edit_assignment_form"):
                        st.subheader("Edit Assignment Details")
                        
                        # Assignment basic info
                        assignment_name = st.text_input(
                            "Assignment Name", 
                            value=selected_assignment.get('name', '')
                        )
                        
                        due_date_str = selected_assignment.get('due_date', '')
                        try:
                            import datetime
                            # Parse the date string into a datetime object
                            # This assumes the date format is "YYYY-MM-DD"
                            due_date_parts = due_date_str.split('-')
                            if len(due_date_parts) == 3:
                                year, month, day = map(int, due_date_parts)
                                default_date = datetime.date(year, month, day)
                            else:
                                default_date = datetime.date.today()
                        except:
                            default_date = datetime.date.today()
                            
                        due_date = st.date_input(
                            "Due Date", 
                            value=default_date
                        )
                        
                        weight = st.number_input(
                            "Overall Weight (%)", 
                            min_value=0.0, 
                            max_value=100.0, 
                            value=float(selected_assignment.get('overall_weight', 0)) * 100,
                            step=5.0
                        ) / 100
                        
                        description = st.text_area(
                            "Assignment Description", 
                            value=selected_assignment.get('description', ''),
                            height=100
                        )
                        
                        # Criteria section
                        st.markdown("### Assignment Criteria")
                        
                        # Display criteria with edit fields
                        criteria_updates = []
                        total_weight = 0
                        
                        for i, criterion in enumerate(st.session_state.criteria):
                            with st.container(border=True):
                                st.markdown(f"#### Criterion {i+1}")
                                
                                cols = st.columns([3, 1, 1])
                                with cols[0]:
                                    criterion_name = st.text_input(
                                        "Name", 
                                        value=criterion.get('name', ''),
                                        key=f"criterion_name_{i}"
                                    )
                                
                                with cols[1]:
                                    criterion_value = st.number_input(
                                        "Points", 
                                        min_value=0.0,
                                        step=0.5,
                                        value=float(criterion.get('value', 10)),
                                        key=f"criterion_value_{i}"
                                    )
                                
                                with cols[2]:
                                    criterion_weight = st.number_input(
                                        "Weight (%)", 
                                        min_value=0.0,
                                        max_value=100.0,
                                        step=5.0,
                                        value=float(criterion.get('weight', 0)) * 100,
                                        key=f"criterion_weight_{i}"
                                    ) / 100
                                
                                total_weight += criterion_weight * 100
                                
                                # Store updated criterion
                                criterion_update = {
                                    "criterion_id": criterion.get('criterion_id'),
                                    "name": criterion_name,
                                    "value": criterion_value,
                                    "weight": criterion_weight
                                }
                                criteria_updates.append(criterion_update)
                        
                        # Weight validation
                        if abs(total_weight - 100) > 0.01:
                            st.warning(f"Total criteria weight is {total_weight:.1f}%. It should equal 100%.")
                        
                        # Form submission
                        submit = st.form_submit_button("Save Changes", type="primary")
                        
                        if submit:
                            if not assignment_name:
                                st.error("Assignment name is required")
                            elif abs(total_weight - 100) > 0.01 and len(st.session_state.criteria) > 0:
                                # Only error if there are criteria and weight doesn't sum to 100
                                st.error("Criteria weights must sum to 100%")
                            else:
                                success = True
                                
                                # Update assignment basic info
                                assignment_updated = updateAssignmnet(
                                    class_id=st.session_state.selected_class_id,
                                    assignment_id=selected_assignment_id,
                                    name=assignment_name,
                                    due=due_date.strftime("%Y-%m-%d"),
                                    weight=weight
                                )
                                
                                if not assignment_updated:
                                    st.error("Failed to update assignment details")
                                    success = False
                                
                                # Update or create criteria
                                for criterion in criteria_updates:
                                    criterion_id = criterion["criterion_id"]
                                    
                                    if criterion_id and criterion_id > 0:
                                        # Update existing criterion
                                        criterion_updated = updateAssignmentCriterion(
                                            class_id=st.session_state.selected_class_id,
                                            assignment_id=selected_assignment_id,
                                            criterion_id=criterion_id,
                                            name=criterion["name"],
                                            value=criterion["value"],
                                            weight=criterion["weight"]
                                        )
                                        
                                        if not criterion_updated:
                                            st.error(f"Failed to update criterion: {criterion['name']}")
                                            success = False
                                    else:
                                        # Create new criterion
                                        new_criterion_id = createAssignmentCriterion(
                                            class_id=st.session_state.selected_class_id,
                                            assignment_id=selected_assignment_id,
                                            name=criterion["name"],
                                            value=criterion["value"],
                                            weight=criterion["weight"]
                                        )
                                        
                                        if not new_criterion_id:
                                            st.error(f"Failed to create criterion: {criterion['name']}")
                                            success = False
                                
                                if success:
                                    st.success("Assignment updated successfully!")
                                    # Reset state to show updated information
                                    if "criteria" in st.session_state:
                                        del st.session_state.criteria
                                    st.rerun()
                    
                    # Comment Management Section
                    st.markdown("### Manage Comments")
                    
                    # Get existing comments
                    try:
                        comments = getComments(st.session_state.selected_class_id, selected_assignment_id)
                        
                        if comments and len(comments) > 0:
                            st.markdown("#### Existing Comments:")
                            for comment in comments:
                                author = f"{comment.get('author_first_name', 'Unknown')} {comment.get('author_last_name', 'User')}"
                                message = comment.get('message', 'No content')
                                created_on = comment.get('created_on', 'Unknown date')
                                
                                st.markdown(f"""
                                <div style='margin-bottom: 1rem; padding: 0.75rem; background-color: #f5f5f5; border-radius: 6px;'>
                                    <p style='font-size: 0.9rem; color: #666; margin-bottom: 0.25rem;'><b>{author}</b> • {created_on}</p>
                                    <p style='margin: 0;'>{message}</p>
                                </div>
                                """, unsafe_allow_html=True)
                        else:
                            st.info("No comments available for this assignment.")
                    except Exception as e:
                        st.error(f"Error fetching comments: {str(e)}")
                    
                    # Add new comment form
                    with st.form("add_comment_form"):
                        st.markdown("#### Add Comment")
                        
                        # Comment input
                        comment_text = st.text_area("Comment", height=150)
                        
                        # Submit button
                        submit_comment = st.form_submit_button("Add Comment", type="primary")
                        
                        if submit_comment:
                            if comment_text:
                                try:
                                    # Use the createComment function to add a new comment
                                    success = createComment(
                                        st.session_state.selected_class_id,
                                        selected_assignment_id,
                                        comment_text
                                    )
                                    
                                    if success:
                                        st.success("Comment added successfully!")
                                        st.rerun()
                                    else:
                                        st.error("Failed to add comment.")
                                except Exception as e:
                                    st.error(f"Error adding comment: {str(e)}")
                            else:
                                st.error("Comment text cannot be empty.")
            else:
                st.error("Could not find selected assignment")
    
    st.markdown("</div>", unsafe_allow_html=True)

elif st.session_state.selected_section == "roster":
    # Display the class roster at the bottom after it is clicked
    if canViewRoster or canManageAssignments:  # Show only if user has the correct permission
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
            for student in class_roster:
                with st.expander(f"{student['first_name']} {student['last_name']}"):
                    for k in permissionMap.keys():
                        st.checkbox(k, key=f"{student['user_id']}.{k}")
        
        st.markdown("</div>", unsafe_allow_html=True)
    else:
        st.write("You do not have permission to view the class roster.")
else:
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