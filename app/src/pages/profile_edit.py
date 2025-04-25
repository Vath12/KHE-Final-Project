import streamlit as st
import logging
from util.verification import isValidSession
from util.request import *

logger = logging.getLogger(__name__)

def get_social_links_dict():
    try:
        links = getUserProfileLinks()
        return {link["platform_id"]: link["link"] for link in links}
    except:
        return {}

def edit_profile_page():
    st.set_page_config(page_title="Edit Profile", layout="centered")

    try:
        isValidSession()
    except Exception as e:
        st.error("Session validation failed")
        st.stop()

    try:
        user_info = getUserInfo()
    except Exception as e:
        st.error("Failed to load user information")
        logger.error(f"API error: {str(e)}")
        st.stop()

    social_links = get_social_links_dict()

    st.markdown("""
    <style>
        .edit-form {
            background-color: #f8f9fa;
            border-radius: 15px;
            padding: 2rem;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            margin-left: 10%;
            margin-right: 10%;
        }
        .social-input {
            display: flex;
            align-items: center;
            margin-bottom: 10px;
        }
        .social-input img {
            height: 30px;
            margin-right: 10px;
        }
    </style>
    """, unsafe_allow_html=True)

    with st.sidebar:
        if st.button("Home"):
            st.switch_page("pages/home.py")
        if st.button("Profile"):
            st.switch_page("pages/profile_display.py")
        if st.button("Logout"):
            st.session_state.clear()
            st.switch_page("pages/home.py")

    st.title("Edit Profile")

    with st.form(key="edit_profile_form", clear_on_submit=True):
        with st.container(border=True):
            st.markdown("<div class='edit-form'>", unsafe_allow_html=True)

            cols = st.columns(2)
            with cols[0]:
                first_name = st.text_input("First Name", value=user_info['first_name'], key="edit_first_name")
                last_name = st.text_input("Last Name", value=user_info['last_name'], key="edit_last_name")
                username = st.text_input("Username (cannot be changed)", value=user_info['username'], disabled=True)

            with cols[1]:
                email = st.text_input("Email (not required)", value=user_info['email'], key="edit_email")
                new_password = st.text_input("New Password", type="password", key="new_pass")
                confirm_password = st.text_input("Confirm Password", type="password", key="confirm_pass")

            st.markdown("#### Social Media Links")

            link_inputs = [
                (0, "LinkedIn", "assets/link.png"),
                (1, "Snapchat", "assets/snap.png"),
                (2, "Instagram", "assets/insta.png"),
                (3, "Discord", "assets/disc.png"),
                (4, "GitHub", "assets/hub.png"),
                (5, "Facebook", "assets/face.png")
            ]

            new_links = {}
            for platform_id, label, icon_path in link_inputs:
                current_val = social_links.get(platform_id, "")
                col1, col2 = st.columns([1, 5])
                with col1:
                    st.image(icon_path, width=30)
                with col2:
                    new_links[platform_id] = st.text_input(label, value=current_val, key=f"social_{platform_id}")

            bio = st.text_area("Bio", value=user_info.get('bio', ''), height=100, key="edit_bio")

            st.markdown("</div>", unsafe_allow_html=True)

            col1, col2 = st.columns([1, 2])
            with col1:
                submitted = st.form_submit_button("Save Changes", use_container_width=True, type="primary")
            with col2:
                if st.form_submit_button("Cancel", use_container_width=True):
                    st.switch_page("pages/profile_display.py")

        if submitted:
            if not first_name:
                st.error("Please fill in all required fields")
                st.stop()
            if new_password and (new_password != confirm_password):
                st.error("Passwords do not match!")
                st.stop()

            
            setUserInfo(
                first_name=None if first_name == "" else first_name,
                last_name=None if last_name == "" else last_name,
                email=None if email == "" else email,
                bio=None if bio == "" else bio,
                password=None if new_password == "" else new_password
            )

            for platform_id, link in new_links.items():
                setUserProfileLink(platform_id, link)

            st.success("Profile updated successfully!")
            st.switch_page("pages/profile_display.py")

           

if __name__ == "__main__":
    edit_profile_page()
