import streamlit as st

st.set_page_config(page_title="homepage", layout="wide")

# ---------- Session State Initialization ----------
if 'is_ta' not in st.session_state:
    st.session_state.is_ta = True  # True for TA, False for student

# ---------- Sidebar ---------- 
st.sidebar.markdown(
    """
    <style>
        .sidebar-title {
            font-size: 24px;
            font-weight: bold;
            padding-bottom: 20px;
        }
        .sidebar-link {
            font-size: 18px;
            color: #2e86de;
            padding: 10px 0;
            cursor: pointer;
        }
        .sidebar-link:hover {
            color: #1b4f72;
        }
        .ta-section {
            border-top: 2px solid #2e86de;
            padding-top: 20px;
            margin-top: 20px;
        }
    </style>
    """,
    unsafe_allow_html=True
)

st.sidebar.markdown("<div class='sidebar-title'>📘 GradeBook</div>", unsafe_allow_html=True)

# TA-specific sidebar options
if st.session_state.is_ta:
    st.sidebar.markdown("<div class='ta-section'>", unsafe_allow_html=True)
    st.sidebar.markdown("### TA Controls")
    if st.sidebar.button("➕ Create New Class", use_container_width=True):
        st.switch_page("pages/add_class.py")
    st.sidebar.markdown("</div>", unsafe_allow_html=True)

# General sidebar links
st.sidebar.markdown("<div class='sidebar-link'>🔔 Notifications</div>", unsafe_allow_html=True)
st.sidebar.markdown("<div class='sidebar-link'>📚 Courses</div>", unsafe_allow_html=True)
st.sidebar.markdown("<div class='sidebar-link'>👨‍🏫 Instructors</div>", unsafe_allow_html=True)
st.sidebar.markdown("<div class='sidebar-link'>🙍 Profile</div>", unsafe_allow_html=True)

# ---------- Page Title ----------
st.markdown(
    """
    <h1 style='color: #2e86de;'>Welcome to Your Dashboard</h1>
    <p style='font-size: 18px; color: #555;'>Click on course to view details</p>
    """,
    unsafe_allow_html=True
)

# ---------- Class Cards Layout ---------- 
cols = st.columns(3)

for i in range(6):  # 2 rows of 3 cards
    with cols[i % 3]:
        # Class Card Container
        with st.container(border=True):
            # Main class card content
            st.markdown(
                f"""
                <div style='
                    padding: 15px;
                    margin: 10px 0;
                    border-radius: 10px;
                    background-color: {'#f8f9fa' if i%2 else '#e8f0fe'};
                    transition: 0.3s;
                    cursor: pointer;
                '>
                    <h4 style='margin: 0; color: #1b4f72;'>Class {i+1}</h4>
                    <p style='margin: 5px 0 0; color: #34495e;'>Instructor Name</p>
                </div>
                """,
                unsafe_allow_html=True
            )
            
            # TA-specific management buttons
            if st.session_state.is_ta:
                col1, col2 = st.columns([3, 1])
                with col1:
                    if st.button("View Class", key=f"view_{i}", use_container_width=True):
                        st.switch_page("pages/classes.py")
                with col2:
                    if st.button("⚙️", key=f"manage_{i}", help="Manage Class Settings"):
                        st.switch_page("pages/manage_class.py")

# Add Class Floating Button (TA only)
if st.session_state.is_ta:
    st.markdown(
        """
        <style>
            .floating-button {
                position: fixed;
                bottom: 30px;
                right: 30px;
                z-index: 999;
            }
        </style>
        """,
        unsafe_allow_html=True
    )
    
    if st.button("➕ Create New Class", key="float_add"):
        st.switch_page("pages/add_class.py")
