# Quickstart Guide: Todo Backend

## Prerequisites
- Python 3.11+
- pip package manager
- Access to Neon Serverless PostgreSQL instance

## Setup Instructions

### 1. Clone the repository
```bash
git clone <repository-url>
cd <project-directory>
```

### 2. Create virtual environment and install dependencies
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install fastapi sqlmodel uvicorn psycopg2-binary python-dotenv pytest
```

### 3. Configure environment variables
Create a `.env` file in the project root with your database connection details:
```env
DATABASE_URL=postgresql://username:password@host:port/database_name
```

### 4. Initialize the database
```bash
# Run database migrations (not implemented in initial version)
# For now, the app will create tables automatically on startup
```

### 5. Start the development server
```bash
uvicorn backend.src.main:app --reload --port 8000
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
  -d '{"title": "Updated task", "description": "Updated description", "completed": false, "user_id": 1}'
```

### Mark a task as complete
```bash
curl -X PATCH http://localhost:8000/api/1/tasks/1/complete
```

### Delete a task
```bash
curl -X DELETE http://localhost:8000/api/1/tasks/1
```

## Running Tests
```bash
pytest backend/tests/
```