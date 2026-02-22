# Architecture Documentation

Detailed architecture overview of APIverse platform.

## System Overview

APIverse is a serverless API management platform built on AWS, designed to proxy, monitor, and manage APIs with built-in authentication, usage tracking, and analytics capabilities.

## High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         Internet                                 │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
                    ┌────────────────┐
                    │  API Gateway   │
                    │   (HTTP API)   │
                    └────────┬───────┘
                             │
                             ▼
                    ┌────────────────┐
                    │  Lambda        │
                    │  (FastAPI)     │
                    │  - Auth        │
                    │  - API Mgmt    │
                    │  - Proxy       │
                    └────┬───────────┘
                         │
         ┌───────────────┼───────────────┐
         │               │               │
         ▼               ▼               ▼
    ┌────────┐     ┌─────────┐    ┌──────────┐
    │  RDS   │     │  Redis  │    │ Upstream │
    │Postgres│     │ElastiCache   │   APIs   │
    └────────┘     └─────────┘    └──────────┘
         │
         ▼
    ┌────────────┐
    │  Secrets   │
    │  Manager   │
    └────────────┘
```

## Components

### 1. API Gateway

**Purpose**: HTTP API endpoint for client requests

**Configuration**:
- Type: HTTP API (cheaper than REST API)
- Stage: `/dev`
- Integration: Lambda proxy integration
- CORS: Enabled for all origins
- Throttling: Not configured (future)

**Endpoints**:
- `POST /auth/register` - User registration
- `POST /auth/login` - User authentication
- `GET /apis` - List APIs
- `POST /apis` - Create API
- `GET /apis/{id}` - Get API details
- `PUT /apis/{id}` - Update API
- `DELETE /apis/{id}` - Delete API
- `POST /api-keys` - Create API key
- `GET /api-keys` - List API keys
- `DELETE /api-keys/{id}` - Revoke API key
- `<METHOD> /proxy/{api_id}/{path}` - Proxy requests

**Benefits**:
- Automatic SSL/TLS
- DDoS protection
- Request/response transformation
- Built-in monitoring

---

### 2. Lambda Function (FastAPI)

**Purpose**: Main application logic

**Configuration**:
- Runtime: Python 3.12 (Docker container)
- Memory: 512 MB
- Timeout: 30 seconds
- Architecture: x86_64
- Handler: Mangum (ASGI adapter)

**Components**:

#### Core
- `database.py` - Database connection and session management
- `config.py` - Application configuration

#### Models (SQLAlchemy)
- `User` - User accounts
- `API` - Registered APIs
- `APIKey` - API keys for authentication
- `APIVersion` - API version tracking
- `RateLimit` - Rate limiting configuration
- `UsageMetric` - Request tracking
- `WebhookSubscription` - Webhook configurations
- `WebhookDelivery` - Webhook delivery tracking

#### Schemas (Pydantic)
- Request validation
- Response serialization
- Type safety

#### Routers
- `auth.py` - Authentication endpoints
- `apis.py` - API management endpoints
- `api_keys.py` - API key management
- `proxy.py` - Request proxying

#### Services
- `auth.py` - Authentication business logic
- `api_service.py` - API management logic
- `api_key_service.py` - API key operations

#### Utils
- `security.py` - Password hashing, JWT tokens
- `dependencies.py` - FastAPI dependencies
- `logger.py` - Logging configuration

**Networking**:
- VPC: Private subnets with NAT for internet access
- Security Group: Allows outbound to RDS, Redis, and internet

---

### 3. RDS PostgreSQL

**Purpose**: Persistent data storage

**Configuration**:
- Engine: PostgreSQL 15
- Instance: db.t3.micro
- Storage: 20 GB GP2
- Multi-AZ: Disabled (single AZ for cost)
- Backup: 1 day retention
- Encryption: Enabled at rest

**Network**:
- VPC: Private subnet (no public access)
- Security Group: Allows inbound from Lambda only

**Tables**:
```sql
users
├── id (PK)
├── email (unique)
├── password_hash
├── full_name
├── is_active
├── created_at
└── updated_at

apis
├── id (PK)
├── user_id (FK → users)
├── name
├── description
├── base_url
├── auth_type
├── auth_config (JSON)
├── is_active
├── created_at
└── updated_at

api_keys
├── id (PK)
├── user_id (FK → users)
├── key_hash
├── key_prefix
├── name
├── environment
├── is_active
├── created_at
├── last_used_at
└── expires_at

