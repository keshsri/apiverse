import streamlit as st
from api_client import APIClient
from pages import auth, dashboard, apis, api_keys, rate_limits, analytics, webhooks, proxy_tester

st.set_page_config(
    page_title="APIverse Dashboard",
    layout="wide",
    initial_sidebar_state="expanded"
)

if "client" not in st.session_state:
    st.session_state.client = APIClient()

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "selected_api_id" not in st.session_state:
    st.session_state.selected_api_id = None

def render_sidebar():
    st.sidebar.title("APIverse")
    st.sidebar.markdown(f"**User:** {st.session_state.user_email}")
    
    page = st.sidebar.radio(
        "Navigation",
        ["Dashboard", "APIs", "API Keys", "Rate Limits", "Analytics", "Webhooks", "Proxy Tester"],
        label_visibility="collapsed"
    )
    
    st.sidebar.markdown("---")
    
    if st.sidebar.button("Logout", use_container_width=True):
        st.session_state.logged_in = False
        st.session_state.client.token = None
        st.session_state.selected_api_id = None
        st.rerun()
    
    st.sidebar.markdown("---")
    st.sidebar.markdown("**Quick Stats**")
    try:
        apis_data = st.session_state.client.list_apis()
        keys_data = st.session_state.client.list_api_keys()
        st.sidebar.metric("Total APIs", apis_data.get("total", 0))
        st.sidebar.metric("Active Keys", len([k for k in keys_data.get("api_keys", []) if not k.get("is_revoked")]))
    except:
        pass
    
    return page

def main():
    if not st.session_state.logged_in:
        auth.render_login()
    else:
        page = render_sidebar()
        
        if page == "Dashboard":
            dashboard.render()
        elif page == "APIs":
            apis.render()
        elif page == "API Keys":
            api_keys.render()
        elif page == "Rate Limits":
            rate_limits.render()
        elif page == "Analytics":
            analytics.render()
        elif page == "Webhooks":
            webhooks.render()
        elif page == "Proxy Tester":
            proxy_tester.render()

if __name__ == "__main__":
    main()
