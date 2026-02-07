from fastapi import FastAPI
from fastapi.security import HTTPBearer
from .logging_config import setup_logging
from src.database.database import engine
from sqlmodel import SQLModel

# Set up logging
logger = setup_logging()

# T062: Configure Bearer authentication for Swagger UI
security = HTTPBearer()

# Create FastAPI app
app = FastAPI(
    title="Todo Backend API",
    description="""
RESTful API for managing user tasks in a Todo application.

## Authentication

All API endpoints (except root) require JWT Bearer token authentication.

To authenticate:
1. Obtain a JWT token from your authentication provider (Better Auth)
2. Click the "Authorize" button below
3. Enter your token in the format: `Bearer <your-token>`
4. All subsequent requests will include the authentication header

## Security

- All endpoints enforce user data isolation
- Tokens are verified on every request
- Expired tokens are automatically rejected
- Users can only access their own tasks
    """,
    version="2.0.0",
    swagger_ui_parameters={
        "persistAuthorization": True
    }
)

@app.on_event("startup")
async def startup_event():
    """
    Initialize database tables on startup
    """
    logger.info("Creating database tables...")
    SQLModel.metadata.create_all(bind=engine)
    logger.info("Database tables created successfully")


@app.get("/")
async def root():
    """
    Root endpoint
    """
    return {"message": "Welcome to the Todo Backend API"}

# Import and include API routes (moved to bottom to avoid circular imports)
def register_routes():
    from src.api.task_routes import router as task_router
    app.include_router(task_router, prefix="/api", tags=["tasks"])

# Register routes after app is created
register_routes()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)