import streamlit as st
import requests
import time
from util.verification import isValidSession
from util.request import *

isValidSession()

# Get class ID from session state or set a default
if "selected_class_id" not in st.session_state:
    st.switch_page("home.py")

# Get class information
class_info = getClassInfo(st.session_state.selected_class_id)

# Get class permissions for the current user
permissions = getClassPermissions(st.session_state.selected_class_id)

canGradeAssignments = permissions.get("CAN_GRADE_ASSIGNMENT", False)

# Set up page
st.set_page_config(layout="wide", page_title=f"Course: {class_info['name']} - Manage Assignments")

# Create a row for the header and home button
col_left, col_right = st.columns([6, 1])

with col_left:
    st.markdown(f"<p style='color: #7F27FF; font-size: 2.5em;'>{class_info['name']}: Manage Assignments</p>", unsafe_allow_html=True)

with col_right:
    if st.button("Back to Course", use_container_width=True):
        st.switch_page("pages/classes.py")

st.markdown("---")

if not canGradeAssignments:
    st.error("You do not have permission to manage assignments.")
    st.stop()

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
                            
                            # Get existing comments/feedback for this specific student
                            try:
                                current_comments = getComments(
                                    st.session_state.selected_class_id,
                                    selected_assignment_id,
                                    selected_student_id
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
                                
                                # Show existing comments/feedback for this student
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
                                    feedback_result = True
                                    if new_feedback:
                                        status_placeholder.info("Submitting feedback...")
                                        try:
                                            # Use the createComment function to submit feedback specifically for this student
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
                                            feedback_result = False
                                    
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
                                # Call the deleteAssignment function with proper error handling
                                try:
                                    # Make a direct API call instead of using the function
                                    url = f"{API}/modifyAssignment/{st.session_state.get('session_key')}/{st.session_state.selected_class_id}/{selected_assignment_id}"
                                    response = safeDelete(url, {})
                                    
                                    if response and response.status_code == 200:
                                        st.success(f"Assignment '{selected_assignment.get('name')}' deleted successfully")
                                        # Redirect back to the main course page after deletion
                                        st.switch_page("pages/classes.py")
                                    else:
                                        st.error(f"Failed to delete assignment. Status code: {response.status_code if response else 'No response'}")
                                except Exception as e:
                                    st.error(f"Error deleting assignment: {str(e)}")
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

                # Split screen layout
                left_col, right_col = st.columns(2)

                # Left column: Assignment details
                with left_col:
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

                    # Assignment details form
                    with st.form("edit_assignment_form"):
                        st.subheader("Assignment Details")
                        
                        # Assignment basic info
                        assignment_name = st.text_input(
                            "Assignment Name", 
                            value=selected_assignment.get('name', '')
                        )
                        
                        due_date_str = selected_assignment.get('due_date', '')
                        try:
                            import datetime
                            # Parse the date string into a datetime object
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
                        
                        # Submit button
                        submit = st.form_submit_button("Save Changes", type="primary", use_container_width=True)
                        
                        criteria_updates = []
                        
                        # Prepare criteria updates from session state
                        for i, criterion in enumerate(st.session_state.criteria):
                            criterion_update = {
                                "criterion_id": criterion.get('criterion_id'),
                                "name": criterion.get('name', ''),
                                "value": criterion.get('value', 10.0),
                                "weight": criterion.get('weight', 0.0)
                            }
                            criteria_updates.append(criterion_update)
                        
                        # Calculate total weight - FIXED
                        total_weight = 0
                        for c in criteria_updates:
                            try:
                                # Make sure weight is a float
                                weight = float(c["weight"])
                                total_weight += weight * 100
                            except (ValueError, TypeError):
                                # Skip any invalid weights
                                pass
                        
                        # Form submission handler
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
                                        # Update existing criterion - direct API call to fix endpoint issue
                                        data = {
                                            'name': criterion["name"],
                                            'value': criterion["value"],
                                            'weight': criterion["weight"]
                                        }
                                        
                                        # Fix for the incorrect URL in updateAssignmentCriterion
                                        result = safePut(
                                            f"{API}/assignmentCriteria/{st.session_state.get('session_key')}/{st.session_state.selected_class_id}/{selected_assignment_id}/{criterion_id}",
                                            data
                                        )
                                        
                                        if result.status_code != 200:
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
                
                # Right column: Criteria management
                with right_col:
                    st.subheader("Assignment Criteria")
                    
                    # Weight validation notice
                    total_weight = 0
                    for c in st.session_state.criteria:
                        try:
                            weight = float(c.get('weight', 0))
                            total_weight += weight * 100
                        except (ValueError, TypeError):
                            pass
                            
                    if abs(total_weight - 100) > 0.01 and len(st.session_state.criteria) > 0:
                        st.warning(f"Total criteria weight is {total_weight:.1f}%. It should equal 100%.")
                    
                    # Display criteria with edit fields
                    for i, criterion in enumerate(st.session_state.criteria):
                        with st.container(border=True):
                            # Inline layout with delete button
                            header_col, delete_col = st.columns([9, 1])
                            with delete_col:
                                if st.button("🗑️", key=f"remove_criterion_{i}", help="Delete this criterion"):
                                    # If this is an existing criterion, delete it from database
                                    criterion_id = criterion.get('criterion_id')
                                    if criterion_id and criterion_id > 0:
                                        success = deleteAssignmentCriterion(
                                            st.session_state.selected_class_id, 
                                            selected_assignment_id, 
                                            criterion_id
                                        )
                                        
                                        if success:
                                            st.success(f"Criterion deleted successfully")
                                    
                                    # Remove from session state
                                    st.session_state.criteria.pop(i)
                                    st.rerun()
                            
                            # Streamlined input fields without redundant labels
                            criterion_name = st.text_input(
                                "Criterion name",
                                value=criterion.get('name', ''),
                                key=f"criterion_name_{i}",
                                placeholder="Enter criterion name"
                            )
                            
                            # Store updates directly in session state for immediate effect
                            st.session_state.criteria[i]['name'] = criterion_name
                            
                            # Value and weight in same row
                            value_col, weight_col = st.columns(2)
                            with value_col:
                                criterion_value = st.number_input(
                                    "Points", 
                                    min_value=0.0,
                                    step=0.5,
                                    value=float(criterion.get('value', 10)),
                                    key=f"criterion_value_{i}"
                                )
                                st.session_state.criteria[i]['value'] = criterion_value
                            
                            with weight_col:
                                criterion_weight = st.number_input(
                                    "Weight (%)", 
                                    min_value=0.0,
                                    max_value=100.0,
                                    step=5.0,
                                    value=float(criterion.get('weight', 0)) * 100,
                                    key=f"criterion_weight_{i}"
                                ) / 100
                                st.session_state.criteria[i]['weight'] = criterion_weight
        else:
            st.error("Could not find selected assignment")

st.markdown("</div>", unsafe_allow_html=True)