# APIverse API Documentation

Complete API reference for APIverse platform.

## Base URLs

- **Local Development**: `http://localhost:8000`
- **AWS Deployment**: `https://your-api-gateway-url.amazonaws.com/dev`

## Authentication

APIverse uses two authentication methods:

1. **JWT Tokens** - For managing your account and APIs
2. **API Keys** - For proxying requests through APIverse

### JWT Authentication

Include JWT token in the Authorization header:
```
Authorization: Bearer <jwt_token>
```

JWT tokens expire after 24 hours. Obtain a new token by logging in again.

### API Key Authentication

Include API key in the X-API-Key header:
```
X-API-Key: apv_live_<random_string>
```

API keys can be set to expire or remain valid indefinitely.

---

## Endpoints

### Authentication

#### Register User

Create a new user account.

**Endpoint**: `POST /auth/register`

**Request Body**:
```json
{
  "email": "user@example.com",
  "password": "SecurePass123",
  "full_name": "John Doe"
}
```

**Response** (201 Created):
```json
{
  "id": 1,
  "email": "user@example.com",
  "full_name": "John Doe",
  "is_active": true,
  "created_at": "2024-02-22T10:00:00Z"
}
```

**Validation Rules**:
- Email must be valid format
- Password minimum 8 characters
- Email must be unique

---

#### Login

Authenticate and receive JWT token.

**Endpoint**: `POST /auth/login`

**Request Body**:
```json
{
  "email": "user@example.com",
  "password": "SecurePass123"
}
```

