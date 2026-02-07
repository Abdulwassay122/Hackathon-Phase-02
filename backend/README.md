# Todo Backend API

A RESTful API for managing user tasks in a Todo application built with FastAPI and SQLModel.

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

Create a `.env` file in the project root with your database connection details:

```env
DATABASE_URL=postgresql://username:password@host:port/database_name
LOG_LEVEL=INFO
```

For local development with SQLite, you can use the default:

```env
DATABASE_URL=sqlite:///./todo_app.db
```

### 3. Start the development server

```bash
uvicorn src.main:app --reload --port 8000
```

The API will be available at `http://localhost:8000`

## API Usage Examples

### Create a new task
```bash
curl -X POST http://localhost:8000/api/1/tasks \
  -H "Content-Type: application/json" \
  -d '{"title": "Buy groceries", "description": "Milk, bread, eggs", "user_id": 1}'
```

### Get all tasks for user 1
```bash
curl http://localhost:8000/api/1/tasks
```

### Get a specific task
```bash
curl http://localhost:8000/api/1/tasks/1
```

### Update a task
```bash
curl -X PUT http://localhost:8000/api/1/tasks/1 \
  -H "Content-Type: application/json" \
  -d '{"title": "Updated task", "description": "Updated description", "completed": false}'
```

### Mark a task as complete
```bash
curl -X PATCH http://localhost:8000/api/1/tasks/1/complete \
  -H "Content-Type: application/json" \
  -d '{"completed": true}'
```

### Delete a task
```bash
curl -X DELETE http://localhost:8000/api/1/tasks/1
```

## Running Tests

```bash
# Run all tests
pytest backend/tests/

# Run specific test types
pytest backend/tests/unit/
pytest backend/tests/integration/
pytest backend/tests/contract/
```

## Features

- Full CRUD operations for tasks
- User-scoped tasks (tasks are isolated by user_id)
- Task completion status management
- Comprehensive error handling
- Automatic API documentation with Swagger UI and ReDoc
- Input validation
- Structured logging

## Architecture

The application follows a clean architecture with separation of concerns:

- `models/` - Data models using SQLModel
- `api/` - API route handlers
- `services/` - Business logic
- `database/` - Database connection and initialization
- `tests/` - Unit, integration, and contract tests