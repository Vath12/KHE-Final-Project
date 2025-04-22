import logging
import requests
import os,hashlib
import streamlit as st

logger = logging.getLogger(__name__)

def edit_profile_page():
    st.set_page_config(layout='wide')
    
    if not st.session_state.get('authenticated'):
        st.warning("Please log in to edit your profile")
        st.stop()

    SideBarLinks(show_home=False)
    st.title("Edit Profile")

    with st.form("edit_profile_form"):
        cols = st.columns(2)
        with cols[0]:
            # Username display (non-editable)
            st.markdown("**Username**")
            st.markdown(f'`{st.session_state.get("username", "")}`')
            
            first_name = st.text_input("First Name", 
                                     value=st.session_state.get('first_name', ''))
            last_name = st.text_input("Last Name", 
                                    value=st.session_state.get('last_name', ''))
        
        with cols[1]:
            email = st.text_input("Email", 
                                value=st.session_state.get('email', ''))
            new_password = st.text_input("New Password", 
                                       type="password",
                                       placeholder="Leave blank to keep current")
            confirm_password = st.text_input("Confirm Password", 
                                            type="password",
                                            placeholder="Leave blank to keep current")
        
        bio = st.text_area("Bio", 
                         value=st.session_state.get('bio', ''), 
                         height=100,
                         placeholder="Tell us about yourself...")
        
        if st.form_submit_button("Save Changes"):
            # Password validation
            if new_password and (new_password != confirm_password):
                st.error("Passwords do not match!")
                return
                
            # Update session state (excluding username)
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
            st.switch_page('pages/Profile.py')

    if st.button("Cancel"):
        st.switch_page('pages/Profile.py')

if __name__ == "__main__":
    edit_profile_page()
    