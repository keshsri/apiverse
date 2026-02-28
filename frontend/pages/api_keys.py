import streamlit as st

def render():
    st.title("API Keys Management")
    
    tab1, tab2 = st.tabs(["My API Keys", "Generate New Key"])
    
    with tab1:
        render_key_list()
    
    with tab2:
        render_create_key()

def render_key_list():
    try:
        keys_data = st.session_state.client.list_api_keys()
        keys = keys_data.get("api_keys", [])
        
        if keys:
            active_keys = [k for k in keys if not k.get("is_revoked")]
            revoked_keys = [k for k in keys if k.get("is_revoked")]
            
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Active Keys", len(active_keys))
            with col2:
                st.metric("Revoked Keys", len(revoked_keys))
            
            st.markdown("---")
            
            filter_option = st.radio("Filter", ["All", "Active", "Revoked"], horizontal=True)
            
            if filter_option == "Active":
                display_keys = active_keys
            elif filter_option == "Revoked":
                display_keys = revoked_keys
            else:
                display_keys = keys
            
            for key in display_keys:
                is_revoked = key.get('is_revoked', False)
                status_color = "red" if is_revoked else "green"
                status_text = "Revoked" if is_revoked else "Active"
                
                with st.expander(f"{key['name']} - {key['environment']} - :{status_color}[{status_text}]"):
                    col1, col2 = st.columns([2, 1])
                    
                    with col1:
                        st.markdown(f"**ID:** {key['id']}")
                        st.markdown(f"**Prefix:** `{key['key_prefix']}`")
                        st.markdown(f"**Environment:** {key['environment']}")
                        st.markdown(f"**Created:** {key['created_at']}")
                        
                        if key.get('expires_at'):
                            st.markdown(f"**Expires:** {key['expires_at']}")
                        else:
                            st.markdown("**Expires:** Never")
                        
                        if key.get('last_used_at'):
                            st.markdown(f"**Last Used:** {key['last_used_at']}")
                        else:
                            st.markdown("**Last Used:** Never")
                    
                    with col2:
                        if not is_revoked:
                            if st.button("Revoke Key", key=f"revoke_{key['id']}", type="secondary", use_container_width=True):
                                if st.session_state.get(f"confirm_revoke_{key['id']}", False):
                                    try:
                                        st.session_state.client.revoke_api_key(key['id'])
                                        st.success("API key revoked successfully")
                                        st.rerun()
                                    except Exception as e:
                                        st.error(f"Error: {str(e)}")
                                else:
                                    st.session_state[f"confirm_revoke_{key['id']}"] = True
                                    st.warning("Click again to confirm")
        else:
            st.info("No API keys found. Generate your first API key in the 'Generate New Key' tab.")
    except Exception as e:
        st.error(f"Error loading API keys: {str(e)}")

def render_create_key():
    st.subheader("Generate New API Key")
    
    with st.form("create_key_form"):
        key_name = st.text_input("Key Name", placeholder="Production Key")
        environment = st.selectbox("Environment", ["development", "production"])
        
        st.markdown("**Expiration**")
        expiration_option = st.radio("Expires", ["Never", "Custom"], horizontal=True)
        
        expires_in_days = None
        if expiration_option == "Custom":
            expires_in_days = st.number_input("Days until expiration", min_value=1, max_value=365, value=30)
        
        submit = st.form_submit_button("Generate API Key", use_container_width=True)
        
        if submit:
            if not key_name:
                st.error("Key name is required")
            else:
                try:
                    result = st.session_state.client.create_api_key(
                        key_name,
                        environment,
                        expires_in_days if expiration_option == "Custom" else None
                    )
                    st.success("API key generated successfully")
                    
                    st.markdown("---")
                    st.markdown("**Your API Key**")
                    st.code(result['api_key'], language=None)
                    st.warning("Save this key now. You won't be able to see it again!")
                    
                    st.markdown("**Key Details**")
                    st.json({
                        "id": result['id'],
                        "prefix": result['key_prefix'],
                        "name": result['name'],
                        "environment": result['environment'],
                        "created_at": result['created_at'],
                        "expires_at": result.get('expires_at', 'Never')
                    })
                except Exception as e:
                    st.error(f"Error: {str(e)}")
