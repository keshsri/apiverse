import streamlit as st

def render_login():
    st.markdown("""
        <style>
        .main-header {
            text-align: center;
            padding: 2rem 0;
        }
        .feature-box {
            padding: 1rem;
            border-radius: 0.5rem;
            background-color: #f0f2f6;
            margin: 0.5rem 0;
        }
        </style>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown("<h1 class='main-header'>APIverse</h1>", unsafe_allow_html=True)
        st.markdown("<p style='text-align: center; color: #666;'>API Management Platform</p>", unsafe_allow_html=True)
        
        tab1, tab2 = st.tabs(["Login", "Register"])
        
        with tab1:
            render_login_form()
        
        with tab2:
            render_register_form()
        
        st.markdown("---")
        st.markdown("""
            <div class='feature-box'>
            <h4>Platform Features</h4>
            <ul>
                <li>Manage multiple APIs from one dashboard</li>
                <li>Secure API key generation and management</li>
                <li>Real-time analytics and monitoring</li>
                <li>Rate limiting and usage tracking</li>
                <li>Webhook integrations</li>
            </ul>
            </div>
        """, unsafe_allow_html=True)

def render_login_form():
    st.subheader("Login to Your Account")
    
    with st.form("login_form"):
        email = st.text_input("Email", placeholder="your@email.com")
        password = st.text_input("Password", type="password", placeholder="Enter your password")
        submit = st.form_submit_button("Login", use_container_width=True)
        
        if submit:
            if not email or not password:
                st.error("Please fill in all fields")
            else:
                try:
                    with st.spinner("Logging in..."):
                        result = st.session_state.client.login(email, password)
                        st.session_state.logged_in = True
                        st.session_state.user_email = email
                        st.success("Login successful")
                        st.rerun()
                except Exception as e:
                    st.error(f"Login failed: {str(e)}")

def render_register_form():
    st.subheader("Create New Account")
    
    with st.form("register_form"):
        reg_name = st.text_input("Full Name", placeholder="John Doe")
        reg_email = st.text_input("Email", placeholder="your@email.com", key="reg_email_input")
        reg_password = st.text_input("Password", type="password", placeholder="Choose a strong password", key="reg_password_input")
        reg_password_confirm = st.text_input("Confirm Password", type="password", placeholder="Re-enter password")
        submit_reg = st.form_submit_button("Register", use_container_width=True)
        
        if submit_reg:
            if not reg_name or not reg_email or not reg_password:
                st.error("Please fill in all fields")
            elif reg_password != reg_password_confirm:
                st.error("Passwords do not match")
            elif len(reg_password) < 8:
                st.error("Password must be at least 8 characters")
            else:
                try:
                    with st.spinner("Creating account..."):
                        st.session_state.client.register(reg_email, reg_password, reg_name)
                        st.success("Registration successful! Please login.")
                except Exception as e:
                    st.error(f"Registration failed: {str(e)}")
