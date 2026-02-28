# APIverse Frontend

Streamlit-based dashboard for APIverse API Management Platform.

## Project Structure

```
frontend/
├── app.py                 # Main application entry point
├── api_client.py          # API client wrapper
├── config.py              # Configuration management
├── pages/                 # Page modules
│   ├── __init__.py
│   ├── auth.py           # Login/Register
│   ├── dashboard.py      # Overview dashboard
│   ├── apis.py           # API management
│   ├── api_keys.py       # API keys management
│   ├── rate_limits.py    # Rate limits configuration
│   ├── analytics.py      # Analytics dashboard
│   ├── webhooks.py       # Webhooks management
│   └── proxy_tester.py   # API proxy tester
├── requirements.txt
├── .env.example
└── README.md
```

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Configure environment:
```bash
cp .env.example .env
```

Edit `.env` and set your API base URL:
- Local: `API_BASE_URL=http://localhost:8000`
- Cloud: `API_BASE_URL=https://your-api-gateway-url.amazonaws.com/dev`

3. Run the application:
```bash
streamlit run app.py
```

## Features

- User Authentication (Login/Register)
- API Management (Create, List, Update, Delete)
- API Keys Management (Create, List, Revoke)
- Rate Limits Configuration
- Analytics Dashboard (Usage, Endpoints, Errors, Performance)
- Webhooks Management (Subscriptions, Deliveries)
- Proxy Tester (Test APIs directly)

## Usage

1. Register a new account or login
2. Create APIs to manage
3. Generate API keys for authentication
4. Configure rate limits
5. View analytics and metrics
6. Set up webhook subscriptions
7. Test APIs using the proxy tester

## Navigation

- Dashboard: Overview with quick stats
- APIs: Manage your APIs
- API Keys: Create and manage API keys
- Rate Limits: Configure rate limiting
- Analytics: View usage statistics and performance metrics
- Webhooks: Manage webhook subscriptions and view deliveries
- Proxy Tester: Test API requests through the proxy

## Development

The application is modular with each page in a separate file for maintainability:
- `app.py` - Main entry point and routing
- `pages/` - Individual page modules
- `api_client.py` - Centralized API communication
- `config.py` - Environment configuration
