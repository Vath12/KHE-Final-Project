# modules/nav.py
import streamlit as st

# Add this new function for profile navigation
def ProfileNav():
    st.sidebar.page_link("pages/Profile.py", label="My Profile", icon="👤")

# Modified SideBarLinks function
def SideBarLinks(show_home=False):
    """Enhanced sidebar navigation with profile support"""
    
    # Sidebar logo
    st.sidebar.image("assets/logo.png", width=150)
    
    # Authentication check
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False
        st.switch_page("Home.py")

    # Home link
    if show_home:
        st.sidebar.page_link("Home.py", label="Home", icon="🏠")

    # Authenticated user menu
    if st.session_state["authenticated"]:
        # Add profile link at the top
        ProfileNav()
        
        # Role-based navigation
        role = st.session_state.get("role", "")
        
        if role == "pol_strat_advisor":
            st.sidebar.page_link("pages/00_Pol_Strat_Home.py", label="Strategist Home", icon="👤")
            st.sidebar.page_link("pages/01_World_Bank_Viz.py", label="World Bank Viz", icon="🏦")
            st.sidebar.page_link("pages/02_Map_Demo.py", label="Map Demo", icon="🗺️")
            
        elif role == "usaid_worker":
            st.sidebar.page_link("pages/11_Prediction.py", label="Predictions", icon="📈")
            st.sidebar.page_link("pages/12_API_Test.py", label="API Test", icon="🛜")
            st.sidebar.page_link("pages/13_Classification.py", label="Classification", icon="🌺")
            
        elif role == "administrator":
            st.sidebar.page_link("pages/20_Admin_Home.py", label="Admin Home", icon="🖥️")
            st.sidebar.page_link("pages/21_ML_Model_Mgmt.py", label="Model Mgmt", icon="🏢")

    # About page (always visible)
    st.sidebar.page_link("pages/30_About.py", label="About", icon="🧠")

    # Logout button
    if st.session_state["authenticated"]:
        if st.sidebar.button("Logout", type="primary"):
            # Clear all session state variables
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.switch_page("Home.py")
            