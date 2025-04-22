import streamlit as st

# Page setup
st.set_page_config(layout="wide", page_title="Assignments")

# Header
st.markdown("<h1 style='color: #7F27FF;'>Assignments</h1>", unsafe_allow_html=True)

# Home button
st.markdown(
    "<div style='text-align: right;'>"
    "<a href='Home.py'>"
    "<button style='padding: 0.5rem 1rem; font-size: 1rem; background-color: #9C4DFF; color: white; border: none; border-radius: 6px; cursor: pointer;'>🏠 Home</button>"
    "</a>"
    "</div>",
    unsafe_allow_html=True
)

st.markdown("---")

# Due Dates Section
st.markdown("##Due Dates")
with st.expander("View assignment due dates"):
    st.dataframe({
        "Assignment": [],
        "Due Date": []
    })

# Grading Rubric Section
st.markdown("## Grading Rubric")
with st.expander("View grading criteria"):
    st.dataframe({
        "Assignment": [],
        "Points Possible": [],
        "Weight (%)": []
    })

# Grade Input Section
st.markdown("## Final Grade Calculator")

with st.form("grade_calculator"):
    st.markdown("### Enter assignment grades:")

    num_assignments = st.number_input("Number of Assignments", min_value=1, max_value=20, value=3)
    assignment_scores = []
    total_weight = 0

    for i in range(int(num_assignments)):
        col1, col2, col3 = st.columns(3)
        with col1:
            name = st.text_input(f"Assignment {i+1} Name", key=f"name_{i}")
        with col2:
            score = st.number_input(f"Score (%) for {name or f'Assignment {i+1}'}", min_value=0.0, max_value=100.0, key=f"score_{i}")
        with col3:
            weight = st.number_input(f"Weight (%)", min_value=0.0, max_value=100.0, key=f"weight_{i}")

        assignment_scores.append((score, weight))
        total_weight += weight

    submitted = st.form_submit_button("Calculate Final Grade")

    if submitted:
        if total_weight != 100:
            st.error("Total weight must equal 100%.")
        else:
            final_grade = sum(score * (weight / 100) for score, weight in assignment_scores)
            st.success(f"Final Grade: {final_grade:.2f}%")

st.markdown("---")
