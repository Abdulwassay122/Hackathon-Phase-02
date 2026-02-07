# Quickstart Guide: JWT Authentication for Task API

## Prerequisites

- Completed Phase 1 (001-todo-backend) implementation
- Python 3.11+
- Access to Neon Serverless PostgreSQL instance
- Better Auth configured to issue JWT tokens
- Shared secret (BETTER_AUTH_SECRET) from Better Auth configuration

## Setup Instructions

### 1. Install JWT Authentication Dependencies

```bash
cd backend
pip install PyJWT[crypto]==2.8.0
```

Update `requirements.txt`:
```txt
fastapi==0.104.1
sqlmodel==0.0.8
psycopg2-binary==2.9.7
python-dotenv==1.0.0
pytest==7.4.3
uvicorn==0.23.2
PyJWT[crypto]==2.8.0
```

### 2. Configure Environment Variables

Add JWT configuration to your `.env` file:

```env
# Existing configuration
DATABASE_URL=postgresql://username:password@host:port/database_name

# JWT Authentication (Phase 2)
BETTER_AUTH_SECRET=your-32-byte-minimum-secret-key-here
JWT_ALGORITHM=HS256
```

**Important**: The `BETTER_AUTH_SECRET` must match the secret configured in Better Auth.

### 3. Verify Backend Structure

Your backend should have this structure after Phase 2 implementation:

```
backend/
├── src/
│   ├── auth/                    # NEW: Authentication module
│   │   ├── __init__.py
│   │   ├── jwt_handler.py       # JWT verification logic
│   │   └── dependencies.py      # FastAPI auth dependencies
│   ├── models/
│   │   └── task_model.py        # Existing from Phase 1
│   ├── api/
│   │   └── task_routes.py       # Updated with authentication
│   ├── services/
│   │   └── task_service.py      # Existing from Phase 1
│   ├── database/
│   │   └── database.py          # Existing from Phase 1
│   ├── config.py                # Updated with JWT config
│   ├── logging_config.py        # Existing from Phase 1
│   └── main.py                  # Existing from Phase 1
└── tests/
    ├── unit/
    │   ├── test_models.py       # Existing from Phase 1
    │   └── test_jwt_handler.py  # NEW: JWT handler tests
    ├── integration/
    │   └── test_api_auth.py     # NEW: Authenticated API tests
    └── contract/
        └── test_contracts.py    # Updated with auth tests
```

### 4. Start the Development Server

```bash
cd backend
uvicorn src.main:app --reload --port 8000
```

The API will be available at `http://localhost:8000`

## Testing Authentication

### Obtain a JWT Token

**Option 1: Using Better Auth Frontend**
1. Log in through the Better Auth-enabled frontend
2. Extract the JWT token from the response or browser storage
3. Use the token in API requests

**Option 2: Generate Test Token (Development Only)**

For testing purposes, you can generate a test token:

```python
import jwt
from datetime import datetime, timedelta

SECRET = "your-secret-key"
payload = {
    "sub": "1",  # User ID
    "email": "test@example.com",
    "iat": datetime.utcnow(),
    "exp": datetime.utcnow() + timedelta(days=1)
}
token = jwt.encode(payload, SECRET, algorithm="HS256")
print(token)
```

### API Usage Examples with Authentication

All requests must include the `Authorization` header with a Bearer token.

#### Get All Tasks (Authenticated User)

```bash
curl -X GET http://localhost:8000/api/tasks \
  -H "Authorization: Bearer YOUR_JWT_TOKEN_HERE"
```

**Response (200 OK)**:
```json
[
  {
    "id": 1,
    "title": "Buy groceries",
    "description": "Milk, bread, eggs",
    "completed": false,
    "user_id": 1,
    "created_at": "2026-02-07T10:30:00Z",
    "updated_at": "2026-02-07T10:30:00Z"
  }
]
```

#### Create a New Task

```bash
curl -X POST http://localhost:8000/api/tasks \
  -H "Authorization: Bearer YOUR_JWT_TOKEN_HERE" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Buy groceries",
    "description": "Milk, bread, eggs"
  }'
```

**Response (201 Created)**:
```json
{
  "id": 1,
  "title": "Buy groceries",
  "description": "Milk, bread, eggs",
  "completed": false,
  "user_id": 1,
  "created_at": "2026-02-07T10:30:00Z",
  "updated_at": "2026-02-07T10:30:00Z"
}
```

**Note**: The `user_id` is automatically set from the JWT token, not from the request body.

#### Get a Specific Task

```bash
curl -X GET http://localhost:8000/api/tasks/1 \
  -H "Authorization: Bearer YOUR_JWT_TOKEN_HERE"
```

**Response (200 OK)**: Same as create response

