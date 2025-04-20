import logging
logger = logging.getLogger(__name__)

import streamlit as st

st.set_page_config(layout = 'wide')

col1, col2, col3 = st.columns([1, 2, 1])
with col2:  
    st.text_input("Username")
    st.text_input("Password", type="password")
    st.button("Login")
st.session_state['auth_key'] = 0
