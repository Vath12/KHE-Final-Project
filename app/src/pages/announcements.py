import streamlit as st
import time
from util.verification import isValidSession
from util.request import getClassInfo, getAnnouncements, getClassPermissions, deleteAnnouncement, API, safePost, safePut

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
if 'editing_announcement_index' not in st.session_state:
    st.session_state.editing_announcement_index = None

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
    
    # Create a new announcement section
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
                    # Use direct API call for creating announcement
                    data = {
                        'title': new_title,
                        'message': new_message
                    }
                    result = safePost(f"{API}/announcements/{st.session_state.get('session_key')}/{st.session_state.selected_class_id}", data)
                    
                    if result and result.status_code == 200:
                        st.success("Announcement posted successfully!")
                        time.sleep(1)
                        st.rerun()
                    else:
                        st.error("Failed to post announcement. Please try again.")
    
    st.markdown("</div>", unsafe_allow_html=True)

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
    # Loop through and display each announcement
    for i, announcement in enumerate(announcements):
        title = announcement.get('title', 'Untitled Announcement')
        message = announcement.get('message', 'No message content')
        date = announcement.get('date_posted', 'Unknown date')
        author_id = announcement.get('author_id')
        
        # Fix for the announcement ID field issue
        # Looking at the backend API in announcement.py, the field is expected to be 'announcement_id'
        announcement_id = None
        
        # Try all possible keys for the announcement ID
        if 'announcement_id' in announcement:
            announcement_id = announcement['announcement_id']
        else:
            # If we can't find the ID, we'll now look in other fields
            # Check if any field looks like an ID
            for key, value in announcement.items():
                if (key.endswith('id') or key == '_id' or key == 'id') and isinstance(value, (int, str)):
                    announcement_id = value
                    break
        
        # Check if this announcement is being edited
        if st.session_state.editing_announcement_index == i:
            # Edit form for this announcement
            with st.form(key=f"edit_announcement_{i}"):
                st.subheader("Edit Announcement")
                
                edited_title = st.text_input("Title*", value=title)
                edited_message = st.text_area("Message*", value=message, height=150)
                
                # Store the announcement ID in a hidden field
                st.session_state[f"edit_announcement_id_{i}"] = announcement_id
                
                col1, col2 = st.columns(2)
                with col1:
                    save_button = st.form_submit_button("Save Changes", use_container_width=True)
                with col2:
                    cancel_edit_button = st.form_submit_button("Cancel", use_container_width=True)
                
                if save_button:
                    if not edited_title or not edited_message:
                        st.warning("Both title and message are required")
                    else:
                        # Direct API call to update announcement
                        data = {
                            'announcement_id': announcement_id,
                            'title': edited_title,
                            'message': edited_message
                        }
                        
                        # Directly call the API route without relying on helper functions
                        url = f"{API}/announcements/{st.session_state.get('session_key')}/{st.session_state.selected_class_id}"
                        result = safePut(url, data)
                        
                        if result and result.status_code == 200:
                            st.success("Announcement updated successfully!")
                            # Exit edit mode
                            st.session_state.editing_announcement_index = None
                            # Force refresh to show the updated announcement
                            time.sleep(1)
                            st.rerun()
                        else:
                            st.error(f"Failed to update announcement. Status code: {result.status_code if result else 'Unknown'}")
                
                if cancel_edit_button:
                    # Exit edit mode without saving
                    st.session_state.editing_announcement_index = None
                    st.rerun()
        else:
            # Normal display with edit/delete options for instructors
            with st.container(border=True):
                if is_instructor:
                    # Add edit and delete buttons for instructors
                    col1, col2, col3 = st.columns([8, 1, 1])
                    
                    with col1:
                        st.markdown(f"<h4>{title}</h4>", unsafe_allow_html=True)
                    
                    with col2:
                        # Edit button
                        if st.button("✏️", key=f"edit_btn_{i}", help="Edit this announcement"):
                            st.session_state.editing_announcement_index = i
                            st.rerun()
                    
                    with col3:
                        # Delete button
                        if st.button("🗑️", key=f"delete_btn_{i}", help="Delete this announcement"):
                            # Store the announcement being deleted in session state
                            st.session_state[f"deleting_announcement_{i}"] = True
                            st.rerun()
                            
                    # Handle deletion confirmation
                    if st.session_state.get(f"deleting_announcement_{i}", False):
                        st.warning("Are you sure you want to delete this announcement?")
                        
                        confirm_col1, confirm_col2 = st.columns(2)
                        with confirm_col1:
                            if st.button("Yes, Delete", key=f"confirm_delete_{i}", use_container_width=True):
                                # Use the backend API function for deletion
                                result = deleteAnnouncement(
                                    st.session_state.selected_class_id,
                                    announcement_id
                                )
                                
                                # Check if deletion was successful
                                if result:
                                    st.success("Announcement deleted successfully!")
                                    # Force refresh to remove the deleted announcement
                                    time.sleep(1)
                                    # Clear the deletion state
                                    if f"deleting_announcement_{i}" in st.session_state:
                                        del st.session_state[f"deleting_announcement_{i}"]
                                    st.rerun()
                                else:
                                    st.error("Failed to delete announcement.")
                                    
                        with confirm_col2:
                            if st.button("Cancel", key=f"cancel_delete_{i}", use_container_width=True):
                                # Clear the deletion state
                                if f"deleting_announcement_{i}" in st.session_state:
                                    del st.session_state[f"deleting_announcement_{i}"]
                                st.rerun()
                else:
                    # Regular title display for non-instructors
                    st.markdown(f"<h4>{title}</h4>", unsafe_allow_html=True)
                
                # Date and message content (shown for all users)
                st.markdown(f"<p style='font-size: 0.9rem; color: #666;'>Posted: {date}</p>", unsafe_allow_html=True)
                st.markdown(f"<p>{message}</p>", unsafe_allow_html=True)

st.markdown("</div>", unsafe_allow_html=True)