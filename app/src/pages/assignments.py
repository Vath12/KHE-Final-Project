import streamlit as st
from util.verification import isValidSession
from util.request import createAssignment  # Import the createAssignment function

# Authentication check
try:
    isValidSession()  # Check if the session is valid
except Exception as e:
    st.error("Session validation failed. Please log in again.")
    st.stop()  # Prevent further code execution

# ---------- Page Setup ----------
st.set_page_config(page_title="Create Assignment", layout="centered")


# ---------- Page Title ----------
st.markdown(
    "<h1 style='color: #2e86de;'>Create New Assignment</h1>",
    unsafe_allow_html=True
)

st.markdown("<hr>", unsafe_allow_html=True)

# ---------- Input Fields ----------
assignment_name = st.text_input("Assignment Name", max_chars=100)
due_date = st.date_input("Due Date")
weight = st.number_input("Weight (%)", min_value=0, max_value=100, value=0)
points = st.number_input("Total Points", min_value=0, value=0)
description = st.text_area("Description", height=150)

# ---------- Create Assignment Button ----------
if st.button("Create Assignment", use_container_width=True):
    if not assignment_name or not due_date or not description:
        st.warning("Please fill out all required fields.")
    else:
        try:
            # Use the selected class ID from session state
            class_id = st.session_state.selected_class_id
            
            # Create the assignment using the provided function
            assignment_id = createAssignment(class_id, assignment_name, due_date, weight)

            # Display success message
            st.success(f"Assignment '{assignment_name}' created successfully!")

            # Redirect back to the class page
            st.session_state["assignment_created"] = True 
            st.switch_page(f"pages/classes.py")  #

        except Exception as e:
            st.error(f"Failed to create assignment: {e}")

# ---------- Back Button ----------
if st.button("Back to Class", use_container_width=True):
    st.switch_page(f"pages/classes.py")  # Go back to_
