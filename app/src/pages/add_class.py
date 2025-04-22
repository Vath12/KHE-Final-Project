import streamlit as st
from datetime import time

def add_class_page():
    st.set_page_config(page_title="Add New Class", layout="centered")

    # # Authorization check
    # if st.session_state.get('role') != 'ta':
    #     st.error("⛔ Unauthorized access. TA privileges required.")
    #     st.stop()

    # Style configuration
    st.markdown("""
    <style>
        .class-form {
            background-color: #f8f9fa;
            border-radius: 10px;
            padding: 2rem;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05);
        }
        .required-asterisk {
            color: #e74c3c;
            margin-left: 3px;
        }
        .time-input > div {
            gap: 1rem;
        }
    </style>
    """, unsafe_allow_html=True)

    st.title("📝 Create New Class")
    
    with st.form(key="class_creation_form", clear_on_submit=True):
        with st.container(border=True):
            st.markdown("<div class='class-form'>", unsafe_allow_html=True)
            
            # Form Header
            st.subheader("Class Information")
            st.markdown("---")
            
            # Form Layout
            col1, col2 = st.columns(2)
            with col1:
                class_name = st.text_input(
                    "Class Name",
                    help="Enter the official course name",
                    key="class_name"
                )
                
                class_code = st.text_input(
                    "Class Code",
                    help="Unique course code (e.g. CS-101)",
                    key="class_code"
                )
                
            with col2:
                section_number = st.number_input(
                    "Section Number",
                    min_value=1,
                    max_value=50,
                    value=1,
                    key="section"
                )
                
                schedule = st.multiselect(
                    "Class Days",
                    options=["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"],
                    default=["Monday", "Wednesday"],
                    key="days"
                )
            
            # Time Input
            st.markdown("<div class='time-input'>", unsafe_allow_html=True)
            start_time, end_time = st.columns(2)
            with start_time:
                class_start = st.time_input(
                    "Start Time",
                    value=time(9, 0),
                    key="start_time"
                )
            with end_time:
                class_end = st.time_input(
                    "End Time",
                    value=time(10, 30),
                    key="end_time"
                )
            st.markdown("</div>", unsafe_allow_html=True)
            
            # Additional Information
            class_description = st.text_area(
                "Course Description",
                height=100,
                help="Brief overview of the course content",
                key="description"
            )
            
            st.markdown("</div>", unsafe_allow_html=True)  # End class-form div
            
            # Form Submission
            submit_col, cancel_col = st.columns([1, 2])
            with submit_col:
                submitted = st.form_submit_button(
                    "🚀 Create Class",
                    use_container_width=True,
                    type="primary"
                )
            with cancel_col:
                if st.form_submit_button("❌ Cancel", use_container_width=True):
                    st.switch_page("home.py")

        # Validation and Processing
        if submitted:
            if not all([class_name, class_code, schedule]):
                st.error("Please fill all required fields (marked with *)")
                st.stop()
                
            if class_start >= class_end:
                st.error("End time must be after start time")
                st.stop()
                
            # Check for existing class codes
            existing_classes = st.session_state.get('classes', [])
            if any(c['code'] == class_code for c in existing_classes):
                st.error(f"Class code {class_code} already exists!")
                st.stop()
            
            # Create class object
            new_class = {
                "name": class_name,
                "code": class_code,
                "section": section_number,
                "schedule": {
                    "days": schedule,
                    "start": str(class_start),
                    "end": str(class_end)
                },
                "description": class_description,
                "students": []
            }
            
            # Update session state
            if 'classes' not in st.session_state:
                st.session_state.classes = []
            st.session_state.classes.append(new_class)
            
            st.success("🎉 Class created successfully!")
            st.balloons()
            st.switch_page("home.py")

if __name__ == "__main__":
    add_class_page()