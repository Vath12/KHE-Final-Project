import logging
import requests

import os
logger = logging.getLogger(__name__)

import streamlit as st

col1, col2, col3 = st.columns([1, 2, 1])
with col2:  
    st.title("testtest")
st.session_state['auth_key'] = 0