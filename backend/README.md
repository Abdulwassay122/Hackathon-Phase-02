# Todo Backend API

A RESTful API for managing user tasks in a Todo application built with FastAPI and SQLModel with JWT authentication.

## Prerequisites

- Python 3.11+
- pip package manager
- Access to PostgreSQL database (or SQLite for development)

## Setup Instructions

### 1. Install dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure environment variables

Create a `.env` file in the project root with your database connection details and JWT configuration:

```env
# Database Configuration
DATABASE_URL=postgresql://username:password@host:port/database_name
LOG_LEVEL=INFO

# JWT Authentication (Phase 2)
BETTER_AUTH_SECRET=your-32-byte-minimum-secret-key-here
JWT_ALGORITHM=HS256
```

For local development with SQLite:

```env
DATABASE_URL=sqlite:///./todo_app.db
LOG_LEVEL=INFO
BETTER_AUTH_SECRET=your-secure-secret-key-at-least-32-characters-long
JWT_ALGORITHM=HS256
```

**Important:** The `BETTER_AUTH_SECRET` must be at least 32 characters long for security. Generate a secure random string for production use.

### 3. Start the development server

```bash
uvicorn src.main:app --reload --port 8000
```

The API will be available at `http://localhost:8000`

## CORS Configuration

Cross-Origin Resource Sharing (CORS) must be configured to allow your frontend application to communicate with the backend API.

### Setup

Add the `CORS_ORIGINS` environment variable to your `.env` file:

```env
# CORS Configuration
CORS_ORIGINS=http://localhost:3000
```

**Format:**
- **Single origin**: `CORS_ORIGINS=http://localhost:3000`
- **Multiple origins** (comma-separated): `CORS_ORIGINS=http://localhost:3000,http://localhost:3001`

**Examples:**
- Development: `CORS_ORIGINS=http://localhost:3000`
- Staging: `CORS_ORIGINS=https://staging.example.com,http://localhost:3000`
- Production: `CORS_ORIGINS=https://app.example.com`

### Security Requirements

The CORS configuration enforces strict security policies:

- ✅ **Explicit origins only** - Must specify exact URLs (e.g., `http://localhost:3000`)
- ✅ **Protocol required** - Must include `http://` or `https://`
- ✅ **No trailing slashes** - Use `http://localhost:3000`, not `http://localhost:3000/`
- ✅ **No wildcards** - Wildcard `*` origins are rejected for security
- ✅ **Credentials enabled** - Supports JWT tokens in Authorization headers
- ✅ **Explicit methods** - Only allows GET, POST, PUT, PATCH, DELETE
- ✅ **Explicit headers** - Only allows Authorization and Content-Type headers

### Verification

When the backend starts, it logs the CORS configuration:

```
============================================================
CORS Configuration
============================================================
Allowed Origins (1):
  - http://localhost:3000
Allow Credentials: True
Allow Methods: ['GET', 'POST', 'PUT', 'PATCH', 'DELETE']
Allow Headers: ['Authorization', 'Content-Type']
============================================================
```

If `CORS_ORIGINS` is not set, you'll see a warning:

```
WARNING: No origins configured - cross-origin requests will be blocked!
```

### Troubleshooting Common CORS Issues

#### Issue: "CORS policy: No 'Access-Control-Allow-Origin' header"

**Cause**: `CORS_ORIGINS` environment variable is not set or empty.

**Solution**:
1. Add `CORS_ORIGINS=http://localhost:3000` to your `.env` file
2. Restart the backend server
3. Check startup logs to confirm the origin is loaded

#### Issue: "Origin 'http://localhost:3001' blocked by CORS policy"

**Cause**: The requesting origin is not in the allowed origins list.

**Solution**: Add the origin to `CORS_ORIGINS`:
```env
CORS_ORIGINS=http://localhost:3000,http://localhost:3001
```

#### Issue: "Wildcard origin (*) not allowed per security policy"

**Cause**: Attempted to use `CORS_ORIGINS=*` which is rejected for security.

**Solution**: Use explicit origin URLs:
```env
CORS_ORIGINS=http://localhost:3000
```

#### Issue: "Invalid origin format" or origin validation errors

**Common causes and solutions**:
- **Missing protocol**: Use `http://localhost:3000`, not `localhost:3000`
- **Trailing slash**: Use `http://localhost:3000`, not `http://localhost:3000/`
- **Wrong protocol**: Ensure `http://` for local development, `https://` for production
- **Whitespace**: Remove spaces around origins in comma-separated lists

#### Issue: Preflight OPTIONS requests failing

**Cause**: Browser sends OPTIONS request before actual request, but CORS headers are missing.

**Solution**:
1. Verify CORS middleware is added in `main.py` (already configured)
2. Check that `CORS_ORIGINS` includes the requesting origin
3. Ensure the backend is running and accessible

#### Issue: "Credentials mode is 'include' but Access-Control-Allow-Credentials is missing"

**Cause**: Frontend is sending credentials (JWT tokens) but CORS is not configured to allow them.

