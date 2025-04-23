import streamlit as st
import requests

def isValidSession():
    if (st.session_state.get("session_key")==None):
        st.switch_page("Login.py")
    result = requests.get(f"http://api:4000/isValidSession/{st.session_state.get('session_key')}")
    if (result.status_code != 200):
        st.switch_page("Login.py")
    return True
