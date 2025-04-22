import streamlit as st

# Page setup
st.set_page_config(layout="wide", page_title="Assignments")

# ---------- Navigation ----------
col_left, col_right = st.columns([6, 2])
with col_left:
    st.title("Assignments")
with col_right:
    col_h1, col_h2 = st.columns(2)
    with col_h1:
        if st.button("Home"):
            st.switch_page("home.py")
    with col_h2:
        if st.button("Classes"):
            st.switch_page("pages/classes.py")

st.markdown("---")

# ---------- Assignment Storage ----------
if "assignments" not in st.session_state:
    st.session_state.assignments = []

# ---------- View Toggle ----------
view_mode = st.radio("View as:", ["Student", "TA"], horizontal=True)

# ---------- Student View ----------
if view_mode == "Student":
    st.subheader("Assignment List")
    if st.session_state.assignments:
        st.table([{
            "Assignment": a["name"],
            "Description": a["description"] if "description" in a else "No description",
            "Due Date": a["due_date"],
            "Score (%)": a["score"] if "score" in a else "Not Graded",
            "Weight (%)": a["weight"]
        } for a in st.session_state.assignments])
    else:
        st.info("No assignments available yet.")

    # Final grade calculation
    if st.session_state.assignments:
        total_weight = sum(a["weight"] for a in st.session_state.assignments)
        if total_weight == 100:
            final_grade = sum(a["score"] * (a["weight"] / 100) for a in st.session_state.assignments if "score" in a)
            st.success(f"Final Grade: {final_grade:.2f}%")
        else:
            st.warning(f"Total weight is {total_weight}%. Final grade requires exactly 100%.")

# ---------- TA View ----------
else:
    with st.expander("Create Assignment (TA Access – currently open to everyone)"):
        with st.form("create_assignment_form"):
            name = st.text_input("Assignment Name")
            description = st.text_area("Assignment Description")
            due_date = st.date_input("Due Date")
            score = st.number_input("Score (%)", min_value=0.0, max_value=100.0)
            weight = st.number_input("Weight (%)", min_value=0.0, max_value=100.0)
            submit = st.form_submit_button("Add Assignment")

            if submit and name:
                st.session_state.assignments.append({
                    "name": name,
                    "description": description,
                    "due_date": due_date,
                    "score": score,
                    "weight": weight
                })
                st.success(f"Assignment '{name}' added.")

    st.subheader("Your Assignments")
    if st.session_state.assignments:
        st.table([{
            "Assignment": a["name"],
            "Description": a["description"],
            "Due Date": a["due_date"],
            "Score (%)": a["score"] if "score" in a else "Not Graded",
            "Weight (%)": a["weight"]
        } for a in st.session_state.assignments])
    else:
        st.info("No assignments added yet.")

    # Grading Existing Assignments
    st.subheader("Grade Student Assignments")
    student_name = st.text_input("Enter Student Name for Grading")
    assignment_to_grade = st.selectbox("Select Assignment to Grade", 
                                      [a["name"] for a in st.session_state.assignments])
    student_score = st.number_input("Enter Score (%)", min_value=0, max_value=100)

    grade_button = st.button("Grade Assignment")

    if grade_button:
        # Check if the student assignment exists, and if so, update the grade
        for assignment in st.session_state.assignments:
            if assignment["name"] == assignment_to_grade:
                assignment["score"] = student_score
                st.success(f"Assigned grade of {student_score}% for {student_name} on {assignment_to_grade}")

    if st.session_state.assignments:
        total_weight = sum(a["weight"] for a in st.session_state.assignments)
        if total_weight != 100:
            st.warning(f"Total weight is {total_weight}%. Final grade requires exactly 100%.")
        else:
            final_grade = sum(a["score"] * (a["weight"] / 100) for a in st.session_state.assignments if "score" in a)
            st.success(f"Final Grade: {final_grade:.2f}%")
