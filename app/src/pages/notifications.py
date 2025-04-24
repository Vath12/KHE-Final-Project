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
        # "Home" button that switches to the homepage
        if st.button("Home"):
            st.switch_page("pages/home")  # Switch to the homepage page

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
        .notif-box {
            background-color: #f8f9fa;
            padding: 1.5rem 2rem;
            border-radius: 15px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.05);
            max-width: 600px;
            width: 100%;
            text-align: left;
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
    
    # Fetch notifications
    notifications = getNotifications()

    if notifications:
        selected_notifications = []

        for notification in notifications:
            # Extract details from the notification
            notification_date = notification.get('notification_date', 'Date not available')
            assignment_name = notification.get('assignment_name', 'Assignment name not available')
            class_name = notification.get('class_name', 'Class name not available')
            assignment_id = notification.get('assignment_id', 'ID not available')

            # Display each notification with a checkbox
            message = f"Your assignment '{assignment_name}' for class '{class_name}' was graded on {notification_date}."

            with st.container():
                # Checkbox for selecting notification
                if st.checkbox(f"Select to delete: {message}", key=assignment_id):
                    selected_notifications.append(assignment_id)

        # Button to delete selected notifications
        if st.button("Delete Selected Notifications"):
            for assignment_id in selected_notifications:
                removeNotifications(assignment_id)  # Remove the notification using the assignment ID
            st.success("Selected notifications have been deleted.")
            st.experimental_rerun()  # Refresh the page to reflect the update

    else:
        st.write("You don't have any notifications yet.")

    st.markdown("</div>", unsafe_allow_html=True)

if __name__ == "__main__":
    notifications_page()
