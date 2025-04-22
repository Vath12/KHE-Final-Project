import logging
import requests
import os
logger = logging.getLogger(__name__)

import streamlit as st
st.set_page_config(layout = 'wide', page_title="Login Page")

st.session_state['session_key'] = -1

col1, col2, col3 = st.columns([1, 2, 1])
with col2:  
    st.text_input("Username",max_chars=64,key="input_username")
    st.text_input("Password", type="password",max_chars=128,key="input_password")

    if st.button("Login"):
        code = 200 if (st.session_state["input_username"] == "a") else 401
        st.session_state["session_key"] = 99
        if (code == 200):
            st.switch_page("pages/home.py")
        else:
            st.markdown("<p style='text-align: center; color: Red;'>incorrect username or password</p>", unsafe_allow_html=True)
        #results = requests.get(f'http://api:4000/khe/trylogin/{st.session_state["input_username"]}/{st.session_state["input_password"]}')
        #os.write(1,bytes(f'Login Attempt Result code:{results.status_code} content:{results.content}\n',"utf-8"))
        