usage_metrics
├── id (PK)
├── api_id (FK → apis)
├── endpoint
├── method
├── status_code
├── response_time_ms
└── timestamp
```

**Indexes**:
- Primary keys on all tables
- Unique index on `users.email`
- Unique index on `api_keys.key_hash`
- Composite index on `usage_metrics(api_id, timestamp)`
- Composite index on `usage_metrics(api_id, endpoint)`

---

### 4. ElastiCache Redis

**Purpose**: Caching and rate limiting (future)

**Configuration**:
- Engine: Redis 7.x
- Instance: cache.t3.micro
- Nodes: 1 (no replication)
- Encryption: In-transit and at-rest

**Network**:
- VPC: Private subnet
- Security Group: Allows inbound from Lambda only

**Planned Usage**:
- Rate limiting counters
- API response caching
- Session storage
- Real-time analytics

---

### 5. Secrets Manager

**Purpose**: Secure credential storage

**Secrets Stored**:
- RDS master credentials
  - Username
  - Password
  - Host
  - Port
  - Database name

**Access**:
- Lambda has IAM permission to read secrets
- Automatic rotation: Not configured (manual for now)

---

### 6. VPC and Networking

**VPC Configuration**:
- CIDR: 10.0.0.0/16
- Availability Zones: 2

**Subnets**:
- Public Subnets (2): 10.0.0.0/24, 10.0.1.0/24
  - NAT Instance for Lambda internet access
  - Internet Gateway attached
  
- Private Subnets (2): 10.0.2.0/24, 10.0.3.0/24
  - Lambda functions
  - RDS database
  - ElastiCache Redis

**Security Groups**:

1. **Lambda SG**:
   - Outbound: All traffic (0.0.0.0/0)
   - Inbound: None

2. **RDS SG**:
   - Inbound: PostgreSQL (5432) from Lambda SG
   - Outbound: None

3. **Redis SG**:
   - Inbound: Redis (6379) from Lambda SG
   - Outbound: None

4. **NAT Instance SG**:
   - Inbound: All from private subnets
   - Outbound: All to internet

**Cost Optimization**:
- Using NAT Instance instead of NAT Gateway (saves ~$30/month)
- Single NAT Instance (not HA, but sufficient for dev)

---

### 7. EventBridge & SQS (Webhooks)

**Purpose**: Webhook event processing (future implementation)

**Components**:
- EventBridge Event Bus: Custom event bus for API events
- SQS Queue: Dead letter queue for failed webhook deliveries
- Lambda (future): Webhook delivery processor

**Event Flow**:
```
API Event → EventBridge → Lambda → HTTP POST → Webhook URL
                              ↓ (failure)
                            SQS DLQ
```

---

## Data Flow

### 1. User Registration Flow

```
Client
  ↓ POST /auth/register
API Gateway
  ↓
Lambda (FastAPI)
  ↓ Hash password (Argon2)
  ↓ INSERT INTO users
RDS PostgreSQL
  ↓ Return user data
Lambda
  ↓ 201 Created
Client
```

### 2. Authentication Flow

```
Client
  ↓ POST /auth/login
API Gateway
  ↓
Lambda
  ↓ SELECT FROM users WHERE email
RDS
  ↓ Verify password (Argon2)
  ↓ Generate JWT token
Lambda
  ↓ 200 OK + JWT
Client
```

### 3. API Registration Flow

```
Client
  ↓ POST /apis + JWT
API Gateway
  ↓
Lambda
  ↓ Verify JWT
  ↓ INSERT INTO apis
RDS
  ↓ Return API data
Lambda
  ↓ 201 Created
Client
```

### 4. Proxy Request Flow

```
Client
  ↓ GET /proxy/1/users + API Key
API Gateway
  ↓
Lambda
  ↓ Extract API key
  ↓ SELECT FROM api_keys WHERE key_prefix
RDS
  ↓ Verify key hash (Argon2)
  ↓ Check expiration, is_active
  ↓ SELECT FROM apis WHERE id
  ↓ Get API config (base_url, auth)
Lambda
  ↓ Build target URL
  ↓ Add auth headers
  ↓ HTTP request (httpx)
Upstream API
  ↓ Response
Lambda
  ↓ INSERT INTO usage_metrics
RDS
  ↓ Return response
Lambda
  ↓ 200 OK + upstream response
