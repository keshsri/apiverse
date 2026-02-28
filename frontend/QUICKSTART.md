# APIverse Frontend - Quick Start Guide

## Installation

1. Navigate to frontend directory:
```bash
cd frontend
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Configure API endpoint:
```bash
cp .env.example .env
```

Edit `.env` file:
```
API_BASE_URL=http://localhost:8000
```

For AWS deployment, use your API Gateway URL:
```
API_BASE_URL=https://your-id.execute-api.region.amazonaws.com/dev
```

## Running the Application

Start the Streamlit app:
```bash
streamlit run app.py
```

The dashboard will open in your browser at `http://localhost:8501`

## Features Overview

### Dashboard
- Overview of all APIs and keys
- Quick stats and metrics
- Quick action buttons

### APIs Management
- Create new APIs with authentication configuration
- View and edit existing APIs
- Activate/deactivate APIs
- Delete APIs with confirmation

### API Keys
- Generate new API keys
- View active and revoked keys
- Revoke keys with confirmation
- Filter by status

### Rate Limits
- Configure per-API rate limits
- Set hourly and daily request limits
- Choose tier levels

### Analytics
- Usage statistics
- Endpoint performance metrics
- Error distribution charts
- Response time analysis

### Webhooks
- Create webhook subscriptions
- View delivery history
- Manage event types
- Delete subscriptions

### Proxy Tester
- Test API requests through proxy
- Support all HTTP methods
- View response details
- Custom headers and body

## First Time Setup

1. Register a new account
2. Login with your credentials
3. Create your first API
4. Generate an API key
5. Configure rate limits (optional)
6. Test using the Proxy Tester

## Tips

- Save API keys immediately after generation
- Use development keys for testing
- Monitor analytics regularly
- Set appropriate rate limits
- Test webhooks with public endpoints
