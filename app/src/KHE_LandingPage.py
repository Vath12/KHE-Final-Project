import logging
logger = logging.getLogger(__name__)

import streamlit as st

st.set_page_config(layout = 'wide')

st.title(f"KHEsoft")
st.session_state['auth_key'] = 0
