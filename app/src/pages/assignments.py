import streamlit as st
import requests
from util.verification import isValidSession
from util.request import getClassInfo, getAssignments, getAssignmentDetails, getComments

isValidSession()

# Get class ID from session state or set a default
if "selected_class_id" not in st.session_state:
    st.switch_page("home.py")

# Get class information
class_info = getClassInfo(st.session_state.selected_class_id)

# Set up page
st.set_page_config(layout="wide", page_title=f"Course: {class_info['name']} - Assignments")

# Create a row for the header and home button
col_left, col_right = st.columns([6, 1])

with col_left:
    st.markdown(f"<p style='color: #7F27FF; font-size: 2.5em;'>{class_info['name']}: Assignments</p>", unsafe_allow_html=True)

with col_right:
    if st.button("Back to Course", use_container_width=True):
        st.switch_page("pages/classes.py")

st.markdown("---")

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
            
            # Get and display comments for the current user for this assignment
            try:
                # Use current user's ID (-1)
                comments = getComments(st.session_state.selected_class_id, assignment_id, -1)
                
                if comments and len(comments) > 0:
                    st.markdown("#### Instructor Feedback:")
                    for comment in comments:
                        author = f"{comment.get('author_first_name', 'Unknown')} {comment.get('author_last_name', 'User')}"
                        message = comment.get('message', 'No content')
                        created_on = comment.get('created_on', 'Unknown date')
                        
                        st.markdown(f"""
                        <div style='margin-bottom: 1rem; padding: 0.75rem; background-color: #F0FFF0; border-left: 3px solid #00CC66; border-radius: 6px;'>
                            <p style='font-size: 0.9rem; color: #666; margin-bottom: 0.25rem;'><b>{author}</b> • {created_on}</p>
                            <p style='margin: 0;'>{message}</p>
                        </div>
                        """, unsafe_allow_html=True)
            except:
                # No need to display an error to the user
                pass
    
    st.markdown("</ul>", unsafe_allow_html=True)

st.markdown("</div>", unsafe_allow_html=True)