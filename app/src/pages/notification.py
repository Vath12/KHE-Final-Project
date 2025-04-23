import streamlit as st
from util.verification import isValidSession
from util.request import *
from datetime import datetime, timedelta
from email.utils import parsedate_to_datetime

isValidSession()

def relative_time(dt_str):
    """Parse RFC 1123 format dates (like 'Mon, 20 Jan 2025 13:24:05 GMT')"""
    try:
        dt = parsedate_to_datetime(dt_str)
    except (TypeError, ValueError):
        return "recently"
    
    now = datetime.now(dt.tzinfo)
    delta = now - dt
    
    if delta < timedelta(seconds=0):
        return "soon"
    
    seconds = delta.total_seconds()
    minutes = seconds // 60
    hours = minutes // 60
    days = hours // 24
    weeks = days // 7
    
    time_parts = []
    if weeks > 0:
        time_parts.append(f"{int(weeks)}w")
        days %= 7
    if days > 0:
        time_parts.append(f"{int(days)}d")
    if hours % 24 > 0 and weeks == 0:
        time_parts.append(f"{int(hours % 24)}h")
    if minutes % 60 > 0 and days == 0:
        time_parts.append(f"{int(minutes % 60)}m")
    
    return " ".join(time_parts[:2]) + " ago" if time_parts else "just now"

st.set_page_config(page_title="Notifications", layout="centered")

# Home button at top right
col1, col2 = st.columns([6, 1])
with col2:
    if st.button("Home"):
        st.switch_page("pages/home.py")

st.title("Graded Assignments")

try:
    notifications = getNotifications()
except Exception as e:
    st.error("Failed to load notifications")
    st.stop()

if not notifications:
    st.info("No new notifications")

for note in notifications:
    with st.expander(f"{note['assignment_name']} — {note['class_name']} ({relative_time(note['notification_date'])})"):
        st.markdown(f"""
        <div style='
            padding: 1rem;
            background: #fffcf5;
            border-radius: 8px;
            border: 1px solid #eee;
        '>
            <div style='margin-bottom: 0.5rem;'>
                <strong>Your Grade:</strong> {note.get('grade', 'N/A')}
            </div>
            <div style='margin-bottom: 0.5rem;'>
                <strong>Feedback:</strong> {note.get('feedback', 'No feedback available')}
            </div>
            <div style='color: #666; font-size: 0.9em;'>
                Due date: {note.get('due_date', 'Unknown')}
            </div>
        </div>
        """, unsafe_allow_html=True)
