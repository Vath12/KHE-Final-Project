import streamlit as st
from datetime import time

def manage_class_page():
    st.set_page_config(page_title="Manage Class", layout="centered")
    
    # # Authorization check
    # if st.session_state.get('role') != 'ta':
    #     st.error("⛔ Unauthorized access. TA privileges required.")
    #     st.stop()

    # Style configuration
    st.markdown("""
    <style>
        .management-section {
            background-color: #f8f9fa;
            border-radius: 10px;
            padding: 1.5rem;
            margin: 1rem 0;
            box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
        }
        .danger-zone {
            border: 2px solid #e74c3c;
            border-radius: 8px;
            padding: 1rem;
            margin-top: 2rem;
        }
    </style>
    """, unsafe_allow_html=True)

    st.title("⚙️ Manage Class")

    # Check for existing classes
    if 'classes' not in st.session_state or len(st.session_state.classes) == 0:
        st.warning("No classes available. Create a class first!")
        if st.button("Create New Class"):
            st.switch_page("pages/add_class.py")
        return

    # Class selection dropdown
    selected_class = st.selectbox(
        "Select Class to Manage",
        options=[c['code'] for c in st.session_state.classes],
        format_func=lambda code: f"{code} - {next(c['name'] for c in st.session_state.classes if c['code'] == code)}"
    )

    # Get class details
    class_index = next(i for i, c in enumerate(st.session_state.classes) if c['code'] == selected_class)
    current_class = st.session_state.classes[class_index]

    with st.form(key="class_management_form"):
        # Section 1: Class Information
        with st.container(border=True):
            st.subheader("📚 Class Details")
            col1, col2 = st.columns(2)
            
            with col1:
                new_name = st.text_input(
                    "Class Name",
                    value=current_class['name'],
                    key=f"name_{selected_class}"
                )
                new_code = st.text_input(
                    "Class Code",
                    value=current_class['code'],
                    key=f"code_{selected_class}"
                )
                
            with col2:
                new_section = st.number_input(
                    "Section Number",
                    value=current_class['section'],
                    min_value=1,
                    max_value=50,
                    key=f"section_{selected_class}"
                )
                new_days = st.multiselect(
                    "Class Days",
                    options=["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"],
                    default=current_class['schedule']['days'],
                    key=f"days_{selected_class}"
                )

            # Time inputs
            st.markdown("**Class Schedule**")
            start_col, end_col = st.columns(2)
            with start_col:
                new_start = st.time_input(
                    "Start Time",
                    value=time.fromisoformat(current_class['schedule']['start']),
                    key=f"start_{selected_class}"
                )
            with end_col:
                new_end = st.time_input(
                    "End Time",
                    value=time.fromisoformat(current_class['schedule']['end']),
                    key=f"end_{selected_class}"
                )

            new_desc = st.text_area(
                "Course Description",
                value=current_class['description'],
                height=100,
                key=f"desc_{selected_class}"
            )

        # Section 2: Student Management
        with st.container(border=True):
            st.subheader("👥 Student Enrollment")
            
            # Get all students (mock data - replace with actual student list)
            all_students = ["student1@uni.edu", "student2@uni.edu", "student3@uni.edu"]
            current_students = current_class['students']
            
            enrolled_students = st.multiselect(
                "Enrolled Students",
                options=all_students,
                default=current_students,
                key=f"students_{selected_class}"
            )

        # Section 3: Danger Zone
        with st.container(border=True):
            st.subheader("⚠️ Danger Zone")
            st.markdown("<div class='danger-zone'>", unsafe_allow_html=True)
            
            if st.button("🗑️ Delete This Class", type="secondary"):
                del st.session_state.classes[class_index]
                st.success("Class deleted successfully!")
                st.switch_page("home.py")
            
            st.markdown("</div>", unsafe_allow_html=True)

        # Form Submission
        col1, col2 = st.columns([1, 3])
        with col1:
            if st.form_submit_button("💾 Save Changes", use_container_width=True):
                # Update class details
                st.session_state.classes[class_index] = {
                    "name": new_name,
                    "code": new_code,
                    "section": new_section,
                    "schedule": {
                        "days": new_days,
                        "start": str(new_start),
                        "end": str(new_end)
                    },
                    "description": new_desc,
                    "students": enrolled_students
                }
                st.success("Class details updated successfully!")
                st.rerun()

        with col2:
            if st.form_submit_button("❌ Cancel", use_container_width=True):
                st.switch_page("home.py")

if __name__ == "__main__":
    manage_class_page()