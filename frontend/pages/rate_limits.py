import streamlit as st

def render():
    st.title("Rate Limits Management")
    
    try:
        apis_data = st.session_state.client.list_apis()
        apis = apis_data.get("apis", [])
        
        if not apis:
            st.info("No APIs found. Create an API first.")
            return
        
        api_options = {f"{api['name']} (ID: {api['id']})": api['id'] for api in apis}
        selected_api = st.selectbox("Select API", list(api_options.keys()))
        api_id = api_options[selected_api]
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Current Rate Limit")
            try:
                rate_limit = st.session_state.client.get_rate_limit(api_id)
                st.metric("Tier", rate_limit['tier'])
                st.metric("Requests per Hour", rate_limit['requests_per_hour'])
                st.metric("Requests per Day", rate_limit['requests_per_day'])
            except Exception as e:
                st.info("No rate limit configured for this API")
        
        with col2:
            st.subheader("Update Rate Limit")
            
            with st.form("rate_limit_form"):
                tier = st.selectbox("Tier", ["standard", "premium", "enterprise"])
                requests_per_hour = st.number_input("Requests per Hour", min_value=1, value=1000)
                requests_per_day = st.number_input("Requests per Day", min_value=1, value=10000)
                
                submit = st.form_submit_button("Update Rate Limit", use_container_width=True)
                
                if submit:
                    try:
                        st.session_state.client.create_rate_limit(api_id, tier, requests_per_hour, requests_per_day)
                        st.success("Rate limit updated successfully")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Error: {str(e)}")
        
        st.markdown("---")
        st.subheader("Rate Limit Tiers")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown("**Standard**")
            st.caption("1,000 requests/hour")
            st.caption("10,000 requests/day")
        
        with col2:
            st.markdown("**Premium**")
            st.caption("5,000 requests/hour")
            st.caption("50,000 requests/day")
        
        with col3:
            st.markdown("**Enterprise**")
            st.caption("10,000 requests/hour")
            st.caption("100,000 requests/day")
        
    except Exception as e:
        st.error(f"Error: {str(e)}")
