import streamlit as st
from util.verification import isValidSession
from util.request import getClassInfo, getAnnouncements

isValidSession()

# Get class ID from session state or set a default
if "selected_class_id" not in st.session_state:
    st.switch_page("home.py")

# Get class information
class_info = getClassInfo(st.session_state.selected_class_id)

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