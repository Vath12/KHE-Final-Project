import streamlit as st
import time
from util.verification import isValidSession
from util.request import (
    getClassInfo, 
    getAnnouncements, 
    createAnnouncement,
    updateAnnouncement,
    deleteAnnouncement,
    getClassPermissions
)

isValidSession()

# Get class ID from session state or set a default
if "selected_class_id" not in st.session_state:
    st.switch_page("home.py")

# Get class information
class_info = getClassInfo(st.session_state.selected_class_id)

# Get class permissions to check if user is an instructor
permissions = getClassPermissions(st.session_state.selected_class_id)
is_instructor = permissions.get("IS_INSTRUCTOR", False)

# Set up page
st.set_page_config(layout="wide", page_title=f"Course: {class_info['name']} - Announcements")

# Create a row for the header and home button
col_left, col_right = st.columns([6, 1])

with col_left:
    st.markdown(f"<p style='color: #7F27FF; font-size: 2.5em;'>{class_info['name']}: Announcements</p>", unsafe_allow_html=True)

with col_right:
    if st.button("Back to Course", use_container_width=True):
        st.switch_page("pages/classes.py")

st.markdown("---")

# Initialize session state for editing announcements
if 'editing_announcement' not in st.session_state:
    st.session_state.editing_announcement = None

# Get all announcements for this class
announcements = getAnnouncements(st.session_state.selected_class_id) or []

# Add a creation form if the user is an instructor
if is_instructor:
    st.markdown(
        """
        <div style='padding: 1rem; background-color: #F0F8FF; border-left: 8px solid #4682B4; border-radius: 8px; margin-bottom: 1.5rem;'>
            <h3>Manage Announcements</h3>
        """,
        unsafe_allow_html=True
    )
    
    with st.expander("Create New Announcement", expanded=False):
        with st.form("create_announcement_form"):
            new_title = st.text_input("Announcement Title*", placeholder="Enter a title for your announcement")
            new_message = st.text_area("Announcement Message*", height=150, placeholder="Enter the announcement message")
            
            col1, col2 = st.columns(2)
            with col1:
                submit_button = st.form_submit_button("Post Announcement", use_container_width=True)
            with col2:
                cancel_button = st.form_submit_button("Cancel", use_container_width=True)
            
            if submit_button:
                if not new_title or not new_message:
                    st.warning("Both title and message are required")
                else:
                    response = createAnnouncement(
                        st.session_state.selected_class_id,
                        new_title,
                        new_message
                    )
                    
                    if response:
                        st.success("Announcement posted successfully!")
                        time.sleep(1)
                        st.rerun()

# Display all announcements
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
    for i, announcement in enumerate(announcements):
        title = announcement.get('title', 'Untitled Announcement')
        message = announcement.get('message', 'No message content')
        date = announcement.get('date_posted', 'Unknown date')
        announcement_id = announcement.get('id')
        
        if not announcement_id:
            with st.container(border=True):
                st.markdown(f"<h4>{title}</h4>", unsafe_allow_html=True)
                st.markdown(f"<p style='font-size: 0.9rem; color: #666;'>Posted: {date}</p>", unsafe_allow_html=True)
                st.markdown(f"<p>{message}</p>", unsafe_allow_html=True)
            continue

        if st.session_state.editing_announcement == announcement_id:
            with st.form(key=f"edit_form_{announcement_id}"):
                st.subheader("Edit Announcement")
                
                edited_title = st.text_input("Title*", value=title)
                edited_message = st.text_area("Message*", value=message, height=150)
                
                col1, col2 = st.columns(2)
                with col1:
                    save_button = st.form_submit_button("Save Changes", use_container_width=True)
                with col2:
                    cancel_edit_button = st.form_submit_button("Cancel", use_container_width=True)
                
                if save_button:
                    if not edited_title or not edited_message:
                        st.warning("Both title and message are required")
                    else:
                        response = updateAnnouncement(
                            st.session_state.selected_class_id,
                            announcement_id,
                            edited_title,
                            edited_message
                        )
                        
                        if response and response.get('status') == 'success':
                            st.success("Announcement updated successfully!")
                            st.session_state.editing_announcement = None
                            time.sleep(1)
                            st.rerun()
                
                if cancel_edit_button:
                    st.session_state.editing_announcement = None
                    st.rerun()
        else:
            with st.container(border=True):
                if is_instructor:
                    col1, col2, col3 = st.columns([8, 1, 1])
                    
                    with col1:
                        st.markdown(f"<h4>{title}</h4>", unsafe_allow_html=True)
                    
                    with col2:
                        if st.button("✏️", key=f"edit_{i}", help="Edit this announcement"):
                            st.session_state.editing_announcement = announcement_id
                            st.rerun()
                    
                    with col3:
                        if st.button("🗑️", key=f"delete_{i}", help="Delete this announcement"):
                            st.warning("Are you sure you want to delete this announcement?")
                            
                            confirm_col1, confirm_col2 = st.columns(2)
                            with confirm_col1:
                                if st.button("Yes, Delete", key=f"confirm_delete_{i}", use_container_width=True):
                                    response = deleteAnnouncement(
                                        st.session_state.selected_class_id,
                                        announcement_id
                                    )
                                    
                                    if response and response.get('status') == 'success':
                                        st.success("Announcement deleted successfully!")
                                        time.sleep(1)
                                        st.rerun()
                                        
                            with confirm_col2:
                                if st.button("Cancel", key=f"cancel_delete_{i}", use_container_width=True):
                                    st.rerun()
                else:
                    st.markdown(f"<h4>{title}</h4>", unsafe_allow_html=True)
                
                st.markdown(f"<p style='font-size: 0.9rem; color: #666;'>Posted: {date}</p>", unsafe_allow_html=True)
                st.markdown(f"<p>{message}</p>", unsafe_allow_html=True)

st.markdown("</div>", unsafe_allow_html=True)