**Solution**: This is already configured (`allow_credentials=True`). Verify:
1. `CORS_ORIGINS` is set to an explicit origin (not `*`)
2. Backend logs show "Allow Credentials: True"
3. Frontend is using the correct origin URL

### Testing CORS Configuration

**Test 1: Verify CORS headers in browser DevTools**
1. Open your frontend application in a browser
2. Open DevTools (F12) → Network tab
3. Make an API request to the backend
4. Click on the request and check Response Headers:
   - `access-control-allow-origin` should match your frontend URL
   - `access-control-allow-credentials` should be `true`

**Test 2: Test with curl**
```bash
curl -H "Origin: http://localhost:3000" \
     -H "Access-Control-Request-Method: POST" \
     -H "Access-Control-Request-Headers: Authorization,Content-Type" \
     -X OPTIONS \
     http://localhost:8000/api/tasks \
     -v
```

Expected response headers:
- `access-control-allow-origin: http://localhost:3000`
- `access-control-allow-credentials: true`
- `access-control-allow-methods: GET, POST, PUT, PATCH, DELETE`
- `access-control-allow-headers: Authorization, Content-Type`

## Authentication

All API endpoints (except the root endpoint) require JWT Bearer token authentication.

### Obtaining a Token

In production, tokens are issued by Better Auth on the frontend when users log in. For testing purposes, you can generate a test token using Python:

```python
import jwt
from datetime import datetime, timedelta

# Your secret from .env file
SECRET = "your-secure-secret-key-at-least-32-characters-long"

# Create a token for user ID 1
payload = {
    "sub": "1",  # User ID
    "exp": datetime.utcnow() + timedelta(hours=24)  # Expires in 24 hours
}

token = jwt.encode(payload, SECRET, algorithm="HS256")
print(f"Token: {token}")
```

### Using Swagger UI

1. Navigate to `http://localhost:8000/docs`
2. Click the "Authorize" button (lock icon)
3. Enter your token in the format: `Bearer <your-token>`
4. Click "Authorize"
5. All subsequent requests will include the authentication header

## Authentication Endpoints

The backend provides authentication endpoints for user registration and login.

### User Signup (Registration)

Create a new user account and receive a JWT token for immediate use.

**Endpoint**: `POST /api/auth/signup`

**Request Body**:
```json
{
  "email": "user@example.com",
  "password": "SecurePass123",
  "name": "John Doe"
}
```

**Password Requirements**:
- Minimum 8 characters
- At least one letter (a-z or A-Z)
- At least one number (0-9)

**Success Response** (201 Created):
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "token_type": "bearer",
  "user": {
    "id": 1,
    "email": "user@example.com",
    "name": "John Doe"
  }
}
```

**Error Responses**:
- `400 Bad Request`: Password too short, missing letter/number, or empty name
- `409 Conflict`: Email already registered
- `422 Unprocessable Entity`: Invalid email format

**Example with curl**:
```bash
curl -X POST http://localhost:8000/api/auth/signup \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "SecurePass123",
    "name": "John Doe"
  }'
```

### User Login

Authenticate with existing credentials and receive a JWT token.

**Endpoint**: `POST /api/auth/login`

**Request Body**:
```json
{
  "email": "user@example.com",
  "password": "SecurePass123"
}
```

**Success Response** (200 OK):
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "token_type": "bearer",
  "user": {
    "id": 1,
    "email": "user@example.com",
    "name": "John Doe"
  }
}
```

**Error Responses**:
- `401 Unauthorized`: Invalid email or password
- `422 Unprocessable Entity`: Invalid email format

**Example with curl**:
```bash
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "SecurePass123"
  }'
```

### Using the JWT Token

After signup or login, use the `access_token` from the response to authenticate subsequent requests:

```bash
# Save the token
TOKEN="eyJ0eXAiOiJKV1QiLCJhbGc..."

# Use it in requests
curl http://localhost:8000/api/users/1/tasks \
  -H "Authorization: Bearer $TOKEN"
```

**Token Details**:
- Expires after 24 hours
- Contains user ID and email in payload
- Must be included in `Authorization` header as `Bearer <token>`

### Troubleshooting Authentication Issues

#### Issue 1: "Email already registered" (409 Conflict)

**Cause**: Attempting to signup with an email that already exists in the database.

**Solution**:
- Use a different email address for signup
- Or login with the existing email and password
- To reset for testing: Delete the user from the database

#### Issue 2: "Invalid email or password" (401 Unauthorized)

**Possible Causes**:
1. Wrong password entered
2. Email doesn't exist in the database
3. Password was changed after account creation

**Solution**:
- Verify the email and password are correct
- Check for typos (passwords are case-sensitive)
- If forgotten, password reset is not yet implemented (out of scope)
- For testing: Create a new account with signup endpoint

#### Issue 3: "Password must be at least 8 characters" (400 Bad Request)

**Cause**: Password doesn't meet complexity requirements.

**Solution**: Ensure password has:
- At least 8 characters
- At least one letter (a-z or A-Z)
- At least one number (0-9)

**Valid Examples**:
- `SecurePass123`
- `MyPassword1`
- `Test1234`