Client
```

---

## Security Architecture

### Authentication & Authorization

**JWT Tokens**:
- Algorithm: HS256
- Expiration: 24 hours
- Payload: `{"sub": user_id, "exp": timestamp}`
- Secret: Environment variable

**API Keys**:
- Format: `apv_{environment}_{random_32_bytes}`
- Hashing: Argon2 (same as passwords)
- Storage: Only hash stored in database
- Prefix: First 12 characters for lookup

**Password Security**:
- Hashing: Argon2 (memory-hard, resistant to GPU attacks)
- No plaintext storage
- Salted automatically by Argon2

### Network Security

**Defense in Depth**:
1. API Gateway (DDoS protection, throttling)
2. Lambda in private subnet (no direct internet access)
3. RDS in private subnet (no public endpoint)
4. Security groups (least privilege)
5. Secrets Manager (encrypted credentials)

**Data Encryption**:
- In-transit: TLS 1.2+ (API Gateway, RDS, Redis)
- At-rest: AES-256 (RDS, Redis, Secrets Manager)

---

## Scalability

### Current Limits

**Lambda**:
- Concurrent executions: 1000 (default account limit)
- Memory: 512 MB
- Timeout: 30 seconds

**RDS**:
- Instance: db.t3.micro (2 vCPU, 1 GB RAM)
- Connections: ~100 max
- IOPS: Baseline 100, burst 3000

**Redis**:
- Instance: cache.t3.micro (2 vCPU, 0.5 GB RAM)
- Connections: 65,000 max

### Scaling Strategies

**Horizontal Scaling**:
- Lambda: Automatic (up to account limit)
- RDS: Read replicas (future)
- Redis: Cluster mode (future)

**Vertical Scaling**:
- Lambda: Increase memory (up to 10 GB)
- RDS: Upgrade instance type
- Redis: Upgrade instance type

**Optimization**:
- Connection pooling (SQLAlchemy)
- Database query optimization
- Redis caching (future)
- CDN for static assets (future)

---

## Monitoring & Observability

### Metrics

**Lambda Metrics** (CloudWatch):
- Invocations
- Duration
- Errors
- Throttles
- Concurrent Executions
- Iterator Age (for streams)

**RDS Metrics**:
- CPU Utilization
- Database Connections
- Free Storage Space
- Read/Write Latency
- Read/Write IOPS

**Redis Metrics**:
- CPU Utilization
- Cache Hits/Misses
- Evictions
- Network Bytes In/Out

**Custom Metrics** (Application):
- Request count by endpoint
- Response time percentiles
- Error rate by endpoint
- API key usage

### Logging

**Log Levels**:
- INFO: Normal operations
- WARNING: Potential issues
- ERROR: Errors that need attention

**Log Aggregation**:
- CloudWatch Logs
- Retention: 7 days
- Log Groups:
  - `/aws/lambda/apiverse-api`
  - `/aws/lambda/apiverse-migration`

**Structured Logging**:
```python
api_logger.info(
    f"Proxy request: api_id={api_id}, "
    f"path={path}, method={method}, "
    f"user_id={user_id}"
)
```

---

## Disaster Recovery

### Backup Strategy

**RDS Backups**:
- Automated daily backups
- Retention: 1 day
- Point-in-time recovery: Enabled
- Manual snapshots: As needed

**Recovery Time Objective (RTO)**: ~30 minutes
**Recovery Point Objective (RPO)**: 24 hours (last backup)

### Failure Scenarios

**Lambda Failure**:
- Automatic retry (3 times)
- Dead letter queue (future)
- Rollback deployment

**RDS Failure**:
- Restore from latest backup
- Multi-AZ for automatic failover (optional)

**Region Failure**:
- Manual deployment to another region
- Restore database from snapshot

---

## Future Enhancements

### Phase 3B - Advanced Features
- Rate limiting with Redis
- Response caching
- Request/response transformation

### Phase 4 - Analytics
- Usage dashboard
- Real-time metrics
- Cost tracking per API

### Phase 5 - Webhooks
- Event-driven webhooks
- Retry logic
- Delivery tracking

### Phase 6 - AI Features
- AI-powered API testing
- Anomaly detection
- Documentation generation

### Phase 7 - Frontend
- React/Next.js dashboard
- API explorer
- Analytics visualizations

---

## Technology Decisions

### Why FastAPI?
- Modern Python framework
- Automatic OpenAPI documentation
- Type hints and validation
- Async support
- High performance

### Why Lambda?
- Serverless (no server management)
- Auto-scaling
- Pay per request
- Easy deployment

### Why PostgreSQL?
- ACID compliance
- JSON support
- Mature ecosystem

### Why Redis?
- In-memory performance
- Rate limiting support
- Pub/sub for webhooks

### Why AWS CDK?
- Infrastructure as Code
- Type safety (TypeScript)
- Reusable constructs
- Better than CloudFormation

---

## References

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [AWS Lambda Best Practices](https://docs.aws.amazon.com/lambda/latest/dg/best-practices.html)
- [AWS CDK Documentation](https://docs.aws.amazon.com/cdk/)
- [PostgreSQL Documentation](https://www.postgresql.org/docs/)
- [Redis Documentation](https://redis.io/documentation)
