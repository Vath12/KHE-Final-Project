import streamlit as st
from util.verification import isValidSession


isValidSession()
def notifications_page():
    st.set_page_config(page_title="Notifications", layout="wide")


    # Sidebar Navigation
    with st.sidebar:
        if st.button("Home"):
            st.switch_page("pages/home.py")

    st.title("Notifications")

    # Notifications toggle
    st.markdown("### Notification Settings")
    notify_enabled = st.checkbox("Receive notifications when assignments are graded", value=True)

    if notify_enabled:
        st.success("Notifications are enabled.")
    else:
        st.warning("Notifications are disabled. You won't be notified of assignment updates.")

    # Placeholder for future notifications
    st.markdown("---")
    st.subheader("Recent Notifications")
    st.info("You have no notifications at this time.")

if __name__ == "__main__":
    notifications_page()
