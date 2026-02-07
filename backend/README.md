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
