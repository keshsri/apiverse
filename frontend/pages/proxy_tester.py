import streamlit as st
import json
import requests
from datetime import datetime

def render():
    st.title("API Proxy Tester")
    
    st.markdown("""
    Test your proxied APIs directly from the dashboard. Make requests through APIverse proxy
    and see the responses in real-time.
    """)
    
    try:
        apis_data = st.session_state.client.list_apis()
        apis = apis_data.get("apis", [])
        
        keys_data = st.session_state.client.list_api_keys()
        keys = [k for k in keys_data.get("api_keys", []) if not k.get("is_revoked")]
        
        if not apis:
            st.warning("No APIs found. Create an API first.")
            return
        
        if not keys:
            st.warning("No active API keys found. Generate an API key first.")
            return
        
        col1, col2 = st.columns(2)
        
        with col1:
            api_options = {f"{api['name']} (ID: {api['id']})": api['id'] for api in apis if api.get('is_active')}
            if not api_options:
                st.error("No active APIs found. Activate an API first.")
                return
            
            selected_api = st.selectbox("Select API", list(api_options.keys()))
            api_id = api_options[selected_api]
        
        with col2:
            key_options = {f"{key['name']} ({key['key_prefix']}...)": key['key_prefix'] for key in keys}
            selected_key_name = st.selectbox("Select API Key", list(key_options.keys()))
            selected_key = key_options[selected_key_name]
        
        st.markdown("---")
        
        col1, col2 = st.columns([1, 3])
        
        with col1:
            method = st.selectbox("Method", ["GET", "POST", "PUT", "DELETE", "PATCH"])
        
        with col2:
            path = st.text_input("Endpoint Path", placeholder="users/1", help="Path after the base URL")
        
        if method in ["POST", "PUT", "PATCH"]:
            body = st.text_area("Request Body (JSON)", placeholder='{"key": "value"}', height=150)
        else:
            body = None
        
        headers = st.text_area("Custom Headers (JSON)", placeholder='{"Custom-Header": "value"}', height=100)
        
        if st.button("Send Request", type="primary", use_container_width=True):
            if not path:
                st.error("Endpoint path is required")
            else:
                send_request(api_id, path, method, selected_key, body, headers)
    
    except Exception as e:
        st.error(f"Error: {str(e)}")

def send_request(api_id, path, method, api_key, body, headers):
    try:
        proxy_url = f"{st.session_state.client.base_url}/proxy/{api_id}/{path}"
        
        request_headers = {"X-API-Key": api_key}
        if headers:
            try:
                custom_headers = json.loads(headers)
                request_headers.update(custom_headers)
            except:
                st.warning("Invalid headers JSON, using default headers only")
        
        request_body = None
        if body:
            try:
                request_body = json.loads(body)
            except:
                st.error("Invalid JSON body")
                return
        
        with st.spinner("Sending request..."):
            start_time = datetime.now()
            
            response = requests.request(
                method=method,
                url=proxy_url,
                headers=request_headers,
                json=request_body,
                timeout=30
            )
            
            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds() * 1000
        
        st.markdown("---")
        st.subheader("Response")
        
        col1, col2, col3 = st.columns(3)
        with col1:
            status_color = "green" if response.status_code < 400 else "red"
            st.metric("Status Code", response.status_code)
        with col2:
            st.metric("Response Time", f"{duration:.2f} ms")
        with col3:
            st.metric("Size", f"{len(response.content)} bytes")
        
        st.markdown("**Response Headers**")
        headers_dict = dict(response.headers)
        
        rate_limit_headers = {k: v for k, v in headers_dict.items() if 'ratelimit' in k.lower()}
        if rate_limit_headers:
            st.info("Rate Limit Information")
            for key, value in rate_limit_headers.items():
                st.caption(f"{key}: {value}")
        
        with st.expander("All Headers", expanded=False):
            st.json(headers_dict)
        
        st.markdown("**Response Body**")
        try:
            response_json = response.json()
            st.json(response_json)
        except:
            st.code(response.text)
        
        if response.status_code >= 400:
            st.error(f"Request failed with status {response.status_code}")
        else:
            st.success("Request completed successfully")
        
    except requests.exceptions.Timeout:
        st.error("Request timed out after 30 seconds")
    except requests.exceptions.ConnectionError:
        st.error("Failed to connect to the API. Check your network connection.")
    except Exception as e:
        st.error(f"Request failed: {str(e)}")
