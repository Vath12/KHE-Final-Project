import streamlit as st
import logging

logger = logging.getLogger(__name__)

def profile_page():
    st.set_page_config(page_title="User Profile", layout="wide")
    
    # # Authentication check
    # if not st.session_state.get('authenticated'):
    #     st.warning("Please log in to view your profile")
    #     st.stop()
    
    # Custom CSS styling
    st.markdown("""
    <style>
        .profile-card {
            padding: 2rem;
            border-radius: 15px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            background-color: #f8f9fa;
            margin-bottom: 1.5rem;
        }
        .divider {
            border-top: 2px solid #eee;
            margin: 1rem 0;
        }
        .info-label {
            color: #666;
            font-size: 0.9rem;
            margin-bottom: 0.2rem;
        }
        .info-value {
            margin-bottom: 1rem;
            font-size: 1.1rem;
        }
        .avatar-img {
            width: 200px;
            height: 200px;
            border-radius: 50%;
            object-fit: cover;
            margin: 0 auto;
            display: block;
        }
    </style>
    """, unsafe_allow_html=True)

    # Sidebar Navigation
    with st.sidebar:
        st.image("assets/logo.png", width=150)
        if st.button("🏠 Home"):
            st.switch_page("home.py")
        if st.button("📚 Courses"):
            st.switch_page("pages/classes.py")
        if st.button("✏️ Edit Profile"):
            st.switch_page("pages/Edit_Profile.py")
        if st.button("🚪 Logout"):
            st.session_state.clear()
            st.switch_page("home.py")

    # Main Content
    st.title("👤 User Profile")
    
    col1, col2 = st.columns([1, 2], gap="large")

    with col1:
        st.markdown("<div class='profile-card'>", unsafe_allow_html=True)
        st.image("assets/default-avatar.png", use_column_width=True, caption="Profile Picture", output_format="PNG")
        st.markdown("</div>", unsafe_allow_html=True)

    with col2:
        st.markdown("<div class='profile-card'>", unsafe_allow_html=True)
        st.header(f"{st.session_state.get('first_name', 'User')}'s Profile")
        st.markdown("<div class='divider'></div>", unsafe_allow_html=True)

        # User Information
        cols = st.columns(2)
        with cols[0]:
            st.markdown("<div class='info-label'>First Name</div>", unsafe_allow_html=True)
            st.markdown(f"<div class='info-value'>{st.session_state.get('first_name', '')}</div>", unsafe_allow_html=True)
            
            st.markdown("<div class='info-label'>Last Name</div>", unsafe_allow_html=True)
            st.markdown(f"<div class='info-value'>{st.session_state.get('last_name', '')}</div>", unsafe_allow_html=True)
            
            st.markdown("<div class='info-label'>Username</div>", unsafe_allow_html=True)
            st.markdown(f"<div class='info-value'>{st.session_state.get('username', '')}</div>", unsafe_allow_html=True)

        with cols[1]:
            st.markdown("<div class='info-label'>Email</div>", unsafe_allow_html=True)
            st.markdown(f"<div class='info-value'>{st.session_state.get('email', '')}</div>", unsafe_allow_html=True)
            
            st.markdown("<div class='info-label'>Role</div>", unsafe_allow_html=True)
            role_display = st.session_state.get('role', 'student').replace('_', ' ').title()
            st.markdown(f"<div class='info-value'>{role_display}</div>", unsafe_allow_html=True)
            
            st.markdown("<div class='info-label'>Member Since</div>", unsafe_allow_html=True)
            st.markdown(f"<div class='info-value'>{st.session_state.get('join_date', '2024-01-01')}</div>", unsafe_allow_html=True)

        # Bio Section
        st.markdown("<div class='divider'></div>", unsafe_allow_html=True)
        st.markdown("<div class='info-label'>Bio</div>", unsafe_allow_html=True)
        st.markdown(f"<div class='info-value'>{st.session_state.get('bio', 'No bio provided')}</div>", unsafe_allow_html=True)
        
        st.markdown("</div>", unsafe_allow_html=True)

if __name__ == "__main__":
    profile_page()