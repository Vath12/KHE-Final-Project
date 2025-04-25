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
        if st.button("Home"):
            st.switch_page("pages/home.py")

    # CSS styles
    st.markdown("""
    <style>
        .title-container {
            padding-top: 40px;
            padding-bottom: 10px;
            margin-left: -30px;
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
        .notif-box {
            background-color: #f8f9fa;
            padding: 1.5rem 2rem;
            border-radius: 15px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.05);
            max-width: 600px;
            width: 100%;
            text-align: left;
            position: relative;
            margin-bottom: 1rem;
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
    st.markdown("<div class='centered-container'>", unsafe_allow_html=True)

    # Initialize state
    if "selected_notifications" not in st.session_state:
        st.session_state.selected_notifications = []
    if "deleted_ids" not in st.session_state:
        st.session_state.deleted_ids = set()

    notifications = [n for n in getNotifications() if n.get("assignment_id") not in st.session_state.deleted_ids]

    if notifications:
        for notification in notifications:
            assignment_id = notification.get('assignment_id', 'ID not available')
            assignment_name = notification.get('assignment_name', 'Assignment name not available')
            class_name = notification.get('class_name', 'Class name not available')
            notification_date = notification.get('notification_date', 'Date not available')

            message = f"Your assignment '{assignment_name}' for class '{class_name}' was graded on {notification_date}."

            if st.checkbox(f"Select to delete: {message}", key=str(assignment_id)):
                if assignment_id not in st.session_state.selected_notifications:
                    st.session_state.selected_notifications.append(assignment_id)
            else:
                if assignment_id in st.session_state.selected_notifications:
                    st.session_state.selected_notifications.remove(assignment_id)

        if st.button("Delete Selected Notifications"):
            for assignment_id in st.session_state.selected_notifications:
                removeNotifications(assignment_id)
                st.session_state.deleted_ids.add(assignment_id)

            st.success("Selected notifications have been deleted.")
            st.session_state.selected_notifications = []

    else:
        st.write("You don't have any notifications yet.")

    st.markdown("</div>", unsafe_allow_html=True)

if __name__ == "__main__":
    notifications_page()
