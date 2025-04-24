import streamlit as st
from util.verification import isValidSession
from util.request import getNotifications, removeNotifications

def notifications_page():
    st.set_page_config(page_title="Notifications", layout="wide")

    # Session validation
    try:
        isValidSession()
    except Exception:
        st.error("Session validation failed")
        st.stop()

    # Sidebar
    with st.sidebar:
        # "Home" button filling the column
        st.button("Home", use_container_width=True)

    # Custom CSS for layout adjustments
    st.markdown("""
    <style>
        .title-container {
            padding-top: 40px;
            padding-bottom: 10px;
            margin-left: -30px;  /* move title further left */
        }
        .main-title {
            font-size: 2.5rem;
            font-weight: bold;
            color: #007bff;
            text-align: left;
        }
        .centered-container {
            display: flex;
            flex-direction: column;
            align-items: center;
        }
        .toggle-switch {
            margin-top: -20px;  /* Move the toggle switch closer to the title */
            margin-left: -30px;  /* Move toggle switch further left */
            margin-bottom: 1.5rem;  /* Reduced bottom margin to keep it closer to the title */
        }
        .notif-box {
            background-color: #f8f9fa;
            padding: 1.5rem 2rem;
            border-radius: 15px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.05);
            max-width: 600px;
            width: 100%;
            text-align: center;
            position: relative;
            margin-bottom: 1rem;  /* Add space between notifications */
        }
        .delete-button {
            margin-top: 10px;
            background-color: #dc3545;
            color: white;
            border-radius: 5px;
            padding: 0.5rem;
            width: 100%;
        }
        .delete-button:hover {
            background-color: #c82333;
        }
    </style>
    """, unsafe_allow_html=True)

    # Title
    st.markdown("<div class='title-container'><div class='main-title'>Notifications</div></div>", unsafe_allow_html=True)

    # Main content area
    st.markdown("<div class='centered-container'>", unsafe_allow_html=True)
    
    # Toggle switch right below the title, closer and more to the left
    st.markdown("<div class='toggle-switch'>", unsafe_allow_html=True)
    notifications_enabled = st.toggle("Receive Notifications", value=True)
    st.session_state['notifications_enabled'] = notifications_enabled
    st.markdown("</div>", unsafe_allow_html=True)

    # Fetch notifications
    notifications = getNotifications()

    if notifications:
        for notification in notifications:
            # Display each notification with delete button
            with st.container():
                st.markdown(f"<div class='notif-box'>{notification['message']}", unsafe_allow_html=True)
                # "Delete" button for deleting the notification
                if st.button("Delete", key=notification['id'], help="Delete Notification"):
                    removeNotifications(notification['id'])  # Remove the notification
                    st.experimental_rerun()  # Refresh the page to reflect the update
                st.markdown("</div>", unsafe_allow_html=True)

    else:
        st.write("You don't have any notifications yet.")

    st.markdown("</div>", unsafe_allow_html=True)

if __name__ == "__main__":
    notifications_page()
