import streamlit as st
from util.verification import isValidSession
from util.request import joinClass  # Import the joinClass function

# Authentication check
try:
    isValidSession()  # Check if the session is valid
except Exception as e:
    st.error("Session validation failed. Please log in again.")
    st.stop()  # Prevent further code execution

# Set page layout
st.set_page_config(page_title="Join a Class", layout="centered")

# ---------- Page Title ----------
st.markdown(
    "<h1 style='color: #2e86de;'>Join an Existing Class</h1>",
    unsafe_allow_html=True
)

st.markdown("<hr>", unsafe_allow_html=True)

# ---------- Class Code Input ----------
class_code = st.text_input("Enter Class Code (max 8 characters)", max_chars=8)

# ---------- Join Class Button ----------
if st.button("Join Class", use_container_width=True):
    if not class_code:
        st.warning("Please enter a class code.")
    else:
        try:
            # Attempt to join the class using the provided code
            if joinClass(class_code):  
                st.success(f"Successfully joined class with code: {class_code}")
                
                # Optionally, redirect the user to another page, e.g., their class page
                st.switch_page("pages/home.py")
            else:
                st.error("Failed to join the class. Please check the code and try again.")
        except Exception as e:
            st.error(f"An error occurred while joining the class: {e}")

# ---------- Home Button ----------
if st.button("Go Home", use_container_width=True):
    st.switch_page("pages/home.py")
