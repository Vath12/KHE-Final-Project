import streamlit as st
import requests
from util.verification import isValidSession
from util.request import *

def class_management_page():
    st.set_page_config(page_title="Manage Classes", layout="centered")
    
    # Authentication check
    try:
        isValidSession()
    except Exception as e:
        st.error("Session validation failed")
        st.switch_page("pages/error.py")
    
    # Get current user data and classes
    try:
        user_info = getUserInfo()
        current_classes = getClassList()
    except Exception as e:
        st.error("Failed to load user information")
        st.switch_page("pages/error.py")

    # Custom CSS styling
    st.markdown("""
    <style>
        .page-section {
            background-color: #f8f9fa;
            border-radius: 15px;
            padding: 2rem;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            margin-bottom: 2rem;
        }
        .section-title {
            font-size: 1.5rem;
            font-weight: bold;
            margin-bottom: 1.5rem;
            color: #333;
        }
        .class-card {
            background-color: white;
            border-radius: 8px;
            padding: 1rem;
            margin-bottom: 1rem;
            border-left: 4px solid #3498db;
        }
        .class-title {
            font-size: 1.2rem;
            font-weight: bold;
            margin-bottom: 0.5rem;
        }
    </style>
    """, unsafe_allow_html=True)

    # Top navigation
    col1, col2 = st.columns([6, 1])
    with col2:
        if st.button("Home", use_container_width=True):
            st.switch_page("pages/home.py")

    st.title("Manage Your Classes")
    
    # Join Class Section
    st.markdown("<div class='page-section'>", unsafe_allow_html=True)
    st.markdown("<div class='section-title'>Join a New Class</div>", unsafe_allow_html=True)
    
    with st.form("join_class_form"):
        class_code = st.text_input("Enter Class Code", placeholder="e.g., ABC123")
        join_submitted = st.form_submit_button("Join Class", type="primary", use_container_width=True)
        
        if join_submitted and class_code:
            # Here you would implement the API call to join a class
            # Sample success message
            
            try:
                # Simulated API call (you would replace this with the actual API call)
                # response = requests.post(
                #     "http://api:4000/joinClass",
                #     json={
                #         "session_key": st.session_state.session_key,
                #         "class_code": class_code
                #     }
                # )
                
                # if response.status_code != 200:
                #     raise Exception(response.json().get('error', 'Failed to join class'))
                
                st.success(f"Successfully joined class with code: {class_code}")
                st.rerun()  # Refresh the page to show the newly joined class
                
            except Exception as e:
                st.error(f"Error joining class: {str(e)}")
    
    st.markdown("</div>", unsafe_allow_html=True)
    
    # Current Classes Section
    st.markdown("<div class='page-section'>", unsafe_allow_html=True)
    st.markdown("<div class='section-title'>Your Current Classes</div>", unsafe_allow_html=True)
    
    if not current_classes:
        st.info("You are not enrolled in any classes yet.")
    else:
        for class_info in current_classes:
            st.markdown(f"""
            <div class='class-card'>
                <div class='class-title'>{class_info.get('name', 'Unnamed Class')}</div>
                <div style='display: flex; justify-content: space-between; align-items: center;'>
                    <div>Class ID: {class_info.get('class_id', 'N/A')}</div>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            # Leave Class Button
            if st.button(f"Leave Class: {class_info.get('name', 'Unnamed Class')}", key=f"leave_{class_info.get('class_id')}"):
                try:
                    # Simulated API call (you would replace this with the actual API call)
                    # response = requests.post(
                    #     "http://api:4000/leaveClass",
                    #     json={
                    #         "session_key": st.session_state.session_key,
                    #         "class_id": class_info.get('class_id')
                    #     }
                    # )
                    
                    # if response.status_code != 200:
                    #     raise Exception(response.json().get('error', 'Failed to leave class'))
                    
                    st.success(f"Successfully left class: {class_info.get('name', 'Unnamed Class')}")
                    st.rerun()  # Refresh the page to show updated class list
                    
                except Exception as e:
                    st.error(f"Error leaving class: {str(e)}")
    
    st.markdown("</div>", unsafe_allow_html=True)

if __name__ == "__main__":
    class_management_page()