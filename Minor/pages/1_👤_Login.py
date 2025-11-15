"""
Dedicated Login/Signup Page (Optional)
Note: Login is already in the sidebar of app.py
This is an alternative full-page login experience
"""

import streamlit as st
from utils.auth import verify_user, create_user

st.set_page_config(
    page_title="Login - College AI Portal",
    page_icon="🔐",
    layout="centered"
)

# Custom CSS
st.markdown("""
<style>
    .login-container {
        max-width: 500px;
        margin: 0 auto;
        padding: 2rem;
        border-radius: 15px;
        background: white;
        box-shadow: 0 10px 30px rgba(0,0,0,0.1);
    }
    .stButton>button {
        width: 100%;
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        padding: 0.75rem 1rem;
        font-size: 1.1rem;
        border-radius: 8px;
        cursor: pointer;
        transition: all 0.3s;
    }
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 5px 15px rgba(102, 126, 234, 0.4);
    }
</style>
""", unsafe_allow_html=True)

# If already logged in, redirect
if st.session_state.get('authenticated', False):
    st.success(f"✅ Already logged in as {st.session_state.username}")
    
    role = st.session_state.user_role
    if role == "admin":
        st.info("Navigate to Admin Dashboard →")
        if st.button("📊 Go to Admin Dashboard"):
            st.switch_page("pages/2_👨‍💼_Admin_Dashboard.py")
    elif role == "faculty":
        st.info("Navigate to Faculty Portal →")
        if st.button("📚 Go to Faculty Portal"):
            st.switch_page("pages/3_👨‍🏫_Faculty_Portal.py")
    else:
        st.info("Navigate to Student Portal →")
        if st.button("🤖 Go to Student Portal"):
            st.switch_page("pages/4_👨‍🎓_Student_Portal.py")
    
    if st.button("🚪 Logout"):
        st.session_state.authenticated = False
        st.session_state.user_role = None
        st.session_state.username = None
        st.session_state.user_id = None
        st.rerun()
    
    st.stop()

# Login/Signup interface
st.markdown("""
<div style="text-align: center; margin-bottom: 2rem;">
    <h1 style="background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
               -webkit-background-clip: text;
               -webkit-text-fill-color: transparent;">
        🎓 College AI Portal
    </h1>
    <p style="font-size: 1.2rem; color: #666;">Welcome back! Please login to continue.</p>
</div>
""", unsafe_allow_html=True)

tab1, tab2 = st.tabs(["🔐 Login", "📝 Sign Up"])

with tab1:
    st.markdown("### Login to Your Account")
    
    with st.form("login_form", clear_on_submit=False):
        username = st.text_input(
            "Username",
            placeholder="Enter your username",
            key="login_username"
        )
        password = st.text_input(
            "Password",
            type="password",
            placeholder="Enter your password",
            key="login_password"
        )
        
        col1, col2 = st.columns([1, 1])
        with col1:
            remember = st.checkbox("Remember me")
        with col2:
            st.markdown("<div style='text-align: right;'><a href='#'>Forgot password?</a></div>", 
                       unsafe_allow_html=True)
        
        submit = st.form_submit_button("🚀 Login", use_container_width=True)
        
        if submit:
            if not username or not password:
                st.error("❌ Please fill in all fields")
            else:
                with st.spinner("🔍 Verifying credentials..."):
                    user = verify_user(username, password)
                    
                    if user:
                        st.session_state.authenticated = True
                        st.session_state.username = user['username']
                        st.session_state.user_role = user['role']
                        st.session_state.user_id = user['id']
                        
                        st.success(f"✅ Welcome back, {username}!")
                        st.balloons()
                        
                        # Redirect based on role
                        if user['role'] == 'admin':
                            st.info("Redirecting to Admin Dashboard...")
                            st.switch_page("pages/2_👨‍💼_Admin_Dashboard.py")
                        elif user['role'] == 'faculty':
                            st.info("Redirecting to Faculty Portal...")
                            st.switch_page("pages/3_👨‍🏫_Faculty_Portal.py")
                        else:
                            st.info("Redirecting to Student Portal...")
                            st.switch_page("pages/4_👨‍🎓_Student_Portal.py")
                    else:
                        st.error("❌ Invalid username or password")

with tab2:
    st.markdown("### Create New Account")
    
    with st.form("signup_form", clear_on_submit=False):
        new_username = st.text_input(
            "Username",
            placeholder="Choose a username",
            key="signup_username"
        )
        new_email = st.text_input(
            "Email",
            placeholder="your.email@example.com",
            key="signup_email"
        )
        new_password = st.text_input(
            "Password",
            type="password",
            placeholder="Choose a strong password",
            key="signup_password"
        )
        confirm_password = st.text_input(
            "Confirm Password",
            type="password",
            placeholder="Re-enter your password",
            key="signup_confirm"
        )
        new_role = st.selectbox(
            "I am a:",
            ["student", "faculty"],
            format_func=lambda x: "🎓 Student" if x == "student" else "👨‍🏫 Faculty"
        )
        
        agree = st.checkbox("I agree to the Terms of Service and Privacy Policy")
        
        submit = st.form_submit_button("✨ Create Account", use_container_width=True)
        
        if submit:
            if not all([new_username, new_email, new_password, confirm_password]):
                st.error("❌ Please fill in all fields")
            elif not agree:
                st.warning("⚠️ Please accept the terms to continue")
            elif new_password != confirm_password:
                st.error("❌ Passwords don't match")
            elif len(new_password) < 6:
                st.error("❌ Password must be at least 6 characters")
            elif "@" not in new_email:
                st.error("❌ Please enter a valid email")
            else:
                with st.spinner("🔨 Creating your account..."):
                    success = create_user(new_username, new_password, new_role, new_email)
                    
                    if success:
                        st.success("✅ Account created successfully!")
                        st.balloons()
                        st.info("👈 Please switch to the Login tab to sign in")
                    else:
                        st.error("❌ Username already exists. Please choose a different one.")

# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #666; padding: 1rem;">
    <p>🎓 College AI Portal v1.0</p>
    <p>Powered by AI | Built with ❤️</p>
</div>
""", unsafe_allow_html=True)