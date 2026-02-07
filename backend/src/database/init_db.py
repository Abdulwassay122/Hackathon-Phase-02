from sqlmodel import SQLModel
from .database import engine


def create_db_and_tables():
    """
    Create database tables
    """
    SQLModel.metadata.create_all(bind=engine)
    print("Database tables created successfully")