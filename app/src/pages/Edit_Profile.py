import streamlit as st
import logging

logger = logging.getLogger(__name__)

def edit_profile_page():
    st.set_page_config(page_title="Edit Profile", layout="centered")
    
    # # Authentication check
    # if not st.session_state.get('authenticated'):
    #     st.warning("Please log in to edit your profile")
    #     st.stop()

    # Custom CSS styling
    st.markdown("""
    <style>
        .edit-form {
            background-color: #f8f9fa;
            border-radius: 15px;
            padding: 2rem;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        }
        .required-asterisk {
            color: #e74c3c;
            margin-left: 3px;
        }
    </style>
    """, unsafe_allow_html=True)

    # Sidebar Navigation
    with st.sidebar:
        if st.button("Home"):
            st.switch_page("home.py")
        if st.button("Profile"):
            st.switch_page("pages/Profile.py")
        if st.button("Logout"):
            st.session_state.clear()
            st.switch_page("home.py")

    # Main Content
    st.title("✏️ Edit Profile")
    
    with st.form(key="edit_profile_form", clear_on_submit=True):
        with st.container(border=True):
            st.markdown("<div class='edit-form'>", unsafe_allow_html=True)
            
            cols = st.columns(2)
            with cols[0]:
                first_name = st.text_input(
                    "First Name",
                    value=st.session_state.get('first_name', ''),
                    key="edit_first_name"
                )
                last_name = st.text_input(
                    "Last Name",
                    value=st.session_state.get('last_name', ''),
                    key="edit_last_name"
                )
                username = st.text_input(
                    "Username",
                    value=st.session_state.get('username', ''),
                    disabled=True,
                    help="Username cannot be changed"
                )
                
            with cols[1]:
                email = st.text_input(
                    "Email",
                    value=st.session_state.get('email', ''),
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
            
            bio = st.text_area(
                "Bio",
                value=st.session_state.get('bio', ''),
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
                    st.switch_page("pages/Profile.py")

        # Handle form submission
        if submitted:
            if not all([first_name, email]):
                st.error("Please fill in all required fields")
                st.stop()
                
            if new_password and (new_password != confirm_password):
                st.error("Passwords do not match!")
                st.stop()
                
            # Update session state
            updates = {
                'first_name': first_name,
                'last_name': last_name,
                'email': email,
                'bio': bio
            }
            
            if new_password:
                updates['password'] = new_password
                
            st.session_state.update(updates)
            st.success("Profile updated successfully!")
            st.switch_page("pages/Profile.py")

if __name__ == "__main__":
    edit_profile_page()