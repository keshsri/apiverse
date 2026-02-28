import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

def render():
    st.title("Analytics Dashboard")
    
    try:
        apis_data = st.session_state.client.list_apis()
        apis = apis_data.get("apis", [])
        
        if not apis:
            st.info("No APIs found. Create an API first.")
            return
        
        api_options = {f"{api['name']} (ID: {api['id']})": api['id'] for api in apis}
        
        if st.session_state.get('selected_api_id'):
            default_api = next((k for k, v in api_options.items() if v == st.session_state.selected_api_id), list(api_options.keys())[0])
        else:
            default_api = list(api_options.keys())[0]
        
        selected_api = st.selectbox("Select API", list(api_options.keys()), index=list(api_options.keys()).index(default_api))
        api_id = api_options[selected_api]
        
        try:
            usage_stats = st.session_state.client.get_usage_stats(api_id)
            
            st.subheader("Usage Overview")
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Total Requests", usage_stats['total_requests'])
            with col2:
                st.metric("Successful", usage_stats['successful_requests'])
            with col3:
                st.metric("Failed", usage_stats['failed_requests'])
            with col4:
                st.metric("Avg Response Time", f"{usage_stats['avg_response_time_ms']:.2f} ms")
            
            if usage_stats['total_requests'] > 0:
                success_rate = (usage_stats['successful_requests'] / usage_stats['total_requests']) * 100
                st.progress(success_rate / 100)
                st.caption(f"Success Rate: {success_rate:.1f}%")
            
            st.markdown("---")
            
            st.subheader("Top Endpoints")
            try:
                endpoint_stats = st.session_state.client.get_endpoint_stats(api_id, limit=10)
                if endpoint_stats:
                    df = pd.DataFrame(endpoint_stats)
                    
                    st.dataframe(
                        df[['endpoint', 'method', 'request_count', 'avg_response_time_ms', 'success_rate']],
                        use_container_width=True,
                        hide_index=True
                    )
                    
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        fig = px.bar(
                            df,
                            x='endpoint',
                            y='request_count',
                            color='method',
                            title='Requests by Endpoint',
                            labels={'request_count': 'Request Count', 'endpoint': 'Endpoint'}
                        )
                        st.plotly_chart(fig, use_container_width=True)
                    
                    with col2:
                        fig = px.bar(
                            df,
                            x='endpoint',
                            y='avg_response_time_ms',
                            color='method',
                            title='Average Response Time by Endpoint',
                            labels={'avg_response_time_ms': 'Avg Response Time (ms)', 'endpoint': 'Endpoint'}
                        )
                        st.plotly_chart(fig, use_container_width=True)
                else:
                    st.info("No endpoint data available")
            except Exception as e:
                st.info("No endpoint statistics available")
            
            st.markdown("---")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.subheader("Error Distribution")
                try:
                    error_stats = st.session_state.client.get_error_stats(api_id)
                    if error_stats:
                        df_errors = pd.DataFrame(error_stats)
                        fig = px.pie(
                            df_errors,
                            values='error_count',
                            names='status_code',
                            title='Errors by Status Code',
                            hover_data=['percentage']
                        )
                        st.plotly_chart(fig, use_container_width=True)
                        
                        st.dataframe(
                            df_errors[['status_code', 'error_count', 'percentage', 'sample_endpoint']],
                            use_container_width=True,
                            hide_index=True
                        )
                    else:
                        st.info("No errors recorded")
                except Exception as e:
                    st.info("No error statistics available")
            
            with col2:
                st.subheader("Performance Metrics")
                try:
                    perf_stats = st.session_state.client.get_performance_stats(api_id)
                    
                    st.metric("Min Response Time", f"{perf_stats['min_response_time_ms']:.2f} ms")
                    st.metric("Avg Response Time", f"{perf_stats['avg_response_time_ms']:.2f} ms")
                    st.metric("Max Response Time", f"{perf_stats['max_response_time_ms']:.2f} ms")
                    
                    fig = go.Figure()
                    fig.add_trace(go.Bar(
                        x=['Min', 'Avg', 'Max'],
                        y=[
                            perf_stats['min_response_time_ms'],
                            perf_stats['avg_response_time_ms'],
                            perf_stats['max_response_time_ms']
                        ],
                        marker_color=['green', 'blue', 'red']
                    ))
                    fig.update_layout(
                        title='Response Time Distribution',
                        yaxis_title='Time (ms)',
                        showlegend=False
                    )
                    st.plotly_chart(fig, use_container_width=True)
                except Exception as e:
                    st.info("No performance data available")
                
        except Exception as e:
            st.info("No analytics data available for this API. Make some requests through the proxy to see analytics.")
    except Exception as e:
        st.error(f"Error: {str(e)}")
