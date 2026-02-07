from sqlmodel import SQLModel
from .database import engine
from ..models.user_model import User  # Import User model for table creation
from ..models.task_model import Task  # Import Task model for table creation


def create_db_and_tables():
    """
    Create database tables
    """
    SQLModel.metadata.create_all(bind=engine)
    print("Database tables created successfully")