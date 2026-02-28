import streamlit as st
import pandas as pd
import plotly.express as px

def render():
    st.title("Dashboard Overview")
    
    try:
        apis_data = st.session_state.client.list_apis()
        keys_data = st.session_state.client.list_api_keys()
        
        apis = apis_data.get("apis", [])
        keys = keys_data.get("api_keys", [])
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total APIs", len(apis))
        with col2:
            active_apis = len([a for a in apis if a.get("is_active")])
            st.metric("Active APIs", active_apis)
        with col3:
            active_keys = len([k for k in keys if not k.get("is_revoked")])
            st.metric("Active Keys", active_keys)
        with col4:
            revoked_keys = len([k for k in keys if k.get("is_revoked")])
            st.metric("Revoked Keys", revoked_keys)
        
        st.markdown("---")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Recent APIs")
            if apis:
                for api in apis[:5]:
                    status = "Active" if api.get("is_active") else "Inactive"
                    status_color = "green" if api.get("is_active") else "red"
                    st.markdown(f"**{api['name']}** - :{status_color}[{status}]")
                    st.caption(f"Created: {api['created_at'][:10]}")
            else:
                st.info("No APIs created yet")
        
        with col2:
            st.subheader("Recent API Keys")
            if keys:
                for key in keys[:5]:
                    status = "Revoked" if key.get("is_revoked") else "Active"
                    status_color = "red" if key.get("is_revoked") else "green"
                    st.markdown(f"**{key['name']}** ({key['environment']}) - :{status_color}[{status}]")
                    st.caption(f"Created: {key['created_at'][:10]}")
            else:
                st.info("No API keys created yet")
        
        st.markdown("---")
        
        st.subheader("Quick Actions")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("Create New API", use_container_width=True):
                st.session_state.page = "APIs"
                st.rerun()
        
        with col2:
            if st.button("Generate API Key", use_container_width=True):
                st.session_state.page = "API Keys"
                st.rerun()
        
        with col3:
            if st.button("View Analytics", use_container_width=True):
                st.session_state.page = "Analytics"
                st.rerun()
        
        if apis:
            st.markdown("---")
            st.subheader("API Status Overview")
            
            df_apis = pd.DataFrame(apis)
            if not df_apis.empty:
                fig = px.pie(
                    df_apis,
                    names='is_active',
                    title='API Status Distribution',
                    color='is_active',
                    color_discrete_map={True: 'green', False: 'red'}
                )
                fig.update_traces(labels=['Inactive', 'Active'])
                st.plotly_chart(fig, use_container_width=True)
        
    except Exception as e:
        st.error(f"Error loading dashboard: {str(e)}")
