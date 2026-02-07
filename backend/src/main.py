from fastapi import FastAPI
from .logging_config import setup_logging
from src.database.database import engine
from sqlmodel import SQLModel

# Set up logging
logger = setup_logging()

# Create FastAPI app
app = FastAPI(
    title="Todo Backend API",
    description="RESTful API for managing user tasks in a Todo application",
    version="1.0.0"
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
    app.include_router(task_router, prefix="/api/{user_id}", tags=["tasks"])

# Register routes after app is created
register_routes()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)