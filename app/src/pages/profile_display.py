import streamlit as st
from util.verification import isValidSession
from util.request import *

def profile_display():
    st.set_page_config(page_title="User Profile", layout="wide")
    
    # Authentication check
    try:
        isValidSession()
    except Exception as e:
        st.error("Session validation failed")
        st.stop()
    
    # Get user data from API
    try:
        user_info = getUserInfo()
        profile_links = getUserProfileLinks()  # Fetch social media links
    except Exception as e:
        st.error("Failed to load user information")
        st.stop()

    # Platform icons and mapping
    platform_icons = {
        0: "assets/link.png",   # LinkedIn
        1: "assets/snap.png",   # Snapchat
        2: "assets/insta.png",  # Instagram
        3: "assets/disc.png",   # Discord
        4: "assets/hub.png",    # GitHub
        5: "assets/face.png"    # Facebook
    }

    # Custom CSS styling
    st.markdown("""
    <style>
        .profile-card {
            padding: 2rem;
            border-radius: 15px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            background-color: #f8f9fa;
            margin: 2rem auto;
            max-width: 800px;
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
        .social-icons {
            display: flex;
            gap: 10px;
            margin-bottom: 1rem;
        }
        .social-icons img {
            height: 30px;
        }
    </style>
    """, unsafe_allow_html=True)

    # Sidebar Navigation
    with st.sidebar:
        if st.button("Home"):
            st.switch_page("pages/home.py")
        if st.button("Courses"):
            st.switch_page("pages/home.py")
        if st.button("Edit Profile"):
            st.switch_page("pages/profile_edit.py")
        if st.button("Logout"):
            st.session_state.clear()
            st.switch_page("pages/home.py")

    # Main Content
    st.title("User Profile")

    st.markdown("<div class='profile-card'>", unsafe_allow_html=True)
    st.header(f"{user_info['first_name']}'s Profile")
    st.markdown("<div class='divider'></div>", unsafe_allow_html=True)

    cols = None
    col = 4
    # Social Media Links
    if profile_links:
        st.markdown("<div class='social-icons'>", unsafe_allow_html=True)
        for link in profile_links:
            if (col == 4):
                cols = st.columns(4)
                col = 0
            platform = link['platform']
            url = link['link']
            if url != "":
                icon_path = platform_icons.get(platform)
                if icon_path:
                    with cols[col]:
                        l,r = st.columns((0.2,0.8))
                        with l:
                            st.image(icon_path, width=30)
                        with r:
                            st.markdown(f"<p>{url}</p>", unsafe_allow_html=True)
                    col+=1

        st.markdown("</div>", unsafe_allow_html=True)

    # User Information
    cols = st.columns(2)
    with cols[0]:
        st.markdown("<div class='info-label'>First Name</div>", unsafe_allow_html=True)
        st.markdown(f"<div class='info-value'>{user_info['first_name']}</div>", unsafe_allow_html=True)
        
        st.markdown("<div class='info-label'>Last Name</div>", unsafe_allow_html=True)
        st.markdown(f"<div class='info-value'>{user_info['last_name']}</div>", unsafe_allow_html=True)
        
        st.markdown("<div class='info-label'>Username</div>", unsafe_allow_html=True)
        st.markdown(f"<div class='info-value'>{user_info['username']}</div>", unsafe_allow_html=True)

    with cols[1]:
        st.markdown("<div class='info-label'>Email</div>", unsafe_allow_html=True)
        st.markdown(f"<div class='info-value'>{user_info['email']}</div>", unsafe_allow_html=True)
        
        st.markdown("<div class='info-label'>Member Since</div>", unsafe_allow_html=True)
        st.markdown(f"<div class='info-value'>{user_info.get('join_date', '2024-01-01')}</div>", unsafe_allow_html=True)

    # Bio Section
    st.markdown("<div class='divider'></div>", unsafe_allow_html=True)
    st.markdown("<div class='info-label'>Bio</div>", unsafe_allow_html=True)
    st.markdown(f"<div class='info-value'>{user_info.get('bio', 'No bio provided')}</div>", unsafe_allow_html=True)
    
    st.markdown("</div>", unsafe_allow_html=True)

if __name__ == "__main__":
    profile_display()
