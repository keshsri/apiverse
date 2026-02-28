import streamlit as st
import pandas as pd

def render():
    st.title("Webhooks Management")
    
    try:
        apis_data = st.session_state.client.list_apis()
        apis = apis_data.get("apis", [])
        
        if not apis:
            st.info("No APIs found. Create an API first.")
            return
        
        api_options = {f"{api['name']} (ID: {api['id']})": api['id'] for api in apis}
        selected_api = st.selectbox("Select API", list(api_options.keys()))
        api_id = api_options[selected_api]
        
        tab1, tab2 = st.tabs(["Subscriptions", "Create Subscription"])
        
        with tab1:
            render_subscriptions(api_id)
        
        with tab2:
            render_create_subscription(api_id)
    
    except Exception as e:
        st.error(f"Error: {str(e)}")

def render_subscriptions(api_id):
    st.subheader("Webhook Subscriptions")
    
    try:
        subscriptions = st.session_state.client.list_webhook_subscriptions(api_id)
        
        if subscriptions:
            for sub in subscriptions:
                status_color = "green" if sub['is_active'] else "red"
                status_text = "Active" if sub['is_active'] else "Inactive"
                
                with st.expander(f"{sub['event_type']} - :{status_color}[{status_text}]"):
                    col1, col2 = st.columns([2, 1])
                    
                    with col1:
                        st.markdown(f"**ID:** {sub['id']}")
                        st.markdown(f"**Event Type:** {sub['event_type']}")
                        st.markdown(f"**Callback URL:** `{sub['callback_url']}`")
                        st.markdown(f"**Created:** {sub['created_at']}")
                        st.markdown(f"**Updated:** {sub['updated_at']}")
                    
                    with col2:
                        if st.button("Delete", key=f"delete_sub_{sub['id']}", type="secondary", use_container_width=True):
                            if st.session_state.get(f"confirm_delete_sub_{sub['id']}", False):
                                try:
                                    st.session_state.client.delete_webhook_subscription(sub['id'])
                                    st.success("Subscription deleted successfully")
                                    st.rerun()
                                except Exception as e:
                                    st.error(f"Error: {str(e)}")
                            else:
                                st.session_state[f"confirm_delete_sub_{sub['id']}"] = True
                                st.warning("Click again to confirm")
                    
                    st.markdown("---")
                    st.markdown("**Recent Deliveries**")
                    
                    if st.button("Load Deliveries", key=f"load_deliveries_{sub['id']}"):
                        try:
                            deliveries = st.session_state.client.get_webhook_deliveries(sub['id'], limit=20)
                            if deliveries:
                                df = pd.DataFrame(deliveries)
                                st.dataframe(
                                    df[['event_type', 'status', 'response_code', 'attempt_count', 'created_at']],
                                    use_container_width=True,
                                    hide_index=True
                                )
                                
                                success_count = len([d for d in deliveries if d['status'] == 'delivered'])
                                failed_count = len([d for d in deliveries if d['status'] == 'failed'])
                                
                                col1, col2 = st.columns(2)
                                with col1:
                                    st.metric("Successful Deliveries", success_count)
                                with col2:
                                    st.metric("Failed Deliveries", failed_count)
                            else:
                                st.info("No deliveries yet")
                        except Exception as e:
                            st.error(f"Error loading deliveries: {str(e)}")
        else:
            st.info("No webhook subscriptions found. Create one in the 'Create Subscription' tab.")
    except Exception as e:
        st.error(f"Error loading subscriptions: {str(e)}")

def render_create_subscription(api_id):
    st.subheader("Create Webhook Subscription")
    
    st.markdown("""
    Webhooks allow you to receive real-time notifications when events occur in your API.
    Configure a callback URL to receive HTTP POST requests with event data.
    """)
    
    with st.form("create_webhook_form"):
        event_type = st.selectbox("Event Type", [
            "api.request",
            "api.error",
            "api.rate_limit",
            "api.key.created",
            "api.key.revoked"
        ])
        
        st.markdown("**Event Descriptions:**")
        st.caption("- api.request: Triggered on every API request")
        st.caption("- api.error: Triggered when API returns 4xx or 5xx status")
        st.caption("- api.rate_limit: Triggered when rate limit is exceeded")
        st.caption("- api.key.created: Triggered when new API key is created")
        st.caption("- api.key.revoked: Triggered when API key is revoked")
        
        callback_url = st.text_input("Callback URL", placeholder="https://your-domain.com/webhook")
        secret = st.text_input("Secret (optional)", type="password", help="Used for HMAC signature verification")
        
        submit = st.form_submit_button("Create Subscription", use_container_width=True)
        
        if submit:
            if not callback_url:
                st.error("Callback URL is required")
            else:
                try:
                    st.session_state.client.create_webhook_subscription(
                        api_id,
                        event_type,
                        callback_url,
                        secret if secret else None
                    )
                    st.success("Webhook subscription created successfully")
                    st.rerun()
                except Exception as e:
                    st.error(f"Error: {str(e)}")
    
    st.markdown("---")
    st.subheader("Webhook Payload Example")
    
    st.json({
        "event_type": "api.request",
        "api_id": 1,
        "payload": {
            "endpoint": "/users/1",
            "method": "GET",
            "status_code": 200,
            "response_time_ms": 45.2
        },
        "timestamp": "2024-01-01T12:00:00Z"
    })
