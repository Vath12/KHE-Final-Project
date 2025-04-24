import streamlit as st
import logging
from util.verification import isValidSession
from util.request import *

logger = logging.getLogger(__name__)

def edit_profile_page():
    st.set_page_config(page_title="Edit Profile", layout="centered")
    
    # Authentication check
    try:
        isValidSession()
    except Exception as e:
        st.error("Session validation failed")
        st.stop()

    # Get current user data
    try:
        user_info = getUserInfo()
    except Exception as e:
        st.error("Failed to load user information")
        logger.error(f"API error: {str(e)}")
        st.stop()

    # Custom CSS styling
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
        .social-icon {
            height: 24px;
            margin-right: 6px;
        }
        .social-field {
            display: flex;
            align-items: center;
            margin-bottom: 10px;
        }
        .required-asterisk {
            color: #e74c3c;
            margin-left: 3px;
        }
        .stTextInput, .stTextArea {
            margin-bottom: 15px;
        }
    </style>
    """, unsafe_allow_html=True)

    # Sidebar Navigation
    with st.sidebar:
        if st.button("Home"):
            st.switch_page("pages/home.py")
        if st.button("Profile"):
            st.switch_page("pages/profile_display.py")
        if st.button("Logout"):
            st.session_state.clear()
            st.switch_page("pages/home.py")

    # Main Content
    st.title("Edit Profile")
    
    with st.form(key="edit_profile_form", clear_on_submit=True):
        with st.container(border=True):
            st.markdown("<div class='edit-form'>", unsafe_allow_html=True)
            
            cols = st.columns(2)
            with cols[0]:
                first_name = st.text_input(
                    "First Name",
                    value=user_info['first_name'],
                    key="edit_first_name"
                )
                last_name = st.text_input(
                    "Last Name",
                    value=user_info['last_name'],
                    key="edit_last_name"
                )
                username = st.text_input(
                    "Username (cannot be changed)",
                    value=user_info['username'],
                    disabled=True,
                    help="Username cannot be changed"
                )
                
            with cols[1]:
                email = st.text_input(
                    "Email (not required)",
                    value=user_info['email'],
                    key="edit_email"
                )
                new_password = st.text_input(
                    "New Password",
                    type="password",
                    key="new_pass",
                    help="Leave blank to keep current password"
                )
                confirm_password = st.text_input(
                    "Confirm Password",
                    type="password",
                    key="confirm_pass"
                )

            st.markdown("### Social Media Links")

            social_cols = st.columns(5)
            platforms = [
                ("Snapchat", "snap.png", "snapchat_link"),
                ("Instagram", "insta.png", "instagram_link"),
                ("Discord", "disc.png", "discord_link"),
                ("GitHub", "hub.png", "github_link"),
                ("Facebook", "face.png", "facebook_link")
            ]
            social_links = {}

            for i, (label, icon, key_name) in enumerate(platforms):
                with social_cols[i]:
                    st.image(f"assets/{icon}", width=24)
                    social_links[key_name] = st.text_input("", value=user_info.get(key_name, ""), key=key_name, label_visibility="collapsed")

            bio = st.text_area(
                "Bio",
                value=user_info.get('bio', ''),
                height=100,
                key="edit_bio"
            )

            st.markdown("</div>", unsafe_allow_html=True)
            
            # Form Controls
            col1, col2 = st.columns([1, 2])
            with col1:
                submitted = st.form_submit_button(
                    "Save Changes",
                    use_container_width=True,
                    type="primary"
                )
            with col2:
                if st.form_submit_button("Cancel", use_container_width=True):
                    st.switch_page("pages/profile_display.py")

        # Handle form submission
        if submitted:
            if not first_name:
                st.error("Please fill in all required fields")
                st.stop()
                
            if new_password and (new_password != confirm_password):
                st.error("Passwords do not match!")
                st.stop()

            try:
                setUserInfo(
                    first_name=None if first_name == "" else first_name,
                    last_name=None if last_name == "" else last_name,
                    email=None if email == "" else email,
                    bio=None if bio == "" else bio,
                    password=None if new_password == "" else new_password,
                    snapchat=social_links["snapchat_link"],
                    instagram=social_links["instagram_link"],
                    discord=social_links["discord_link"],
                    github=social_links["github_link"],
                    facebook=social_links["facebook_link"]
                )
                st.success("Profile updated successfully!")
                st.switch_page("pages/profile_display.py")
            except Exception as e:
                st.error(f"Update failed: {str(e)}")
                logger.error(f"Update error: {str(e)}")

if __name__ == "__main__":
    edit_profile_page()
