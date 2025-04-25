import streamlit as st
import requests
from util.verification import isValidSession
from util.request import getClassInfo, getAssignments, getGrade, getComments, updateComment, deleteComment, API, safeGet

# Ensure the session is valid
isValidSession()

# Get class ID from session state or redirect to home if not present
if "selected_class_id" not in st.session_state:
    st.switch_page("home.py")

# Get class information
class_info = getClassInfo(st.session_state.selected_class_id)

# Set up page
st.set_page_config(layout="wide", page_title=f"Course: {class_info['name']} - Grades")

# Create a row for the header and home button
col_left, col_right = st.columns([6, 1])

with col_left:
    st.markdown(f"<p style='color: #7F27FF; font-size: 2.5em;'>{class_info['name']}: Grades</p>", unsafe_allow_html=True)

with col_right:
    if st.button("Back to Course", use_container_width=True):
        st.switch_page("pages/classes.py")

st.markdown("---")

# Fetch assignments for the selected class
assignments = getAssignments(st.session_state.selected_class_id)

# Display Grades section
st.markdown(
    """
    <div style='padding: 1rem; background-color: #E6FFE6; border-left: 8px solid #00CC66; border-radius: 8px;'>
        <h3>Grades</h3>
    """,
    unsafe_allow_html=True
)

# If no assignments, notify the user
if not assignments:
    st.markdown("<p>No graded assignments available for this course.</p>", unsafe_allow_html=True)
else:
    for assignment in assignments:
        assignment_id = assignment.get('assignment_id')
        assignment_name = assignment.get('name', 'Unnamed Assignment')

        # Force reload grades on each render to ensure up-to-date data
        st.session_state.force_reload_grades = True

        # Get grade data for this assignment using the student_id parameter

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

            # Add a horizontal divider before feedback section if grades exist
            if grades:
                st.markdown("---")

            # Try multiple approaches to get comments since we don't know the exact endpoint structure
            found_comments = False

            # Approach 1: Standard approach with student_id = -1
            try:
                comments = getComments(
                    st.session_state.selected_class_id,
                    assignment_id,
                    -1  # -1 indicates current user
                )

                if comments and len(comments) > 0:
                    found_comments = True
                    st.markdown("#### Instructor Feedback:")
                    for comment in comments:
                        author = f"{comment.get('author_first_name', 'Unknown')} {comment.get('author_last_name', 'User')}"
                        message = comment.get('message', 'No content')
                        created_on = comment.get('created_on', 'Unknown date')

                        # Display the comment with styling
                        st.markdown(f"""
                        <div style='margin-top: 0.5rem; padding: 0.75rem; background-color: #F0FFF0; border-left: 3px solid #00CC66; border-radius: 6px;'>
                            <p style='font-size: 0.9rem; color: #666; margin-bottom: 0.25rem;'><b>{author}</b> • {created_on}</p>
                            <p style='margin: 0;'>{message}</p>
                        </div>
                        """, unsafe_allow_html=True)
            except Exception as e:
                # Silent failure - try the next approach
                pass

            # Approach 2: Try with current user's ID directly from session state
            if not found_comments:
                try:
                    from util.request import getUserInfo

                    # Get user's actual ID from session state
                    user_info = getUserInfo()
                    if user_info and 'user_id' in user_info:
                        actual_user_id = user_info['user_id']

                        # Try with actual user ID
                        comments = getComments(
                            st.session_state.selected_class_id,
                            assignment_id,
                            actual_user_id
                        )

                        if comments and len(comments) > 0:
                            found_comments = True
                            st.markdown("#### Instructor Feedback:")
                            for comment in comments:
                                author = f"{comment.get('author_first_name', 'Unknown')} {comment.get('author_last_name', 'User')}"
                                message = comment.get('message', 'No content')
                                created_on = comment.get('created_on', 'Unknown date')

                                # Display the comment with styling
                                st.markdown(f"""
                                <div style='margin-top: 0.5rem; padding: 0.75rem; background-color: #F0FFF0; border-left: 3px solid #00CC66; border-radius: 6px;'>
                                    <p style='font-size: 0.9rem; color: #666; margin-bottom: 0.25rem;'><b>{author}</b> • {created_on}</p>
                                    <p style='margin: 0;'>{message}</p>
                                </div>
                                """, unsafe_allow_html=True)
                except Exception as e:
                    # Silent failure - try the next approach
                    pass

            # Approach 3: Direct API call with different URL structure
            if not found_comments:
                comments = getComments(
                    st.session_state.selected_class_id,
                    assignment_id, 
                    -1)
                
                if comments and len(comments) > 0:
                    found_comments = True
                    st.markdown("#### Instructor Feedback:")
                    for comment in comments:
                        if isinstance(comment, dict):
                            author = f"{comment.get('author_first_name', 'Unknown')} {comment.get('author_last_name', 'User')}"
                            message = comment.get('message', 'No content')
                            created_on = comment.get('created_on', 'Unknown date')

                            # Display the comment with styling
                            st.markdown(f"""
                            <div style='margin-top: 0.5rem; padding: 0.75rem; background-color: #F0FFF0; border-left: 3px solid #00CC66; border-radius: 6px;'>
                                <p style='font-size: 0.9rem; color: #666; margin-bottom: 0.25rem;'><b>{author}</b> • {created_on}</p>
                                <p style='margin: 0;'>{message}</p>
                            </div>
                            """, unsafe_allow_html=True)
    

            # Display message if no comments found but grades exist
            if not found_comments and grades:
                st.info("No feedback available for this assignment.")

# Close Grades section
st.markdown("</div>", unsafe_allow_html=True)
