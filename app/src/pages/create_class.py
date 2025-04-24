import streamlit as st
from util.request import getUserInfo, createClass, createAssignment  

# ---------- Page Setup ----------
st.set_page_config(page_title="Create Class", layout="centered")

# ---------- Page Title ----------
st.markdown(
    "<h1 style='color: #2e86de;'>Create a New Class</h1>",
    unsafe_allow_html=True
)

st.markdown("<hr>", unsafe_allow_html=True)

# ---------- Input Fields ----------
class_name = st.text_input("Class Name", max_chars=100)
class_description = st.text_area("Syllabus / Description", height=200)
organization = st.text_input("Organization", max_chars=100)

# ---------- Home Button ----------
if st.button("Home", use_container_width=True):
    st.switch_page("pages/home.py")

# ---------- Submit Button ----------
if st.button("Create Class", use_container_width=True):
    if not class_name or not class_description or not organization:
        st.warning("Please fill out all fields.")
    else:
        try:
            # Attempt to create the class and capture the returned class_id
            class_id = createClass(class_name, class_description, organization)
            
            # Check if the class creation was successful
            if class_id:
                # Display success message
                st.success(f"Class '{class_name}' created successfully with ID: {class_id}")
                
                # Redirect to the homepage
                st.switch_page("pages/home.py")
            else:
                st.error("Failed to create the class. Please try again.")
        
        except Exception as e:
            # If there's an error during the API call
            st.error(f"Failed to create class: {e}")
