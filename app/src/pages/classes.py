import streamlit as st
from util.verification import isValidSession
from util.request import getClassInfo, getAssignments, getAnnouncements, getGrade, getAssignmentDetails, getClassPermissions, getClassRoster

isValidSession()

# Get class ID from session state or set a default
if "selected_class_id" not in st.session_state:
    st.session_state.selected_class_id = 1  # Default class ID

# Get class information
class_info = getClassInfo(st.session_state.selected_class_id)

# Get class permissions for the current user
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
col1, col2, col3, col4, col5 = st.columns(5)
with col1:
    if st.button("Assignments"):
        st.session_state.selected_section = "assignments"
with col2:
    if st.button("Announcements"):
        st.session_state.selected_section = "announcements"
with col3:
    if st.button("Grades"):
        st.session_state.selected_section = "grades"
with col4:
    # Check permission to view class roster
    if permissions.get("CAN_VIEW_ROSTER", False):
        if st.button("View Class Roster"):
            st.session_state.selected_section = "roster"
    else:
        # Display the button, but on click, show a message that they can't view the roster
        if st.button("View Class Roster"):
            st.session_state.selected_section = "no_roster_permission"
with col5:
    # Adding the "Join Code" button
    if st.button("Join Code"):
        # Placeholder for join code functionality
        st.write("Join code functionality is not yet implemented.")
    
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
                            st.markdown(f"**Grade**: {earned_points}/{total_points} = {percentage:.2f}%")
                        else:
                            st.markdown("**Grade**: Not graded")
            except Exception as e:
                st.markdown(f"Error loading grade details: {str(e)}")
    
    st.markdown("</div>", unsafe_allow_html=True)

elif st.session_state.selected_section == "roster":
    # Display the class roster at the bottom after it is clicked
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
        for student in class_roster:
            st.write(f"{student['first_name']} {student['last_name']}")
    
    st.markdown("</div>", unsafe_allow_html=True)

elif st.session_state.selected_section == "no_roster_permission":
    st.write("You do not have permission to view the class roster.")
