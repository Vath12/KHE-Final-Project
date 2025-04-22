import logging
import requests
import os
import streamlit as st

logger = logging.getLogger(__name__)

# Initialize session state
if 'authenticated' not in st.session_state:
    st.session_state['authenticated'] = False

st.set_page_config(layout='wide')
col1, col2, col3 = st.columns([1, 2, 1])

with col2:  
    st.image("assets/logo1.png", width=70)
    st.title("KHEsoft")
    
    # Login Form
    st.text_input("Username", max_chars=64, key="input_username")
    st.text_input("Password", type="password", max_chars=128, key="input_password")

    if st.button("Login"):
        try:
            # API call for authentication
            results = requests.get(
                f'http://api:4000/khe/trylogin/'
                f'{st.session_state["input_username"]}/'
                f'{st.session_state["input_password"]}'
            )
            
            # Debug output
            os.write(1, bytes(
                f'Login Attempt Result code:{results.status_code} content:{results.content}\n',
                "utf-8"
            ))
            
            if results.status_code == 200:
                # Successful login - set session state
                st.session_state.update({
                    'authenticated': True,
                    'username': st.session_state["input_username"],
                    'first_name': "User",  # Default values - replace with API data if available
                    'last_name': "",
                    'email': f"{st.session_state['input_username']}@khesoft.com",
                    'role': 'standard_user',
                    'bio': 'KHEsoft user account'
                })
                st.success("Login successful!")
                st.switch_page('pages/Profile.py')  # Redirect to profile
            else:
                st.error("Invalid username or password")
                
        except Exception as e:
            st.error(f"Login failed: {str(e)}")