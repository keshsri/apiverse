# APIverse

> A comprehensive API management platform for proxying, monitoring, and managing your APIs with built-in authentication, usage tracking, and analytics.

[![AWS](https://img.shields.io/badge/AWS-Lambda%20%7C%20RDS%20%7C%20API%20Gateway-orange)](https://aws.amazon.com/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-green)](https://fastapi.tiangolo.com/)
[![Python](https://img.shields.io/badge/Python-3.12-blue)](https://www.python.org/)
[![TypeScript](https://img.shields.io/badge/TypeScript-CDK-blue)](https://aws.amazon.com/cdk/)

## Documentation

- [API Reference](docs/API.md) - Complete API documentation with examples
- [Deployment Guide](docs/DEPLOYMENT.md) - Step-by-step deployment instructions
- [Architecture](docs/ARCHITECTURE.md) - Technical architecture and design decisions

## Features

### Implemented

- **User Authentication**
  - JWT-based authentication
  - Secure password hashing with Argon2
  - User registration and login

- **API Management**
  - Register and manage multiple APIs
  - Support for various authentication types (Bearer, API Key, Basic, Custom)
  - API versioning support
  - Enable/disable APIs

- **API Key Management**
  - Generate secure API keys with Argon2 hashing
  - Environment-based keys (test/live)
  - Key expiration and revocation
  - Last used tracking

- **Request Proxy**
  - Forward requests to registered APIs
  - Support for all HTTP methods (GET, POST, PUT, DELETE, PATCH)
  - Automatic authentication injection
  - Request/response forwarding with proper headers
  - Error handling (timeouts, connection errors)

- **Rate Limiting**
  - Redis-based rate limiting
  - Per-API limits (requests per hour/day)
  - Configurable tiers (standard, premium, enterprise)
  - Rate limit headers in responses

- **Analytics**
  - Usage statistics (total requests, success/fail rates)
  - Endpoint-level metrics
  - Error distribution analysis
  - Performance metrics (response times)

- **Webhooks**
  - Event subscriptions (api.request, api.error, api.rate_limit, etc.)
  - EventBridge integration
  - Delivery tracking and retry logic
  - HMAC signature verification

- **Usage Tracking**
  - Track every proxied request
  - Metrics: endpoint, method, status code, response time
  - Foundation for analytics and billing

- **Frontend Dashboard**
  - Streamlit-based web interface
  - Complete API management UI
  - Real-time analytics visualization
  - Webhook configuration interface

### In Development

- AI-powered API testing

## Frontend

A modular Streamlit-based dashboard for managing and monitoring your APIs.

**Features:**
- User authentication
- API management interface
- API keys generation and management
- Rate limits configuration
- Analytics dashboard with charts
- Webhooks management
- Proxy tester for direct API testing

**Structure:**
```
frontend/
├── app.py              # Main application
├── api_client.py       # API wrapper
├── config.py           # Configuration
└── pages/              # Modular page components
    ├── auth.py
    ├── dashboard.py
    ├── apis.py
    ├── api_keys.py
    ├── rate_limits.py
    ├── analytics.py
    ├── webhooks.py
    └── proxy_tester.py
```

**Setup:**
```bash
cd frontend
pip install -r requirements.txt
cp .env.example .env
# Edit .env with your API URL
streamlit run app.py
```

See [frontend/README.md](frontend/README.md) for detailed instructions.

## Architecture

```
┌─────────────┐
│   Client    │
└──────┬──────┘
       │ API Key
       ▼
┌─────────────────────────────────────┐
│     API Gateway (AWS)               │
└──────┬──────────────────────────────┘
       │
       ▼
┌─────────────────────────────────────┐
│   Lambda (FastAPI)                  │
│   ├─ Authentication                 │
│   ├─ API Management                 │
│   ├─ Proxy Logic                    │
│   └─ Usage Tracking                 │
└──────┬──────────────────────────────┘
       │
       ├──────────────┬─────────────┐
       ▼              ▼             ▼
┌──────────┐   ┌──────────┐  ┌──────────┐
│   RDS    │   │  Redis   │  │ Upstream │
│PostgreSQL│   │ElastiCache│ │   APIs   │
└──────────┘   └──────────┘  └──────────┘
```

## Tech Stack

### Backend
- **FastAPI** - Modern Python web framework
- **SQLAlchemy** - ORM for database operations
- **Alembic** - Database migrations
- **Argon2** - Password and API key hashing
- **httpx** - Async HTTP client for proxying

### Infrastructure
- **AWS CDK** - Infrastructure as Code (TypeScript)
- **AWS Lambda** - Serverless compute
- **API Gateway** - HTTP API endpoint
- **RDS PostgreSQL** - Relational database
- **ElastiCache Redis** - Caching and rate limiting
- **VPC** - Network isolation with private subnets

## Getting Started

### Prerequisites

- Python 3.12+
- Node.js 18+ (for CDK)
- AWS Account with credentials configured
- PostgreSQL (for local development)

### Local Development

1. **Clone the repository**
```bash
git clone https://github.com/yourusername/apiverse.git
cd apiverse
```

2. **Setup Python environment**
```bash
cd services/api
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

3. **Configure environment variables**
```bash
cp .env.example .env
# Edit .env with your database credentials
```

4. **Run database migrations**
```bash
alembic upgrade head
```

5. **Start the development server**
```bash
uvicorn app.main:app --reload
```

6. **Access the API**
- API: http://localhost:8000
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

### AWS Deployment

1. **Install CDK dependencies**
```bash
cd infra/cdk
npm install
```

2. **Bootstrap CDK (first time only)**
```bash
cdk bootstrap
```

3. **Deploy to AWS**
```bash
cdk deploy
```

4. **Run database migrations on AWS**
The migration Lambda is automatically triggered after deployment.

## API Documentation

### Authentication

**Register**
```http
POST /auth/register
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "SecurePass123",
  "full_name": "John Doe"
}
```

**Login**
```http
POST /auth/login
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "SecurePass123"
}
```

### API Management

**Create API**
```http
POST /apis
Authorization: Bearer <jwt_token>
Content-Type: application/json

{
  "name": "My API",
  "description": "API description",
  "base_url": "https://api.example.com",
  "auth_type": "bearer",
  "auth_config": {
    "token": "your-api-token"
  }
}
```

**List APIs**
```http
GET /apis
Authorization: Bearer <jwt_token>
```

### API Key Management

**Create API Key**
```http
POST /api-keys
Authorization: Bearer <jwt_token>
Content-Type: application/json

{
  "name": "Production Key",
  "environment": "live",
  "expires_in_days": 365
}
```

**List API Keys**
```http
GET /api-keys
Authorization: Bearer <jwt_token>
```

### Proxy Requests

**Proxy any request**
```http
GET /proxy/{api_id}/{path}
X-API-Key: apv_live_...

# Example:
GET /proxy/1/users
X-API-Key: apv_live_abc123...
```

All HTTP methods are supported (GET, POST, PUT, DELETE, PATCH).

## Database Schema

### Core Tables

- **users** - User accounts
- **apis** - Registered APIs
- **api_keys** - API keys for authentication
- **api_versions** - API version tracking
- **rate_limits** - Rate limiting configuration
- **usage_metrics** - Request tracking and analytics
- **webhook_subscriptions** - Webhook configurations
- **webhook_deliveries** - Webhook delivery tracking

## Testing with Postman

Import the Postman collections from `postman/collections/`:
- `APIverse Local.postman_collection.json` - For local testing
- `APIverse Cloud.postman_collection.json` - For AWS testing

Create environments with:
- `baseUrl` - API base URL
- `jwt_token` - Auto-populated after login
- `api_key` - Auto-populated after key creation
- `bearerToken` - Set to `{{jwt_token}}`

## Project Structure

```
apiverse/
├── infra/
│   └── cdk/                    # AWS CDK infrastructure
│       ├── lib/
│       │   ├── constructs/     # Reusable CDK constructs
│       │   └── apiverse-stack.ts
│       └── bin/
├── services/
│   └── api/                    # FastAPI application
│       ├── app/
│       │   ├── core/           # Database configuration
│       │   ├── models/         # SQLAlchemy models
│       │   ├── schemas/        # Pydantic schemas
│       │   ├── routers/        # API endpoints
│       │   ├── services/       # Business logic
│       │   └── utils/          # Utilities
│       ├── alembic/            # Database migrations
│       └── requirements.txt
├── postman/
│   └── collections/            # Postman collections
└── README.md
```

## Security

- Passwords hashed with Argon2
- API keys hashed with Argon2
- JWT tokens for authentication
- Private subnets for database and cache
- Security groups for network isolation
- Secrets stored in AWS Secrets Manager

## License

MIT