**Response (403 Forbidden)** if task belongs to another user:
```json
{
  "detail": "Not authorized to access this user's resources"
}
```

#### Update a Task

```bash
curl -X PUT http://localhost:8000/api/tasks/1 \
  -H "Authorization: Bearer YOUR_JWT_TOKEN_HERE" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Buy groceries and supplies",
    "description": "Milk, bread, eggs, coffee",
    "completed": true
  }'
```

**Response (200 OK)**: Updated task object

#### Mark Task as Complete

```bash
curl -X PATCH http://localhost:8000/api/tasks/1/complete \
  -H "Authorization: Bearer YOUR_JWT_TOKEN_HERE" \
  -H "Content-Type: application/json" \
  -d '{"completed": true}'
```

**Response (200 OK)**: Updated task object with `completed: true`

#### Delete a Task

```bash
curl -X DELETE http://localhost:8000/api/tasks/1 \
  -H "Authorization: Bearer YOUR_JWT_TOKEN_HERE"
```

**Response (204 No Content)**: Empty response body

## Authentication Error Responses

### Missing Token (401 Unauthorized)

```bash
curl -X GET http://localhost:8000/api/tasks
```

**Response**:
```json
{
  "detail": "Missing authentication token"
}
```

### Invalid Token (401 Unauthorized)

```bash
curl -X GET http://localhost:8000/api/tasks \
  -H "Authorization: Bearer invalid-token"
```

**Response**:
```json
{
  "detail": "Invalid authentication token"
}
```

### Expired Token (401 Unauthorized)

```bash
curl -X GET http://localhost:8000/api/tasks \
  -H "Authorization: Bearer expired-token"
```

**Response**:
```json
{
  "detail": "Token has expired"
}
```

### Insufficient Permissions (403 Forbidden)

Attempting to access another user's task:

```bash
curl -X GET http://localhost:8000/api/tasks/999 \
  -H "Authorization: Bearer YOUR_JWT_TOKEN_HERE"
```

**Response**:
```json
{
  "detail": "Not authorized to access this user's resources"
}
```

## Testing with Swagger UI

1. Navigate to `http://localhost:8000/docs`
2. Click the "Authorize" button at the top right
3. Enter your JWT token in the format: `Bearer YOUR_TOKEN_HERE`
4. Click "Authorize"
5. All subsequent API calls will include the authentication token

## Running Tests

### Run All Tests

```bash
cd backend
pytest tests/ -v
```

### Run Authentication Tests Only

```bash
pytest tests/integration/test_api_auth.py -v
pytest tests/unit/test_jwt_handler.py -v
```

### Run with Coverage

```bash
pytest tests/ --cov=src --cov-report=html
```

## Troubleshooting

### "Invalid authentication token" Error

**Possible Causes**:
1. Token signed with different secret than backend expects
2. Token format is incorrect
3. Token is malformed

**Solution**:
- Verify `BETTER_AUTH_SECRET` matches between Better Auth and backend
- Check token format (should be three base64-encoded parts separated by dots)
- Validate token at https://jwt.io

### "Token has expired" Error

**Cause**: Token's `exp` claim is in the past

**Solution**:
- Obtain a new token from Better Auth
- Check token expiration time: `jwt.decode(token, options={"verify_signature": False})`

### "Not authorized to access this user's resources" Error

**Cause**: Attempting to access resources belonging to another user

**Solution**:
- Verify the user_id in the JWT token matches the resource owner
- Check that the `sub` claim in the token is correct

### Database Connection Issues

**Cause**: Database URL not configured or incorrect

**Solution**:
- Verify `DATABASE_URL` in `.env` file
- Test database connection: `psql $DATABASE_URL`

## Security Best Practices

1. **Never commit secrets**: Keep `.env` file out of version control
2. **Use HTTPS in production**: Tokens are vulnerable over HTTP
3. **Set reasonable token expiration**: 1-24 hours recommended
4. **Rotate secrets regularly**: Update `BETTER_AUTH_SECRET` periodically
5. **Monitor authentication failures**: Check logs for suspicious activity
6. **Validate all inputs**: Don't trust data even from authenticated users

## Next Steps

After completing Phase 2 (JWT Authentication):

1. **Phase 3**: Implement frontend with Better Auth integration
2. **Phase 4**: Add user registration and login endpoints
3. **Phase 5**: Implement refresh token rotation
4. **Phase 6**: Add role-based access control (RBAC)

## API Documentation

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI Spec**: http://localhost:8000/openapi.json

## Support

For issues or questions:
- Review the specification: `specs/002-jwt-auth/spec.md`
- Check the implementation plan: `specs/002-jwt-auth/plan.md`
- Review test cases: `backend/tests/`
