import streamlit as st

def render():
    st.title("API Management")
    
    tab1, tab2 = st.tabs(["My APIs", "Create New API"])
    
    with tab1:
        render_api_list()
    
    with tab2:
        render_create_api()

def render_api_list():
    try:
        apis_data = st.session_state.client.list_apis()
        apis = apis_data.get("apis", [])
        
        if apis:
            search = st.text_input("Search APIs", placeholder="Search by name...")
            
            filtered_apis = apis
            if search:
                filtered_apis = [a for a in apis if search.lower() in a['name'].lower()]
            
            st.markdown(f"**Total APIs:** {len(filtered_apis)}")
            
            for api in filtered_apis:
                with st.expander(f"{api['name']} - {'Active' if api['is_active'] else 'Inactive'}", expanded=False):
                    col1, col2 = st.columns([2, 1])
                    
                    with col1:
                        st.markdown(f"**ID:** {api['id']}")
                        st.markdown(f"**Base URL:** `{api['base_url']}`")
                        st.markdown(f"**Description:** {api.get('description', 'N/A')}")
                        st.markdown(f"**Auth Type:** {api.get('auth_type', 'none')}")
                        st.markdown(f"**Created:** {api['created_at']}")
                        st.markdown(f"**Updated:** {api['updated_at']}")
                    
                    with col2:
                        status_color = "green" if api['is_active'] else "red"
                        st.markdown(f"**Status:** :{status_color}[{'Active' if api['is_active'] else 'Inactive'}]")
                    
                    st.markdown("---")
                    
                    col_a, col_b, col_c = st.columns(3)
                    
                    with col_a:
                        new_status = not api['is_active']
                        button_text = "Deactivate" if api['is_active'] else "Activate"
                        if st.button(button_text, key=f"toggle_{api['id']}", use_container_width=True):
                            try:
                                st.session_state.client.update_api(api['id'], is_active=new_status)
                                st.success(f"API {button_text.lower()}d successfully")
                                st.rerun()
                            except Exception as e:
                                st.error(f"Error: {str(e)}")
                    
                    with col_b:
                        if st.button("View Analytics", key=f"analytics_{api['id']}", use_container_width=True):
                            st.session_state.selected_api_id = api['id']
                            st.session_state.page = "Analytics"
                            st.rerun()
                    
                    with col_c:
                        if st.button("Delete", key=f"delete_{api['id']}", type="secondary", use_container_width=True):
                            if st.session_state.get(f"confirm_delete_{api['id']}", False):
                                try:
                                    st.session_state.client.delete_api(api['id'])
                                    st.success("API deleted successfully")
                                    st.rerun()
                                except Exception as e:
                                    st.error(f"Error: {str(e)}")
                            else:
                                st.session_state[f"confirm_delete_{api['id']}"] = True
                                st.warning("Click again to confirm deletion")
                    
                    with st.form(f"edit_form_{api['id']}"):
                        st.markdown("**Edit API**")
                        new_name = st.text_input("Name", value=api['name'], key=f"name_{api['id']}")
                        new_base_url = st.text_input("Base URL", value=api['base_url'], key=f"url_{api['id']}")
                        new_description = st.text_area("Description", value=api.get('description', ''), key=f"desc_{api['id']}")
                        
                        if st.form_submit_button("Update API"):
                            try:
                                st.session_state.client.update_api(
                                    api['id'],
                                    name=new_name,
                                    base_url=new_base_url,
                                    description=new_description
                                )
                                st.success("API updated successfully")
                                st.rerun()
                            except Exception as e:
                                st.error(f"Error: {str(e)}")
        else:
            st.info("No APIs found. Create your first API in the 'Create New API' tab.")
    except Exception as e:
        st.error(f"Error loading APIs: {str(e)}")

def render_create_api():
    st.subheader("Create New API")
    
    with st.form("create_api_form"):
        name = st.text_input("API Name", placeholder="My Awesome API")
        base_url = st.text_input("Base URL", placeholder="https://api.example.com")
        description = st.text_area("Description", placeholder="Describe your API...")
        
        auth_type = st.selectbox("Authentication Type", ["none", "bearer", "api_key", "basic"])
        
        auth_config = None
        if auth_type == "bearer":
            st.markdown("**Bearer Token Configuration**")
            token = st.text_input("Token", type="password")
            if token:
                auth_config = {"token": token}
        
        elif auth_type == "api_key":
            st.markdown("**API Key Configuration**")
            key_name = st.text_input("Header Name", value="X-API-Key")
            key_value = st.text_input("Key Value", type="password")
            if key_name and key_value:
                auth_config = {"key_name": key_name, "key_value": key_value}
        
        elif auth_type == "basic":
            st.markdown("**Basic Auth Configuration**")
            username = st.text_input("Username")
            password = st.text_input("Password", type="password")
            if username and password:
                auth_config = {"username": username, "password": password}
        
        submit = st.form_submit_button("Create API", use_container_width=True)
        
        if submit:
            if not name or not base_url:
                st.error("Name and Base URL are required")
            else:
                try:
                    st.session_state.client.create_api(
                        name=name,
                        base_url=base_url,
                        description=description,
                        auth_type=auth_type,
                        auth_config=auth_config
                    )
                    st.success("API created successfully")
                    st.rerun()
                except Exception as e:
                    st.error(f"Error: {str(e)}")
