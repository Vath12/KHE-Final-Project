import streamlit as st

def error_page():
    st.set_page_config(page_title="Error", layout="centered")
    
    # Custom CSS for the error page
    st.markdown("""
    <style>
        .error-container {
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            padding: 4rem 2rem;
            text-align: center;
            background-color: #f8f9fa;
            border-radius: 15px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            margin: 2rem auto;
            max-width: 600px;
        }
        .error-icon {
            font-size: 6rem;
            color: #e74c3c;
            margin-bottom: 1rem;
        }
        .error-title {
            font-size: 2rem;
            font-weight: bold;
            color: #333;
            margin-bottom: 1rem;
        }
        .error-message {
            font-size: 1.1rem;
            color: #555;
            margin-bottom: 2rem;
        }
        .home-button {
            background-color: #3498db;
            color: white;
            padding: 0.5rem 1.5rem;
            border-radius: 5px;
            text-decoration: none;
            font-weight: bold;
            transition: background-color 0.3s;
        }
        .home-button:hover {
            background-color: #2980b9;
        }
    </style>
    """, unsafe_allow_html=True)
    
    # Error content
    st.markdown("""
    <div class="error-container">
        <div class="error-title">Oops, something went wrong</div>
        <div class="error-message">
            We encountered an error while processing your request. 
            Please try again later or contact support if the problem persists.
        </div>
        <a href="/" class="home-button">Return to Home</a>
    </div>
    """, unsafe_allow_html=True)
    
    # Alternative button for Streamlit navigation
    st.markdown("<br><br>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("Return to Home", use_container_width=True):
            st.switch_page("pages/home.py")

if __name__ == "__main__":
    error_page()