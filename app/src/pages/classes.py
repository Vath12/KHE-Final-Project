import streamlit as st
from util.verification import isValidSession

isValidSession()

# Set up page
st.set_page_config(layout="wide", page_title="Course Details")

# Create a row for the header and home button
col_left, col_right = st.columns([6, 1])

with col_left:
    st.markdown("<h1 style='color: #7F27FF;'>📘 Course: [Class Name]</h1>", unsafe_allow_html=True)

with col_right:
    st.markdown(
        "<div style='text-align: right;'>"
        "<button style='padding: 0.5rem 1rem; font-size: 1rem; background-color: #9C4DFF; color: white; border: none; border-radius: 6px; cursor: pointer;'>"
        "🏠 Home"
        "</button>"
        "</div>",
        unsafe_allow_html=True
    )

st.write("")

# Track which section is selected
if "selected_section" not in st.session_state:
    st.session_state.selected_section = "overview"

# Section buttons
st.markdown("### 🧭 Navigate")
col1, col2, col3, col4 = st.columns(4)
with col1:
    if st.button("📄 Syllabus"):
        st.session_state.selected_section = "syllabus"
with col2:
    if st.button("📝 Assignments"):
        st.session_state.selected_section = "assignments"
with col3:
    if st.button("📢 Announcements"):
        st.session_state.selected_section = "announcements"
with col4:
    if st.button("📊 Grades"):
        st.session_state.selected_section = "grades"

st.markdown("---")

# Display content based on section
if st.session_state.selected_section == "syllabus":
    st.markdown(
        """
        <div style='padding: 1rem; background-color: #FFD6EC; border-left: 8px solid #FF2E88; border-radius: 8px;'>
            <h3>📄 Syllabus</h3>
            <p>Syllabus content: Nothing right now.</p>
        </div>
        """,
        unsafe_allow_html=True
    )

elif st.session_state.selected_section == "assignments":
    st.markdown(
        """
        <div style='padding: 1rem; background-color: #FFF6D1; border-left: 8px solid #FFC700; border-radius: 8px;'>
            <h3>📝 Assignments</h3>
            <ul style='line-height: 2;'>
                <li>Assignment 1 - Due: [Date]</li>
                <li>Assignment 2 - Due: [Date]</li>
                <li>Assignment 3 - Due: [Date]</li>
            </ul>
        </div>
        """,
        unsafe_allow_html=True
    )

elif st.session_state.selected_section == "announcements":
    st.markdown(
        """
        <div style='padding: 1rem; background-color: #D9F6FF; border-left: 8px solid #1E90FF; border-radius: 8px;'>
            <h3>📢 Announcements</h3>
            <ul style='line-height: 2;'>
                <li>Welcome to the course!</li>
                <li>Class starts Monday.</li>
                <li>Don’t forget to read the syllabus.</li>
            </ul>
        </div>
        """,
        unsafe_allow_html=True
    )

elif st.session_state.selected_section == "grades":
    st.markdown(
        """
        <div style='padding: 1rem; background-color: #E6FFE6; border-left: 8px solid #00CC66; border-radius: 8px;'>
            <h3>📊 Grades</h3>
            <ul style='line-height: 2;'>
                <li>Assignment 1: [Grade not entered]</li>
                <li>Assignment 2: [Grade not entered]</li>
                <li>Assignment 3: [Grade not entered]</li>
            </ul>
        </div>
        """,
        unsafe_allow_html=True
    )

else:
    st.markdown(
        """
        <div style='padding: 2rem; background-color: #F0EFFF; border-left: 8px solid #9C4DFF; border-radius: 8px;'>
            <h3>📘 Welcome to [Class Name]</h3>
            <p>This is your course dashboard. Select a section above to begin.</p>
        </div>
        """,
        unsafe_allow_html=True
    )
