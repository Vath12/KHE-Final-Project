import streamlit as st
import time
import json
from util.verification import isValidSession
from util.request import getClassInfo, getAnnouncements, createAnnouncement, getClassPermissions, API, safePut, safeDelete, safePost

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
    
# Debug info (will help troubleshoot)
if 'debug_mode' not in st.session_state:
    st.session_state.debug_mode = False

# Get all announcements for this class
announcements = getAnnouncements(st.session_state.selected_class_id)

# Debug toggle in sidebar
if is_instructor:
    st.sidebar.markdown("### Admin Tools")
    st.session_state.debug_mode = st.sidebar.checkbox("Show Debug Info", value=st.session_state.debug_mode)

# Display debug info if enabled
if is_instructor and st.session_state.debug_mode:
    st.sidebar.markdown("### Announcements Data")
    st.sidebar.json(announcements)

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
            new_title = st.text_input("Announcement Title", placeholder="Enter a title for your announcement")
            new_message = st.text_area("Announcement Message", height=150, placeholder="Enter the announcement message")
            
            col1, col2 = st.columns(2)
            with col1:
                submit_button = st.form_submit_button("Post Announcement", use_container_width=True)
            with col2:
                cancel_button = st.form_submit_button("Cancel", use_container_width=True)
            
            if submit_button:
                if not new_title or not new_message:
                    st.error("Both title and message are required.")
                else:
                    # Use direct API call for create with better error handling
                    try:
                        data = {
                            'title': new_title,
                            'message': new_message
                        }
                        # Use safePost for creating new announcements
                        result = safePost(f"{API}/announcements/{st.session_state.get('session_key')}/{st.session_state.selected_class_id}", data)
                        
                        if result and result.status_code == 200:
                            st.success("Announcement posted successfully!")
                            # Force refresh to show the new announcement
                            time.sleep(1)
                            st.rerun()
                        else:
                            st.error(f"Failed to post announcement. Status code: {result.status_code if result else 'Unknown'}")
                    except Exception as e:
                        st.error(f"Error posting announcement: {str(e)}")
    
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
        # Extract announcement details with fallbacks
        # The API seems to return different field names than expected
        title = announcement.get('title', 'Untitled Announcement')
        message = announcement.get('message', 'No message content')
        date = announcement.get('date_posted', 'Unknown date')
        
        # Get announcement ID - inspect all possible fields
        announcement_id = None
        # First try the expected field name
        if 'announcement_id' in announcement:
            announcement_id = announcement['announcement_id']
        # If that's not there, look for other possible field names
        elif 'id' in announcement:
            announcement_id = announcement['id']
        elif '_id' in announcement:
            announcement_id = announcement['_id']
            
        # If still no ID, use the index as a fallback
        if announcement_id is None:
            announcement_id = f"announcement_{i}"
            
        # For debug display
        if is_instructor and st.session_state.debug_mode:
            st.sidebar.markdown(f"### Announcement {i+1}")
            st.sidebar.write(f"ID: {announcement_id}")
            st.sidebar.write(f"Title: {title}")
        
        # Check if this announcement is being edited
        if st.session_state.editing_announcement == announcement_id:
            # Edit form for this announcement
            with st.form(key=f"edit_announcement_{i}"):
                st.subheader("Edit Announcement")
                
                edited_title = st.text_input("Title", value=title)
                edited_message = st.text_area("Message", value=message, height=150)
                
                col1, col2 = st.columns(2)
                with col1:
                    save_button = st.form_submit_button("Save Changes", use_container_width=True)
                with col2:
                    cancel_edit_button = st.form_submit_button("Cancel", use_container_width=True)
                
                if save_button:
                    if not edited_title or not edited_message:
                        st.error("Both title and message are required.")
                    else:
                        # Use direct API call instead of updateAnnouncement function
                        try:
                            data = {
                                'announcement_id': announcement_id,
                                'title': edited_title,
                                'message': edited_message
                            }
                            
                            # If we're using a fallback ID, try to find the real one in the original data
                            if isinstance(announcement_id, str) and announcement_id.startswith("announcement_"):
                                # Show an error as we need the real ID
                                st.error("Cannot update: System could not determine the announcement ID. Please try refreshing the page.")
                                if st.session_state.debug_mode:
                                    st.sidebar.error(f"Edit error: Using fallback ID {announcement_id}")
                            else:
                                # Use the real ID for the API call
                                result = safePut(f"{API}/announcements/{st.session_state.get('session_key')}/{st.session_state.selected_class_id}", data)
                                
                                if st.session_state.debug_mode:
                                    st.sidebar.write("API Call Response:")
                                    st.sidebar.write(f"Status: {result.status_code if result else 'None'}")
                                    try:
                                        st.sidebar.json(result.json() if result else {})
                                    except:
                                        st.sidebar.write("No JSON response")
                                
                                if result and result.status_code == 200:
                                    st.success("Announcement updated successfully!")
                                    # Exit edit mode
                                    st.session_state.editing_announcement = None
                                    # Force refresh to show the updated announcement
                                    time.sleep(1)
                                    st.rerun()
                                else:
                                    st.error(f"Failed to update announcement. Status code: {result.status_code if result else 'Unknown'}")
                        except Exception as e:
                            st.error(f"Error updating announcement: {str(e)}")
                
                if cancel_edit_button:
                    # Exit edit mode without saving
                    st.session_state.editing_announcement = None
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
                        if st.button("✏️", key=f"edit_{i}", help="Edit this announcement"):
                            st.session_state.editing_announcement = announcement_id
                            st.rerun()
                    
                    with col3:
                        # Delete button
                        if st.button("🗑️", key=f"delete_{i}", help="Delete this announcement"):
                            # Show confirmation dialog
                            st.warning("Are you sure you want to delete this announcement?")
                            
                            confirm_col1, confirm_col2 = st.columns(2)
                            with confirm_col1:
                                if st.button("Yes, Delete", key=f"confirm_delete_{i}", use_container_width=True):
                                    # Check if we have a valid ID
                                    if isinstance(announcement_id, str) and announcement_id.startswith("announcement_"):
                                        st.error("Cannot delete: System could not determine the announcement ID. Please try refreshing the page.")
                                        if st.session_state.debug_mode:
                                            st.sidebar.error(f"Delete error: Using fallback ID {announcement_id}")
                                    else:
                                        # We have a valid ID, proceed with delete
                                        try:
                                            data = {
                                                'announcement_id': announcement_id,
                                            }
                                            result = safeDelete(f"{API}/announcements/{st.session_state.get('session_key')}/{st.session_state.selected_class_id}", data)
                                            
                                            if st.session_state.debug_mode:
                                                st.sidebar.write("Delete API Call:")
                                                st.sidebar.write(f"Status: {result.status_code if result else 'None'}")
                                                try:
                                                    st.sidebar.json(result.json() if result else {})
                                                except:
                                                    st.sidebar.write("No JSON response")
                                            
                                            if result and result.status_code == 200:
                                                st.success("Announcement deleted successfully!")
                                                # Force refresh to remove the deleted announcement
                                                time.sleep(1)
                                                st.rerun()
                                            else:
                                                st.error(f"Failed to delete announcement. Status code: {result.status_code if result else 'Unknown'}")
                                        except Exception as e:
                                            st.error(f"Error deleting announcement: {str(e)}")
                                        
                            with confirm_col2:
                                if st.button("Cancel", key=f"cancel_delete_{i}", use_container_width=True):
                                    st.rerun()
                else:
                    # Regular title display for non-instructors
                    st.markdown(f"<h4>{title}</h4>", unsafe_allow_html=True)
                
                # Date and message content (shown for all users)
                st.markdown(f"<p style='font-size: 0.9rem; color: #666;'>Posted: {date}</p>", unsafe_allow_html=True)
                st.markdown(f"<p>{message}</p>", unsafe_allow_html=True)

st.markdown("</div>", unsafe_allow_html=True)