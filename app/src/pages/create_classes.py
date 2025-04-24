import streamlit as st
from util.request import getUserInfo, createClass

# ---------- Page Setup ----------
st.set_page_config(page_title="Create Class", layout="centered")

# ---------- Permissions Check ----------
user_info = getUserInfo()

# Assuming there's a field in user_info to check if they can create a class
if not user_info.get("can_create_class", False):
    st.error("You do not have permission to create a class.")
    st.stop()

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

# ---------- Submit Button ----------
if st.button("Create Class", use_container_width=True):
    if not class_name or not class_description or not organization:
        st.warning("Please fill out all fields.")
    else:
        try:
            class_id = createClass(class_name, class_description, organization)
            st.success(f"Class '{class_name}' created successfully!")
            st.switch_page("Homepage.py")
        except Exception as e:
            st.error(f"Failed to create class: {e}")
