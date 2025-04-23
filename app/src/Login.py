import logging
import requests
import os,hashlib
logger = logging.getLogger(__name__)
import streamlit as st

def hash(string):
    return(hashlib.sha256(bytes(string,"utf-8")).hexdigest())
st.set_page_config(layout = 'wide', page_title="Login Page")

st.session_state['session_key'] = -1

col1, col2, col3 = st.columns([1, 2, 1])
with col2:  
    st.text_input("Username",max_chars=64,key="input_username")
    st.text_input("Password", type="password",max_chars=128,key="input_password")

    if st.button("Login"):
        result = requests.get(f'http://api:4000/trylogin/{st.session_state["input_username"]}/{hash(st.session_state["input_password"])}')
        if (result.status_code == 200):
            st.session_state["session_key"] = int(result.content)
            st.switch_page("pages/home.py")
        else:
            st.markdown("<p style='text-align: center; color: Red;'>incorrect username or password</p>", unsafe_allow_html=True)
        