**Response** (200 OK):
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "user": {
    "id": 1,
    "email": "user@example.com",
    "full_name": "John Doe",
    "is_active": true,
    "created_at": "2024-02-22T10:00:00Z"
  }
}
```

**Error Responses**:
- `401 Unauthorized` - Invalid credentials

---

### API Management

All API management endpoints require JWT authentication.

#### Create API

Register a new API to proxy through APIverse.

**Endpoint**: `POST /apis`

**Headers**:
```
Authorization: Bearer <jwt_token>
Content-Type: application/json
```

**Request Body**:
```json
{
  "name": "JSONPlaceholder API",
  "description": "Free fake REST API for testing",
  "base_url": "https://jsonplaceholder.typicode.com",
  "auth_type": "none",
  "auth_config": null
}
```

**Auth Types**:

1. **none** - No authentication
```json
{
  "auth_type": "none",
  "auth_config": null
}
```

2. **bearer** - Bearer token authentication
```json
{
  "auth_type": "bearer",
  "auth_config": {
    "token": "your-bearer-token"
  }
}
```

3. **api_key** - API key in header
```json
{
  "auth_type": "api_key",
  "auth_config": {
    "key_name": "X-API-Key",
    "key_value": "your-api-key"
  }
}
```

4. **basic** - Basic authentication
```json
{
  "auth_type": "basic",
  "auth_config": {
    "username": "user",
    "password": "pass"
  }
}
```

5. **custom** - Custom headers
```json
{
  "auth_type": "custom",
  "auth_config": {
    "custom_header": "value"
  }
}
```

**Response** (201 Created):
```json
{
  "id": 1,
  "name": "JSONPlaceholder API",
  "description": "Free fake REST API for testing",
  "base_url": "https://jsonplaceholder.typicode.com",
  "auth_type": "none",
  "is_active": true,
  "user_id": 1,
  "created_at": "2024-02-22T10:00:00Z",
  "updated_at": "2024-02-22T10:00:00Z"
}
```

---

#### List APIs

Get all APIs for the authenticated user.

**Endpoint**: `GET /apis`

**Headers**:
```
Authorization: Bearer <jwt_token>
```

**Response** (200 OK):
```json
{
  "total": 2,
  "apis": [
    {
      "id": 1,
      "name": "JSONPlaceholder API",
      "description": "Free fake REST API",
      "base_url": "https://jsonplaceholder.typicode.com",
      "auth_type": "none",
      "is_active": true,
      "user_id": 1,
      "created_at": "2024-02-22T10:00:00Z",
      "updated_at": "2024-02-22T10:00:00Z"
    },
    {
      "id": 2,
      "name": "GitHub API",
      "description": "GitHub REST API",
      "base_url": "https://api.github.com",
      "auth_type": "bearer",
      "is_active": true,
      "user_id": 1,
      "created_at": "2024-02-22T11:00:00Z",
      "updated_at": "2024-02-22T11:00:00Z"
    }
  ]
}
```

---

#### Get API

Get details of a specific API.

**Endpoint**: `GET /apis/{api_id}`

**Headers**:
```
Authorization: Bearer <jwt_token>
```

**Response** (200 OK):
```json
{
  "id": 1,
  "name": "JSONPlaceholder API",
  "description": "Free fake REST API",
  "base_url": "https://jsonplaceholder.typicode.com",
  "auth_type": "none",
  "is_active": true,
  "user_id": 1,
  "created_at": "2024-02-22T10:00:00Z",
  "updated_at": "2024-02-22T10:00:00Z"
}
```

**Error Responses**:
- `404 Not Found` - API not found or access denied

---

#### Update API

Update an existing API.

**Endpoint**: `PUT /apis/{api_id}`

**Headers**:
```
Authorization: Bearer <jwt_token>
Content-Type: application/json
```

**Request Body** (all fields optional):
```json
{
  "name": "Updated API Name",
  "description": "Updated description",
  "base_url": "https://new-url.com",
  "auth_type": "bearer",
  "auth_config": {
    "token": "new-token"
  },
  "is_active": false
}
```

**Response** (200 OK):
```json
{
  "id": 1,
  "name": "Updated API Name",
  "description": "Updated description",
  "base_url": "https://new-url.com",
  "auth_type": "bearer",
  "is_active": false,
  "user_id": 1,
  "created_at": "2024-02-22T10:00:00Z",
  "updated_at": "2024-02-22T12:00:00Z"
}
```

---

#### Delete API

Delete an API and all associated data.

**Endpoint**: `DELETE /apis/{api_id}`

**Headers**:
```
Authorization: Bearer <jwt_token>
```

**Response** (204 No Content)

**Error Responses**:
- `404 Not Found` - API not found or access denied

---

### API Key Management

#### Create API Key

Generate a new API key for proxying requests.

**Endpoint**: `POST /api-keys`

**Headers**:
```
Authorization: Bearer <jwt_token>
Content-Type: application/json
```

**Request Body**:
```json
{
  "name": "Live Key",
  "environment": "live",
  "expires_in_days": 365
}
```

**Fields**:
- `name` (optional) - Friendly name for the key
- `environment` (optional) - "test" or "live" (default: "live")
- `expires_in_days` (optional) - Expiration in days (max 365, default: never expires)

**Response** (201 Created):
```json
{
  "id": 1,
  "api_key": "apv_live_abc123def456ghi789...",
  "key_prefix": "apv_live_abc...",
  "name": "Live Key",
  "environment": "live",
  "created_at": "2024-02-22T10:00:00Z",
  "expires_at": "2025-02-22T10:00:00Z"
}
```

**Important**: The full `api_key` is only shown once. Save it securely!

---

#### List API Keys

Get all API keys for the authenticated user.

**Endpoint**: `GET /api-keys`

**Headers**:
```
Authorization: Bearer <jwt_token>
```

**Response** (200 OK):
```json
{
  "total": 2,
  "api_keys": [
    {
      "id": 1,
      "key_prefix": "apv_live_abc...",
      "name": "Live Key",
      "environment": "live",
      "is_active": true,
      "created_at": "2024-02-22T10:00:00Z",
      "last_used_at": "2024-02-22T11:30:00Z",
      "expires_at": "2025-02-22T10:00:00Z"
    },
    {
      "id": 2,
      "key_prefix": "apv_test_xyz...",
      "name": "Test Key",
      "environment": "test",
      "is_active": true,
      "created_at": "2024-02-22T09:00:00Z",
      "last_used_at": null,
      "expires_at": null
    }
  ]
}
```

---

#### Revoke API Key

Deactivate an API key (cannot be reactivated).

**Endpoint**: `DELETE /api-keys/{key_id}`

**Headers**:
```
Authorization: Bearer <jwt_token>
```

**Response** (204 No Content)

**Error Responses**:
- `404 Not Found` - API key not found or access denied

---

### Proxy

#### Proxy Request

Forward requests to registered APIs through APIverse.

**Endpoint**: `<METHOD> /proxy/{api_id}/{path}`

**Supported Methods**: GET, POST, PUT, DELETE, PATCH

**Headers**:
```
X-API-Key: apv_live_abc123...
Content-Type: application/json  (for POST/PUT/PATCH)
```

**Examples**:

**GET Request**:
```http
GET /proxy/1/users
X-API-Key: apv_live_abc123...
```

**GET with Query Parameters**:
```http
GET /proxy/1/posts?userId=1&_limit=10
X-API-Key: apv_live_abc123...
```

**POST Request**:
```http
POST /proxy/1/posts
X-API-Key: apv_live_abc123...
Content-Type: application/json