**Invalid Examples**:
- `Pass1` (too short)
- `Password` (no number)
- `12345678` (no letter)

#### Issue 4: "Token has expired" (401 Unauthorized)

**Cause**: JWT token is older than 24 hours.

**Solution**:
- Login again to get a new token
- Tokens automatically expire for security
- Store the new token and use it for subsequent requests

#### Issue 5: "Invalid authentication token" (401 Unauthorized)

**Possible Causes**:
1. Token is malformed or corrupted
2. Token was generated with a different secret key
3. Token format is incorrect in Authorization header

**Solution**:
- Verify token format: `Authorization: Bearer <token>`
- Ensure no extra spaces or characters
- Get a fresh token by logging in again
- Check that BETTER_AUTH_SECRET is consistent

#### Issue 6: "Name cannot be empty" (400 Bad Request)

**Cause**: Name field is empty or contains only whitespace.

**Solution**:
- Provide a non-empty name during signup
- Name is required and cannot be just spaces

#### Issue 7: Database connection errors (500 Internal Server Error)

**Possible Causes**:
1. DATABASE_URL is incorrect or missing
2. Database server is not running
3. Network connectivity issues

**Solution**:
- Verify DATABASE_URL in `.env` file
- Check database server is running and accessible
- Test connection with database client
- Check backend logs for detailed error messages

## API Usage Examples

All examples below require a valid JWT token. Replace `YOUR_JWT_TOKEN` with your actual token.

### Create a new task
```bash
curl -X POST http://localhost:8000/api/tasks \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -d '{"title": "Buy groceries", "description": "Milk, bread, eggs", "user_id": 1}'
```

**Note:** The `user_id` in the request body is automatically set from the authenticated user's token and can be omitted.

### Get all tasks for authenticated user
```bash
curl http://localhost:8000/api/tasks \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

### Get a specific task
```bash
curl http://localhost:8000/api/tasks/1 \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

### Update a task
```bash
curl -X PUT http://localhost:8000/api/tasks/1 \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -d '{"title": "Updated task", "description": "Updated description", "completed": false}'
```

### Mark a task as complete
```bash
curl -X PATCH http://localhost:8000/api/tasks/1/complete \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -d '{"completed": true}'
```

### Delete a task
```bash
curl -X DELETE http://localhost:8000/api/tasks/1 \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

## Running Tests

```bash
# Run all tests
pytest backend/tests/

# Run specific test types
pytest backend/tests/unit/           # Unit tests
pytest backend/tests/integration/    # Integration tests
pytest backend/tests/contract/       # Contract tests

# Run with coverage
pytest backend/tests/ --cov=src --cov-report=html
```

## Features

- **JWT Authentication**: Secure token-based authentication
- **User Data Isolation**: Users can only access their own tasks
- **Token Expiry Enforcement**: Expired tokens are automatically rejected
- **Full CRUD operations**: Create, read, update, delete tasks
- **Task completion status management**: Mark tasks as complete/incomplete
- **Comprehensive error handling**: Proper HTTP status codes (401, 403, 404, 422)
- **Security logging**: Unauthorized access attempts are logged
- **Automatic API documentation**: Swagger UI and ReDoc with authentication support
- **Input validation**: Request data validation with clear error messages
- **Structured logging**: Detailed application logs

## Security

- All endpoints require valid JWT Bearer tokens
- Tokens are verified on every request
- User ID is extracted from token, not URL parameters
- Cross-user access attempts return 403 Forbidden
- Expired tokens return 401 Unauthorized
- JWT secret must be at least 32 characters
- Clock skew tolerance of 10 seconds for time synchronization

## Architecture

The application follows a clean architecture with separation of concerns:

- `models/` - Data models using SQLModel
- `api/` - API route handlers with authentication
- `services/` - Business logic and data access
- `database/` - Database connection and initialization
- `auth/` - JWT authentication and authorization
- `tests/` - Unit, integration, and contract tests

## API Endpoints

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| GET | `/` | Root endpoint | No |
| GET | `/api/tasks` | Get all tasks for authenticated user | Yes |
| POST | `/api/tasks` | Create a new task | Yes |
| GET | `/api/tasks/{id}` | Get a specific task | Yes |
| PUT | `/api/tasks/{id}` | Update a task | Yes |
| PATCH | `/api/tasks/{id}/complete` | Mark task as complete/incomplete | Yes |
| DELETE | `/api/tasks/{id}` | Delete a task | Yes |

## Error Responses

| Status Code | Description |
|-------------|-------------|
| 200 | Success |
| 201 | Created |
| 204 | No Content (successful deletion) |
| 400 | Bad Request (validation error) |
| 401 | Unauthorized (missing or invalid token) |
| 403 | Forbidden (insufficient permissions) |
| 404 | Not Found |
| 422 | Unprocessable Entity (validation error) |

## Development Notes

- User ID is automatically extracted from JWT token
- Tasks are filtered by authenticated user ID
- Ownership verification prevents cross-user access
- All authentication failures are logged for security monitoring
