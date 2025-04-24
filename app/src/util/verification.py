import streamlit as st
from util.request import safeGet
import requests

def isValidSession():
    """
    Verifies that the streamlit session state has a valid session_key, redirects to login on failure
    """
    if (st.session_state.get("session_key")==None):
        st.switch_page("Login.py")
    result = safeGet(f"http://api:4000/isValidSession/{st.session_state.get('session_key')}")
    if (result.status_code != 200):
        st.switch_page("Login.py")
    return True