{
  "title": "My Post",
  "body": "Post content",
  "userId": 1
}
```

**PUT Request**:
```http
PUT /proxy/1/posts/1
X-API-Key: apv_live_abc123...
Content-Type: application/json

{
  "id": 1,
  "title": "Updated Post",
  "body": "Updated content",
  "userId": 1
}
```

**DELETE Request**:
```http
DELETE /proxy/1/posts/1
X-API-Key: apv_live_abc123...
```

**Response**: Returns the exact response from the upstream API.

**How it works**:
1. APIverse validates your API key
2. Retrieves the registered API configuration
3. Adds authentication headers (if configured)
4. Forwards the request to the upstream API
5. Tracks usage metrics (endpoint, method, status, response time)
6. Returns the upstream response to you

**Error Responses**:
- `401 Unauthorized` - Invalid or expired API key
- `404 Not Found` - API not found or access denied
- `403 Forbidden` - API is inactive
- `502 Bad Gateway` - Failed to connect to upstream API
- `504 Gateway Timeout` - Upstream API timeout (30s)

---

## Error Responses

All error responses follow this format:

```json
{
  "detail": "Error message"
}
```

### Common HTTP Status Codes

- `200 OK` - Request successful
- `201 Created` - Resource created successfully
- `204 No Content` - Request successful, no content to return
- `400 Bad Request` - Invalid request data
- `401 Unauthorized` - Authentication required or failed
- `403 Forbidden` - Access denied
- `404 Not Found` - Resource not found
- `422 Unprocessable Entity` - Validation error
- `500 Internal Server Error` - Server error
- `502 Bad Gateway` - Upstream API error
- `504 Gateway Timeout` - Request timeout

---

## Rate Limits

Currently, there are no rate limits enforced. Rate limiting will be implemented in a future release.

---

## Usage Tracking

Every proxied request is tracked with the following metrics:

- API ID
- Endpoint path
- HTTP method
- Status code
- Response time (milliseconds)
- Timestamp

This data will be available through analytics endpoints in a future release.

---

## Best Practices

### Security

1. **Never commit API keys or JWT tokens** to version control
2. **Use environment-specific keys** (test vs live)
3. **Rotate API keys regularly**
4. **Set expiration dates** on API keys
5. **Revoke unused keys** immediately

### Performance

1. **Cache responses** when possible (coming soon)
2. **Monitor response times** through usage metrics
3. **Use appropriate timeouts** (default: 30s)

### API Management

1. **Use descriptive names** for APIs and keys
2. **Document auth configurations** in API descriptions
3. **Test with test environment keys** before going live
4. **Monitor API health** through status codes

---

## Postman Collection

Import the Postman collections from the repository:

1. Open Postman
2. Click "Import"
3. Select the collection file from `postman/collections/`
4. Create an environment with `baseUrl`, `jwt_token`, `api_key`, `bearerToken`
5. Run the requests in order: Register → Login → Create API → Create API Key → Proxy

The collections include pre-request scripts that automatically save tokens and add headers.

---

## Support

For issues or questions:
- Open an issue on GitHub
- Check the README for setup instructions
- Review the Swagger UI at `/docs` for interactive documentation
